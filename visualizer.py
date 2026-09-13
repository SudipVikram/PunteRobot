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
    # canvas background
    canvas.background_color("white")

    #========
    # GRID
    #========
    # columns
    for i in range(0, canvas.wwidth, 150):
        canvas.draw_line(start=(i,0),end=(i,canvas.wheight),color="lightgray",width=1)

    # rows
    for j in range(0, canvas.wheight, 150):
        canvas.draw_line(start=(0,j),end=(canvas.wwidth,j),color="lightgray",width=1)

    #=========
    # ODOMETRY DATA
    #=========
    # placeholder for odometry data
    canvas.draw_rect(color="cyan",org=(1150,10),width=150,height=75,border_thickness=0,border_radius=10)

    data_from_serial = odometry_data.receive_serial_data()

    if data_from_serial is not None:
        try:
            line = data_from_serial.strip() # remove carriage return \n

            if line.startswith("L:") and ", R:" in line:
                # splitting the data step by step
                l_encoder = line.split(", R:")[0].strip()      # L:12
                r_encoder = line.split(", R:")[1].strip()      # R:34

                # parse each value
                left = int(l_encoder.replace("L:",""))
                right = int(r_encoder)

        except Exception:
            print("Bad data packet: ",data_from_serial)

    # encoder data
    canvas.draw_text(text="Encoder Data",font_size=16,color=(0,0,0),xpos=1155,ypos=15)
    canvas.draw_text(text=f"Left: {left}",font_size=16,color=(84,84,84),xpos=1155,ypos=35)
    canvas.draw_text(text=f"Right: {right}",font_size=16,color=(84,84,84),xpos=1155,ypos=55)

    #==========
    # KEY STROKES
    #==========
    current_cmd = "S"   # stopping is the default command unless another key is pressed

    if canvas.left_pressed:
        current_cmd = "L"
    elif canvas.right_pressed:
        current_cmd = "R"
    elif canvas.up_pressed:
        current_cmd = "F"
    elif canvas.down_pressed:
        current_cmd = "B"

    odometry_data.send_serial_data_unobstructed((current_cmd + "\n").encode("ascii"))

    # fps
    canvas.set_fps(60)

    # refresh the window buffer
    canvas.refresh_window()