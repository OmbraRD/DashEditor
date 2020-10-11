# DashEditor
**MegaMan Legends Translation Toolkit v0.9.8**  
**Created by \_Ombra_ of SadNES cITy Translations**  
**Website: http://www.sadnescity.it**  

A toolkit to disassemble and reassemble Mega Man Legends PSX files for translation purposes.
Implemented so far:

* Disassembly and Reassembly of BIN files
* Extraction/Insertion of FONT.DAT and KAIFONT.DAT to TIM
* Extraction/Insertion of MSG files to TXT
* Extraction/Insertion of text inside EXE file
* Extraction/Insertion of MML TIM to regular TIM (4bpp and 8bpp)

TODO:

* Reallocation of text in EXE file (expansion)
* Cleanup the code and optimize it (a lot)
* Error checking, especially on MSG files

## Usage:
```
DashEditor.py [option] [file or folder]
  -e   extracts che content of BIN file.
  -i   inserts an extracted folder to BIN file.
```

The software works by extracting the content of BIN files to a folder with the same name. Once the BIN is extracted you
will find the original files and some decoded files as follows:

* TIM: There are a few types. If you see a TIM terminated with _EXT.TIM you should be able to use an editor like
[Tim2view](https://github.com/lab313ru/tim2view/releases "Tim2view Github") to export the image to PNG for editing.
Once edited, the PNGs can be re-imported directly onto the _EXT.TIM files.
* MSG: These contain most of the game's text. These will be extracted to TXT format. You can edit these freely by
respecting the spacing, ending characters and special characters.

Once the files are modified you just need to move the original BIN away from the folder (since we don't want to
overwrite the original files... just in case) and run the insert command by specifying the folder name. This will
convert the TXT files to MSG, the TIM files to the proper format, reinsert and create a new BIN file.

Once the BIN is created you can use a tool like [CDMage 1.02.1 B5](https://www.romhacking.net/utilities/1435/
 "Romhacking.net") to reinsert the modified BIN file into the ISO of the game.
 
## Notes:
 
 - KAIFONT Width table: Inside ROCK_MAN.EXE at offset 0x7B67C to 0x7B700 (This needs testing)
