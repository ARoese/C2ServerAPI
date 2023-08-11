"""Provides a class encapsulating a chivalry 2 instance"""

from PIL import ImageGrab, Image, ImageDraw, ImageFont
import pytesseract
import win32gui, win32con, win32process, win32api
from time import sleep

from . import inputLib

class Chivalry:
    """Class representing a running instance of the Chivalry 2 game.

    This class provides numerous methods for interacting with the Chivalry 2 game programatically.
        Functionality is implemented using a combination of OCR and windows input emulation. Using
        this class may cause difficulties using the computer for anything other than chivalry, and may even
        make it difficult for the user to close it depending on how it's used. USE WITH CAUTION!
    """
    def __init__(self):
        if self.getChivalryWindowHandle() == 0:
            raise RuntimeError("The Chivalry 2 window could not be found. Ensure that chivalry 2 is running\
                               on this machine.")


    __windowHandle = -1
    def getChivalryWindowHandle(self):
        """Obtains and returns the win32 window handle of a chivalry 2 process running on this computer.
        
        This function will only make the associated syscalls once. After that, the cached window handle from the
            first call will be returned instead, regardless of it's validity.
        """
        if self.__windowHandle != -1:
            return self.__windowHandle
        else:
            hwnd = win32gui.FindWindow(None, "Chivalry 2  ") #note the spaces after the 2 here. They're important.
            self.__windowHandle = hwnd
            sleep(0.1) #window handle doesn't seem to be valid until after a warmup period
            return hwnd

    def getFocus(self, hwnd):
        """Give the chivalry 2 window user focus. This visually brings the window in front of all other windows and
            directs user input to it. This is a precondition to many interactions with the chivalry 2 process, especially
            ocr-related operations. Most functions that internally require this will call it themselves unless stated
            otherwise.
        """
        remote_thread, _ = win32process.GetWindowThreadProcessId(hwnd)
        win32process.AttachThreadInput(win32api.GetCurrentThreadId(), remote_thread, True)
        prev_handle = win32gui.SetFocus(hwnd)

    def checkInGameConsoleOpen(self):
        """Returns true or false, indicating if the in-game console is currently open in extended mode.

        TODO: NOTE: this function currenly does not work.
        """
        screenshot = self.getChivScreenshot() #get a screenshot of the chiv game
        width, height = screenshot.size
        screenshot = screenshot.crop((0, height*(47/64)+2, width*0.02, height*(49/64)-2))
        #process to isolate console text, and convert back to RGB
        #TODO: also try to make mode="L" work
        screenshot = screenshot.quantize(colors=256).convert(mode="1").convert(mode="RGB")
        screenshot.show() #DEBUG
        print(pytesseract.image_to_string(screenshot))
        
    def getChivScreenshot(self, tabDown=False):
        """Returns a PIL image of the entire chivalry 2 window, as it appears on-screen to a human user.
        """
        hwnd = self.getChivalryWindowHandle()
        self.getFocus(hwnd)
        #win32gui.SetForegroundWindow(hwnd)
        sleep(0.1)
        if tabDown:
            inputLib.tabDown()
            sleep(0.1)
        
        windowRect = win32gui.GetWindowRect(hwnd)
        #clientRect = win32gui.GetClientRect(hwnd)
        #print(windowRect)
        #print(clientRect)
        image = ImageGrab.grab(windowRect)
        if tabDown:
            inputLib.tabUp()
            sleep(0.1)

        return image

    #precondition: the extended view of the console is open in chivalry
    def getConsoleOutput(self):
        """Returns the currently displayed output of the chivalry console window as a string using OCR.

        PRECONDITIONS:
            The chivalry console must be opened and visible in extended mode in the chivalry 2 process. See
                the checkInGameConsoleOpen(), openConsole() and closeConsole() functions.
        """
        screenshot = self.getChivScreenshot() #get a screenshot of the chiv game
        #get screenshot dimensions
        width, height = screenshot.size
        #crop to console only. 
        #height*(47/64)-2 is a magic number measured empirically.
        #It gets everything up to the horizontal line separating the command line input
        screenshot = screenshot.crop((0, 0, width, height*(47/64)-2))
        #process to isolate console text, and convert back to RGB
        #TODO: also try to make mode="L" work
        screenshot = screenshot.quantize(colors=256).convert(mode="1").convert(mode="RGB")
        #screenshot.show() #DEBUG
        #TODO: improve recognition with custom training
        #https://ironsoftware.com/csharp/ocr/how-to/ocr-custom-font-training/
        text = pytesseract.image_to_string(screenshot)
        #strip empty lines and return them
        return [s for s in text.splitlines() if s]

    def getTimeRemaining(self):
        """Return the time remaining in the game as a string, as displayed in the in-game timer.

        This function internally uses OCR, and does not do cleanup on the string returned. It is the
            responsibility of the caller to ensure that this string is valid, clean, and interpretable
            before using it.

        TODO: add cleanup here?

        NOTE: The in-game console should not be open in extended mode when this function is called.
            It may still work, however, it will be less reliable.
        """
        #get screenshot
        screenshot = self.getChivScreenshot()
        width, height = screenshot.size
        #crop to location of timer on screen
        screenshot = screenshot.crop((0.45*width, 0.08*height, 0.55*width, 0.13*height))
        
        #process and isolate text

        screenshot = screenshot.quantize(colors=128).convert(mode="RGB")
        return pytesseract.image_to_string(screenshot)
    
    def getPlayerCount(self):
        return 0
        #this will eventually return an actual number from the game...
        #the OCR for this is surprisingly difficult
        screenshot = self.getChivScreenshot(tabDown=True)
        width, height = screenshot.size
        
        #crop to location of timer on screen
        screenshot = screenshot.crop((0.47*width, height*0.18, 0.53*width, height*0.22))

        #process and isolate text
        
        screenshot = screenshot.quantize(colors=128).convert(mode="RGB")

        

        screenshot.show()
        return pytesseract.image_to_string(screenshot)


    def isGameEnd(self):
        """Returns true or false, indicating whether or not the game is currently in a game-end state.

        PRECONDITION: The game client is in spectator mode

        NOTE: The UI elements used to detect this are the "GAME END" and "VICTOR" in-game overlays.
            These assume that the client is in spectator mode at game end to get these specific messages.
        """
        screenshot = self.getChivScreenshot()
        width, height = screenshot.size
        #crop to location of game end notification on screen
        screenshot = screenshot.crop((0.3*width, 0.75*height, 0.7*width, 0.9*height))

        screenshot = screenshot.quantize(colors=128).convert(mode="1").convert(mode="RGB")
        #screenshot.show()
        result = pytesseract.image_to_string(screenshot)
        if "GAME END" in result or "VICTOR" in result:
            return True
        else:
            return False
        
    def isMainMenu(self):
        """Returns true or false, indicating if the client is currently at the chivalry main menu.
        """
        screenshot = self.getChivScreenshot()
        width, height = screenshot.size
        #crop to location of exit game button on main menu on screen
        screenshot = screenshot.crop((0.072*width, 0.94*height, 0.13*width, 0.97*height))

        screenshot = screenshot.quantize(colors=128).convert(mode="RGB")
        #screenshot.show()
        result = pytesseract.image_to_string(screenshot)
        #print(result)
        if "EXIT GAME" in result:
            return True
        else:
            return False

    def getRecentCommandOutput(self, command, lines):
        """Returns the output of a command that was recently run.

        PRECONDITION: the extended view of the console is open in chivalry

        @param command: A string containing the command that was run, exactly as it was entered
        @param lines: How many lines of it's output to return. (this depends on the specific command)
        @returns The output of the run command as a string, or None
        """
        console = self.getConsoleOutput()
        #get a view of the console containing only command run lines and no spaces what-so-ever
        #command run lines take the form `>>> command <<<` in the output. We strip spaces because
        #we can't rely on them being detected by OCR. We also cant rely on ALL of the >>> / <<< characters to
        #be correctly OCR'd. Here, we rely on at least two consecutive of both
        #StrippedConsole elements include their index in the actual console output array
        strippedConsole = [
            (index, s.replace(" ", "")) 
            for index,s in enumerate(console) 
            if ">>" in s and "<<" in s
        ]
        index = -1 #sentinel -1 value
        for i, s in reversed(strippedConsole): #searching backwards through all commands run
            if command.replace(" ", "") in s: #if this line is the running of the requested command
                if i < len(console)-1: #if this is not the last line of the console output
                    n = lines+1
                    #return some number of lines, n, output after the command run, or the rest of the
                    #output of the console if there are less than n lines left
                    #this is more general than it needs to be, but this is intended to
                    return console[i+1:i+n] if i+n < len(console) else console[i+1:]
                else:
                    return None
        return None

    def consoleSend(self, message):
        """Write a message to the chivalry command console 
        
        @param message: A string, the command to enter into the chivalry console. This may contain
            multiple lines, one command on each line. They will be entered one after another with no delay.
        """
        hwnd = self.getChivalryWindowHandle()
        self.getFocus(hwnd)
        inputLib.typeString(message)

    def openConsole(self):
        """Open the chivalry console into extended mode

        PRECONDITION: The chivalry console is currently closed
        """
        hwnd = self.getChivalryWindowHandle()
        self.getFocus(hwnd)
        #WARNING: THIS KEYCODE MAY DEPEND ON KEYBOARD LAYOUT
        #note: scan table:
        #https://learn.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-6.0/aa299374(v=vs.60)?redirectedfrom=MSDN
        #seems safe to leave scan code as 0
        inputLib.sendLetterPress('`') #backtick
        sleep(0.1)
        inputLib.sendLetterPress('`') #backtick

    def closeConsole(self):
        """Close the chivalry console from extended mode

        PRECONDITION: The chivalry console is currently open in extended mode
        """
        hwnd = self.getChivalryWindowHandle()
        self.getFocus(hwnd)
        inputLib.sendLetterPress('`') #backtick

    # def walk(self):
    #     """Cause the chivalry client to walk forward in-game for several seconds.

    #     NOTE: this function shouldn't really be called, and is mostly here for testing inputs.
    #         It MAY be useful for tinkering with OCR by moving to a more oportune position.
        
    #     """
    #     hwnd = self.getChivalryWindowHandle()
    #     self.getFocus(hwnd)
    #     win32api.keybd_event(0x57, 0x0, 0)
    #     sleep(4)
    #     win32api.keybd_event(0x57, 0x0, 0x0002)


#Chiv win32gui window class: "UnrealWindow"