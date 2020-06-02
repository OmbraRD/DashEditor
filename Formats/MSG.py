#!/usr/bin/env python3

import os


def do_decode_block(block_data):
    data = block_data.hex().upper()
    data_map = [data[i:i + 2] for i in range(0, len(data), 2)]

    char_map = {
        "00": ["<00>"], "01": ["<01>"], "02": ["<02>"], "03": ["<03>"],
        "04": ["<04>"], "05": ["<05>"], "06": ["<06>"], "07": ["<07>"],
        "08": ["<08>"], "09": ["<09>"], "0A": ["<0A>"], "0B": ["<0B>"],
        "0C": ["<0C>"], "0D": ["!"], "0E": ["?"], "0F": ["<0F>"],
        "10": ["<10>"], "11": ["<11>"], "12": ["<12>"], "13": ["<13>"],
        "14": ["<14>"], "15": ["A"], "16": ["B"], "17": ["C"],
        "18": ["D"], "19": ["E"], "1A": ["F"], "1B": ["G"],
        "1C": ["H"], "1D": ["I"], "1E": ["J"], "1F": ["K"],
        "20": ["L"], "21": ["M"], "22": ["N"], "23": ["O"],
        "24": ["P"], "25": ["Q"], "26": ["R"], "27": ["S"],
        "28": ["T"], "29": ["<29>"], "2A": ["U"], "2B": ["V"],
        "2C": ["W"], "2D": ["X"], "2E": ["Y"], "2F": ["Z"],
        "30": ["a"], "31": ["b"], "32": ["c"], "33": ["d"],
        "34": ["e"], "35": ["f"], "36": ["g"], "37": ["h"],
        "38": ["i"], "39": ["j"], "3A": ["k"], "3B": ["l"],
        "3C": ["m"], "3D": ["n"], "3E": ["<3E>"], "3F": ["o"],
        "40": ["p"], "41": ["q"], "42": ["r"], "43": ["s"],
        "44": ["t"], "45": ["u"], "46": ["v"], "47": ["w"],
        "48": ["x"], "49": ["y"], "4A": ["z"], "4B": ["<4B>"],
        "4C": ["<4C>"], "4D": ["<4D>"], "4E": ["<4E>"], "4F": [" "],
        "50": ["<50>"], "51": ["<51>"], "52": ["-"], "53": ["<53>"],
        "54": ["<54>"], "55": ["<55>"], "56": ["<56>"], "57": ["<57>"],
        "58": ["<58>"], "59": ["<59>"], "5A": ["<5A>"], "5B": ["<5B>"],
        "5C": ["<5C>"], "5D": ["<5D>"], "5E": ["."], "5F": ["<5F>"],
        "60": ["<60>"], "61": ["<61>"], "62": ["<62>"], "63": ["<63>"],
        "64": ["<64>"], "65": ["<65>"], "66": ["<66>"], "67": ["<67>"],
        "68": ["<68>"], "69": ["<69>"], "6A": ["<6A>"], "6B": ["<6B>"],
        "6C": ["<6C>"], "6D": ["<6D>"], "6E": ["<6E>"], "6F": ["<6F>"],
        "70": ["<70>"], "71": ["<71>"], "72": ["<72>"], "73": ["<73>"],
        "74": ["<74>"], "75": ["<75>"], "76": ["<76>"], "77": ["<77>"],
        "78": ["<78>"], "79": ["<79>"], "7A": ["<7A>"], "7B": ["<7B>"],
        "7C": ["<7C>"], "7D": ["<7D>"], "7E": ["<7E>"], "7F": ["<7F>"],
        "80": ["<80>"], "81": ["<81>"], "82": ["<82>"], "83": ["<83>"],
        "84": ["<84>"], "85": ["<85>"], "86": ["\n"], "87": ["<87>"],
        "88": ["<88>"], "89": ["<89>"], "8A": ["<8A>"], "8B": ["<8B>"],
        "8C": ["<8C>"], "8D": ["<8D>"], "8E": ["<8E>"], "8F": ["<8F>"],
        "90": ["<90>"], "91": ["<91>"], "92": ["<92>"], "93": ["<93>"],
        "94": ["<94>"], "95": ["<95>"], "96": ["<96>"], "97": ["<97>"],
        "98": ["<98>"], "99": ["<99>"], "9A": ["<9A>"], "9B": ["<9B>"],
        "9C": ["<9C>"], "9D": ["<9D>"], "9E": ["<9E>"], "9F": ["<9F>"],
        "A0": ["<A0>"], "A1": ["<A1>"], "A2": ["<A2>"], "A3": ["<A3>"],
        "A4": ["<A4>"], "A5": ["<A5>"], "A6": ["<A6>"], "A7": ["<A7>"],
        "A8": ["<A8>"], "A9": ["<A9>"], "AA": ["<AA>"], "AB": ["<AB>"],
        "AC": ["<AC>"], "AD": ["<AD>"], "AE": ["<AE>"], "AF": ["<AF>"],
        "B0": ["<B0>"], "B1": ["<B1>"], "B2": ["<B2>"], "B3": ["<B3>"],
        "B4": ["<B4>"], "B5": ["<B5>"], "B6": ["<B6>"], "B7": ["<B7>"],
        "B8": ["<B8>"], "B9": ["<B9>"], "BA": ["<BA>"], "BB": ["<BB>"],
        "BC": ["<BC>"], "BD": ["<BD>"], "BE": ["<BE>"], "BF": ["<BF>"],
        "C0": ["<C0>"], "C1": ["<C1>"], "C2": ["<C2>"], "C3": ["<C3>"],
        "C4": ["<C4>"], "C5": ["<C5>"], "C6": ["<C6>"], "C7": ["<C7>"],
        "C8": ["<C8>"], "C9": ["<C9>"], "CA": ["<CA>"], "CB": ["<CB>"],
        "CC": ["<CC>"], "CD": ["<CD>"], "CE": ["<CE>"], "CF": ["<CF>"],
        "D0": ["<D0>"], "D1": ["<D1>"], "D2": ["<D2>"], "D3": ["<D3>"],
        "D4": ["<D4>"], "D5": ["<D5>"], "D6": ["<D6>"], "D7": ["<D7>"],
        "D8": ["<D8>"], "D9": ["<D9>"], "DA": ["<DA>"], "DB": ["<DB>"],
        "DC": ["<DC>"], "DD": ["<Dd>"], "DE": ["<DE>"], "DF": ["<DF>"],
        "E0": ["<E0>"], "E1": ["<E1>"], "E2": ["<E2>"], "E3": ["<E3>"],
        "E4": ["<E4>"], "E5": ["<E5>"], "E6": ["<E6>"], "E7": ["<E7>"],
        "E8": ["<E8>"], "E9": ["<E9>"], "EA": ["<EA>"], "EB": ["<EB>"],
        "EC": ["<EC>"], "ED": ["<Ed>"], "EE": ["<EE>"], "EF": ["<EF>"],
        "F0": ["<F0>"], "F1": ["<F1>"], "F2": ["<F2>"], "F3": ["<F3>"],
        "F4": ["<F4>"], "F5": ["<F5>"], "F6": ["<F6>"], "F7": ["<F7>"],
        "F8": ["<F8>"], "F9": ["<F9>"], "FA": ["<FA>"], "FB": ["<FB>"],
        "FC": ["<FC>"], "FD": ["<FD>"], "FE": ["<FE>"], "FF": ["<FF>"],
    }

    decoded_data = [y for x in data_map for y in char_map[x]]

    return "".join(decoded_data)


