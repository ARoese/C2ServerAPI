"""Provides several functions for low-level input to the chivalry window. These functions provide varying levels
    of abstraction to how input is sent to the chivalry window. It is recommended to use sendLetterPress()"""

from time import sleep
import win32api, win32con

KEY_SLEEP_DURATION = 0.005

def sendKeyPress(code):
    """Send the events corresponding to a quick press and release of a given keycode. 
        See https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
        for more information on keycodes
    
    :param code: an int representing the keycode to press and release
    """
    sleep(KEY_SLEEP_DURATION)
    win32api.keybd_event(code, 0x0, 0x0001)
    sleep(KEY_SLEEP_DURATION)
    win32api.keybd_event(code, 0x0, 0x0002)
    sleep(KEY_SLEEP_DURATION)

def sendShiftedKeyPress(letter):
    """Send the events corresponding to a quick press and release of a given keycode with the shift key pressed. 
        See https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
        for more information on keycodes
    
    :param code: an int representing the keycode to press and release
    """
    sleep(KEY_SLEEP_DURATION)
    win32api.keybd_event(win32con.VK_LSHIFT, 0x0, 0x0001)
    win32api.keybd_event(win32con.VK_RSHIFT, 0x0, 0x0001)
    sendKeyPress(letter)
    win32api.keybd_event(win32con.VK_LSHIFT, 0x0, 0x0002)
    win32api.keybd_event(win32con.VK_RSHIFT, 0x0, 0x0002)
    sleep(KEY_SLEEP_DURATION)

def sendLetterPress(letter):
    """Send the keypresses required to type a specific letter or character. The shift
        key will be pressed as needed.

    NOTE: not all characters are implemented. Only alphanumeric and
        -_+=,.!?
        are implemented.

    :param letter: The letter that should be typed. (As if they user entered it on the keyboard)
    """
    sleep(KEY_SLEEP_DURATION)
    if letter.isalpha() or letter.isnumeric() or letter == ' ':
        if letter.isupper():
            sendShiftedKeyPress(ord(letter.upper()))
        else:
            sendKeyPress(ord(letter.upper()))
    elif letter == '-':
        sendKeyPress(0xBD) #VK_OEM_MINUS
    elif letter == '_':
        sendShiftedKeyPress(0xBD) #VK_OEM_MINUS
    elif letter == '+':
        sendShiftedKeyPress(0xBB) #VK_OEM_PLUS
    elif letter == '=':\
        sendKeyPress(0xBB) #VK_OEM_PLUS
    elif letter == ',':
        sendKeyPress(0xBC) #VK_OEM_COMMA
    elif letter == '.':
        sendKeyPress(0xBE) #VK_OEM_PERIOD
    elif letter == '!':
        sendShiftedKeyPress(ord('1'))
    elif letter == '?':
        sendShiftedKeyPress(0xBF) #VK_OEM_2 (/?)
    elif letter == '`':
        sendKeyPress(0xC0) #backtick
    else:
        print("Unable to send key '" + letter + "'")
        return
    sleep(KEY_SLEEP_DURATION)

def typeString(string):
    """Send keypresses required to type out the contents of the given string

    Newlines are allowed. The enter key will be pressed for each newline character, and will always be
        pressed at least once per function call (I.E. It will be pressed even if the string contains
        no newline characters)

    The contents of this string follow the same restrictions as those provided by the sendLetterPress() function.

    :param string: the string whose contents should be converted to keypresses (as if typed by the user on the keyboard)
    """
    for line in string.splitlines():
        for char in line:
            sendLetterPress(char)
        sendKeyPress(win32con.VK_RETURN)