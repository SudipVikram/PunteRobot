'''
Punte Robot - Visualizer
Developed by - Beyond Apogee, Nepal
Innovator - Sudip Vikram Adhikari
Tasks - visualization, mapping, sensing and data processing
'''

from sajilopygame import * # used for all tasks related to visualization
from sajilocv import *  # used for serial communication

# instantiating classes
canvas = sajilopygame(wwidth=1350, wheight=750)
serialData = sajilocv()
odometry_data = serialData.ucontroller(serialData,port='COM7',baudrate=115200,timeout=1)

# window title
canvas.window_title("Punte Robot - Visualizer")

while True:
    canvas.background_color("white")

    # fps
    canvas.set_fps(60)

    # refresh the window buffer
    canvas.refresh_window()