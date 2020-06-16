#!/usr/bin/env python3

from Formats.BIN import bytes_to_uint, ulong_to_bytes, uint_to_bytes


def do_ord_pixel_data(tim_colors, tim_img_size, tim_width, tim_height, tim_pixel_data, encode=None):

    timcolors: int = 0
    timw: int = 0
    timh: int = 0
    ord_pixel_data: list = []

    if not encode:
        timcolors = bytes_to_uint(tim_colors)
        timh = bytes_to_uint(tim_height)
        timw = bytes_to_uint(tim_width)
        ord_pixel_data = [0] * (bytes_to_uint(tim_img_size) - 12)
    elif encode:
        timcolors = tim_colors
        timh = tim_height
        timw = tim_width
        ord_pixel_data = [0] * (tim_img_size - 12)

    blockw = 64
    blockh = 32

    rofs = 0

    if timcolors == 16:
        inc = 2
        blockw = blockw * 2
        timw = timw * 4  # Multiply by 4 to get the real width

        for y in range(0, timh, blockh):
            for x in range(0, timw, blockw):
                for by in range(0, blockh):
                    for bx in range(0, blockw, inc):
                        if not encode:
                            px = tim_pixel_data[rofs]
                            ord_pixel_data[((y + by) * (timw // 2)) + ((x + bx) // 2)] = px
                        else:
                            px = tim_pixel_data[((y + by) * (timw // 2)) + ((x + bx) // 2)]
                            ord_pixel_data[rofs] = px
                        rofs += 1
        return ord_pixel_data

    elif timcolors == 256:
        inc = 1
        timw = timw * 2  # Multiply by 2 to get the real width

        for y in range(0, timh, blockh):
            for x in range(0, timw, blockw):
                for by in range(0, blockh):
                    for bx in range(0, blockw, inc):
                        if not encode:
                            px = tim_pixel_data[rofs]
                            ord_pixel_data[((y + by) * timw) + (x + bx)] = px
                        else:
                            px = tim_pixel_data[((y + by) * timw) + (x + bx)]
                            ord_pixel_data[rofs] = px
                        rofs += 1
        return ord_pixel_data


def do_compress_tim(original_tim, edited_tim):
    header = 2048  # 0x800

    print("Converting {}".format(original_tim))
    # Open TIM file
    original_tim = open(original_tim, "rb+")
    edited_tim = open(edited_tim, "rb").read()

    # Check if TIM file
    if edited_tim[0:4] == b'\x10\x00\x00\x00' and any(bpp in edited_tim[4:6] for bpp in (b'\x08\x00', b'\x09\x00')):

        # Check if it is a 4bpp or 8bpp TIM
        tim_colors: int = 0
        if edited_tim[16:18] == b'\x10\x00':  # 16 colors, 4bpp
            tim_colors: int = 16
        elif edited_tim[16:18] == b'\x00\x01':  # 256 colors, 8bpp
            tim_colors: int = 256
        # Read CLUT size to derive offsets for required TIM information
        tim_clut_size: int = bytes_to_uint(edited_tim[8:12])
        # Derive needed information
        tim_img_size: int = bytes_to_uint(edited_tim[tim_clut_size + 8: tim_clut_size + 12])
        tim_width: int = bytes_to_uint(edited_tim[tim_clut_size + 16: tim_clut_size + 18])
        tim_height: int = bytes_to_uint(edited_tim[tim_clut_size + 18: tim_clut_size + 20])
        tim_pixel_data: bytes = edited_tim[tim_clut_size + 20:]

        ord_pixel_data = do_ord_pixel_data(tim_colors, tim_img_size, tim_width, tim_height, tim_pixel_data, encode=True)

        original_tim.seek(header)
        original_tim.write(bytearray(ord_pixel_data))
        original_tim.close()


def do_extract_tim(file_path):
    header = 2048  # 0x800

    print("Converting {}".format(file_path))
    # Open TIM file
    tim_file = open(file_path, "rb").read()

    # 4bpp and 8bpp TIM file
    if tim_file[0:4] == b'\x01\x00\x00\x00':
        tim_tag = b'\x10\x00\x00\x00'
        tim_bpp = b''
        tim_clut_size = b''
        if tim_file[20:22] == b'\x10\x00':  # 4bpp
            tim_clut_size = ulong_to_bytes((bytes_to_uint(tim_file[24:26]) * 32 + 12))
            tim_bpp = b'\x08\x00\x00\x00'
        elif tim_file[20:22] == b'\x00\x01':  # 8bpp
            tim_clut_size = ulong_to_bytes((bytes_to_uint(tim_file[24:26]) * 512 + 12))
            tim_bpp = b'\x09\x00\x00\x00'
        tim_fb_pal_x = tim_file[12:14]
        tim_fb_pal_y = tim_file[16:18]
        tim_colors = tim_file[20:22]
        tim_clut_num = tim_file[24:26]
        cluts = tim_file[256:256 + (bytes_to_uint(tim_clut_size) - 12)]
        tim_img_size = ulong_to_bytes((bytes_to_uint(tim_file[36:40]) * bytes_to_uint(tim_file[40:44]) * 2 + 12))
        tim_fb_img_x = tim_file[28:30]
        tim_fb_img_y = tim_file[32:34]
        tim_width = tim_file[36:38]
        tim_height = tim_file[40:42]
        tim_pixel_data: bytes = tim_file[header:]

        # Reversing nibble order should fix MML PC TIM files
        # tim_pixel_data = bytes(((x << 4 & 0xF0) + (x >> 4)) for x in tim_pixel_data)

        ord_pixel_data = do_ord_pixel_data(tim_colors, tim_img_size, tim_width, tim_height, tim_pixel_data, encode=False)

        # Write the decoded TIM to file
        output_file = open(file_path.split(".")[0] + "_EXT.TIM", "wb")
        output_file.write(
            tim_tag + tim_bpp + tim_clut_size + tim_fb_pal_x + tim_fb_pal_y + tim_colors + tim_clut_num +
            cluts + tim_img_size + tim_fb_img_x + tim_fb_img_y + tim_width + tim_height + bytearray(ord_pixel_data)
        )
        output_file.close()

    elif tim_file[0:4] == b'\x09\x00\x00\x00':
        print("CLUT only TIM file")

    elif tim_file[0:4] == b'\x0A\x00\x00\x00':
        print("CLUT Patch inside TIM file")
