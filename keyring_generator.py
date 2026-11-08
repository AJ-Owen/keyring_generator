#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
import argparse
import sys
import tempfile
import xml.etree.ElementTree as ET


def parse_args():
    parser = argparse.ArgumentParser(description="Generate STL files from OpenSCAD templates with custom names and icons.")
    parser.add_argument("--names_file", type=str, help="Path to the file containing list of names.")
    parser.add_argument("--name", type=str, help="A single name to generate a keyring for.")
    parser.add_argument("--output_dir", type=str, default="output_stl", help="Directory to save STL files.")
    parser.add_argument("--icon", type=str, default="", help="Optional icon file in the icons directory.")
    parser.add_argument("--no_clean", action="store_true", help="Use the icon as-is instead of auto-cleaning it for OpenSCAD.")

    args = parser.parse_args()

    # Validate files
    if args.names_file is None and args.name is None:
        print("Provide either a --name or a path in --names_file")
        sys.exit(1)

    if args.names_file and not os.path.isfile(args.names_file):
        print(f"Error: Name file '{args.names_file}' not found.")
        sys.exit(1)

    if args.icon and not os.path.isfile(f"icons/{args.icon}"):
        print(f"Error: Icon file '{args.icon}' not found.")
        sys.exit(1)


    # Process names
    args.names = []
    try:
        if args.names_file:
            with open(args.names_file, "r") as file:
                for line in file:
                    args.names.append(line.strip())
    except AttributeError:
        pass
    try:
        if args.name:
            args.names.append(args.name)
    except AttributeError:
        pass

    return args


SVG_NS = "http://www.w3.org/2000/svg"
SHAPE_TAGS = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon"}
# Elements whose contents are never drawn directly
NON_RENDERED_TAGS = {"defs", "mask", "clipPath", "filter", "pattern", "symbol", "marker", "style", "title", "metadata"}
INHERITED_PROPS = ("fill", "stroke", "stroke-width", "display", "visibility")


def log_icon(message):
    print(f"  [icon] {message}")


def local_tag(element):
    return element.tag.rsplit("}", 1)[-1]


def element_style(element, inherited):
    """Resolve the style properties OpenSCAD cares about, including inherited ones."""
    style = dict(inherited)
    # Classes are styled by CSS we don't parse, so treat their fill as unknown (assume visible)
    if element.get("class"):
        style["fill"] = "unknown"
    for prop in INHERITED_PROPS:
        if element.get(prop) is not None:
            style[prop] = element.get(prop).strip()
    for declaration in (element.get("style") or "").split(";"):
        if ":" in declaration:
            prop, value = (part.strip() for part in declaration.split(":", 1))
            if prop in INHERITED_PROPS:
                style[prop] = value
    return style


def is_hidden(style):
    return style.get("display") == "none" or style.get("visibility") == "hidden"


def has_fill(style):
    return style.get("fill", "black") != "none"


def has_stroke(style):
    width = re.match(r"[\d.]+", style.get("stroke-width", "1"))
    return style.get("stroke", "none") != "none" and not (width and float(width.group()) == 0)


def parse_viewbox(root):
    numbers = [float(n) for n in re.split(r"[\s,]+", (root.get("viewBox") or "").strip()) if n]
    if len(numbers) != 4:
        return None
    min_x, min_y, width, height = numbers
    return {(min_x, min_y), (min_x + width, min_y), (min_x, min_y + height), (min_x + width, min_y + height)}


def is_canvas_rectangle(subpath, corners):
    """True if a path segment just traces the edge of the whole canvas."""
    tokens = re.findall(r"[MLHVZmlhvz]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?", subpath)
    points, x, y, command, i = [], 0.0, 0.0, None, 0
    try:
        while i < len(tokens):
            if tokens[i].isalpha():
                command = tokens[i]
                i += 1
                continue
            if command in ("M", "L"):
                x, y = float(tokens[i]), float(tokens[i + 1])
                i += 2
            elif command == "H":
                x = float(tokens[i])
                i += 1
            elif command == "V":
                y = float(tokens[i])
                i += 1
            else:
                # Relative or curved commands - not a simple canvas outline
                return False
            points.append((x, y))
    except (ValueError, IndexError):
        # Couldn't follow the path, so leave it alone
        return False
    return bool(points) and set(points) == corners


def remove_canvas_subpaths(element, corners):
    """Strip canvas-sized rectangles out of a path. Returns True if nothing is left."""
    subpaths = [s for s in re.findall(r"[Mm][^Mm]*", element.get("d", ""))]
    kept = [s for s in subpaths if not is_canvas_rectangle(s, corners)]
    if len(kept) != len(subpaths):
        log_icon(f"Removing {len(subpaths) - len(kept)} canvas-sized background rectangle(s) from <path id='{element.get('id', '')}'>")
        element.set("d", " ".join(s.strip() for s in kept))
    return not kept


def is_canvas_rect_element(element, corners):
    try:
        x, y = float(element.get("x", 0)), float(element.get("y", 0))
        right, bottom = x + float(element.get("width")), y + float(element.get("height"))
    except (TypeError, ValueError):
        return False
    return {(x, y), (right, y), (x, bottom), (right, bottom)} == corners


