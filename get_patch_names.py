from MidiPlayer import *
import json
from time import sleep
print("Waiting for MIDI Player...")
prgHandle,bankHandle,chnHandle=getMidiPlayer()

def getAllPrograms(prgHan,bankHan,chnHan):
    #banks={"Melodic": {}, "Percussion": {}}
    melodic_banks={}
    percussion_banks={}
    setChannel(chnHan,1)
    sleep(0.03)
    # get names of all melodic instruments
    for x in range(128):
        setBank(bankHan,x)
        sleep(0.03)
        bankBuff=getPrgList(prgHan)
        if len(bankBuff) != 0:
            #banks["Melodic"][x]=bankBuff
            melodic_banks[x]=bankBuff
    setBank(bankHan,0)
    sleep(0.03)
    setChannel(chnHan,10)
    sleep(0.03)
    # get names of all percussion instruments
    for x in range(128):
        setBank(bankHan,x)
        sleep(0.03)
        bankBuff=getPrgList(prgHan)
        if len(bankBuff) != 0:
            #banks["Percussion"][x]=bankBuff
            percussion_banks[x]=bankBuff
    #return banks
    return melodic_banks, percussion_banks

print("Retrieving program list...")
allPrograms=getAllPrograms(prgHandle,bankHandle,chnHandle)

#with open("program_names.json", "w") as prgNames:
    #prgNames.write(json.dumps(allPrograms, indent=4))

with open("program_names_melodic.json", "w") as prgNames:
    prgNames.write(json.dumps(allPrograms[0], indent=4))

with open("program_names_pecussion.json", "w") as prgNames:
    prgNames.write(json.dumps(allPrograms[1], indent=4))
    
