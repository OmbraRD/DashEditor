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
##### EXTRACTION:
1. Use [CDMage 1.02.1 B5](https://www.romhacking.net/utilities/1435/
 "Romhacking.net") to extract the contents of the ISO to a folder.
2. Put the software in the \CDDATA\ folder.
3. Either run the software with the -e option or use the batch file to extract everything at once.

##### INSERTION:
1. Move (or delete) the *.BIN files inside the \CDDATA\DAT\ folder.
2. Either run the software with the -i option or use the batch file to insert everything at once.
3. Use [CDMage 1.02.1 B5](https://www.romhacking.net/utilities/1435/
 "Romhacking.net") to replace the BIN files inside the \CDDATA\DAT\ folder.

## Information:
The software works by extracting the content of BIN files inside the CDDATA\DAT\ folder to a folder with the same name.
Once the BIN is extracted you will find the original files and some decoded files as follows:

* TIM: There are a few types. If you see a TIM terminated with _EXT.TIM you should be able to use an editor like
[Tim2view](https://github.com/lab313ru/tim2view/releases "Tim2view Github") to export the image to PNG for editing.
Once edited, the PNGs can be re-imported directly onto the _EXT.TIM files. (Pay attetion to the used palettes)
* MSG: These contain most of the game's text. These will be extracted to TXT format. You can edit these freely by
respecting the spacing, ending characters and special characters.

## Notes:
 
 - KAIFONT.DAT Width table: Inside ROCK_MAN.EXE at offset 0x7B67C to 0x7B700 (This needs testing)
 - ROCK_MAN.EXE text limit is 7044 bytes (for now)
