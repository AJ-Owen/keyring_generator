# KEYRING GENERATOR

- Ensure openscad is installed
- Add a list of names to "names.txt", or run with a single name
- Run the python file
- Each name generates two STLs: `<name>_body.stl` and `<name>_inlay.stl` (the text and icon, set 1mm into the body and flush with its top)
- Import both `.stl`s into BambuStudio together and choose "Yes" when asked to load them as a single object with multiple parts
- Assign the inlay part your orange filament and the body its own filament in the AMS
- PRINT!

## Example usage

```
.
├── icons
│   ├── bear-face.svg
│   ├── horse-shoe.svg
│   └── paw-print.svg
├── keyring_generator.py
├── keyring.scad
├── names.txt
└── output_stl
```

Using a single name passed in as an arg
`./keyring_generator.py --name "hello world" --icon paw-print.svg`

Using a list of names
`./keyring_generator.py --names_list "names.txt" --icon horse-shoe.svg`

Without an icon (`--icon` is optional)
`./keyring_generator.py --name "hello world"`

More info on args provided in `--help`

## Icons

Icons are SVGs in the `icons` directory. Before rendering, each icon is automatically cleaned so OpenSCAD draws it the way a browser would (the original file is not modified):

- Invisible shapes (no fill and no stroke) and canvas-sized background rectangles are removed, as OpenSCAD would otherwise render them as a solid block
- Line-drawn (stroke-only) icons are converted to solid shapes using [Inkscape](https://inkscape.org/), as OpenSCAD otherwise leaves gaps where lines overlap. Inkscape must be on your `PATH` for this step

Each step is logged with an `[icon]` prefix. Use `--no_clean` to use an icon exactly as-is.

## Fonts

The font can be modified in the openscad file; any system font can be used.
Ensure that a Monospace font is used as otherwise a name with lots of wide letters ("m", "w") may not generate correctly.

