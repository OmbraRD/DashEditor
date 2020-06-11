#!/usr/bin/env python3

from Formats.BIN import bytes_to_uint, ulong_to_bytes, uint_to_bytes


def do_decode_pixel_data(tim_pixel_data, tim_img_size, tim_colors, tim_height, tim_width):

    decoded_pixel_data = [0] * bytes_to_uint(tim_img_size)
    blockw = 128
    blockh = 32
    timcolors = bytes_to_uint(tim_colors)
    timh = bytes_to_uint(tim_height)

    rofs = 0

    if timcolors == 16:
        inc = 2
        timw = bytes_to_uint(tim_width) * 4  # Multiply by 4 to get the real width

        for y in range(0, timh, blockh):
            for x in range(0, timw, blockw):
                for by in range(0, blockh):
                    for bx in range(0, blockw, inc):
                        px = tim_pixel_data[rofs]
                        decoded_pixel_data[((y + by) * (timw // 2)) + ((x + bx) // 2)] = px
                        rofs += 1
        return decoded_pixel_data

    elif timcolors == 256:
        inc = 1
        timw = bytes_to_uint(tim_width) * 2  # Multiply by 2 to get the real width
        blockw = blockw // 2

        for y in range(0, timh, blockh):
            for x in range(0, timw, blockw):
                for by in range(0, blockh):
                    for bx in range(0, blockw, inc):
                        px = tim_pixel_data[rofs]
                        decoded_pixel_data[((y + by) * timw) + (x + bx)] = px
                        rofs += 1
        return decoded_pixel_data


# def do_fix_header(tim_file):
#     return header

def do_extract_tim(file_path):
    header = 2048  # 0x800

    print("Extracting {}".format(file_path))
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
        tim_pixel_data = tim_file[2048:]

        # Reversing nibble order should fix MML PC TIM files
        # tim_pixel_data = bytes(((x << 4 & 0xF0) + (x >> 4)) for x in tim_pixel_data)

        pixel_data = do_decode_pixel_data(tim_pixel_data, tim_img_size, tim_colors, tim_height, tim_width)

        # Write the decoded TIM to file
        output_file = open(file_path.split(".")[0] + "_EXT.TIM", "wb")
        output_file.write(
            tim_tag + tim_bpp + tim_clut_size + tim_fb_pal_x + tim_fb_pal_y + tim_colors + tim_clut_num +
            cluts + tim_img_size + tim_fb_img_x + tim_fb_img_y + tim_width + tim_height + bytearray(pixel_data)
        )
        output_file.close()

    elif tim_file[0:4] == b'\x09\x00\x00\x00':
        print("CLUT only TIM file")

    elif tim_file[0:4] == b'\x0A\x00\x00\x00':
        print("CLUT Patch inside TIM file")