def do_decode_msg(index_file_path):

    header = 2048  # 0x800
    # Open the index file
    index_file = open(index_file_path, "r").read()
    # Get the file path for .MSG files
    msg_file_name = ([x for x in index_file.splitlines() if ".msg" in x])[0].split(",")[0]
    msg_file_path = "{}/{}".format((os.path.splitext(index_file_path))[0].split("/")[0], msg_file_name)

    print("\nDecoding {}".format(msg_file_path))
    # Open MSG file
    msg_file = open(msg_file_path, "rb").read()
    # Read pointer table size
    ptr_tbl_size = int.from_bytes(msg_file[header:header + 2], byteorder="little")
    # Read pointer table data
    ptr_tbl_data = msg_file[header:header + ptr_tbl_size]

    print("Pointer table contains {} blocks".format(int(ptr_tbl_size / 2 - 1)))

    output_file = open(msg_file_path + ".txt", "w")

    ptr_tbl_offset = 0
    block_number = 1

    while ptr_tbl_offset < ptr_tbl_size - 2:
        block_start_offset = header + int.from_bytes(ptr_tbl_data[ptr_tbl_offset:ptr_tbl_offset + 2], byteorder="little")
        block_end_offset = header + int.from_bytes(ptr_tbl_data[ptr_tbl_offset + 2:ptr_tbl_offset + 4], byteorder="little")

        block_data = msg_file[block_start_offset:block_end_offset]

        # Write each block with offset information
        output_file.write(
            "[Block {}, String: {}-{}]\n".format(block_number, hex(block_start_offset), hex(block_end_offset))
        )

        output_file.write(do_decode_block(block_data) + "\n\n")

        ptr_tbl_offset = ptr_tbl_offset + 2
        block_number = block_number + 1

    output_file.close()