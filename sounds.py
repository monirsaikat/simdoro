import sys
import os

def play_sound():
    if sys.platform == 'win32':
        import winsound
        winsound.Beep(2500, 1000)
    else:
        # os.system('afplay /System/Library/Sounds/Glass.aiff')  # for macOS
        os.system('mpg321 sound.mp3')
        # os.system('aplay /usr/share/sounds/alsa/Front_Center.wav')
        # os.system('aplay /usr/share/sounds/alsa/Front_Center.wav')  # for Linux