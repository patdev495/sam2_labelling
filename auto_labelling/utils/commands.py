from abc import ABC, abstractmethod
from typing import Optional

from auto_labelling.models.annotation import BBox


class Command(ABC):
    @abstractmethod
    def execute(self) -> bool:
        ...

    @abstractmethod
    def undo(self):
        ...

    @property
    def description(self) -> str:
        return self.__class__.__name__


class CommandHistory:
    def __init__(self, max_depth: int = 100):
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []
        self._max_depth = max_depth
        self._merge_cursor: Optional[Command] = None
        self._on_change = None

    def set_on_change(self, callback):
        self._on_change = callback

    def execute(self, cmd: Command) -> bool:
        if cmd.execute():
            self._undo_stack.append(cmd)
            if len(self._undo_stack) > self._max_depth:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
            if self._on_change:
                self._on_change()
            return True
        return False

    def undo(self):
        if not self._undo_stack:
            return
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        if self._on_change:
            self._on_change()

    def redo(self):
        if not self._redo_stack:
            return
        cmd = self._redo_stack.pop()
        cmd.execute()
        self._undo_stack.append(cmd)
        if self._on_change:
            self._on_change()

    @property
    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    @property
    def undo_description(self) -> str:
        return self._undo_stack[-1].description if self._undo_stack else ""

    @property
    def redo_description(self) -> str:
        return self._redo_stack[-1].description if self._redo_stack else ""

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
        if self._on_change:
            self._on_change()


class AddBoxCommand(Command):
    def __init__(self, track, annotation):
        self.track = track
        self.annotation = annotation

    def execute(self) -> bool:
        self.track.add_annotation(self.annotation)
        return True

    def undo(self):
        self.track.remove_annotation(self.annotation.frame_idx)

    @property
    def description(self) -> str:
        return "Add box"


class DeleteBoxCommand(Command):
    def __init__(self, track, annotation):
        self.track = track
        self.annotation = annotation

    def execute(self) -> bool:
        self.track.remove_annotation(self.annotation.frame_idx)
        return True

    def undo(self):
        self.track.add_annotation(self.annotation)

    @property
    def description(self) -> str:
        return "Delete box"


class MoveBoxCommand(Command):
    def __init__(self, annotation, old_bbox: BBox, new_bbox: BBox):
        self.annotation = annotation
        self.old_bbox = old_bbox
        self.new_bbox = new_bbox

    def execute(self) -> bool:
        self.annotation.bbox = self.new_bbox
        return True

    def undo(self):
        self.annotation.bbox = self.old_bbox

    @property
    def description(self) -> str:
        return "Move box"


class ResizeBoxCommand(Command):
    def __init__(self, annotation, old_bbox: BBox, new_bbox: BBox):
        self.annotation = annotation
        self.old_bbox = old_bbox
        self.new_bbox = new_bbox

    def execute(self) -> bool:
        self.annotation.bbox = self.new_bbox
        return True

    def undo(self):
        self.annotation.bbox = self.old_bbox

    @property
    def description(self) -> str:
        return "Resize box"


class ChangeClassCommand(Command):
    def __init__(self, annotation, old_class_id: int, new_class_id: int):
        self.annotation = annotation
        self.old_class_id = old_class_id
        self.new_class_id = new_class_id

    def execute(self) -> bool:
        self.annotation.class_id = self.new_class_id
        return True

    def undo(self):
        self.annotation.class_id = self.old_class_id

    @property
    def description(self) -> str:
        return "Change class"
