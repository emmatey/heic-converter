import os
import pathlib
import sys
from datetime import datetime
import pyheif
from PIL import Image

def decode(path_object):
    print(f"decoding file...{path_object.name}")
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
    print("decoded :)")
    return image

def construct_save_loc(path_object, suffix):
    # get file creation date
    print("constructing save location...")
    stat_result_obj = path_object.stat()
    creation_date_stamp = stat_result_obj.st_mtime
    creation_date = datetime.fromtimestamp(creation_date_stamp).strftime("%Y-%m-%d")

    # get parent dir i.e portrait subject's name
    title = path_object.parent.name
    safe_title = title.replace(" ", "_").replace("-", "_")
    new_filename_str = f"{creation_date};{safe_title}{suffix}"
    
    # Using .with_name() to preserve the parent directory
    # The 'out_path' is now the FULL path to the new JPEG file.
    out_path = path_object.with_name(new_filename_str)

    print("save location constructed :)")

    return out_path

def main():
    # Argument API
    # [renamer.py, root_dir, ".JPEG"/".PNG", "bool"(0/1): delete original?]
    
    argv = sys.argv
    if len(argv) != 4:
        print("Error: Incorret number of arguments.")
        print("Usage: python renamer.py <root_dir> <.JPEG/.PNG> <0/1: delete original?>")
        sys.exit(1)

    ROOT_DIR = argv[1]
    OUT_SUFFIX = argv[2]
    DEL = int(argv[3])

    for (dirpath, dirnames, filenames) in os.walk(ROOT_DIR):
        for file in filenames:
            path_str = os.path.join(dirpath, file)
            source_path = pathlib.Path(path_str)

            if source_path.suffix.lower() == ".heic":
                out_loc = construct_save_loc(source_path, OUT_SUFFIX) 
                pillowImg = decode(source_path)

                try:
                    print("saving...")
                    pillowImg.save(out_loc, "quality": 95, "optimize": True)
                    print(f"Save location = {out_loc}\n")
                    if DEL == 1:
                        os.remove(source_path)
                except Exception as e:
                    print(f"failed to convert {pillowImg}\n{e}")

            elif source_path.suffix.lower() == ".mov":
                out_loc = construct_save_loc(source_path, "_live.mov") 
                try:
                    source_path.rename(out_loc)
                    print(f".MOV renamed to {out_loc.name}\n")

                except Exception as e:
                    print(f"Failed to rename MOV file {source_path.name}. Error: {e}\n")
    

if __name__ == "__main__":
  main()