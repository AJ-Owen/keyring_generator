#!/usr/bin/env python3

import os
import subprocess
import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Generate STL files from OpenSCAD templates with custom names and icons.")
    parser.add_argument("--names_file", type=str, help="Path to the file containing list of names.")
    parser.add_argument("--name", type=str, help="A single name to generate a keyring for.")
    parser.add_argument("--output_dir", type=str, default="output_stl", help="Directory to save STL files.")
    parser.add_argument("--icon", type=str, default="", help="Optional icon file in the icons directory.")

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
    args = parse_args()

    template_file = "keyring.scad"
    openscad_path = subprocess.run(["which", "openscad"], capture_output=True).stdout.strip()

    if not openscad_path:
        print("Error: OpenSCAD not found. Please install it and ensure it's in your PATH.")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    print(args.names)
    for name in args.names:
        print(f"Processing: {name}")
        generate_stl(name, args.icon, args.output_dir, template_file, openscad_path)



if __name__ == "__main__":
    main()
