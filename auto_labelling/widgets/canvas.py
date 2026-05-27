from enum import Enum, auto
from pathlib import Path
from typing import Optional

import numpy as np
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QLineF
from PySide6.QtGui import (
    QPixmap, QPainter, QPen, QColor, QBrush, QImage,
    QWheelEvent, QMouseEvent, QKeyEvent, QFont,
)
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsItem, QRubberBand,
)

from auto_labelling.models.annotation import BBox
from auto_labelling.models.track import Track
from auto_labelling.app.constants import CANVAS_BG_COLOR


class CanvasMode(Enum):
    VIEW = auto()
    PROMPT_CLICK = auto()
    PROMPT_BOX = auto()
    EDIT = auto()


class BoxHandle(Enum):
    NONE = auto()
    MOVE = auto()
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()


HANDLE_SIZE = 8
MIN_BOX_SIZE = 5


class BoxGraphicsItem(QGraphicsRectItem):
    def __init__(self, track: Track, frame_idx: int, img_w: int, img_h: int, parent=None):
        self._track = track
        self._frame_idx = frame_idx
        self._img_w = img_w
        self._img_h = img_h
        self._bbox: Optional[BBox] = None

        ann = track.get_annotation(frame_idx)
        if ann and ann.bbox:
            self._bbox = ann.bbox
            x1, y1, x2, y2 = ann.bbox.to_xyxy(img_w, img_h)
            super().__init__(x1, y1, x2 - x1, y2 - y1, parent)
        else:
            super().__init__(0, 0, 0, 0, parent)

        color = QColor(track.color)
        color.setAlpha(180)
        self._pen = QPen(color, 2)
        self._pen_selected = QPen(color, 3)
        self._brush = QBrush(QColor(track.color + "30"))

        self.setPen(self._pen)
        self.setBrush(self._brush)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)
        self.setZValue(10)

    @property
    def track(self) -> Track:
        return self._track

    @property
    def frame_idx(self) -> int:
        return self._frame_idx

    @property
    def bbox(self) -> Optional[BBox]:
        return self._bbox

    def update_from_annotation(self):
        ann = self._track.get_annotation(self._frame_idx)
        if ann and ann.bbox:
            self._bbox = ann.bbox
            x1, y1, x2, y2 = ann.bbox.to_xyxy(self._img_w, self._img_h)
            self.setRect(x1, y1, x2 - x1, y2 - y1)

    def update_bbox_from_rect(self):
        r = self.rect()
        self._bbox = BBox.from_xyxy(
            r.x(), r.y(), r.x() + r.width(), r.y() + r.height(),
            self._img_w, self._img_h,
        )

    def paint(self, painter: QPainter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(self._pen_selected)
            r = self.rect()
            painter.drawRect(r)
            h = HANDLE_SIZE
            handles = [
                QRectF(r.left() - h / 2, r.top() - h / 2, h, h),
                QRectF(r.right() - h / 2, r.top() - h / 2, h, h),
                QRectF(r.left() - h / 2, r.bottom() - h / 2, h, h),
                QRectF(r.right() - h / 2, r.bottom() - h / 2, h, h),
            ]
            painter.setBrush(QColor(255, 255, 255))
            for handle in handles:
                painter.drawRect(handle)

    def handle_at(self, pos: QPointF) -> BoxHandle:
        r = self.rect()
        h = HANDLE_SIZE
        handles = {
            BoxHandle.TOP_LEFT: QRectF(r.left() - h, r.top() - h, h * 2, h * 2),
            BoxHandle.TOP_RIGHT: QRectF(r.right() - h, r.top() - h, h * 2, h * 2),
            BoxHandle.BOTTOM_LEFT: QRectF(r.left() - h, r.bottom() - h, h * 2, h * 2),
            BoxHandle.BOTTOM_RIGHT: QRectF(r.right() - h, r.bottom() - h, h * 2, h * 2),
        }
        for handle, area in handles.items():
            if area.contains(pos):
                return handle
        if self.contains(pos):
            return BoxHandle.MOVE
        return BoxHandle.NONE


class CanvasWidget(QGraphicsView):
    frame_changed = Signal(int)
    box_selected = Signal(object)
    box_modified = Signal(object, object)  # track, annotation
    prompt_created = Signal(dict)  # {frame_idx, type: "click"|"box", data: {...}}
    mode_changed = Signal(CanvasMode)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self.setBackgroundBrush(QColor(*CANVAS_BG_COLOR))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self._mode: CanvasMode = CanvasMode.VIEW
        self._current_frame: int = 0
        self._image_items: dict[int, QGraphicsPixmapItem] = {}
        self._box_items: dict[str, dict[int, BoxGraphicsItem]] = {}
        self._mask_items: dict[str, dict[int, QGraphicsPixmapItem]] = {}
        self._show_masks: bool = False
        self._image_dir: Optional[Path] = None
        self._image_files: list[str] = []
        self._img_size: tuple[int, int] = (640, 480)
        self._tracks: list[Track] = []
        self._panning: bool = False
        self._last_pan_pos: QPointF = QPointF()
        self._drawing_box: bool = False
        self._draw_start: QPointF = QPointF()
        self._rubber_band: Optional[QRubberBand] = None
        self._resizing: bool = False
        self._resize_handle: BoxHandle = BoxHandle.NONE
        self._resize_orig_rect: QRectF = QRectF()
        self._moving: bool = False
        self._move_orig_pos: QPointF = QPointF()
        self._zoom_level: float = 1.0

    @property
    def mode(self) -> CanvasMode:
        return self._mode

    def set_mode(self, mode: CanvasMode):
        self._mode = mode
        if mode == CanvasMode.VIEW:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif mode in (CanvasMode.PROMPT_CLICK, CanvasMode.PROMPT_BOX):
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self._scene.clearSelection()
        elif mode == CanvasMode.EDIT:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.mode_changed.emit(mode)

    def set_show_masks(self, show: bool):
        self._show_masks = show
        self._update_mask_visibility()

    def load_project(self, image_dir: Path, image_files: list[str],
                     img_size: tuple[int, int], tracks: list[Track]):
        self._image_dir = image_dir
        self._image_files = image_files
        self._img_size = img_size
        self._tracks = tracks
        self._image_items.clear()
        self._box_items.clear()
        self._mask_items.clear()
        self._scene.clear()
        self._current_frame = 0
        self._show_frame(0)

    def set_frame(self, frame_idx: int):
        if 0 <= frame_idx < len(self._image_files):
            self._current_frame = frame_idx
            self._show_frame(frame_idx)

    def _show_frame(self, frame_idx: int):
        self._scene.clear()
        self._image_items.clear()
        self._box_items.clear()
        self._mask_items.clear()

        if not self._image_dir or frame_idx >= len(self._image_files):
            return

        path = self._image_dir / self._image_files[frame_idx]
        if not path.exists():
            return

        pixmap = QPixmap(str(path))
        item = self._scene.addPixmap(pixmap)
        item.setZValue(0)
        self._image_items[frame_idx] = item

        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_level = 1.0

        for track in self._tracks:
            ann = track.get_annotation(frame_idx)
            if ann and ann.bbox:
                box_item = BoxGraphicsItem(track, frame_idx, self._img_size[0], self._img_size[1])
                self._scene.addItem(box_item)
                self._box_items.setdefault(track.id, {})[frame_idx] = box_item

        if self._show_masks:
            self._show_mask_overlays(frame_idx)

    def _show_mask_overlays(self, frame_idx: int):
        mask_dir = self._image_dir / ".masks"
        if not mask_dir.exists():
            return
        for track in self._tracks:
            mask_file = mask_dir / track.id / f"frame_{frame_idx:06d}.npy"
            if mask_file.exists():
                mask = np.load(str(mask_file))
                if mask.shape:
                    color = QColor(track.color)
                    overlay = np.zeros((mask.shape[0], mask.shape[1], 4), dtype=np.uint8)
                    overlay[mask, :] = [color.red(), color.green(), color.blue(), 80]
                    qimg = QImage(overlay.data, overlay.shape[1], overlay.shape[0],
                                  QImage.Format.Format_RGBA8888)
                    pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(qimg))
                    pixmap_item.setZValue(5)
                    self._scene.addItem(pixmap_item)
                    self._mask_items.setdefault(track.id, {})[frame_idx] = pixmap_item

    def _update_mask_visibility(self):
        for track_items in self._mask_items.values():
            for item in track_items.values():
                item.setVisible(self._show_masks)

    def set_image_size(self, w: int, h: int):
        self._img_size = (w, h)

    # --- Mouse events ---

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 0.87
            self.scale(factor, factor)
            self._zoom_level *= factor
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_pan_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        scene_pos = self.mapToScene(event.pos())

        if self._mode == CanvasMode.PROMPT_CLICK:
            if event.button() == Qt.MouseButton.LeftButton:
                self.prompt_created.emit({
                    "frame_idx": self._current_frame,
                    "type": "click",
                    "point": {"x": scene_pos.x(), "y": scene_pos.y()},
                })
                event.accept()
                return

        elif self._mode == CanvasMode.PROMPT_BOX:
            if event.button() == Qt.MouseButton.LeftButton:
                self._draw_start = scene_pos
                self._drawing_box = True
                event.accept()
                return

        elif self._mode == CanvasMode.EDIT:
            if event.button() == Qt.MouseButton.LeftButton:
                item = self._scene.itemAt(scene_pos, self.transform())
                if isinstance(item, BoxGraphicsItem):
                    handle = item.handle_at(item.mapFromScene(scene_pos))
                    if handle == BoxHandle.MOVE:
                        self._moving = True
                        self._move_orig_pos = scene_pos
                        self._scene.clearSelection()
                        item.setSelected(True)
                        self.box_selected.emit(item)
                    elif handle != BoxHandle.NONE:
                        self._resizing = True
                        self._resize_handle = handle
                        self._resize_orig_rect = item.rect()
                        self._scene.clearSelection()
                        item.setSelected(True)
                        self.box_selected.emit(item)
                    else:
                        self._scene.clearSelection()
                        self.box_selected.emit(None)
                else:
                    self._scene.clearSelection()
                    self.box_selected.emit(None)
                    # Start drawing new box
                    self._draw_start = scene_pos
                    self._drawing_box = True
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._panning:
            delta = event.pos() - self._last_pan_pos
            self._last_pan_pos = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        scene_pos = self.mapToScene(event.pos())

        if self._moving:
            items = self._scene.selectedItems()
            for item in items:
                if isinstance(item, BoxGraphicsItem):
                    delta = scene_pos - self._move_orig_pos
                    r = item.rect()
                    item.setRect(r.x() + delta.x(), r.y() + delta.y(), r.width(), r.height())
                    self._move_orig_pos = scene_pos
            event.accept()
            return

        if self._resizing:
            items = self._scene.selectedItems()
            for item in items:
                if isinstance(item, BoxGraphicsItem):
                    r = self._resize_orig_rect
                    h = self._resize_handle
                    x, y, w, h_val = r.x(), r.y(), r.width(), r.height()
                    if h in (BoxHandle.TOP_LEFT, BoxHandle.BOTTOM_LEFT):
                        x = scene_pos.x()
                        w = r.right() - x
                    elif h in (BoxHandle.TOP_RIGHT, BoxHandle.BOTTOM_RIGHT):
                        w = scene_pos.x() - r.left()
                    if h in (BoxHandle.TOP_LEFT, BoxHandle.TOP_RIGHT):
                        y = scene_pos.y()
                        h_val = r.bottom() - y
                    elif h in (BoxHandle.BOTTOM_LEFT, BoxHandle.BOTTOM_RIGHT):
                        h_val = scene_pos.y() - r.top()
                    if w > MIN_BOX_SIZE and h_val > MIN_BOX_SIZE:
                        item.setRect(x, y, w, h_val)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton and self._panning:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        if self._drawing_box:
            self._drawing_box = False
            end_pos = self.mapToScene(event.pos())
            r = QRectF(self._draw_start, end_pos).normalized()

            if self._mode == CanvasMode.PROMPT_BOX:
                if r.width() > MIN_BOX_SIZE and r.height() > MIN_BOX_SIZE:
                    self.prompt_created.emit({
                        "frame_idx": self._current_frame,
                        "type": "box",
                        "box": {
                            "x1": r.left(), "y1": r.top(),
                            "x2": r.right(), "y2": r.bottom(),
                        },
                    })
            elif self._mode == CanvasMode.EDIT:
                if r.width() > MIN_BOX_SIZE and r.height() > MIN_BOX_SIZE:
                    # Will be handled by the parent via signal
                    pass

            event.accept()
            return

        if self._moving:
            self._moving = False
            items = self._scene.selectedItems()
            for item in items:
                if isinstance(item, BoxGraphicsItem):
                    old_bbox = item.bbox
                    item.update_bbox_from_rect()
                    self.box_modified.emit(item.track, item.track.get_annotation(item.frame_idx))
            event.accept()
            return

        if self._resizing:
            self._resizing = False
            self._resize_handle = BoxHandle.NONE
            items = self._scene.selectedItems()
            for item in items:
                if isinstance(item, BoxGraphicsItem):
                    old_bbox = item.bbox
                    item.update_bbox_from_rect()
                    self.box_modified.emit(item.track, item.track.get_annotation(item.frame_idx))
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def delete_selected_boxes(self):
        for item in list(self._scene.selectedItems()):
            if isinstance(item, BoxGraphicsItem):
                item.track.remove_annotation(item.frame_idx)
                self._scene.removeItem(item)
                self.box_modified.emit(item.track, None)

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
