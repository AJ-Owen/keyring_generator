#!/usr/bin/env python3

import os
import subprocess
import sys

if sys.argv[1]:
    name_file = sys.argv[1]
else:
    name_file = "names.txt"

if sys.argv[2]:
    output_folder = sys.argv[2]
else:
    output_folder = "output_stl"

template_file = "keyring.scad"
openscad_path = subprocess.run(["which", "openscad"], capture_output=True).stdout.strip()

os.makedirs(output_folder, exist_ok=True)

with open(name_file, "r") as file:
    for line in file.readlines():
        name = line.strip()
        print(f"Working on: {name}")
        # Generate a temporary OpenSCAD file with the substituted NAME
        scad_file = f"{output_folder}/{name}.scad"
        with open(template_file, "r") as template:
            content = template.read().replace("{{NAME}}", f"{name}")
        with open(scad_file, "w") as scad:
            scad.write(content)

        # Generate the custom STL
        stl_file = f"{output_folder}/{name}.stl"
        subprocess.run([openscad_path, "-o", stl_file, scad_file])
        os.remove(scad_file)
        print(f"Generated: {stl_file}")


