#!/usr/bin/env python3

import os


def bytes_to_uint(data):
    data = int.from_bytes(data, byteorder="little")
    return data


def uint_to_bytes(data):
    two_bytes = data.to_bytes(2, byteorder="little")
    return two_bytes


def ulong_to_bytes(data):
    four_bytes = data.to_bytes(4, byteorder="little")
    return four_bytes


def do_extract_font(font_file):
    # palette = ["#000", "#fff", "#bbb", "#888"]

    img_width = 256
    img_height = 256

    tim_tag = b'\x10\x00\x00\x00'
    tim_bpp = b'\x08\x00\x00\x00'
    tim_clut_size = b'\x2c\x00\x00\x00'
    tim_fb_pal_x = b'\x00\x00'  # Not known
    tim_fb_pal_y = b'\x00\x00'  # Not known
    tim_colors = b'\x10\x00'
    tim_clut_num = b'\x01\x00'
    clut = b'\x00\x00\xFF\xFF\xEF\xBD\xCE\xB9\xAD\xB5\x8C\xB1\x6B\xAD\x4A\xA9' \
           b'\x29\xA5\x08\xA1\xE7\x9C\xC6\x98\xA5\x94\x84\x90\x63\x8C\x42\x88'
    tim_img_size = ulong_to_bytes((img_width // 4) * img_height * 2 + 12)
    tim_fb_img_x = b'\x00\x00'  # Not known
    tim_fb_img_y = b'\x00\x00'  # Not known
    tim_width = b'\x40\x00'
    tim_height = b'\x00\x01'
    tim_pixel_data = font[2048:]

    block_width = 128
    block_height = 32

    decoded_pixel_data = [0] * bytes_to_uint(tim_img_size)
    offset = 0

    for y in range(0, img_height, block_height):
        for x in range(0, img_width, block_width):
            for by in range(0, block_height):
                for bx in range(0, block_width, 2):
                    px = tim_pixel_data[offset]
                    # a = byte & 0x03
                    # b = ((byte & 0x30) >> 4)
                    # c = ((byte >> 2) & 0x3)
                    # d = (((byte >> 2) & 0x30) >> 4)
                    decoded_pixel_data[((y + by) * (img_width // 2)) + ((x + bx) // 2)] = px
                    offset += 1

    output_file.write(
        tim_tag + tim_bpp + tim_clut_size + tim_fb_pal_x + tim_fb_pal_y + tim_colors + tim_clut_num +
        clut + tim_img_size + tim_fb_img_x + tim_fb_img_y + tim_width + tim_height + bytearray(decoded_pixel_data)
    )

    #output_file.write(Image.frombytes("P", (img_width, img_height), bytes(decoded_img_data)))


font = open("font.dat", "rb").read()
output_file = open("font.tim", "wb")
do_extract_font(font)
output_file.close()
font = open("kaifont.dat", "rb").read()
output_file = open("kaifont.tim", "wb")
do_extract_font(font)
output_file.close()
print("DONE")