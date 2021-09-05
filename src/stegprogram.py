from PIL import Image
import sys
import pdb

def steg_write(string, filename, picture):
    # Load bitmap
    bitmap = picture.load()

    # Get size
    width, height = picture.size

    if (len(string) * 8) > (width * height * 3):
        print('Message too large')
        return

    # Tracks how much of the string has been written
    string_iter = 0
    # Tracks how much of a character has been written
    char_iter = 0
    length = len(string)

    for xcoor in range(0, width):
        for ycoor in range(0, height):
            
            # List determines how much the pixels need to be altered
            alter_by = [0,0,0]

            for byte in range(0, 3):
                if string_iter < length:
                    # Find the next bit that needs to be written
                    bit_val = (string[string_iter] >> char_iter) & 1
                    
                    # If the bit isn't already a match, add 1
                    if (bitmap[xcoor, ycoor][byte] & 1) != bit_val:
                        alter_by[byte] = 1

                    # Increment iterators
                    char_iter = (char_iter + 1) % 8
                    if char_iter == 0:
                        string_iter += 1

            # Assign new pixel value
            bitmap[xcoor, ycoor] = (bitmap[xcoor, ycoor][0] + alter_by[0], bitmap[xcoor, ycoor][1] + alter_by[1], bitmap[xcoor, ycoor][2] + alter_by[2])
            
    picture.save(filename)
    print('Message successfully written')


def steg_read_string(picture):
    # Load bitmap
    bitmap = picture.load()

    # Get size
    width, height = picture.size

    # Buffer that stores sixe previously read characters
    # used to identify _HSTEG and _ESTEG
    format_buf = '      '
    # Buffer for storing message if found
    string_buf = ''
    # Tells program whether message is being read
    reading_str = False
    # Iterates through each char
    char_iter = 0
    # Stores the char byte currently being constructed
    curr_char = 0

    for xcoor in range(0, width):
        for ycoor in range(0, height):
            
            for byte in range(0, 3):
                # Find last bit value
                bit = bitmap[xcoor, ycoor][byte] & 1

                # Add it to the appropriate position in current char
                curr_char = curr_char | (bit << char_iter)

                # Executes when a char has been fuly constructed
                if char_iter == 7:
                    
                    if reading_str == True:
                        # Adding to the message string
                        string_buf += chr(curr_char)
                    
                    # Adding to the format string and removing an item at front
                    format_buf += chr(curr_char)
                    format_buf = format_buf[1:]

                    curr_char = 0

                    # Beginning of message found
                    if format_buf == '_HSTEG':
                        reading_str = True

                    # End of message found
                    if format_buf == '_ESTEG':
                        print(f'Message found!: {string_buf[:-6]}')
                        reading_str = False

                # Iterate char
                char_iter = (char_iter + 1) % 8


def steg_read_file(picture, filepath):
    # Load bitmap
    bitmap = picture.load()

    # Get size
    width, height = picture.size

    # Buffer that stores sixe previously read characters
    # used to identify _HSTEG and _ESTEG
    format_buf = '      '
    # Setting up file to write to
    byte_array = []
    # Tells program whether file is being read
    reading_str = False
    # Iterates through each char
    char_iter = 0
    # Stores the char byte currently being constructed
    curr_char = 0

    for xcoor in range(0, width):
        for ycoor in range(0, height):
            
            for byte in range(0, 3):
                # Find last bit value
                bit = bitmap[xcoor, ycoor][byte] & 1

                # Add it to the appropriate position in current char
                curr_char = curr_char | (bit << char_iter)

                # Executes when a char has been fuly constructed
                if char_iter == 7:
                    
                    if reading_str == True:
                        # Writing to the file
                        byte_array.append(curr_char)
                    
                    # Adding to the format string and removing an item at front
                    format_buf += chr(curr_char)
                    format_buf = format_buf[1:]

                    curr_char = 0

                    # Beginning of message found
                    if format_buf == '_HSTEG':
                        reading_str = True

                    # End of message found
                    if format_buf == '_ESTEG':
                        print(f'File found! Written to {filepath}')
                        byte_array = byte_array[:-6]
                        wfile = open(filepath, 'wb')
                        for byte in byte_array:
                            wfile.write(bytes([byte]))

                        wfile.close()
                        reading_str = False

                # Iterate char
                char_iter = (char_iter + 1) % 8



# Open picture
picture = Image.open(sys.argv[2]).convert('RGB')

# python3 stegprogram.py wt [srcimagepath] [dstimagepath] [message]
if sys.argv[1] == 'wt':
    byte_string = '_HSTEG'.encode('utf-8') + ' '.join(sys.argv[4:]).encode('utf-8') + '_ESTEG'.encode('utf-8')
    # Generate byte string for writing

    steg_write(byte_string, sys.argv[3], picture)

# python3 stegprogram.py rt [srcimagepath]
elif sys.argv[1] == 'rt':
    steg_read_string(picture)
# python3 stegprogram.py wf [srcimagepath] [dstimagepath] [filepath]
elif sys.argv[1] == 'wf':
    wfile = open(sys.argv[4], 'rb')
    byte_string = wfile.read()
    wfile.close()
    byte_string = '_HSTEG'.encode('utf-8') + byte_string + '_ESTEG'.encode('utf-8')
    steg_write(byte_string, sys.argv[3], picture)
# python3 stegprogram.py rf [srcimagepath] [destfilepath]
elif sys.argv[1] == 'rf':
    steg_read_file(picture, sys.argv[3])
else:
    print('Must use flag')
