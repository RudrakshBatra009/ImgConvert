# imgconvert

This is small tool for change photo format like png to jpg or jpg to webp etc. You can give one photo or full folder also, it will convert all photo inside. Very simple to use, no need big knowledge, just run command in terminal and it will do work.

## What it does

- Converts between JPG, PNG, WEBP, BMP, GIF, TIFF, and HEIC (iPhone photos)
- Works on a single file or an entire folder (with `--recursive` for subfolders too)
- Shows before/after file size for each image, and total savings at the end
- Handles transparency properly when converting to JPEG (flattens to white background)
- Has a `--dry` mode to preview what will happen before actually converting anything

## Install

```bash
pip install Pillow
pip install pillow-heif    # only if you have iPhone HEIC photos
```

Then make it runnable from anywhere:

**macOS / Linux**
```bash
cp imgconvert.py ~/.local/bin/imgconvert
chmod +x ~/.local/bin/imgconvert
```

**Windows**
Put `imgconvert.py` in `C:\tools\` and create `imgconvert.bat` next to it:
```bat
@echo off
python "%~dp0imgconvert.py" %*
```

## Usage

```bash
# single file
imgconvert photo.png --to jpg

# whole folder
imgconvert ./photos --to webp

# include subfolders
imgconvert ./photos --to jpg --recursive

# custom output folder
imgconvert ./photos --to png --out ./final

# control jpeg/webp quality (1-100, default 90)
imgconvert ./photos --to jpg --quality 95

# preview only, converts nothing
imgconvert ./photos --to webp --dry

# iPhone HEIC photos to jpg
imgconvert ./iphone_photos --to jpg --recursive
```

## Notes

- If a source folder isn't given an output folder, it creates `<foldername>_converted` next to it.
- HEIC support is optional — if `pillow-heif` isn't installed, HEIC files are just skipped with a warning instead of crashing the whole run.
- For animated GIFs converted to a non-GIF format, only the first frame is kept.