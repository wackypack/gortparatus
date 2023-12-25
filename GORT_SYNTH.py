import sys
import os
import time
import rtmidi
import configparser
import json
from threading import Thread
from minibox import picoLCD

os.system("cls" if os.name == "nt" else "clear")
print("Starting...")

gortConfig=configparser.ConfigParser()

gortConfig.read("gort.cfg")

inDev=gortConfig["MIDI"]["In"]
outDev=gortConfig["MIDI"]["Out"]

midiout = rtmidi.MidiOut()
midiin = rtmidi.MidiIn()

prgNamesMelo=json.load(open("program_names_melodic.json"))
prgNamesPerc=json.load(open("program_names_pecussion.json"))

def clearScreen():
    # clear the terminal window
    os.system("cls" if os.name == "nt" else "clear")

def padZeroes(n_str, leng):
    # add zeroes to the beginning of a string
    return "0"*((len(n_str)*-1)+leng)+n_str

def spit(two_line_output):
    # clear the terminal window and print two lines
    # input is formatted as a list, e.g. ["foo", "bar"]
    clearScreen()
    print(two_line_output[0]+"\n"+two_line_output[1])

class MidiChannel:
    def __init__(self, isMelodic=True, bank=0, bankSet=0, program=0, programName="---"):
        self.isMelodic = isMelodic
        self.bank = bank
        self.bankSet = bankSet
        self.program = program
        self.programName = programName

    def updatePrgName(self):
        try:
            if self.isMelodic:
                self.programName = prgNamesMelo[str(self.bankSet)][str(self.program)]
            else:
                self.programName = prgNamesPerc[str(self.bankSet)][str(self.program)]
        except KeyError:
            self.programName = "---"

