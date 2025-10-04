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

def get_exif_date(pillow_image):
    # EXIF tag ID for 'DateTimeOriginal' is 36867
    exif_tag_id = 36867
    
    # Get the EXIF data dictionary
    exif_data = pillow_image.getexif()

    if exif_data and exif_tag_id in exif_data:
        # EXIF date format is usually "YYYY:MM:DD HH:MM:SS"
        date_str = exif_data[exif_tag_id]
        
        try:
            # Parse the EXIF date string
            # The .replace(":", "-", 2) handles the date part (YYYY:MM:DD) 
            # while leaving the time part (HH:MM:SS) alone for strptime.
            return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            print(f"Warning: Malformed EXIF date: {date_str}. Falling back to file mtime.")
            return None
    return None

def construct_save_loc(path_object, suffix, pillow_image = None):
    print("constructing save location...")
    
    creation_date = None
    
    # 1. Attempt to get date from EXIF data (most accurate)
    if pillow_image:
        exif_dt = get_exif_date(pillow_image)
        if exif_dt:
            creation_date = exif_dt.strftime("%Y-%m-%d")

    # 2. Fallback to file system modification time (less accurate)
    if not creation_date:
        stat_result_obj = path_object.stat()
        creation_date_stamp = stat_result_obj.st_mtime
        creation_date = datetime.fromtimestamp(creation_date_stamp).strftime("%Y-%m-%d")
        print(f"Using file modification time for {path_object.name}")

    # get parent dir i.e portrait subject's name
    title = path_object.parent.name
    safe_title = title.replace(" ", "_").replace("-", "_")
    new_filename_str = f"{creation_date};{safe_title}{suffix}"
    
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
                pillowImg = decode(source_path)
                
                # construct_save_loc now uses the EXIF date (if available) for naming
                out_loc = construct_save_loc(source_path, OUT_SUFFIX, pillowImg) 

                print("saving...")
                save_kwargs = {"quality": 95, "optimize": True}
                
                # Check for and use EXIF directly from the Pillow object for saving
                exif_data_to_save = pillowImg.getexif()
                if exif_data_to_save:
                    save_kwargs["exif"] = exif_data_to_save
                    
                try:
                    pillowImg.save(out_loc, **save_kwargs)
                    print(f"Save location = {out_loc}\n")
                    if DEL == 1:
                        os.remove(source_path)
                except Exception as e:
                    print(f"failed to convert {source_path.name}\n{e}")

            elif source_path.suffix.lower() == ".mov":
                out_loc = construct_save_loc(source_path, "_live.mov") 
                try:
                    source_path.rename(out_loc)
                    print(f".MOV renamed to {out_loc.name}\n")

                except Exception as e:
                    print(f"Failed to rename MOV file {source_path.name}. Error: {e}\n")
    

if __name__ == "__main__":
  main()