#!/usr/bin/env python3

from Formats.BIN import bytes_to_uint, ulong_to_bytes


img_width = 256
img_height = 512
block_width = 128
block_height = 32


def do_insert_font(original_font, edited_font):
    print("Inserting {}".format(edited_font))
    # Open FONT file
    original_font = open(original_font, "rb+")
    edited_font = open(edited_font, "rb").read()

    pixel_data = edited_font[64:]

    ord_pixel_data = [0] * 32768

    offset = 0

    for y in range(0, img_height // 2, block_height):
        for x in range(0, img_width, block_width):
            for by in range(0, block_height):
                for bx in range(0, block_width, 2):
                    px_top = pixel_data[((y + by) * (img_width // 2)) + ((x + bx) // 2)]
                    px_top = px_top << 0
                    px_bottom = pixel_data[32768 + (((y + by) * (img_width // 2)) + ((x + bx) // 2))]
                    px_bottom = px_bottom << 2

                    ord_pixel_data[offset] = px_top + px_bottom
                    offset += 1

    original_font.seek(2048)
    original_font.write(bytearray(ord_pixel_data))
    original_font.close()


def do_extract_font(file_path):
    print("Extracting {}".format(file_path))
    # Open FONT file
    font_file = open(file_path, "rb").read()

    # Create Header of TIM
    tim_tag = b'\x10\x00\x00\x00'
    tim_bpp = b'\x08\x00\x00\x00'
    tim_clut_size = b'\x2c\x00\x00\x00'
    tim_fb_pal_x = b'\x00\x00'  # Not known but needed
    tim_fb_pal_y = b'\x00\x00'  # Not known but needed
    tim_colors = b'\x10\x00'
    tim_clut_num = b'\x01\x00'
    # Palette = #000, #FFF, #BBB, #888
    clut = b'\x00\x00\xFF\xFF\xF7\xDE\xEF\xBD\x00\x00\x00\x00\x00\x00\x00\x00' \
           b'\x00\x00\xFF\xFF\xF7\xDE\xEF\xBD\x00\x00\x00\x00\x00\x00\x00\x00'
    tim_img_size = ulong_to_bytes((img_width // 4) * img_height * 2 + 12)
    tim_fb_img_x = b'\x00\x00'  # Not known but needed
    tim_fb_img_y = b'\x00\x00'  # Not known but needed
    tim_width = b'\x40\x00'
    tim_height = b'\x00\x02'
    tim_pixel_data = font_file[2048:]

    decoded_pixel_data_top = [0] * ((bytes_to_uint(tim_img_size) - 12) // 2)
    decoded_pixel_data_bottom = [0] * ((bytes_to_uint(tim_img_size) - 12) // 2)
    offset = 0

    for y in range(0, img_height // 2, block_height):
        for x in range(0, img_width, block_width):
            for by in range(0, block_height):
                for bx in range(0, block_width, 2):
                    px = tim_pixel_data[offset]
                    a = px & 0x03
                    b = px & 0x30
                    c = (px >> 2) & 0x03
                    d = (px >> 2) & 0x30
                    decoded_pixel_data_top[((y + by) * (img_width // 2)) + ((x + bx) // 2)] = b + a
                    decoded_pixel_data_bottom[((y + by) * (img_width // 2)) + ((x + bx) // 2)] = d + c
                    offset += 1

    output_file = open(file_path.split(".")[0] + ".TIM", "wb")
    output_file.write(
        tim_tag + tim_bpp + tim_clut_size + tim_fb_pal_x + tim_fb_pal_y + tim_colors + tim_clut_num +
        clut + tim_img_size + tim_fb_img_x + tim_fb_img_y + tim_width + tim_height +
        bytearray(decoded_pixel_data_top) + bytearray(decoded_pixel_data_bottom)
    )
    output_file.close()

    print("\nFound font. Extraction complete.")
