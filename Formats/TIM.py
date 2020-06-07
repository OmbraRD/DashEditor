#!/usr/bin/env python3


def do_extract_tim(tim_file_path):

    header = 2048  # 0x800

    print("\nExtracting {}".format(tim_file_path))
    # Open MSG file
    #tim_file = open(tim_file_path, "rb").read()


    #output_file = open(tim_file_path.split(".")[0] + "_EXT.TIM", "w")

    ptr_tbl_offset = 0
    block_number = 1
