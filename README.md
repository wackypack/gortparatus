# gortparatus
Sound Blaster Live in a box

## Prerequisites:
- Python 3.4
- MidiPlayer 6.1 (to access patch names from loaded Soundfonts)
- pywin32 >=2.2.1 (to automaticaly retrieve patch names from MidiPlayer)
- rtmidi >=1.1.0 (for MIDI handling)
- [USBLCDServer for picoLCD](http://resources.mini-box.com/online/picoLCD%2020x2%20(OEM)/Software/Windows/usblcd-applications.zip)

### Scripts
- GORT_SYNTH.py - main application that does everything important. Run at boot time or whenever you wish. Requires that USBLCDServer also be running.
- get_patch_names.py - dump all patch names into .json files. Requires that MidiPlayer also be running.
- get_ports.py - show all the midi ports available on the system (this is needed to set up gort.cfg)

### Libraries
- MidiPlayer.py - library for messing with window elements on Falcosoft's MIDI Player application, used as a workaround hack for retrieving SBLive patch names, includes some unused features for grabbing and setting program/bank/channel.
- minibox.py - picoLCD library. `from minibox import picoLCD`

### Other files
- gmp_profile.json - used for MidiPlayer.py in case you have your own version and need to get the handle child numbers yourself.
- gort.cfg - config file that specifies midi in/out devices.
- program_names_melodic.json - list of melodic program names dumped from MidiPlayer
- program_names_pecussion.json - list of percussion names dumped from MidiPlayer
