import time
import socket
from threading import Thread

class picoLCD:
    th = None
    def __init__(self, host = "127.0.0.1", port = 10000):
        self.th = Thread(target=self.keyListener)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.packetTrailer = bytearray(b"")
        self.keyListening = False
        self.pressedKey = b"x00"

    def connect(self):
        self.sock.connect((self.host, self.port))
        
    def send(self, msg):
        msgFixed = msg+b"\x00"
        totalsent = 0
        while totalsent < len(msg)+1:
            sent = self.sock.send(msgFixed[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def sliceReturn(self, string):
        # first return: everything up until the first occurrence of CRLF
        # second return: everything after CRLF
        crlf=string.find(b"\r\n")
        if crlf == -1:
            crlf=string.find("\r\n")
            if crlf == -1:
                return string, None
        if len(string) > crlf+2:
            return string[:crlf+2], string[crlf+2:]
        else:
            return string, None

    def receive(self):
        chunks = []
        chunksStr=bytearray(b"")
        bytes_recd=0
        toSave = None
        # Returns anything that was previously in the buffer
        # Any complete messages are sent right away
        # Otherwise they are passed along to the chunk buffer
        if len(self.packetTrailer) != 0:
            savedMsg=self.packetTrailer
            self.packetTrailer=bytearray(b"")
            if b"\r\n" in savedMsg:
                toSend, toSave=self.sliceReturn(savedMsg)
                if toSave is not None:
                    self.packetTrailer.append(toSave)
                chunks.append(toSend)
                return b"".join(chunks)
            else:
                chunksStr.extend(savedMsg)
        while b"\r\n" not in chunksStr:
            chunk = self.sock.recv(min(4, 2048))
            chunksStr.extend(chunk)
            if chunk == b"":
                raise RuntimeError("socket connection broken receiving")
        if b"\r\n" in chunksStr:
            toSend, toSave=self.sliceReturn(chunksStr)
            #chunksStr.extend(toSend)
            if toSave is not None:
                self.packetTrailer.extend(toSave)
            return b""+toSend
        else:
            self.packetTrailer.extend(chunk)

    def keyListener(self):
        # x0a: up
        # x0b: down
        print("Now Listening")
        self.keyListening = True
        while self.keyListening:
            Rcv = self.receive()
            if Rcv is not None:
                if Rcv[:10] == b"notify key":
                    self.pressedKey=Rcv[11:14]
                    #print(self.pressedKey)
        
    def startListening(self):
        self.th.start()

    def setText(self, col, row, text, clearLine=False, raw=False):
        colBytes = str(col).encode("utf-8")
        rowBytes = str(row).encode("utf-8")
        if clearLine:
            trailer = b"\x20"*((20-col)+(len(text)*-1))
        else:
            trailer = b""
        if raw:
            self.send(b"set text "+colBytes+b" "+rowBytes+b" "+text+trailer+b"\x00")
        else:
            self.send(b"set text "+colBytes+b" "+rowBytes+b" "+text.encode("utf-8")+trailer+b"\x00")

    def clear(self):
        self.send(b"set clear")