def clean_svg_tree(root):
    """Remove shapes OpenSCAD would wrongly draw. Returns how many stroke-only shapes remain."""
    corners = parse_viewbox(root)
    stroke_only = 0

    def walk(parent, inherited):
        nonlocal stroke_only
        for element in list(parent):
            tag = local_tag(element)
            if tag in NON_RENDERED_TAGS:
                continue
            style = element_style(element, inherited)
            description = f"<{tag} id='{element.get('id', '')}'>"

            if tag in SHAPE_TAGS:
                if is_hidden(style) or (not has_fill(style) and not has_stroke(style)):
                    # Browsers draw nothing for these, but OpenSCAD fills them in solid
                    log_icon(f"Removing invisible {description} (no fill, no stroke)")
                    parent.remove(element)
                    continue
                if corners and tag == "rect" and is_canvas_rect_element(element, corners):
                    log_icon(f"Removing canvas-sized background {description}")
                    parent.remove(element)
                    continue
                if corners and tag == "path" and remove_canvas_subpaths(element, corners):
                    log_icon(f"Removing {description}, it was only a background rectangle")
                    parent.remove(element)
                    continue
                if not has_fill(style) and has_stroke(style):
                    stroke_only += 1
            else:
                walk(element, style)

    walk(root, element_style(root, {}))
    return stroke_only


def register_namespaces(svg_path):
    for _, (prefix, uri) in ET.iterparse(svg_path, events=["start-ns"]):
        ET.register_namespace(prefix, uri)


def outline_strokes(svg_path, out_path):
    """Use Inkscape to turn strokes into filled shapes merged into a single path."""
    inkscape = shutil.which("inkscape")
    if not inkscape:
        log_icon("WARNING: Inkscape not found, cannot convert strokes. Icon may render with gaps.")
        return False
    log_icon("Converting strokes to solid shapes with Inkscape")
    actions = f"select-all;object-stroke-to-path;select-all;path-union;export-plain-svg;export-filename:{out_path};export-do"
    result = subprocess.run([inkscape, svg_path, f"--actions={actions}"], capture_output=True, text=True)
    if result.returncode != 0 or not os.path.isfile(out_path):
        log_icon(f"WARNING: Inkscape failed, using icon without stroke conversion:\n{result.stderr}")
        return False
    return True


def clean_icon(icon_path, work_dir):
    """Write a copy of the icon that OpenSCAD renders the same way a browser would."""
    print(f"Cleaning icon: {icon_path}")
    register_namespaces(icon_path)
    tree = ET.parse(icon_path)
    stroke_only = clean_svg_tree(tree.getroot())

    cleaned_path = os.path.join(work_dir, "cleaned_" + os.path.basename(icon_path))
    tree.write(cleaned_path, xml_declaration=True, encoding="utf-8")

    if stroke_only:
        log_icon(f"Found {stroke_only} stroke-only shape(s), which OpenSCAD renders with gaps where lines overlap")
        outlined_path = os.path.join(work_dir, "outlined_" + os.path.basename(icon_path))
        if outline_strokes(cleaned_path, outlined_path):
            cleaned_path = outlined_path
    else:
        log_icon("No stroke-only shapes found")

    log_icon(f"Using cleaned icon: {cleaned_path}")
    return cleaned_path


def generate_stl(name, icon, output_folder, template_file, openscad_path):
    scad_file = f"{output_folder}/{name}.scad"

    # Substitute template placeholders
    with open(template_file, "r") as template:
        content = template.read().replace("{{NAME}}", name).replace("{{ICON}}", icon)

    with open(scad_file, "w") as scad:
        scad.write(content)

    # Generate one STL per part so each can be assigned its own filament
    for part in ("body", "inlay"):
        stl_file = f"{output_folder}/{name}_{part}.stl"
        result = subprocess.run([openscad_path, "-o", stl_file, "-D", f'PART="{part}"', scad_file])
        if result.returncode != 0:
            os.remove(scad_file)
            print(f"Error: OpenSCAD failed to generate {stl_file}")
            sys.exit(1)
        print(f"Generated: {stl_file}")
    os.remove(scad_file)


def main():
    # Keep our log lines in order with OpenSCAD's output when piped to a file
    sys.stdout.reconfigure(line_buffering=True)
    args = parse_args()

    template_file = "keyring.scad"
    openscad_path = shutil.which("openscad")

    if not openscad_path:
        print("Error: OpenSCAD not found. Please install it and ensure it's in your PATH.")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as work_dir:
        icon = os.path.abspath(f"icons/{args.icon}") if args.icon else ""
        if icon and args.no_clean:
            print(f"Skipping icon cleaning, using as-is: {icon}")
        elif icon:
            icon = clean_icon(icon, work_dir)

        print(args.names)
        for name in args.names:
            print(f"Processing: {name}")
            generate_stl(name, icon, args.output_dir, template_file, openscad_path)


if __name__ == "__main__":
    main()
