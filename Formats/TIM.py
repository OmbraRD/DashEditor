#!/usr/bin/env python3


def do_extract_tim(file_path):
    header = 2048  # 0x800

    print("\nExtracting {}".format(file_path))
    # Open TIM file
    tim_file = open(file_path, "rb").read()
    output_file = open(file_path.split(".")[0] + "_EXT.TIM", "wb")

    # 4bpp TIM file
    if tim_file[0:4] == b'\x01\x00\x00\x00' and tim_file[20:22] == b'\x10\x00':
        tim_tag = b'\x10\x00\x00\x00'
        tim_bpp = b'\x08\x00\x00\x00'
        tim_clut_size = (int.from_bytes(tim_file[24:26], byteorder="little") * 32 + 12).to_bytes(4, byteorder="little")
        print(tim_clut_size.hex())
        tim_fb_pal_x = tim_file[12:14]
        tim_fb_pal_y = tim_file[16:18]
        tim_colors = tim_file[20:22]
        tim_clut_num = tim_file[24:26]
        print(int.from_bytes(tim_clut_num, byteorder="little"))
        cluts = tim_file[256:256 + (int.from_bytes(tim_clut_size, byteorder="little") - 12)]
        print(len(cluts))
        tim_img_size = (int.from_bytes(tim_file[36:40], byteorder="little") *
                        int.from_bytes(tim_file[40:44], byteorder="little") * 2 + 12).to_bytes(4, byteorder="little")
        tim_fb_img_x = tim_file[28:30]
        tim_fb_img_y = tim_file[32:34]
        tim_width = tim_file[36:38]
        tim_height = tim_file[40:42]
        tim_pixel_data = tim_file[2048:len(tim_file)]

        pixel_data = [0] * len(tim_pixel_data)
        blockw = 128
        blockh = 32
        timh = int.from_bytes(tim_file[40:44], byteorder="little")
        timw = int.from_bytes(tim_file[36:40], byteorder="little") * 4
        rofs = 0

        for y in range(0, timh, blockh):
            for x in range(0, timw, blockw):
                for by in range(0, blockh):
                    for bx in range(0, blockw, 2):
                        px = tim_pixel_data[rofs]
                        pixel_data[((y + by) * blockw) + ((x + bx) // 2)] = px  # (px << 4 & 0xF0) + (px >> 4)
                        rofs += 1

        # Reversing nibble order should fix MML PC TIM files
        # tim_reversed_data = bytes(((x << 4 & 0xF0) + (x >> 4)) for x in tim_pixel_data)
        output_file.write(
            tim_tag + tim_bpp + tim_clut_size + tim_fb_pal_x + tim_fb_pal_y + tim_colors + tim_clut_num +
            cluts + tim_img_size + tim_fb_img_x + tim_fb_img_y + tim_width + tim_height + bytearray(pixel_data)
        )

    output_file.close()
