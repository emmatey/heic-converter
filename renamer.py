from datetime import datetime
from loader import loader
import os
import pathlib
from PIL import Image
import pyheif
import sys


def decode(path_object):
    print(f"Decoding file...{path_object.name}...")
    heif_file = pyheif.read(path_object)
    image = Image.frombytes(
        heif_file.mode, 
        heif_file.size, 
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
        )
    # return value is a pillow image object, use 
    # save(path, ".imgtype") to convert.
    return image

def construct_save_loc(path_object, suffix, RENAME = 1):
    # get file creation date
    stat_result_obj = path_object.stat()
    creation_date_stamp = stat_result_obj.st_mtime
    creation_date = datetime.fromtimestamp(creation_date_stamp).strftime("%Y-%m-%d")

    # get parent dir's name to use in renaming.
    title = path_object.parent.name
    safe_title = title.replace(" ", "_").replace("-", "_")
    new_filename_str = f"{creation_date};{safe_title}{suffix}"

    if RENAME == 0:
        out_path = path_object.with_suffix(suffix)
        return out_path
    
    out_path = path_object.with_name(new_filename_str)

    return out_path

def main():
    # Argument API
    # [renamer.py, root_dir, ".JPEG"/".PNG", "bool"(0/1): delete original?, "bool"(0/1): rename?]
    
    argv = sys.argv
    if len(argv) != 5:
        print("Error: Incorret number of arguments.")
        print("Usage: python renamer.py <root_dir> <.JPEG/.PNG> <0/1: delete original?> <0/1: rename?>")
        sys.exit(1)

    ROOT_DIR = argv[1]
    OUT_SUFFIX = argv[2]
    DEL = int(argv[3])
    RENAME = int(argv[4])

    loading_object = loader(ROOT_DIR)

    for (dirpath, dirnames, filenames) in os.walk(ROOT_DIR):
        for file in filenames:
            path_str = os.path.join(dirpath, file)
            source_path = pathlib.Path(path_str)

            if source_path.suffix.lower() == ".heic":
                out_loc = construct_save_loc(source_path, OUT_SUFFIX, RENAME)
                pillowImg = decode(source_path)

                try:
                    print(f"Converting to {OUT_SUFFIX}")
                    pillowImg.save(out_loc, quality = 95, optimize = True)
                    print(f"Save location = {out_loc}")
                    loading_object.load(source_path)
                    if DEL == 1:
                        os.remove(source_path)
                except Exception as e:
                    print(f"failed to convert {pillowImg}\n{e}")

            elif source_path.suffix.lower() == ".mov":
                if RENAME == 0:
                    mov_suffix = ".mov"
                if RENAME == 1:
                    mov_suffix = "_live.mov"

                out_loc = construct_save_loc(source_path, mov_suffix, RENAME) 
                
                try:
                    source_path.rename(out_loc)
                    print(f".MOV renamed to {out_loc.name}")
                    loading_object.load(out_loc)

                except Exception as e:
                    print(f"Failed to rename MOV file {source_path.name}. Error: {e}\n")
    
    loading_object.complete_load()

if __name__ == "__main__":
  main()