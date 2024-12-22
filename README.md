# KEYRING GENERATOR

- Ensure openscad is installed
- Add a list of names to "names.txt", or run with a single name
- Run the python file
- Import the generated `.stl`s into BambuStudio
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

