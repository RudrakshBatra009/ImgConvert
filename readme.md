# imgconvert

A simple CLI tool to convert images between formats. Works on a single file or a whole folder.

## How to use it?

Download `main.py`, install the requirements, and run it from your terminal:

```
pip install -r requirements.txt
python main.py photo.png --to jpg
```

Or grab the built executable from the releases page if you don't want to deal with Python.

## Why I created this?

I kept having to manually convert HEIC photos from my phone every time I wanted to upload them somewhere, so I made a script for it. Ended up adding folder support, quality control, etc. and turned it into a proper little tool.

## Functions

* Convert between JPG, PNG, WEBP, BMP, GIF, TIFF, and HEIC
* Convert a single file or a whole folder (with `--recursive` for subfolders)
* Quality control for JPEG/WEBP output
* Dry run mode to preview before converting
* Shows file size before/after so you can see how much space you saved
## Commands

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


