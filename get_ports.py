import rtmidi

inPorts = rtmidi.MidiIn().get_ports()
outPorts = rtmidi.MidiOut().get_ports()

print("Available MIDI In ports:\n")
for x in range(len(inPorts)):
    print(inPorts[x])
print(" \n\nAvailable MIDI Out ports:\n")
for x in range(len(outPorts)):
    print(outPorts[x])

input("\n\nPress Enter to exit")