class monOverview:
    th = None
    def __init__(self, chnList, lcd, cursorPos=0, currentChn=0, screen=0, monitoring=False):
        self.th = Thread(target=self.monitor)
        self.chnList = chnList
        self.lcd = lcd
        self.cursorPos = cursorPos
        self.cursorMon = cursorPos
        self.currentChn = currentChn
        self.monitoring = monitoring
        self.bankMon=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.prgMon=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.screen = screen
        
    def pack(cursorPos, prgName, bnk, prg, chn):
        # deprecated, was used for spitting into terminal but no longer used.
        if cursorPos==0:
            return prgName, "Prg >"+padZeroes(str(bnk),3)+":"+padZeroes(str(prg),3)+"  Ch  "+padZeroes(str(chn),2)
        if cursorPos==1:
            return prgName, "Prg  "+padZeroes(str(bnk),3)+":"+padZeroes(str(prg),3)+"< Ch  "+padZeroes(str(chn),2)
        if cursorPos==2:
            return prgName, "Prg  "+padZeroes(str(bnk),3)+":"+padZeroes(str(prg),3)+"  Ch >"+padZeroes(str(chn),2)

    def cgramify(self, in_str):
        # replace specific Unicode characters with picoLCD CGRAM references.
        # éóøú€¼½¾
        return in_str.replace("é", "\\0").replace("ó", "\\1").replace("ø", "\\2").replace("ú", "\\3").replace("€", "\\4").replace("¼","\\5").replace("½","\\6").replace("¾","\\7").replace("ˆ","^").replace("º","o")

    def update(self):
        # Don't use this, stopped using spit because it was resulting in hangs.
        # use updateAll instead
        spit(monOverview.pack(self.cursorPos,
                              self.chnList[self.currentChn].programName,
                              self.bankMon[self.currentChn],
                              self.prgMon[self.currentChn],
                              self.currentChn+1)
             )
        self.updateAll()
        
    def initDisplay(self):
        self.lcd.clear()
        self.lcd.setText(0, 1, "Prg     :     Ch")

    def updateBank(self):
        self.lcd.setText(5, 1, padZeroes(str(self.bankMon[self.currentChn]), 3))

    def updatePrg(self):
        self.lcd.setText(9, 1, padZeroes(str(self.prgMon[self.currentChn]), 3))

    def updatePrgName(self):
        self.lcd.setText(0, 0, self.cgramify(self.chnList[self.currentChn].programName), True)

    def updateAll(self):
        # these were going off of bankMon before, if it poses an issue I'll change it back
        bankStr = padZeroes(str(self.chnList[self.currentChn].bankSet), 3)
        prgStr = padZeroes(str(self.chnList[self.currentChn].program), 3)
        chnStr = padZeroes(str(self.currentChn+1), 2)
        self.updatePrgName()
        self.lcd.setText(0, 1, "Prg  "+bankStr+":"+prgStr+"  Ch  "+chnStr)
        self.updateCursor()

    def updateCursor(self):
        if self.screen == 0:
            cursors=[[4, ">"], [12, "<"], [17, ">"]]
            if self.cursorMon != self.cursorPos:
                self.lcd.setText(cursors[self.cursorMon][0], 1, " ")
            self.lcd.setText(cursors[self.cursorPos][0], 1, cursors[self.cursorPos][1])
            self.cursorMon = self.cursorPos

    def increment(self, mode, direction):
        currChn = self.currentChn
        c = self.chnList[currChn]
        if mode == "program":
            if direction == "up":
                program = c.program + 1 if c.program < 127 else 0
            if direction == "down":
                program = c.program - 1 if c.program > 0 else 127
            c.program = program
            c.updatePrgName()
            self.prgMon[currChn] = program
            midiout.send_message([192+currChn, program, 0])
        if mode == "bank":
            if direction == "up":
                bank = c.bankSet + 1 if c.bankSet < 127 else 0
            if direction == "down":
                bank = c.bankSet - 1 if c.bankSet > 0 else 127
            c.bank = bank
            c.bankSet = bank
            c.updatePrgName()
            self.bankMon[currChn] = bank
            midiout.send_message([176+currChn, 0, bank])
            midiout.send_message([192+currChn, c.program, 0])
        self.updateAll()

    def monitor(self):
        print("I Hath Awoken")
        self.monitoring=True
        keyMon=b""
        oldChn=self.currentChn
        self.initDisplay()
        self.lcd.startListening()
        while self.monitoring:
            # check each channel for bank or patch change
            for idx, chn in enumerate(self.chnList):
                if self.bankMon[idx] != chn.bankSet:
                    self.bankMon[idx] = chn.bankSet
                    if idx == self.currentChn:
                        self.updateAll()
                if self.prgMon[idx] != chn.program:
                    self.prgMon[idx] = chn.program
                    if idx == self.currentChn:
                        self.updateAll()
            # update screen when current channel has changed
            # disabled as this should not happen externally
            if self.currentChn != oldChn:
                print(oldChn)
                print(self.currentChn)
                oldChn = self.currentChn
                #self.update()
                if self.currentChn == 9:
                    self.updateAll()
            # update screen when cursor position has changed
            # deprecated as this should not happen externally

            # alright! now. everything to make the display respond to key input
            if self.lcd.pressedKey != keyMon:
                keyMon = self.lcd.pressedKey
                if self.screen == 0:
                    
                    # when direction UP is pressed
                    if keyMon == b"x0a":
                        # cursor is hovering over BANK no.
                        if self.cursorPos == 0:
                            self.increment("bank", "up")
                            i=0
                            while self.lcd.pressedKey == b"x0a":
                                i+=1
                                if i > 6 and i%2 == 0:
                                    self.increment("bank", "up")
                                time.sleep(0.05)

                        # cursor is hovering over PROGRAM no.
                        elif self.cursorPos == 1:
                            self.increment("program", "up")
                            i=0
                            while self.lcd.pressedKey == b"x0a":
                                i+=1
                                if i > 6 and i%2 == 0:
                                    self.increment("program", "up")
                                time.sleep(0.05)

                        # cursor is hovering over CHANNEL no.        
                        elif self.cursorPos == 2:
                            self.currentChn = self.currentChn + 1 if self.currentChn < 15 else 0
                            oldChn = self.currentChn
                            self.updateAll()
                            i=0
                            while self.lcd.pressedKey == b"x0a":
                                i+=1
                                if i > 6 and i%2 == 0:
                                    self.currentChn = self.currentChn + 1 if self.currentChn < 15 else 0
                                    oldChn = self.currentChn
                                    self.updateAll()
                                time.sleep(0.05)

                    # when direction DOWN is pressed
                    if keyMon == b"x0b":
                        if self.cursorPos == 0:
                            self.increment("bank", "down")
                            i=0
                            while self.lcd.pressedKey == b"x0b":
                                i+=1
                                if i > 6 and i%2 == 0:
                                    self.increment("bank", "down")
                                time.sleep(0.05)
                        
                        elif self.cursorPos == 1:
                            self.increment("program", "down")
                            i=0
                            while self.lcd.pressedKey == b"x0b":
                                i+=1
                                if i > 6 and i%2 == 0:
                                    self.increment("program", "down")
                                time.sleep(0.05)
                                
                        elif self.cursorPos == 2:
                            self.currentChn = self.currentChn - 1 if self.currentChn > 0 else 15
                            oldChn = self.currentChn
                            self.updateAll()
                            i=0
                            while self.lcd.pressedKey == b"x0b":
                                i+=1
                                if i > 6 and i%2 == 0:
                                    self.currentChn = self.currentChn - 1 if self.currentChn > 0 else 15
                                    oldChn = self.currentChn
                                    self.updateAll()
                                time.sleep(0.05)
                        
                    if keyMon == b"x08":
                        self.cursorPos = self.cursorPos - 1 if self.cursorPos > 0 else 2
                        self.updateCursor()
                    if keyMon == b"x09":
                        self.cursorPos = self.cursorPos + 1 if self.cursorPos < 2 else 0
                        self.updateCursor()
            time.sleep(0.05)

    def beginMon(self):
        self.th.start()

