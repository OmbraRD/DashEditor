#!/usr/bin/env python3

import os
import re


def bytes_to_uint(data):
    data = int.from_bytes(data, byteorder="little")
    return data


def uint_to_bytes(data):
    two_bytes = data.to_bytes(2, byteorder="little")
    return two_bytes


def ulong_to_bytes(data):
    four_bytes = data.to_bytes(4, byteorder="little")
    return four_bytes


def do_unpack_bin(full_path_and_file_no_ext, f_data, index_file):
    # Find all files inside the archive
    occurrences = re.findall(b"\\x2E\\x2E\\x5C", f_data)
    print("Found {} files. Extracting...\n".format(str(len(occurrences))))

    offset = 0
    padding = 2048  # 0x800

    # Check if the amount of extracted files is correct
    loop_counter = 0

    while offset < len(f_data):

        if f_data[offset:offset + 4].startswith(b'\xFF\xFF\xFF\xFF'):
            break
        else:
            # Check if if it starts with a ..\
            if f_data[offset + 64:offset + 128].startswith(b"..\\"):

                # Get folders and filename and replace \ with / (Fix for Linux since os.path.norpath does not work)
                inner_folder_and_file: str = (
                    f_data[offset + 67:offset + 128].replace(b'\x00', b'').decode().replace("\\", "/"))

                # Get folders names
                for folders in [inner_folder_and_file.split("/")]:
                    # Skip all items that contains a dot (beginning and filename)
                    full_path = full_path_and_file_no_ext + "/" + "/".join([x for x in folders if not "." in x])
                    # Check if the folder has already been created. If not, create it
                    if not os.path.exists(full_path):
                        os.makedirs(full_path)

                # Check file type for extraction

                # Data = 00             Generic
                # TIM = 01              Full TIM image
                # Font = 03
                # CLUT = 04             Separate CLUT file "CLT"
                # VAB = 05              Sound file
                # SEP = 08              Sound file
                # TIMCLUTOnly = 09      Also separate CLUT, but in an imageless TIM
                # TIMCLUTPatch = 0A     Same header as TIM without FB coords and image size. Same Palette

                # Size = Width (0x24) * Height (0x28) * 2
                # Regular TIM
                if f_data[offset:offset + 4] == b'\x01\x00\x00\x00':  # TIM
                    tim_width = bytes_to_uint(f_data[offset + 36:offset + 40])
                    tim_height = bytes_to_uint(f_data[offset + 40:offset + 44])
                    file_len = tim_width * tim_height * 2

                # CLT, Imageless TIM with CLUT only or Imageless TIM with CLUT Patch
                # Size = Width (0x14) * Height (0x18) * 2
                elif ((f_data[offset:offset + 4] == b'\x04\x00\x00\x00') or  # CLT
                      (f_data[offset:offset + 4] == b'\x09\x00\x00\x00') or  # Imageless CLUT (in TIM format)
                      (f_data[offset:offset + 4] == b'\x0A\x00\x00\x00')):  # Imagelesss CLUT Patch(in TIM format)
                    clt_tim_width = bytes_to_uint(f_data[offset + 20:offset + 24])
                    clt_tim_height = bytes_to_uint(f_data[offset + 24:offset + 28])
                    file_len = clt_tim_width * clt_tim_height * 2

                # FONT
                elif f_data[offset:offset + 4] == b'\x03\x00\x00\x00':  # FONT
                    file_len = bytes_to_uint(f_data[offset + 4:offset + 8]) + 1

                # Anything else.
                else:
                    file_len = bytes_to_uint(f_data[offset + 4:offset + 8]) + padding

                    padded_fsize = ((file_len // padding) + 1) * padding
                    # This fixes files that already have an aligned size or that still have data in the middle
                    if f_data[offset + file_len + 64:offset + file_len + 67].startswith(b"..\\"):
                        file_len = file_len - 1
                    elif not (f_data[offset + padded_fsize + 64:offset + padded_fsize + 67].startswith(b"..\\") or
                              f_data[offset + padded_fsize:offset + padded_fsize + 4].startswith(b"\xFF\xFF\xFF\xFF")):
                        file_len = file_len + padding

                # Add the file length to the offset and align to 0x800. If it is already a multiple add 1
                padded_fsize = ((file_len // padding) + 1) * padding

                # Get file name and extension
                inner_file_name = os.path.basename(inner_folder_and_file)
                # inner_folder_and_file.split("/")[-1]

                # Check if there are files with the same names (it happens). Add number to name and get ready for write
                inner_file_name_only = inner_file_name.split(".")[0]
                inner_file_name_extension = inner_file_name.split(".")[-1]

                file_name_to_write = "{}/{}".format(full_path, inner_file_name)

                if os.path.exists(file_name_to_write):
                    existing_file_counter = 0
                    while os.path.exists(file_name_to_write):
                        file_name_to_write = "{}/{}_{}.{}".format(
                            full_path, inner_file_name_only, str(existing_file_counter), inner_file_name_extension)
                        existing_file_counter += 1

                inner_file = open(file_name_to_write, "wb")

                print("Extracting {} to folder {}".format(inner_file_name, os.path.dirname(file_name_to_write)))
                print("Real file size: {} byes - Aligned file size: {} bytes.".format(str(file_len), str(padded_fsize)))

                # Write file
                inner_file.write(f_data[offset:offset + padded_fsize])
                inner_file.close()

                # Write file info to index file for packing later
                index_file.write(re.sub(r'^.*?/', "", file_name_to_write) + "," + str(padded_fsize) + "\n")

                # Set offset to the old offset + the size of the aligned files
                offset = offset + padded_fsize
                # Add 1 to the loop counter
                loop_counter += 1
            else:
                # If it does not start with ..\ just add padding to the offset
                offset = offset + padding

    if len(occurrences) == loop_counter:
        print("\nThe amount of extracted files matches the occurrences.")
    else:
        print("\nSome files where not extracted successfully.")


def do_pack_bin(full_file_or_folder_name, index_file_data):
    # Initialize the needed variables
    index_file_item: int = 0

    # Check if all files inside the index exists and are the correct size
    error = False

    while index_file_item < len(index_file_data):

        path_inner_file_to_write = (
                full_file_or_folder_name + "/" + index_file_data[index_file_item].replace("\\n", "").split(",")[0])
        file_to_write_index_len = index_file_data[index_file_item].replace("\\n", "").split(",")[1]

        # If the path does not exist. ERROR
        if not os.path.exists(path_inner_file_to_write):
            print("{} does not exists".format(path_inner_file_to_write))
            index_file_item += 1
            error = True
        # If the file sizes don't match. ERROR
        elif os.path.getsize(path_inner_file_to_write) != int(file_to_write_index_len):
            print("{} has a size of {} instead of {} bytes".format(
                path_inner_file_to_write, str(os.path.getsize(path_inner_file_to_write)), file_to_write_index_len))
            index_file_item += 1
            error = True
        else:
            index_file_item += 1

    # If all the tests pass,
    if not error:
        print("Creating {}.BIN file...".format(full_file_or_folder_name))
        output_bin = open("{}.BIN".format(full_file_or_folder_name), "ab")

        index_file_item = 0
        end_file_size = 0
        padding = 2048  # 0x800

        while index_file_item < len(index_file_data):
            # Get file path and open it
            path_inner_file_to_write = "{}/{}".format(
                full_file_or_folder_name, index_file_data[index_file_item].replace("\\n", "").split(",")[0])
            file_to_write = open(path_inner_file_to_write, "rb")
            # Write the contents of opened file to destination BIN and close opened file
            output_bin.write(file_to_write.read())
            file_to_write.close()
            # Add the written file size to a variable for use with padding calculations
            end_file_size = end_file_size + os.path.getsize(path_inner_file_to_write)
            index_file_item += 1

        # Add Archive termination before padding
        output_bin.write(b'\xFF\xFF\xFF\xFF')

        # Calculate end padding and write it
        end_padding = (((end_file_size // padding) + 1) * padding) - end_file_size - 4
        output_bin.write(end_padding * b'\x00')

        output_bin.close()
