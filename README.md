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

More info on args provided in `--help`

## Fonts

The font can be modified in the openscad file; any system font can be used.
Ensure that a Monospace font is used as otherwise a name with lots of wide letters ("m", "w") may not generate correctly.

