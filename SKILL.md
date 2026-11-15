---
name: epub-novel-illustrator
description: >-
  Use when transforming an EPUB novel into an illustrated EPUB with per-chapter
  multi-panel artwork, source-grounded scene briefs, spoiler-free visual
  continuity, E-Ink grayscale optimization, and dedicated fullscreen
  illustration pages.
---

# EPUB Novel Illustrator

Transform an EPUB novel into a source-faithful illustrated EPUB with **one 4-panel illustration per target chapter**, placed on its own dedicated fullscreen page after each chapter.

**Core principle:** Narrative accuracy and source fidelity take precedence over visual spectacle. Never invent unsupported details or leak future plot spoilers.

## Non-Negotiable Rules

1. **Source fidelity & no unsupported invention:** Classify every visual detail as `CONFIRMED` (explicitly in text), `INTERPRETED` (conservative choice consistent with text), or `UNKNOWN` (do not invent). Never substitute generic genre tropes for actual scene events.
2. **Spoiler prevention (progressive references):** Chapter *N* briefs may use details established in Chapters `1..N` only—never future appearances, relationships, locations, or revelations.
3. **Original content immutability:** Never rewrite, shorten, reorder, or alter original chapter text, metadata, CSS, or TOC navigation. Only add illustration images, dedicated illustration XHTML pages, and the OPF `<manifest>`/`<spine>` entries needed to display them.
4. **Zero text in artwork:** Unless explicitly required by the brief, panels must contain **no speech bubbles, captions, sound effects, labels, or watermarks**.

## Workflow

### Phase 1: EPUB Inspection & Chapter Inventory
Run [inspect_epub.py](./scripts/inspect_epub.py) on the input `.epub`:
```bash
python scripts/inspect_epub.py "<input.epub>" --out-dir ./work
```
This extracts `work/spine_summary.json` and `work/chapters_raw.json` without modifying the source EPUB.
- Do not assume 1 XHTML file = 1 chapter; inspect headings and boundaries to distinguish front matter, part dividers, and narrative chapters.
- Build a production manifest mapping each `unit_id` (`U-01`, `U-02`, ...) to its exact title, `part_file`, reading order, and status.

### Phase 2: Art Direction & User Confirmation Gate
Before generating images, confirm with the user:
1. **Target chapters** (all chapters, or a subset/skip range).
2. **Target device & style** (default: **Kindle Paperwhite 7th Gen** — `1072x1448` 3:4 portrait, 300 ppi, 16-level grayscale high-contrast ink & wash). See [art-direction-eink.md](./references/art-direction-eink.md).
3. **Pilot batch approval:** Generate the first **3** chapters (`U-01`–`U-03`, or first 3 active chapters) and get user approval before scaling.

### Phase 3: Narrative Analysis & Verbatim Quote Verification
For each target chapter:
- Read **only** that chapter's text (plus the progressive visual reference log up to chapter `N-1`).
- Select **4 complementary visual beats** representing actual events, character interactions, discoveries, or setting shifts.
- Record a **verbatim supporting quote** from `chapters_raw.json` for every panel, and update the progressive visual reference guide.
- Compile `work/image_briefs.json` and verify **0 quote mismatches** before generating any images:
```bash
python scripts/verify_quotes.py --chapters work/chapters_raw.json --briefs work/image_briefs.json
```

### Phase 4–6: Batched Image Generation & Visual QC
- Respect delegation/subagent limits (e.g., max **3** `image-generator` subagents in parallel; wait for all 3 to finish before launching the next batch).
- Assign **1 illustration per `image-generator` subagent**, passing the approved 4-panel prompt and device style rules.
- **Inspect every generated image directly** via image-reading tool against [qc-checklist.md](./references/qc-checklist.md). Reject and regenerate any image with:
  - Wrong panel count (must be exactly 4)
  - Speech bubbles, captions, or garbled text
  - Color bleed (for B&W E-Ink targets)
  - Narrative inaccuracy, missing key details, or future spoilers
- **Quota (`429 RESOURCE_EXHAUSTED`) handling:** Never retry immediately on quota exhaustion. Record the exact completed/failed units and reset timestamp, and either schedule a one-shot wakeup timer past reset or pause cleanly for user confirmation.

### Phase 7: Fullscreen EPUB Compilation & Validation
Once all target illustrations pass QC, run [compile_epub.py](./scripts/compile_epub.py):
```bash
python scripts/compile_epub.py "<input.epub>" \
  --briefs work/image_briefs.json \
  --images-map work/approved_images.json \
  --out "<output_illustrated.epub>"
```
The compiler:
- Converts each approved image to 8-bit grayscale JPEG sized to `1072x1448` (configurable via `--width`, `--height`, `--color`).
- Creates one dedicated fullscreen XHTML page (`text/illus_<unit_id>.html`) per illustration (`margin:0; padding:0`, centered `max-width:100%; max-height:100%`).
- Registers images and XHTML pages in `content.opf` `<manifest>` and inserts each illustration page immediately after its chapter in `<spine>`.
- Validates ZIP structure (`mimetype` stored uncompressed first), XML/OPF well-formedness, and complete manifest/spine integrity.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Subagent adds speech bubbles or narrative captions | Explicitly forbid text/captions/SFX in prompt; inspect every image and regenerate on violation |
| Subtle color tints (green LEDs, warm sepia) in B&W prompts | Enforce strict monochrome grayscale in prompt AND convert to 8-bit grayscale (`L` mode) in `compile_epub.py` |
| Subagent saves images to root artifact directory ignoring subfolder | Track exact returned file paths in `approved_images.json` rather than assuming subfolder paths |
| Inserting illustration inside chapter HTML breaks Calibre page-break anchors | Keep original chapter HTML untouched; insert a dedicated XHTML page immediately after the chapter in `content.opf` `<spine>` |
| Retrying immediately after `429` image quota error | Stop batch, log progress + reset time, and wait past reset before resuming |
