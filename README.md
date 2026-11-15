# epub-novel-illustrator

An Antigravity agent skill and Python toolkit for transforming EPUB novels into source-faithful illustrated editions—featuring 4-panel per-chapter artwork, verbatim quote verification, spoiler-free progressive visual continuity, Kindle Paperwhite / E-Ink grayscale optimization, and dedicated fullscreen illustration pages.

## Features

- **Source-Grounded 4-Panel Storytelling:** Every panel is anchored to a verbatim quote from its assigned chapter with zero unsupported invention and zero future plot spoilers.
- **Progressive Visual Reference Sharing:** Character, clothing, object, and location continuity advances strictly chapter-by-chapter (`1..N`).
- **E-Ink / Kindle Paperwhite Optimization:** Targets `1072x1448` (3:4 portrait, 300 ppi) 8-bit grayscale high-contrast ink & wash, free of speech bubbles, captions, or color bleed.
- **Immutable Original Text:** Preserves all original EPUB chapters, metadata, CSS, and TOC navigation; inserts each approved illustration on its own dedicated fullscreen XHTML page immediately after its chapter in `<spine>`.
- **Automated Verification & Compilation:** Includes reusable scripts for EPUB spine inspection, verbatim quote checking, and validated EPUB packaging.

## Repository Structure

```text
epub-novel-illustrator/
├── SKILL.md                       # Antigravity skill definition & workflow
├── README.md
├── .gitignore
├── references/
│   ├── art-direction-eink.md      # E-Ink / Kindle Paperwhite visual rules
│   └── qc-checklist.md            # Independent illustration QC checklist
└── scripts/
    ├── inspect_epub.py            # Extract OPF metadata, spine & chapter text
    ├── verify_quotes.py           # Verify verbatim panel quotes against chapters
    └── compile_epub.py            # Convert images & compile fullscreen-page EPUB
```

## Installation (Antigravity)

Copy or symlink this repository into your global Antigravity skills directory (or a workspace's `.agents/skills/` folder):

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse -Force .\epub-novel-illustrator "$env:USERPROFILE\.gemini\config\skills\epub-novel-illustrator"
```

**macOS / Linux:**
```bash
cp -r ./epub-novel-illustrator ~/.gemini/config/skills/epub-novel-illustrator
```

Once installed, Antigravity will automatically discover `epub-novel-illustrator` when you ask to illustrate an EPUB novel.

## CLI Toolkit Usage

Requires Python 3.10+ and `Pillow` (`pip install Pillow`) for `compile_epub.py`.

1. **Inspect an EPUB:**
   ```bash
   python scripts/inspect_epub.py "novel.epub" --out-dir ./work
   ```
2. **Verify panel quotes against extracted chapter text:**
   ```bash
   python scripts/verify_quotes.py --chapters work/chapters_raw.json --briefs work/image_briefs.json
   ```
3. **Compile the illustrated EPUB (8-bit grayscale `1072x1448` by default):**
   ```bash
   python scripts/compile_epub.py "novel.epub" \
     --briefs work/image_briefs.json \
     --images-map work/approved_images.json \
     --out "novel_illustrated.epub"
   ```
