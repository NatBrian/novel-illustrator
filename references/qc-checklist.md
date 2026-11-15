# Illustration Quality-Control (QC) Checklist

Inspect **every** generated illustration directly before marking its unit `PASS`.

## 1. Format & Composition
- [ ] **Exact panel count:** Exactly 4 distinct panels (never 3, 5, or merged/ambiguous borders).
- [ ] **Aspect ratio:** Vertical `3:4` portrait suitable for fullscreen page display.
- [ ] **Borders & gutters:** Clean white gutters and solid black borders separating all 4 panels.
- [ ] **Zero text:** No speech bubbles, no narrative caption boxes, no sound effects, no garbled text or watermarks.

## 2. E-Ink Visual Quality (for B&W targets)
- [ ] **Strict monochrome:** No color bleed (watch out for colored indicator LEDs, glowing screens, or warm/cool tints).
- [ ] **Readability:** Strong black/white separation; faces, props, and focal actions are not lost in muddy dark gray.

## 3. Narrative Fidelity & Continuity
- [ ] **Beat alignment:** Each panel clearly depicts its assigned beat from `image_briefs.json`.
- [ ] **Character & prop consistency:** Matches established physical traits, attire, and tech from the progressive reference guide.
- [ ] **Zero unsupported invention:** No ungrounded sci-fi/fantasy clichés (e.g., random spaceships, holograms, armor, or castles not in the scene).
- [ ] **Zero spoilers:** Contains no characters, objects, identities, or locations revealed only in later chapters.

## Decision
- **PASS:** All checks satisfied → record path in `approved_images.json`.
- **FAIL:** Any check fails → log specific failure reason and regenerate (or target-edit if minor and quota allows).
