#!/usr/bin/env python3
"""Inspect an EPUB archive and extract spine metadata and chapter text."""

import argparse
import json
import os
import posixpath
import re
import zipfile
from html.parser import HTMLParser
import xml.etree.ElementTree as ET


class _TextExtractor(HTMLParser):
    """Extract readable text and first heading from an XHTML document."""

    def __init__(self) -> None:
        super().__init__()
        self._skip = False
        self._in_heading = False
        self.headings: list[str] = []
        self._current_heading: list[str] = []
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t in ("script", "style"):
            self._skip = True
        elif t in ("h1", "h2", "h3"):
            self._in_heading = True
            self._current_heading = []
        elif t in ("p", "div", "br", "li", "blockquote", "h1", "h2", "h3", "h4"):
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in ("script", "style"):
            self._skip = False
        elif t in ("h1", "h2", "h3") and self._in_heading:
            self._in_heading = False
            heading = re.sub(r"\s+", " ", "".join(self._current_heading)).strip()
            if heading:
                self.headings.append(heading)
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        self._chunks.append(data)
        if self._in_heading:
            self._current_heading.append(data)

    def get_text(self) -> str:
        raw = "".join(self._chunks)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
        return "\n".join(line for line in lines if line)


def _find_opf_path(zf: zipfile.ZipFile) -> str:
    container_xml = zf.read("META-INF/container.xml")
    root = ET.fromstring(container_xml)
    for elem in root.iter():
        if elem.tag.endswith("rootfile") and "full-path" in elem.attrib:
            return elem.attrib["full-path"]
    raise ValueError("Could not locate OPF rootfile in META-INF/container.xml")


def inspect_epub(epub_path: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    with zipfile.ZipFile(epub_path, "r") as zf:
        opf_path = _find_opf_path(zf)
        opf_dir = posixpath.dirname(opf_path)
        opf_root = ET.fromstring(zf.read(opf_path))

        version = opf_root.attrib.get("version", "unknown")
        metadata: dict[str, str] = {}
        manifest: dict[str, dict[str, str]] = {}
        spine_ids: list[str] = []

        for child in opf_root:
            tag = child.tag.split("}")[-1]
            if tag == "metadata":
                for meta in child:
                    mtag = meta.tag.split("}")[-1]
                    if meta.text and meta.text.strip():
                        metadata.setdefault(mtag, meta.text.strip())
            elif tag == "manifest":
                for item in child:
                    if item.tag.split("}")[-1] == "item":
                        manifest[item.attrib["id"]] = {
                            "href": item.attrib["href"],
                            "media_type": item.attrib.get("media-type", ""),
                        }
            elif tag == "spine":
                for itemref in child:
                    if itemref.tag.split("}")[-1] == "itemref":
                        spine_ids.append(itemref.attrib["idref"])

        spine_summary = []
        chapters_raw = {}

        for idx, idref in enumerate(spine_ids, start=1):
            item = manifest.get(idref)
            if not item:
                continue
            href = item["href"]
            arc_path = posixpath.normpath(posixpath.join(opf_dir, href)) if opf_dir else href
            text = ""
            headings: list[str] = []
            word_count = 0

            if "html" in item["media_type"] or href.endswith((".html", ".xhtml", ".htm")):
                raw_html = zf.read(arc_path).decode("utf-8", errors="replace")
                parser = _TextExtractor()
                parser.feed(raw_html)
                text = parser.get_text()
                headings = parser.headings
                word_count = len(text.split())

            spine_summary.append(
                {
                    "spine_index": idx,
                    "idref": idref,
                    "href": href,
                    "archive_path": arc_path,
                    "media_type": item["media_type"],
                    "headings": headings,
                    "word_count": word_count,
                }
            )
            chapters_raw[href] = {
                "spine_index": idx,
                "idref": idref,
                "archive_path": arc_path,
                "headings": headings,
                "word_count": word_count,
                "text": text,
            }

        summary_payload = {
            "epub_path": os.path.abspath(epub_path),
            "epub_version": version,
            "opf_path": opf_path,
            "metadata": metadata,
            "manifest_count": len(manifest),
            "spine_count": len(spine_ids),
            "spine": spine_summary,
        }

        summary_file = os.path.join(out_dir, "spine_summary.json")
        chapters_file = os.path.join(out_dir, "chapters_raw.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_payload, f, indent=2, ensure_ascii=False)
        with open(chapters_file, "w", encoding="utf-8") as f:
            json.dump(chapters_raw, f, indent=2, ensure_ascii=False)

        print(f"EPUB Version : {version}")
        print(f"OPF Path     : {opf_path}")
        print(f"Manifest     : {len(manifest)} items")
        print(f"Spine        : {len(spine_ids)} items")
        print(f"Saved        : {summary_file}")
        print(f"Saved        : {chapters_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect an EPUB and extract chapter text.")
    parser.add_argument("epub", help="Path to the source .epub file")
    parser.add_argument("--out-dir", default="./work", help="Output directory for extracted JSON")
    args = parser.parse_args()
    inspect_epub(args.epub, args.out_dir)


if __name__ == "__main__":
    main()
