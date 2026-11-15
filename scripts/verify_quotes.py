#!/usr/bin/env python3
"""Verify that every panel quote in image_briefs.json exists verbatim in its chapter."""

import argparse
import json
import re
import sys


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def verify_quotes(chapters_path: str, briefs_path: str) -> int:
    with open(chapters_path, "r", encoding="utf-8") as f:
        chapters = json.load(f)
    with open(briefs_path, "r", encoding="utf-8") as f:
        briefs = json.load(f)

    entries = briefs if isinstance(briefs, list) else briefs.get("units", [])
    total_panels = 0
    mismatches: list[str] = []

    for entry in entries:
        unit_id = entry.get("unit_id", "UNKNOWN")
        part_file = entry.get("part_file", "")
        chapter = chapters.get(part_file)
        if not chapter:
            mismatches.append(f"{unit_id}: part_file '{part_file}' not found in chapters_raw.json")
            continue

        norm_text = _normalize(chapter.get("text", ""))
        panels = entry.get("panels", [])
        if len(panels) != 4:
            mismatches.append(f"{unit_id}: expected 4 panels, found {len(panels)}")

        for idx, panel in enumerate(panels, start=1):
            total_panels += 1
            quote = _normalize(panel.get("quote", ""))
            if not quote:
                mismatches.append(f"{unit_id} Panel {idx}: empty quote")
            elif quote not in norm_text:
                mismatches.append(
                    f"{unit_id} Panel {idx} ({part_file}): quote not found verbatim -> {quote[:80]!r}"
                )

    print(f"Verified {len(entries)} units ({total_panels} panels).")
    if mismatches:
        print(f"FAILED with {len(mismatches)} mismatch(es):")
        for err in mismatches:
            print(f"  - {err}")
        return 1

    print("PASS: 0 quote mismatches.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify verbatim panel quotes against extracted chapters.")
    parser.add_argument("--chapters", required=True, help="Path to chapters_raw.json")
    parser.add_argument("--briefs", required=True, help="Path to image_briefs.json")
    args = parser.parse_args()
    sys.exit(verify_quotes(args.chapters, args.briefs))


if __name__ == "__main__":
    main()
