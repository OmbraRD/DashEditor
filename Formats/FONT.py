#!/usr/bin/env python3

from Formats.BIN import bytes_to_uint, ulong_to_bytes


def do_extract_font(file_path):

    print("Extracting {}".format(file_path))
    # Open FONT file
    font_file = open(file_path, "rb").read()

    img_width = 256
    img_height = 512

    tim_tag = b'\x10\x00\x00\x00'
    tim_bpp = b'\x08\x00\x00\x00'
    tim_clut_size = b'\x2c\x00\x00\x00'
    tim_fb_pal_x = b'\x00\x00'  # Not known
    tim_fb_pal_y = b'\x00\x00'  # Not known
    tim_colors = b'\x10\x00'
    tim_clut_num = b'\x01\x00'
    # Palette = #000, #FFF, #BBB, #888
    clut = b'\x00\x00\xFF\xFF\xF7\xDE\xEF\xBD\x00\x00\x00\x00\x00\x00\x00\x00' \
           b'\x00\x00\xFF\xFF\xF7\xDE\xEF\xBD\x00\x00\x00\x00\x00\x00\x00\x00'
    tim_img_size = ulong_to_bytes((img_width // 4) * img_height * 2 + 12)
    tim_fb_img_x = b'\x00\x00'  # Not known
    tim_fb_img_y = b'\x00\x00'  # Not known
    tim_width = b'\x40\x00'
    tim_height = b'\x00\x02'
    tim_pixel_data = font_file[2048:]

    block_width = 128
    block_height = 32

    decoded_pixel_data_top = [0] * ((bytes_to_uint(tim_img_size) - 12) // 2)
    decoded_pixel_data_bottom = [0] * ((bytes_to_uint(tim_img_size) - 12) // 2)
    offset = 0

    for y in range(0, img_height // 2, block_height):
        for x in range(0, img_width, block_width):
            for by in range(0, block_height):
                for bx in range(0, block_width, 2):
                    byte = tim_pixel_data[offset]
                    a = byte & 0x03
                    b = ((byte & 0x30) >> 4)
                    c = ((byte >> 2) & 0x3)
                    d = (((byte >> 2) & 0x30) >> 4)
                    decoded_pixel_data_top[((y + by) * (img_width // 2)) + ((x + bx) // 2)] = (b * 16) + a
                    decoded_pixel_data_bottom[((y + by) * (img_width // 2)) + ((x + bx) // 2)] = (d * 16) + c
                    offset += 1

    output_file = open(file_path.split(".")[0] + ".TIM", "wb")
    output_file.write(
        tim_tag + tim_bpp + tim_clut_size + tim_fb_pal_x + tim_fb_pal_y + tim_colors + tim_clut_num +
        clut + tim_img_size + tim_fb_img_x + tim_fb_img_y + tim_width + tim_height +
        bytearray(decoded_pixel_data_top) + bytearray(decoded_pixel_data_bottom)
    )

    print("\nFound font. Extraction complete")