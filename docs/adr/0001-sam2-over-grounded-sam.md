# ADR-0001: SAM 2 over Grounded-SAM for video labeling

## Status

Accepted

## Context

We need an annotation acceleration tool for YOLO person detection training. The raw material is video footage from a fixed warehouse door camera. The goal is to produce bounding-box labels with minimal manual effort.

Two candidate approaches:

- **Grounded-SAM**: Grounding DINO performs open-vocabulary detection ("person") on every frame independently, then SAM refines each detection into a mask → box. Fully automatic, zero prompts.
- **SAM 2**: User provides one prompt (click or box) per person, SAM 2 propagates that identity through all video frames. Semi-automatic, requires manual prompting.

## Decision

Use **SAM 2** (tiny variant) as the core auto-labeling engine.

## Rationale

1. **Identity consistency matters more than full automation.** In a multi-person tracking task, Grounded-SAM detects each frame independently with no identity linking. Identity switches between frames are frequent (person A detected in frame 1, person B in frame 2, no way to know they differ). Correcting identity switches across hundreds of frames is more labor-intensive than providing 2–5 prompts per video upfront.

2. **SAM 2's temporal propagation handles occlusion.** The warehouse setting has racks, pillars, and people walking behind each other. SAM 2's visual memory recovers identity after occlusion. Grounded-SAM re-detects from scratch and may assign a different instance.

3. **Fixed camera, few subjects.** Warehouse door camera is static. Typical scene: 1–5 people transiting. Prompt cost is negligible (1 click per person × 3 people = 3 clicks for a full video) compared to the review cost of fixing identity-swapped labels from Grounded-SAM.

4. **Model size.** SAM 2 tiny (~47M params) fits commodity GPU (8 GB VRAM). Grounding DINO + SAM combined are significantly heavier.

## Consequences

- User must manually prompt each person. Acceptable given the low person count per video.
- If two people stand very close together, SAM 2 may merge their masks. The review stage handles this via manual box correction.
- Grounded-SAM remains a viable fallback if the person count grows significantly (e.g., 20+ simultaneous subjects) where prompt cost becomes prohibitive.
