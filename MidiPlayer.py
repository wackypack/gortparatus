import sys
import win32gui as wgui
import win32process as wproc
import win32api as wapi
import win32con as wcon
import win32clipboard as wclip
from time import sleep
from threading import Thread
import json
import ctypes

# init. global vars

VK_CODE = {'backspace':0x08,
           'tab':0x09,
           'clear':0x0C,
           'enter':0x0D,
           'shift':0x10,
           'ctrl':0x11,
           'alt':0x12,
           'pause':0x13,
           'caps_lock':0x14,
           'esc':0x1B,
           'spacebar':0x20,
           'page_up':0x21,
           'page_down':0x22,
           'end':0x23,
           'home':0x24,
           'left_arrow':0x25,
           'up_arrow':0x26,
           'right_arrow':0x27,
           'down_arrow':0x28,
           'select':0x29,
           'print':0x2A,
           'execute':0x2B,
           'print_screen':0x2C,
           'ins':0x2D,
           'del':0x2E,
           'help':0x2F,
           '0':0x30,
           '1':0x31,
           '2':0x32,
           '3':0x33,
           '4':0x34,
           '5':0x35,
           '6':0x36,
           '7':0x37,
           '8':0x38,
           '9':0x39,
           'a':0x41,
           'b':0x42,
           'c':0x43,
           'd':0x44,
           'e':0x45,
           'f':0x46,
           'g':0x47,
           'h':0x48,
           'i':0x49,
           'j':0x4A,
           'k':0x4B,
           'l':0x4C,
           'm':0x4D,
           'n':0x4E,
           'o':0x4F,
           'p':0x50,
           'q':0x51,
           'r':0x52,
           's':0x53,
           't':0x54,
           'u':0x55,
           'v':0x56,
           'w':0x57,
           'x':0x58,
           'y':0x59,
           'z':0x5A,
           'numpad_0':0x60,
           'numpad_1':0x61,
           'numpad_2':0x62,
           'numpad_3':0x63,
           'numpad_4':0x64,
           'numpad_5':0x65,
           'numpad_6':0x66,
           'numpad_7':0x67,
           'numpad_8':0x68,
           'numpad_9':0x69,
           'multiply_key':0x6A,
           'add_key':0x6B,
           'separator_key':0x6C,
           'subtract_key':0x6D,
           'decimal_key':0x6E,
           'divide_key':0x6F,
           'F1':0x70,
           'F2':0x71,
           'F3':0x72,
           'F4':0x73,
           'F5':0x74,
           'F6':0x75,
           'F7':0x76,
           'F8':0x77,
           'F9':0x78,
           'F10':0x79,
           'F11':0x7A,
           'F12':0x7B,
           'F13':0x7C,
           'F14':0x7D,
           'F15':0x7E,
           'F16':0x7F,
           'F17':0x80,
           'F18':0x81,
           'F19':0x82,
           'F20':0x83,
           'F21':0x84,
           'F22':0x85,
           'F23':0x86,
           'F24':0x87,
           'num_lock':0x90,
           'scroll_lock':0x91,
           'left_shift':0xA0,
           'right_shift ':0xA1,
           'left_control':0xA2,
           'right_control':0xA3,
           'left_menu':0xA4,
           'right_menu':0xA5,
           'browser_back':0xA6,
           'browser_forward':0xA7,
           'browser_refresh':0xA8,
           'browser_stop':0xA9,
           'browser_search':0xAA,
           'browser_favorites':0xAB,
           'browser_start_and_home':0xAC,
           'volume_mute':0xAD,
           'volume_Down':0xAE,
           'volume_up':0xAF,
           'next_track':0xB0,
           'previous_track':0xB1,
           'stop_media':0xB2,
           'play/pause_media':0xB3,
           'start_mail':0xB4,
           'select_media':0xB5,
           'start_application_1':0xB6,
           'start_application_2':0xB7,
           'attn_key':0xF6,
           'crsel_key':0xF7,
           'exsel_key':0xF8,
           'play_key':0xFA,
           'zoom_key':0xFB,
           'clear_key':0xFE,
           '+':0xBB,
           ',':0xBC,
           '-':0xBD,
           '.':0xBE,
           '/':0xBF,
           '`':0xC0,
           ';':0xBA,
           '[':0xDB,
           '\\':0xDC,
           ']':0xDD,
           "'":0xDE,
           '`':0xC0}

mpChildren=[]

# setup for clipboard

CF_TEXT=1

kernel32 = ctypes.windll.kernel32
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
user32 = ctypes.windll.user32
user32.GetClipboardData.restype = ctypes.c_void_p

### WINDOWS Specific Functions

# get the text that is on the clipboard
def getClipboardText():
    user32.OpenClipboard(0)
    try:
        if user32.IsClipboardFormatAvailable(CF_TEXT):
            data = user32.GetClipboardData(CF_TEXT)
            data_locked = kernel32.GlobalLock(data)
            text = ctypes.c_char_p(data_locked)
            value = text.value
            kernel32.GlobalUnlock(data_locked)
            return value
    finally:
        user32.CloseClipboard()

# get all children handles of main window
def getMpChildren(hwnd, param):
    mpChildren.append(hwnd)

# keyboard events
def keyDown(key):
    wapi.keybd_event(VK_CODE[key], 0,0,0)
def keyUp(key):
    wapi.keybd_event(VK_CODE[key], 0,wcon.KEYEVENTF_KEYUP,0)
