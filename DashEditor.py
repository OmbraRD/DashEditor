import sys, os, re, math


def do_pack_bin():
    # Initialize the needed variables
    index_file_item = 0

    # Check if all files inside the index exists and are the correct size
    error = False

    while index_file_item < len(index_file_data):

        path_file_to_write = str(folder_name + "/" +
                                 index_file_data[index_file_item]).replace("\\n", "").split(",")[0]
        file_to_write_index_len = str(index_file_data[index_file_item]).replace("\\n", "").split(",")[1]
        # If the path does not exist. ERROR
        if not os.path.exists(path_file_to_write):
            print(path_file_to_write + " does not exists")
            index_file_item += 1
            error = True
        # If the file sizes don't match. ERROR
        elif os.path.getsize(path_file_to_write) != int(file_to_write_index_len):
            print(path_file_to_write + " has a size of " + str(os.path.getsize(path_file_to_write)) +
                  " instead of " + file_to_write_index_len + " bytes")
            index_file_item += 1
            error = True
        else:
            index_file_item += 1

    # If all the tests pass,
    if not error:
        print("Creating " + folder_name + ".BIN file...")
        output_bin = open(folder_name + ".BIN", "ab")

        index_file_item = 0
        end_file_size = 0
        padding = 2048  # 0x800

        while index_file_item < len(index_file_data):
            # Get file path and open it
            path_file_to_write = str(folder_name + "/" +
                                     index_file_data[index_file_item]).replace("\\n", "").split(",")[0]
            file_to_write = open(path_file_to_write, "rb")
            # Write the contents of opened file to destination BIN and close opened file
            output_bin.write(file_to_write.read())
            file_to_write.close()
            # Add the written file size to a variable for use with padding calculations
            end_file_size = end_file_size + os.path.getsize(path_file_to_write)
            index_file_item += 1

        # Add Archive termination before padding
        output_bin.write(b'\xFF\xFF\xFF\xFF')

        # Calculate end padding and write it
        end_padding = (((end_file_size // padding) + 1) * padding) - end_file_size - 4
        output_bin.write(end_padding * b'\x00')

        output_bin.close()
    return


def do_unpack_bin():
    # Find all files inside the archive
    occurrences = re.findall(b"\\x2E\\x2E\\x5C", file_data)
    print("Found " + str(len(occurrences)) + " files. Extracting...\n")

    offset = 0
    padding = 2048  # 0x800

    # Check if the amount of extracted files is correct
    loop_counter = 0
    existing_file_counter = 0

    while offset < len(file_data):

        if file_data[offset:offset + 4].startswith(b'\xFF\xFF\xFF\xFF'):
            break
        else:
            # Check if if it starts with a ..\
            if file_data[offset + 64:offset + 128].startswith(b"..\\"):

                # Get folder and filename
                file_name_and_folders: str = file_data[offset + 64:offset + 128].replace(b'\x00', b'').decode()

                # Get folders names
                for folders in [file_name_and_folders.split("\\")]:
                    # Skip all items that contains a dot (beginning and filename)
                    full_path = file_path + "/" + "/".join([x for x in folders if not "." in x])
                    # Check if the folder has already been created. If not, create it
                    if not os.path.exists(full_path):
                        os.makedirs(full_path)

                # Get file name and extension
                inner_file_name = file_name_and_folders.split("\\")[-1]
                inner_file_extension = inner_file_name.split(".")[-1].upper()
                file_name_to_write = full_path + "/" + inner_file_name

                # Check if there are files with the same names (it happens). Add number to name and get ready for write
                if os.path.exists(file_name_to_write):
                    file_name_to_write = (
                            full_path + "/" + inner_file_name.split(".")[0] + "_"
                            + str(existing_file_counter) + "." + inner_file_name.split(".")[-1])
                    inner_file = open(file_name_to_write, "wb")
                else:
                    inner_file = open(file_name_to_write, "wb")

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

                if file_data[offset:offset + 4] == b'\x01\x00\x00\x00':  # TIM
                    tim_width = int.from_bytes(
                        [file_data[offset + 39], file_data[offset + 38],
                         file_data[offset + 37], file_data[offset + 36]], byteorder="big"
                    )
                    tim_height = int.from_bytes(
                        [file_data[offset + 43], file_data[offset + 42],
                         file_data[offset + 41], file_data[offset + 40]], byteorder="big"
                    )
                    file_len = tim_width * tim_height * 2

                # CLT, Imageless TIM with CLUT only or Imageless TIM with CLUT Patch
                # Size = Width (0x14) * Height (0x18) * 2

                elif ((file_data[offset:offset + 4] == b'\x04\x00\x00\x00') or  # CLT
                      (file_data[offset:offset + 4] == b'\x09\x00\x00\x00') or  # Imageless CLUT (in TIM format)
                      (file_data[offset:offset + 4] == b'\x0A\x00\x00\x00')):  # Imagelesss CLUT Patch(in TIM format)
                    clt_tim_width = int.from_bytes(
                        [file_data[offset + 23], file_data[offset + 22],
                         file_data[offset + 21], file_data[offset + 20]], byteorder="big"
                    )
                    clt_tim_height = int.from_bytes(
                        [file_data[offset + 27], file_data[offset + 26],
                         file_data[offset + 25], file_data[offset + 24]], byteorder="big"
                    )
                    file_len = clt_tim_width * clt_tim_height * 2

                # FONT
                elif file_data[offset:offset + 4] == b'\x03\x00\x00\x00':  # FONT
                    file_len = int.from_bytes(
                        [file_data[offset + 7], file_data[offset + 6],
                         file_data[offset + 5], file_data[offset + 4]], byteorder="big"
                        ) + 1

                # Anything else.
                else:
                    file_len = int.from_bytes(
                        [file_data[offset + 7], file_data[offset + 6],
                         file_data[offset + 5], file_data[offset + 4]], byteorder="big"
                    ) + padding
                    padded_file_size = ((file_len // padding) + 1) * padding
                    # This fixes files that already have an aligned size or that still have data in the middle
                    if file_data[offset + file_len + 64:offset + file_len + 67].startswith(b"..\\"):
                        file_len = file_len - 1
                    elif not (
                            file_data[offset + padded_file_size + 64:offset + padded_file_size + 67].startswith(b"..\\") or
                            file_data[offset + padded_file_size:offset + padded_file_size + 4].startswith(b"\xFF\xFF\xFF\xFF")):
                        file_len = file_len + padding

                # Add the file length to the offset and align to 0x800. If it is already a multiple add 1
                padded_file_size = ((file_len // padding) + 1) * padding

                print("Extracting " + inner_file_name + " to folder /" + full_path)
                print("Real file size: " + str(file_len) + " byes / Aligned file size: "
                      + str(padded_file_size) + " bytes.")

                # Write file
                inner_file.write(file_data[offset:offset + padded_file_size])
                inner_file.close()

                # Write file info to index file for packing later
                index_file.write(
                    str(file_name_to_write.replace(file_path + "/", "")) + "," + str(padded_file_size) + "\n")

                # Set offset to the old offset + the size of the aligned files
                offset = offset + padded_file_size
                # Add 1 to the loop counter
                loop_counter += 1
            else:
                # If it does not start with ..\ just add padding to the offset
                offset = offset + padding

    # Close the index file and return
    index_file.close()

    if len(occurrences) == loop_counter:
        print("\nThe amount of extracted files matches the occurrences.")
    else:
        print("\nSome files where not extracted successfully.")
    return


help_msg = ("DashEditor v0.2 - Mega Man Legends Hacking Suite\n"
            "Created by _Ombra_ of SadNES cITy Translations\n"
            "Website: http://www.sadnescity.it\n\n"
            "DashEditor.py [option] [file or folder]\n\n"
            "  -e   unpacks che content of BIN files.\n"
            "  -c   packs a folder to BIN files.\n")

# Check if 2 arguments are passed
if len(sys.argv) != 3:
    print(help_msg + "\nOne or more arguments missing or too many")
# If they are, check if the command argument is valid
elif sys.argv[1] != "-e" and sys.argv[1] != "-c":
    print(help_msg + "\nInvalid command!")
# If the command argument is valid, check if file exists and open it
elif not os.path.exists(sys.argv[2]):
    print("File or folder not found")
# If second argument is -e and third argument is file
elif sys.argv[1] == "-e" and not os.path.isfile(sys.argv[2]):
    print("Expected file. Provided folder")
elif sys.argv[1] == "-e" and os.path.isfile(sys.argv[2]):
    file_name: str = sys.argv[2]
    file = open(file_name, "rb")
    file_data: bytes = file.read()

    # Check if the file is a valid MML BIN file
    try:
        assert file_data[64:67].decode("ascii") == "..\\"
    except AssertionError:
        print("Not a valid MML PSX BIN file\n")

    # Normalize slashes if file is in sub-folders in Windows
    # Ex: TEST\\TEST2\\FILE.BIN == TEST/TEST2/FILE.BIN
    file_name = file_name.replace('\\', '/')
    # Get only the file name from the normalized path
    # Ex: TEST/TEST2/FILE.BIN == FILE.BIN
    file_name_only = os.path.split(file_name)[-1]
    # Get only the paths
    # Ex: TEST/TEST2/FILE.BIN == TEST/TEST2/FILE
    file_path = file_name.replace(".BIN", "")

    # Create index file
    if not os.path.exists(file_name.replace(".BIN", "")):
        os.mkdir(file_name.replace(".BIN", ""))

    index_file = open(file_path + "/" + file_name_only.replace(".BIN", ".txt"), "w+")

    # Proceed with extraction
    do_unpack_bin()
    file.close()

# If argument is -c, pack BIN files
elif sys.argv[1] == "-c" and os.path.isdir(sys.argv[2]):

    # Normalize slashes if file is in sub-folders
    # Ex: TEST\\TEST2 == TEST/TEST2
    folder_name: str = sys.argv[2].replace('\\', '/')
    # Get only the index file name from the normalized path
    # Ex: TEST/TEST2 == TEST.txt
    index_file_name = sys.argv[2].split("/")[-1] + ".txt"
    # Full path to the index file
    index_full_path = folder_name + "/" + index_file_name

    if not os.path.exists(index_full_path):
        print("Index file missing")
    elif os.path.exists(folder_name + ".BIN"):
        print("BIN file already exists")
    else:
        index_file = open(index_full_path, "r")
        index_file_data: list = index_file.readlines()
        index_file.close()
        do_pack_bin()
