#!/usr/bin/env python3

import sys
from Formats.BIN import *
from Formats.MSG import do_decode_msg
from Formats.TIM import do_extract_tim, do_compress_tim
from Formats.FONT import do_extract_font

help_msg = (
    """\nDashEditor v0.6 - Mega Man Legends Hacking Suite
Created by _Ombra_ of SadNES cITy Translations
Website: http://www.sadnescity.it\n
DashEditor.py [option] [file_or_folder]\n
  -e       unpacks the content of BIN files.
  -c       packs a folder to BIN files.\n""")

# Check if 2 arguments are passed
if len(sys.argv) != 3:
    print("{}\nOne or more arguments missing or too many".format(help_msg))
# If they are, check if the command argument is valid
elif not any(cmd in sys.argv[1] for cmd in ("-e", "-c")):
    print("{}\nInvalid command!".format(help_msg))
# If the command argument is valid, check if file exists and open it
elif not os.path.exists(sys.argv[2]):
    print("\nFile or folder not found")
# If second argument is -e and third argument is file
elif sys.argv[1] == "-e" and not os.path.isfile(sys.argv[2]):
    print("\nExpected file. Provided folder")
elif sys.argv[1] == "-c" and not os.path.isdir(sys.argv[2]):
    print("\nExpected folder. Provided file")
else:
    # Ex: TEST/TEST2/FILE.BIN or TEST/TEST2
    full_file_or_folder_name: str = sys.argv[2].replace("\\", "/")
    # Get only the paths from the normalized path
    # Ex: TEST/TEST2/FILE.BIN == TEST/TEST2/FILE
    full_path_and_file_no_ext = os.path.splitext(full_file_or_folder_name)[0]
    # Get only the file name from the normalized path
    # Ex: TEST/TEST2/FILE.BIN == FILE.BIN
    file_name_only = os.path.basename(full_file_or_folder_name)

    # Full path to the index file
    # Ex: TEST/TEST2/TEST2.BIN == TEST/TEST2/TEST2.txt
    index_file_path = "{}/{}.txt".format(full_path_and_file_no_ext, file_name_only.replace(".BIN", ""))

    if sys.argv[1] == "-e" and os.path.isfile(sys.argv[2]):
        file_data = open(full_file_or_folder_name, "rb").read()

        # Check if the file is a valid MML BIN file
        try:
            assert file_data[64:67].decode() == "..\\"
        except AssertionError:
            print("\nNot a valid MML PSX BIN file")
        else:

            # Create index file
            if not os.path.exists(full_path_and_file_no_ext):
                os.mkdir(full_path_and_file_no_ext)

            index_file = open(index_file_path, "w+")

            # Proceed with extraction
            do_unpack_bin(full_path_and_file_no_ext, file_data, index_file)

            index_file.seek(0)
            index_file_content = index_file.read().splitlines()
            index_file_line = 0

            while index_file_line < len(index_file_content):
                file_name = index_file_content[index_file_line].split(",")[0]
                file_path = index_file_path.replace(os.path.basename(index_file_path), "") + file_name
                # If MSG files are found, dump them
                if any(fn in index_file_content[index_file_line].upper() for fn in [".MSG"]):
                    do_decode_msg(file_path)
                    index_file_content = index_file_content.pop(0)
                    index_file_line += 1
                # If TIM files are found, convert them
                elif any(fn in index_file_content[index_file_line].upper() for fn in [".TIM"]):
                    do_extract_tim(file_path)
                    index_file_line += 1
                # If FONT files are found, convert them
                elif any(fn in index_file_content[index_file_line].upper() for fn in ("FONT.DAT", "KAIFONT.DAT")):
                    do_extract_font(file_path)
                    index_file_line += 1
                else:
                    index_file_line += 1

            # Close the index file and return
            index_file.close()

    # If argument is -c, pack BIN files
    elif sys.argv[1] == "-c" and os.path.isdir(sys.argv[2]):

        if not os.path.exists(index_file_path):
            print("\nIndex file missing")
        elif os.path.exists("{}.BIN".format(full_file_or_folder_name)):
            print("\nBIN file already exists. Please delete or move/delete before creation.")
        else:
            index_file_content = open(index_file_path, "r").readlines()

            index_file_line = 0

            while index_file_line < len(index_file_content):
                file_name = index_file_content[index_file_line].split(",")[0].upper()

                if any(fn in index_file_content[index_file_line].upper() for fn in [".TIM"]):
                    original_tim = (index_file_path.replace(os.path.basename(index_file_path), "") + file_name)
                    edited_tim = (index_file_path.replace(os.path.basename(index_file_path), "")
                                  + file_name.replace(".TIM", "_EXT.TIM"))
                    if os.path.exists(original_tim) and os.path.exists(edited_tim):
                        do_compress_tim(original_tim, edited_tim)
                    index_file_line += 1
                else:
                    index_file_line += 1

            do_pack_bin(full_file_or_folder_name, index_file_content)
