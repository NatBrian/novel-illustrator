# E-Ink & Kindle Paperwhite Art Direction

Default target specification: **Kindle Paperwhite 7th Gen** (and compatible 300 ppi Carta E-Ink readers).

## Technical Display Constraints
- **Aspect Ratio & Resolution:** `3:4` vertical portrait (`1072 x 1448` px).
- **Color Space:** Strict **8-bit grayscale** (`L` mode JPEG, zero RGB color tint).
- **Contrast:** High-contrast black-and-white graphic-novel ink & wash. Pure black (`#000000`) linework, bold chiaroscuro shadows, clean mid-tone ink wash/hatching, and crisp white highlights (`#FFFFFF`) so panels remain legible without muddy grays on 16-level E-Ink.
- **Panel Layout:** Exactly **4 distinct panels** per page (2x2 grid or dynamic 4-panel storytelling layout) separated by crisp white gutters (`~16-24 px` equivalent) and solid black panel borders.

## Prompt Guardrails
Include these directives in every `image-generator` brief:
1. **Strict Monochrome:** `"Pure black-and-white ink and grayscale wash illustration, zero color, no sepia, no colored LEDs or UI glow."`
2. **No Text:** `"No speech bubbles, no dialogue, no caption boxes, no sound effects, no labels, no page numbers, no watermarks."`
3. **4-Panel Framing:** `"Single vertical 3:4 portrait page composed of exactly 4 distinct rectangular panels with crisp white gutters and solid black panel borders, reading top-left (Panel 1), top-right (Panel 2), bottom-left (Panel 3), bottom-right (Panel 4)."`
4. **Progressive Continuity:** Pass only visual descriptions of characters, clothing, interfaces, or environments established up to the current chapter. Never back-port later reveals.
