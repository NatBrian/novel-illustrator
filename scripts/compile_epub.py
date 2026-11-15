#!/usr/bin/env python3
"""Compile approved chapter illustrations into a dedicated-fullscreen-page EPUB."""

import argparse
import io
import json
import os
import posixpath
import sys
import zipfile
import xml.etree.ElementTree as ET

try:
    from PIL import Image, ImageOps
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


OPF_NS = "http://www.idpf.org/2007/opf"
ET.register_namespace("", OPF_NS)
ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
ET.register_namespace("opf", OPF_NS)


def _find_opf_path(zf: zipfile.ZipFile) -> str:
    root = ET.fromstring(zf.read("META-INF/container.xml"))
    for elem in root.iter():
        if elem.tag.endswith("rootfile") and "full-path" in elem.attrib:
            return elem.attrib["full-path"]
    raise ValueError("Could not locate OPF rootfile in META-INF/container.xml")


def _convert_image(src_path: str, width: int, height: int, grayscale: bool, quality: int) -> bytes:
    with Image.open(src_path) as img:
        img = ImageOps.exif_transpose(img)
        if grayscale:
            img = img.convert("L")
        else:
            img = img.convert("RGB")
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()


def _build_fullscreen_xhtml(title: str, img_rel_href: str, alt_text: str) -> bytes:
    escaped_title = (
        title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    escaped_alt = (
        alt_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{escaped_title} — Illustration</title>
  <style type="text/css">
    @page {{ margin: 0; padding: 0; }}
    html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; background-color: #ffffff; text-align: center; }}
    .illus-wrap {{ margin: 0; padding: 0; width: 100%; height: 100%; display: block; text-align: center; }}
    img.illus-full {{ max-width: 100%; max-height: 100%; width: auto; height: auto; display: block; margin: 0 auto; }}
  </style>
</head>
<body>
  <div class="illus-wrap">
    <img class="illus-full" src="{img_rel_href}" alt="{escaped_alt}" />
  </div>
</body>
</html>
"""
    return xhtml.encode("utf-8")


def compile_epub(
    src_epub: str,
    briefs_path: str,
    images_map_path: str,
    out_epub: str,
    width: int,
    height: int,
    grayscale: bool,
    quality: int,
) -> None:
    with open(briefs_path, "r", encoding="utf-8") as f:
        briefs_raw = json.load(f)
    briefs = briefs_raw if isinstance(briefs_raw, list) else briefs_raw.get("units", [])
    brief_by_id = {b["unit_id"]: b for b in briefs}

    with open(images_map_path, "r", encoding="utf-8") as f:
        images_map: dict[str, str] = json.load(f)

    with zipfile.ZipFile(src_epub, "r") as zin:
        opf_path = _find_opf_path(zin)
        opf_dir = posixpath.dirname(opf_path)
        opf_root = ET.fromstring(zin.read(opf_path))

        manifest_el = opf_root.find(f"{{{OPF_NS}}}manifest")
        spine_el = opf_root.find(f"{{{OPF_NS}}}spine")
        if manifest_el is None or spine_el is None:
            manifest_el = opf_root.find("manifest")
            spine_el = opf_root.find("spine")
        if manifest_el is None or spine_el is None:
            raise ValueError("OPF missing <manifest> or <spine> element.")

        href_to_idref: dict[str, str] = {}
        for item in manifest_el:
            href = item.attrib.get("href", "")
            item_id = item.attrib.get("id", "")
            if href and item_id:
                href_to_idref[href] = item_id

        # Detect directory prefix of existing HTML pages (e.g., "text/")
        sample_html_href = next(
            (h for h in href_to_idref if h.endswith((".html", ".xhtml"))), "illus.html"
        )
        html_dir = posixpath.dirname(sample_html_href)
        img_dir = "images"

        new_files: dict[str, bytes] = {}
        insert_after: dict[str, tuple[str, str]] = {}

        for unit_id, img_path in images_map.items():
            if not os.path.isfile(img_path):
                raise FileNotFoundError(f"Approved image missing for {unit_id}: {img_path}")
            brief = brief_by_id.get(unit_id)
            if not brief:
                raise KeyError(f"Unit {unit_id} missing from {briefs_path}")

            part_href = brief["part_file"]
            chapter_idref = href_to_idref.get(part_href)
            if not chapter_idref:
                raise KeyError(f"Chapter href {part_href} ({unit_id}) not found in OPF manifest")

            slug = unit_id.lower().replace("-", "_")
            img_href = posixpath.join(img_dir, f"illus_{slug}.jpg")
            page_href = posixpath.join(html_dir, f"illus_{slug}.html") if html_dir else f"illus_{slug}.html"

            img_arc = posixpath.join(opf_dir, img_href) if opf_dir else img_href
            page_arc = posixpath.join(opf_dir, page_href) if opf_dir else page_href
            img_rel_from_page = posixpath.relpath(img_href, posixpath.dirname(page_href) or ".")

            title = brief.get("title", unit_id)
            alt_text = f"Four-panel illustration for {title}"

            new_files[img_arc] = _convert_image(img_path, width, height, grayscale, quality)
            new_files[page_arc] = _build_fullscreen_xhtml(title, img_rel_from_page, alt_text)

            img_id = f"illus_img_{slug}"
            page_id = f"illus_page_{slug}"

            ET.SubElement(
                manifest_el,
                f"{{{OPF_NS}}}item",
                {"id": img_id, "href": img_href, "media-type": "image/jpeg"},
            )
            ET.SubElement(
                manifest_el,
                f"{{{OPF_NS}}}item",
                {"id": page_id, "href": page_href, "media-type": "application/xhtml+xml"},
            )
            insert_after[chapter_idref] = (page_id, page_arc)

        # Rebuild spine inserting each illustration page right after its chapter
        original_itemrefs = list(spine_el)
        for child in original_itemrefs:
            spine_el.remove(child)
            spine_el.append(child)
            idref = child.attrib.get("idref", "")
            if idref in insert_after:
                page_id, _ = insert_after[idref]
                ET.SubElement(
                    spine_el,
                    f"{{{OPF_NS}}}itemref",
                    {"idref": page_id, "linear": "yes"},
                )

        updated_opf_bytes = ET.tostring(opf_root, encoding="utf-8", xml_declaration=True)

        os.makedirs(os.path.dirname(os.path.abspath(out_epub)), exist_ok=True)
        with zipfile.ZipFile(out_epub, "w") as zout:
            # 1. Write mimetype first and uncompressed per EPUB spec
            if "mimetype" in zin.namelist():
                zout.writestr("mimetype", zin.read("mimetype"), compress_type=zipfile.ZIP_STORED)
            else:
                zout.writestr("mimetype", b"application/epub+zip", compress_type=zipfile.ZIP_STORED)

            # 2. Copy all original entries except mimetype and OPF
            for info in zin.infolist():
                if info.filename in ("mimetype", opf_path):
                    continue
                zout.writestr(info.filename, zin.read(info.filename), compress_type=zipfile.ZIP_DEFLATED)

            # 3. Write updated OPF and new illustration assets/pages
            zout.writestr(opf_path, updated_opf_bytes, compress_type=zipfile.ZIP_DEFLATED)
            for arc_name, payload in new_files.items():
                zout.writestr(arc_name, payload, compress_type=zipfile.ZIP_DEFLATED)

    # Validate output EPUB structure
    with zipfile.ZipFile(out_epub, "r") as zval:
        names = zval.namelist()
        assert names[0] == "mimetype", "mimetype must be first ZIP entry"
        assert zval.getinfo("mimetype").compress_type == zipfile.ZIP_STORED, "mimetype must be uncompressed"
        ET.fromstring(zval.read(opf_path))
        for _, (_, page_arc) in insert_after.items():
            ET.fromstring(zval.read(page_arc))

    print(f"Compiled & validated illustrated EPUB: {os.path.abspath(out_epub)}")
    print(f"Inserted {len(insert_after)} dedicated fullscreen illustration pages.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile illustrated EPUB with fullscreen chapter pages.")
    parser.add_argument("epub", help="Path to original .epub")
    parser.add_argument("--briefs", required=True, help="Path to image_briefs.json")
    parser.add_argument("--images-map", required=True, help="JSON mapping unit_id -> approved image path")
    parser.add_argument("--out", required=True, help="Output .epub path")
    parser.add_argument("--width", type=int, default=1072, help="Max image width (default: 1072)")
    parser.add_argument("--height", type=int, default=1448, help="Max image height (default: 1448)")
    parser.add_argument("--color", action="store_true", help="Preserve RGB color instead of 8-bit grayscale")
    parser.add_argument("--quality", type=int, default=90, help="JPEG quality (default: 90)")
    args = parser.parse_args()
    compile_epub(
        args.epub,
        args.briefs,
        args.images_map,
        args.out,
        args.width,
        args.height,
        not args.color,
        args.quality,
    )


if __name__ == "__main__":
    main()
