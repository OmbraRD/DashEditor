#!/usr/bin/env python3

import sys
from Formats.BIN import *
from Formats.FONT import do_extract_font, do_insert_font
from Formats.MSG import do_extract_msg, do_decode_block, do_insert_msg, do_encode_text_block
from Formats.TIM import do_extract_tim, do_insert_tim


help_msg = (
    """\nDashEditor v0.9.7 - Mega Man Legends Translation Toolkit
Created by _Ombra_ of SadNES cITy Translations
Website: http://www.sadnescity.it\n
DashEditor.py [option] [file_or_folder]\n
  -e   extracts che content of BIN file.
  -i   inserts an extracted folder to BIN file.\n""")

# Check if 2 arguments are passed
if len(sys.argv) != 3:
    print("{}\nOne or more arguments missing or too many".format(help_msg))
# If they are, check if the command argument is valid
elif not any(cmd in sys.argv[1] for cmd in ("-e", "-i")):
    print("{}\nInvalid command!".format(help_msg))
# If the command argument is valid, check if file exists and open it
elif not os.path.exists(sys.argv[2]):
    print("\nFile or folder not found")
else:
    # Replace \ with / since Windows is compatible with both but not Linux or Mac
    # Ex: TEST\TEST2\FILE.BIN or TEST\TEST2 == TEST/TEST2/FILE.BIN or TEST/TEST2
    full_file_or_folder_name: str = sys.argv[2].replace("\\", "/")
    # Get only the paths from the normalized path
    # Ex: TEST/TEST2/FILE.BIN == TEST/TEST2/FILE
    full_path_and_file_no_ext = os.path.splitext(full_file_or_folder_name)[0]
    # Get only the file name from the normalized path
    # Ex: TEST/TEST2/FILE.BIN == FILE.BIN
    file_name_only = os.path.basename(full_file_or_folder_name)
    # Full path to the index file
    # Ex: TEST/TEST2/TEST2.BIN == TEST/TEST2/TEST2.txt
    index_file_path = "{}/{}.txt".format(full_path_and_file_no_ext, os.path.splitext(file_name_only)[0])

    # If second argument is -e and third argument is file
    if sys.argv[1] == "-e" and not os.path.isfile(sys.argv[2]):
        print("\nExpected file. Provided folder")
    elif sys.argv[1] == "-e" and os.path.isfile(sys.argv[2]):
        file_data = open(full_file_or_folder_name, "rb").read()

        if file_name_only == "ROCK_NEO.EXE":
            try:
                assert file_data[559296:559313].decode() == "BASLUS-00603-DASH"
            except AssertionError:
                print("\nNot a valid NTSC MML PSX EXE file")
            else:
                print("\nExtracting text block from {}".format(sys.argv[2].replace("\\", "/").split("/")[-1]))

                # Read pointer table data
                ptr_tbl_data = file_data[512716:513684]
                # Pointer table size
                ptr_tbl_size = len(ptr_tbl_data) // 4

                print("Pointer table contains {} blocks".format(ptr_tbl_size))

                output_file = open(full_path_and_file_no_ext + ".TXT", "w")

                ptr_tbl_ofs = 0
                block_number = 1  # Starting from one so it aligns with EXE_JUMP

                while ptr_tbl_ofs < len(ptr_tbl_data):
                    # Extract block data by subtracting 0x8000F800 since these are PSX memory offsets
                    block_start_ofs = bytes_to_uint(ptr_tbl_data[ptr_tbl_ofs:ptr_tbl_ofs + 4]) - 2147547136
                    # If we reached the last pointer, use the end of the block as end offset
                    if ptr_tbl_ofs == len(ptr_tbl_data) - 4:
                        block_end_ofs = 512716
                    else:
                        block_end_ofs = bytes_to_uint(ptr_tbl_data[ptr_tbl_ofs + 4:ptr_tbl_ofs + 8]) - 2147547136

                    block_data = file_data[block_start_ofs:block_end_ofs]

                    # Write each block with offset information
                    output_file.write(
                        "[Block {:02X}, String: {:04X}-{:04X}]\n".format(block_number, block_start_ofs, block_end_ofs)
                    )

                    output_file.write(do_decode_block(block_data) + "\n\n")

                    ptr_tbl_ofs += 4
                    block_number += 1

                output_file.close()

        else:
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
                    # If MSG files are found, extract them
                    if any(fn in index_file_content[index_file_line].upper() for fn in [".MSG"]):
                        do_extract_msg(file_path)
                        index_file_content = index_file_content.pop(0)
                        index_file_line += 1
                    # If TIM files are found, extract them
                    elif any(fn in index_file_content[index_file_line].upper() for fn in [".TIM"]):
                        do_extract_tim(file_path)
                        index_file_line += 1
                    # If FONT files are found, extract them
                    elif any(fn in index_file_content[index_file_line].upper() for fn in ("FONT.DAT", "KAIFONT.DAT")):
                        do_extract_font(file_path)
                        index_file_line += 1
                    else:
                        index_file_line += 1

                # Close the index file and return
                index_file.close()

    # If arg1 is -i, and arg2 is ROCK_NEO.EXE, insert EXE text
    elif sys.argv[1] == "-i" and file_name_only == "ROCK_NEO.EXE":
        exe_file = open(full_file_or_folder_name, "rb+")

        try:
            exe_file.seek(559296)
            assert exe_file.read(17).decode() == "BASLUS-00603-DASH"
        except AssertionError:
            print("\nNot a valid NTSC MML PSX EXE file")
        else:
            text_file = os.path.splitext(full_file_or_folder_name)[0] + ".TXT"
            print("\nInserting {}".format(text_file))

            # Read TXT file
            text = open(text_file, "r").read()

            ptr_table: list = [2148052808]  # 8008AF48 is the first pointer

            i = 0
            current_block = 1
            encoded_block: list = []

            while i < len(text):
                # Skip the [Blocks] text but separate them for recalculating pointers
                c = text[i]

                if c == '[':
                    # Find the end of the textual Block info and start of next
                    block_end = text.find(']', i + 1)
                    next_block_start = text.find('[', i + 1)

                    # If there is no more blocks after, read until the end of the file
                    if next_block_start == -1:
                        text_block = text[block_end + 2:-2]
                    # If there is another block after, read until the beginning of the next block
                    else:
                        # Remove the \n\n at beginning and end of block
                        text_block = text[block_end + 2:next_block_start - 2]

                    # Encode text block to list of bytes
                    encoded_text_block = do_encode_text_block(text_block)
                    encoded_block.append(encoded_text_block[0:-2])

                    if current_block != 968 // 4:
                        # Append the size of the encoded block to the pointer table
                        ptr_table.append(ptr_table[-1] + len(encoded_text_block) - 2)
                        current_block += 1

                i += 1

            # Convert pointer table int to sequence of bytes
            ptr_table_bytes: bytes = b''
            for items in ptr_table:
                if not items == 968 // 4:
                    ptr_table_bytes += (ulong_to_bytes(items))

            # Convert list of lists of encoded blocks to bytes
            encoded_block_bytes = bytes([val for sublist in encoded_block for val in sublist])
            # print("Encoded text data size is {} bytes".format(len(encoded_block_bytes)))

            if len(encoded_block_bytes) > 7044:
                print("ERROR: New encoded data is {} bytes. Size limit is 7044 bytes.".format(len(encoded_block_bytes)))
            else:
                # Write pointer new pointer table
                exe_file.seek(512716)
                exe_file.write(ptr_table_bytes)
                # Write encoded data
                exe_file.seek(505672)
                exe_file.write(encoded_block_bytes)

            exe_file.close()

    # If argument is -i, and arg2 is FOLDER, pack BIN files
    elif sys.argv[1] == "-i" and not os.path.isdir(sys.argv[2]):
        print("\nExpected folder. Provided file")
    elif sys.argv[1] == "-i" and os.path.isdir(sys.argv[2]):

        if not os.path.exists(index_file_path):
            print("\nIndex file missing")
        elif os.path.exists("{}.BIN".format(full_file_or_folder_name)):
            print("\nBIN file already exists. Please delete or move/delete before creation.")
        else:
            index_file_content = open(index_file_path, "r").readlines()

            index_file_line = 0

            while index_file_line < len(index_file_content):
                file_name = index_file_content[index_file_line].split(",")[0].upper()

                # If any MSG file is found. Insert TXT into MSG
                if any(fn in index_file_content[index_file_line].upper() for fn in [".MSG"]):
                    original_msg = (index_file_path.replace(os.path.basename(index_file_path), "") + file_name)
                    text_file = (index_file_path.replace(os.path.basename(index_file_path), "") + file_name + ".txt")
                    if os.path.exists(original_msg) and os.path.exists(text_file):
                        do_insert_msg(original_msg, text_file)
                    index_file_line += 1
                # If any TIM file is found. Insert TIM into original TIM
                elif any(fn in index_file_content[index_file_line].upper() for fn in [".TIM"]):
                    original_tim = (index_file_path.replace(os.path.basename(index_file_path), "") + file_name)
                    edited_tim = (index_file_path.replace(os.path.basename(index_file_path), "")
                                  + file_name.replace(".TIM", "_EXT.TIM"))
                    if os.path.exists(original_tim) and os.path.exists(edited_tim):
                        do_insert_tim(original_tim, edited_tim)
                    index_file_line += 1
                # If FONT file is found. Insert FONT into original FONT
                elif any(fn in index_file_content[index_file_line].upper() for fn in ("FONT.DAT", "KAIFONT.DAT")):
                    original_font = (index_file_path.replace(os.path.basename(index_file_path), "") + file_name)
                    edited_font = (index_file_path.replace(os.path.basename(index_file_path), "")
                                   + file_name.replace(".DAT", ".TIM"))
                    if os.path.exists(original_font) and os.path.exists(edited_font):
                        do_insert_font(original_font, edited_font)
                    index_file_line += 1
                # Else insert as is
                else:
                    index_file_line += 1

            do_pack_bin(full_file_or_folder_name, index_file_content)