class MidiInHandler:
    def __init__(self, midiOut, chnList):
        self.midiOut = midiOut
        self.chnList = chnList

    def __call__(self, event, *args):
        event, delta = event
        self.midiOut.send_message(event)
        status = event[0] & 0xF0
        data1 = event[1]
        ch = self.chnList[event[0] & 0xF]

        # set bank buffer when coarse bank select event (CC0) is received
        if status == 176 and data1 == 0:
            ch.bank = event[2]

        # update program when program change event is received
        if status == 192:
            ch.program = data1
            ch.bankSet = ch.bank
            ch.updatePrgName()

try:
    midiin.open_port(int(inDev))
    midiout.open_port(int(outDev))
except RuntimeError:
    clearScreen()
    input("Could not open one\nor more MIDI ports.")
    sys.exit()

midiout.send_message([0x99, 53, 112])
time.sleep(0.125)
midiout.send_message([0x89, 53, 0])

# create midi channel objects that keep track of program and bank numbers
midiChannels = []
for c in range(16):
    if c != 9:
        midiChannels.append(MidiChannel(isMelodic=True))
    else:
        midiChannels.append(MidiChannel(isMelodic=False))
    midiChannels[c].updatePrgName()
    
# connect to picoLCD via socket connection (requires USBLCDServer.exe be running)
disp = picoLCD()
disp.connect()

# create objects for display/HID
Overview=monOverview(midiChannels, disp)

# setup custom characters
# U+00E9 ... e with acute
disp.send(b"set font 0 x02 x04 x0e x11 x1f x10 x0e x00")
# U+00F3 ... o with acute
disp.send(b"set font 1 x02 x04 x0e x11 x11 x11 x0e x00")
# U+00F8 ... o with stroke
disp.send(b"set font 2 x00 x00 x0f x13 x15 x19 x1e x00")
# U+00FA ... u with acute
disp.send(b"set font 3 x02 x04 x11 x11 x11 x13 x0d x00")
# U+20AC ... euro
disp.send(b"set font 4 x06 x09 x1c x08 x1c x09 x06 x00")
# U+00BC ... 1/4
disp.send(b"set font 5 x10 x11 x12 x04 x09 x12 x07 x01")
# U+00BD ... 1/2
disp.send(b"set font 6 x10 x11 x12 x04 x0a x11 x02 x07")
# U+00BE ... 3/4
disp.send(b"set font 7 x18 x0c x0d x1a x05 x0a x17 x01")


midiMonitoring=True
chanMonitoring=True

# set up midi handler
handler = MidiInHandler(midiout, midiChannels)
midiin.set_callback(handler)

# initialize thread that handles display and input
DispThd=Thread(target=Overview.beginMon)
DispThd.start()

screen=0

Overview.update()

Overview.currentChn=0
