
import sys
import os
import argparse
from pathlib import Path
from PIL import Image

# formats we know how to read
SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif", ".heic"]

# maps what the user types on the command line to Pillow's internal format name
FORMAT_LOOKUP = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "gif": "GIF",
    "tiff": "TIFF",
    "tif": "TIFF",
}

# and the reverse-ish, for picking a file extension once we know the Pillow format
EXTENSION_FOR_FORMAT = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
    "BMP": ".bmp",
    "GIF": ".gif",
    "TIFF": ".tif",
}

# HEIC is annoying because Pillow doesn't support it out of the box.
# pillow-heif plugs in support for it, but I don't want to force everyone
# to install it if they're not dealing with iPhone photos, so we just
# check if it's there and quietly skip HEIC files if it's not.
heic_supported = False
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    heic_supported = True
except ImportError:
    # that's fine, we'll just warn later if someone actually has a heic file
    pass


def human_size(num_bytes):
    """Turn a byte count into something readable, roughly."""
    if num_bytes < 1024:
        return str(num_bytes) + "B"
    if num_bytes < 1024 * 1024:
        return "{:.0f}KB".format(num_bytes / 1024)
    return "{:.1f}MB".format(num_bytes / (1024 * 1024))


def find_images(input_path, recursive):
    """Figure out what image files we're actually working with."""
    path = Path(input_path)

    if path.is_file():
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            return [path]
        else:
            return []

    if path.is_dir():
        if recursive:
            candidates = path.rglob("*")
        else:
            candidates = path.iterdir()

        found = []
        for f in candidates:
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
                found.append(f)
        return sorted(found)

    # not a file, not a dir... probably doesn't exist, caller checks that already
    return []


def convert_image(src_path, output_folder, target_format, jpeg_quality):
    """Convert a single image. Returns (original_size, new_size) or None if skipped."""

    if src_path.suffix.lower() == ".heic" and not heic_supported:
        print("  skipping {} - heic support not installed (pip install pillow-heif)".format(src_path.name))
        return None

    try:
        image = Image.open(src_path)
    except Exception as err:
        print("  couldn't open {}: {}".format(src_path.name, err))
        return None

    new_extension = EXTENSION_FOR_FORMAT.get(target_format, ".jpg")
    destination = output_folder / (src_path.stem + new_extension)

    # edge case: if somehow the output would overwrite the source file
    # (e.g. converting jpg -> jpg into the same folder), give it a different name
    if destination.resolve() == src_path.resolve():
        destination = output_folder / (src_path.stem + "_converted" + new_extension)

    # JPEG doesn't support transparency, so if we're converting something
    # with an alpha channel to JPEG we need to flatten it onto a background
    # first, otherwise Pillow just throws an error. Using white here since
    # that's usually the safest default.
    if target_format == "JPEG" and image.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        background.paste(image, mask=image.split()[-1])
        image = background

    # animated gifs - for now we only keep the first frame if converting
    # to something that isn't a gif. Could support extracting all frames
    # later but that's a bigger feature than I need right now.
    if src_path.suffix.lower() == ".gif" and target_format != "GIF":
        image.seek(0)

    save_options = {}
    if target_format in ("JPEG", "WEBP"):
        save_options["quality"] = jpeg_quality
        save_options["optimize"] = True
    elif target_format == "PNG":
        save_options["optimize"] = True

    try:
        image.save(destination, format=target_format, **save_options)
    except Exception as err:
        print("  error saving {}: {}".format(src_path.name, err))
        return None

    original_size = src_path.stat().st_size
    new_size = destination.stat().st_size

    print("  {:<35} -> {:<35} {:>8} -> {}".format(
        src_path.name, destination.name, human_size(original_size), human_size(new_size)
    ))

    return (original_size, new_size)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        prog="imgconvert",
        description="Convert images between formats. Works on a single file or a whole folder."
    )
    parser.add_argument("input", help="image file or folder to convert")
    parser.add_argument("--to", required=True, choices=list(FORMAT_LOOKUP.keys()), help="format to convert to")
    parser.add_argument("--out", default=None, help="where to put converted files (default: makes a new folder next to the input)")
    parser.add_argument("--quality", type=int, default=90, help="quality for jpeg/webp, 1-100 (default 90)")
    parser.add_argument("--recursive", action="store_true", help="also look inside subfolders")
    parser.add_argument("--dry", action="store_true", help="just show what would happen, don't actually convert anything")
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    source = Path(args.input).resolve()
    if not source.exists():
        print("can't find: {}".format(source))
        sys.exit(1)

    target_format = FORMAT_LOOKUP[args.to.lower()]

    images = find_images(source, args.recursive)
    if not images:
        print("no supported images found in: {}".format(source))
        sys.exit(0)

    # decide where output goes
    if args.out:
        output_folder = Path(args.out).resolve()
    elif source.is_dir():
        output_folder = source.parent / (source.name + "_converted")
    else:
        output_folder = source.parent / (source.stem + "_converted")

    print()
    print("imgconvert")
    print()
    print("  input  :", source)
    print("  files  :", len(images))
    print("  target :", args.to)
    print("  output :", output_folder)
    if args.dry:
        print("  (dry run, nothing will be written)")
    print()

    if args.dry:
        for img in images:
            new_ext = EXTENSION_FOR_FORMAT.get(target_format)
            print("  would convert: {} -> {}{}".format(img.name, img.stem, new_ext))
        print()
        print("  {} file(s) would be converted".format(len(images)))
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    total_before = 0
    total_after = 0
    done = 0
    skipped = 0

    for img in images:
        result = convert_image(img, output_folder, target_format, args.quality)
        if result is None:
            skipped += 1
        else:
            done += 1
            total_before += result[0]
            total_after += result[1]

    print()
    print("  converted :", done)
    if skipped:
        print("  skipped   :", skipped)
    if total_before > 0:
        difference = total_before - total_after
        label = "saved" if difference >= 0 else "added"
        print("  size      : {} -> {} ({} {})".format(
            human_size(total_before), human_size(total_after), label, human_size(abs(difference))
        ))
    print("  saved to  :", output_folder)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("cancelled")