def keyStrike(key):
    wapi.keybd_event(VK_CODE[key], 0,0,0)
    wapi.keybd_event(VK_CODE[key], 0,wcon.KEYEVENTF_KEYUP,0)

# focus on a child handle (deprecated) 
def focusOnChild(child):
    prev_handle = wgui.SetFocus(mpChildren[child])

# focus on specific handle
def focusOnHandle(handle):
    prev_handle = wgui.SetFocus(handle)

### MIDI PLAYER Specific Functions

# set the currently monitored channel
def setChannel(handle,chn):
    focusOnChild(0)
    focusOnHandle(handle)
    if chn >= 1 and chn <= 9:
        keyStrike(str(chn))
    if chn >= 10 and chn <= 16:
        keyStrike("1")
        keyStrike(str(chn-10))

# get the value of the currently monitored channel
def getChannel(handle):
    print("Get Channel:")
    focusOnChild(0)
    focusOnHandle(handle)
    wgui.SendMessage(handle,wcon.WM_COPY,0,0)
    #wclip.OpenClipboard()
    #buff=wclip.GetClipboardData()
    #wclip.CloseClipboard()
    buff=getClipboardText()
    print(buff)
    return buff

# set the program from a patch number
def setPrg(handle,ind):
    focusOnHandle(handle)
    if ind >= 0 and ind <= 63:
        keyStrike("home")
        for i in range(ind):
            keyStrike("down_arrow")
    if ind >= 64 and ind <= 127:
        keyStrike("end")
        for i in range(ind*-1+127):
            keyStrike("up_arrow")

# get the string defining the currently set program
def getPrg(handle):
    print("Get Program:")
    prgIndex=wgui.SendMessage(handle,wcon.CB_GETCURSEL)
    prgLen=wgui.SendMessage(handle,wcon.CB_GETLBTEXTLEN,prgIndex)
    buff=bytearray(b"\0"*(prgLen*2))
    wgui.SendMessage(handle,wcon.CB_GETLBTEXT,prgIndex,buff)
    return buff.decode("utf-16le")

# get the entire list of programs for the specified bank
def getPrgList(handle):
    prgs={}
    for i in range(128):
        prgLen=wgui.SendMessage(handle,wcon.CB_GETLBTEXTLEN,i)
        buff=bytearray(b"\0"*(prgLen*2))
        wgui.SendMessage(handle,wcon.CB_GETLBTEXT,i,buff)
        prgString=buff.decode("utf-16le")
        #if len(prgString) != 7 and prgString[4:7] != "---":
            #prgs[int(prgString[0:3])] = prgString[4:]
        #else:
            #print(prgString[4:7])
        if len(prgString) == 7:
            if prgString[4:7] != "---":
                prgs[int(prgString[0:3])] = prgString[4:]
        else:
            prgs[int(prgString[0:3])] = prgString[4:]
    return prgs


# set the bank (MSB) number
def setBank(handle,ind):
    focusOnChild(0)
    focusOnHandle(handle)
    if ind >= 0 and ind <= 9:
        keyStrike(str(ind))
    if ind >= 10 and ind <= 99:
        keyStrike(str(ind//10))
        keyStrike(str(ind%10))
    if ind >= 100 and ind <= 127:
        keyStrike("1")
        keyStrike(str((ind-100)//10))
        keyStrike(str((ind-100)%10))

# get the currently set bank
def getBank(handle):
    print("Get Bank:")
    #wgui.SendMessage(handle,wcon.EM_GETLINE
    focusOnChild(0)
    focusOnHandle(handle)
    wgui.SendMessage(handle,wcon.WM_COPY,0,0)
    #wclip.OpenClipboard()
    #buff=wclip.GetClipboardData()
    #wclip.CloseClipboard()
    buff=getClipboardText()
    print(buff)
    return buff
    
# increase the program number by 1
def prgUp(handle):
    focusOnHandle(handle)
    keyStrike("down_arrow")

# decrease the program number by 1
def prgDown(handle):
    focusOnHandle(handle)
    keyStrike("up_arrow")

### MONITORING specific functions

def getMidiPlayer():
    global mpChildren
    while wgui.FindWindow("TMidiPlayerfmMain", None) == 0:
        sleep(0.1)
    mp = wgui.FindWindow("TMidiPlayerfmMain", None)
    print("Window `{0:s}` handle: 0x{1:016X}".format("TMidiPlayerMain",mp))
    if not mp:
        print("Midi Player is not running...")
        return
    remote_thread, _ = wproc.GetWindowThreadProcessId(mp)
    wproc.AttachThreadInput(wapi.GetCurrentThreadId(), remote_thread, True)
    wgui.EnumChildWindows(mp,getMpChildren,None)
    while len(mpChildren) != 41:
        mpChildren=[]
        wgui.EnumChildWindows(mp,getMpChildren,None)
        sleep(0.1)
    prf=json.load(open("gmp_profile.json"))
    prfName=prf["active_profile"]
    for i in prf["profiles"]:
        if i["prf_name"] == prfName:
            print(i["prg_winchild"])
            prgHandle=mpChildren[i["prg_winchild"]]
            bankHandle=mpChildren[i["bank_winchild"]]
            chnHandle=mpChildren[i["chn_winchild"]]
            break
    print(prgHandle)
    print(bankHandle)
    print(chnHandle)
    prev_handle = wgui.SetFocus(mp)
    return(prgHandle,bankHandle,chnHandle)

    
