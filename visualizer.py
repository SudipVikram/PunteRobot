'''
Punte Robot - Visualizer
Developed by - Beyond Apogee, Nepal
Innovator - Sudip Vikram Adhikari
Tasks - visualization, mapping, sensing and data processing
'''

from sajilopygame import * # used for all tasks related to visualization
from sajilocv import *  # used for serial communication
import math

# instantiating classes
canvas = sajilopygame(wwidth=1350, wheight=750)
serialData = sajilocv()
odometry_data = serialData.ucontroller(serialData,port='COM7',baudrate=115200,timeout=1)

# window title
canvas.window_title("Odometry Visualizer")

# robot character
# actual width of the robot{l: 0.1m, b: 0.1m}
# since 1m = 150px, in visualizer l = 0.1*150 = 15px, b = 0.1*150 = 15px
robot_world_width = 15
robot_world_height = 15
robot = canvas.character(parent=canvas,type="shape",character_shape="rectangle",
                         color="red",org=(0,canvas.wheight),width=robot_world_width,height=robot_world_height,
                         border_thickness=0,border_radius=0)

#========= ODOMETRY SETUP ==========
# world coordinates
world_x = 0.0   # meters (right = positive)
world_y = 0.0   # meters (up/forward = positive)
heading = 90.0  # degrees (90 = facing up)

# calibrated value with practical data
# ticks per meter - 6552 (single channel)
# constants
TICKS_PER_METER = 6552 # for a single channel encoder
WHEEL_BASE = 0.118       # wheel to wheel distance = 118mm = 0.118m

# previous encoder values
prev_left = 0
prev_right = 0
#======================================

# distance travelled
distance_travelled = 0.0
straight_distance = 0.0

#=================
# PATH TRACKING
#=================
path_points = []    # list of (world_x, world_y) in meters
path_on_screen = []     # list of (screen_x, world_y) in pixels
MIN_DISTANCE_BETWEEN_POINTS = 0.03  # 3 cm
last_path_point_x = 0.0
last_path_point_y = 0.0
live_trail_flag = False

while True:
    # canvas background
    canvas.background_color("white")

    # grid
    canvas.grid()   # with default grid sizes
    
    # numbering the grid
    canvas.snake_pattern()

    # crosshair in the origin
    canvas.draw_text(text="+",font_size=20,color="blue",xpos=(canvas.wwidth//2)-3,ypos=(canvas.wheight//2)-17)

    #=========
    # ODOMETRY DATA
    #=========
    # placeholder for odometry data
    canvas.draw_rect(color="cyan",org=(1150,10),width=150,height=75,border_thickness=0,border_radius=10)

    data_from_serial = odometry_data.receive_serial_data()

    if data_from_serial is not None:
        try:
            line = data_from_serial.strip() # remove carriage return \n

            if line.startswith("L:") and (", R:" in line) and (", S:" in line):
                # split by comma first
                parts = line.split(", ")
                
                # splitting the data step by step
                l_encoder = parts[0].replace("L:","").strip()      # L:12
                r_encoder = parts[1].replace("R:","").strip()      # R:34
                s_encoder = parts[2].replace("S:","").strip()      # S:56

                # parse each value
                left_enc = int(l_encoder)
                right_enc = int(r_encoder)
                speed = int(s_encoder)

        except Exception:
            print("Bad data packet: ",data_from_serial)

    # title
    canvas.draw_text(text="Punte Robot Visualizer", font_size=20, color=(40,40,80),xpos=10,ypos=10)

    #========= ODOMETRY CALCULATIONS =========
    # wheel diameter = 34mm = 0.034m
    # wheel circumference = pi * diameter = 0.034 * 3.14159 = 0.1068m
    # wheel to wheel distance = 118mm = 0.118m
    # how many ticks since last update
    delta_left = left_enc - prev_left
    delta_right = right_enc - prev_right

    # convert ticks to distance
    # ticks per meter - 6552 (single channel)
    distance_left = delta_left / TICKS_PER_METER
    distance_right = delta_right / TICKS_PER_METER

    # distance the robot center moved forward
    distance = (distance_left + distance_right) / 2.0

    # saving the total distance travelled
    distance_travelled += abs(distance)

    # how much the robot turned(in radians)
    delta_theta = (distance_right - distance_left) / WHEEL_BASE

    # update heading(convert to degrees)
    heading += delta_theta * (180.0 / math.pi)

    # keeping the values between 0 - 360
    heading = heading % 360

    # updating the robot's world position
    world_x += distance * math.cos(math.radians(heading))
    world_y += distance * math.sin(math.radians(heading))

    # save current encoder values for the next loop
    prev_left = left_enc
    prev_right = right_enc

    #==========================================

    # updating the robot position based on odometry data
    # assuming the robot starts at the center of the canvas
    # ideal robot start position in the canvas
    #robot.update_position(xpos=canvas.wwidth//2 - robot_world_width//2,ypos=canvas.wheight//2 - robot_world_height//2)
    # actual robot position based on odometry data
    #========= DRAWING ROBOT AT CALCULATED POSITION =========
    scale = 150     # 150px = 1m (same as the grid in visualizer)
    screen_x = 675 + int(world_x * scale)
    screen_y = 375 - int(world_y * scale)

    # update robot character position
    #robot.update_position(xpos=screen_x-(robot_world_width//2), ypos=screen_y-(robot_world_height//2))

    # Draw rotated robot
    robot.draw_rotated_rect(cx=screen_x, cy=screen_y, width=robot_world_width, height=robot_world_height, angle_deg=-heading, color="red", border_thickness=0)

    # loading the robot
    robot.load()
    #========================================================

    #======================================
    # robot heading and trailing markers
    #======================================
    # robot's center on the screen
    cx = screen_x
    cy = screen_y

    # distance to the marker from robot center(offset)
    front_offset = 8

    # convert heading to radians
    angle = math.radians(-heading)

    # point in front of the robot
    front_x = cx + front_offset * math.cos(angle)
    front_y = cy + front_offset * math.sin(angle)

    # drawing a small circle as a marker
    canvas.draw_circle(color=(0,0,0), center=(front_x,front_y), radius=2)

    #====================
    # Heading and Distance Calculation
    #====================
    if 45 <= heading < 135:
        direction = "UP"
    elif 135 <= heading < 225:
        direction = "LEFT"
    elif 225 <= heading < 315:
        direction = "DOWN"
    else:
        # covers 315–360 and 0–45
        direction = "RIGHT"

    straight_distance = math.sqrt(world_x**2 + world_y**2)

    #================ PATH RECORDING ==================
    # record points only if the robot has moved enough
    if math.hypot(world_x-last_path_point_x, world_y-last_path_point_y) >= MIN_DISTANCE_BETWEEN_POINTS:
        path_points.append((world_x,world_y))
        last_path_point_x = world_x
        last_path_point_y = world_y

        # saving the screen points too
        path_on_screen.append((screen_x,screen_y))

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
    elif canvas.minus_key_pressed:  # slow motor speed by 5
        current_cmd = "-"
    elif canvas.plus_key_pressed:   # increase motor speed by 5
        current_cmd = "+"
    elif canvas.d_key_pressed:      # draws a line from origin to center of robot
        #canvas.draw_line(start=(canvas.wwidth//2,canvas.wheight//2),end=(screen_x,screen_y),color="black",width=1)
        # drawing a dotted line instead of a straight line
        canvas.draw_dotted_line(start=(canvas.wwidth//2,canvas.wheight//2), end=(screen_x,screen_y), color="gray", width=1)
    elif canvas.t_key_pressed or live_trail_flag:      # activate the green trail
        #====== GREEN TRAIL =======
        # the actual path taken by the robot
        if len(path_on_screen) > 1:
            for point in path_on_screen:
                canvas.draw_circle(center=point,radius=1,color=(0,255,100))
    elif canvas.l_key_pressed:
        if live_trail_flag:
            live_trail_flag = False
        else:
            live_trail_flag = True
    elif canvas.s_key_pressed:  # when space key is pressed save path
        '''import json
        with open("saved_trail.json","w") as f:
            json.dump(path_points, f)
        print(f"Saved {len(path_points)} path points to saved_trail.json")'''

    # encoder data
    canvas.draw_text(text="Encoder Data",font_size=16,color=(0,0,0),xpos=1155,ypos=15)
    canvas.draw_text(text=f"Left: {left_enc}",font_size=16,color=(84,84,84),xpos=1155,ypos=35)
    canvas.draw_text(text=f"Right: {right_enc}",font_size=16,color=(84,84,84),xpos=1155,ypos=55)

    # display current command on the canvas
    # placeholder for current command
    canvas.draw_rect(color="yellow",org=(1150,95),width=150,height=45,border_thickness=0,border_radius=10)    
    # current command
    canvas.draw_text(text=f"Cmd: {current_cmd}",font_size=16,color=(0,0,0),xpos=1155,ypos=105)

    # placeholder for motor speed and direction
    canvas.draw_rect(color="lightgreen",org=(1150,150),width=150,height=70,border_thickness=0,border_radius=10)
    canvas.draw_text(text="Speed & Direction",font_size=16,color=(0,0,0),xpos=1155,ypos=155)
    canvas.draw_text(text=f"Motor Speed: {speed}",font_size=16,color=(84,84,84),xpos=1155,ypos=175)
    canvas.draw_text(text=f"Dir: {direction}",font_size=16,color=(84,84,84),xpos=1155,ypos=195)

    #===========================
    # Heading and distance card
    #===========================
    canvas.draw_rect(color="orange",org=(1150,230),width=150,height=95,border_thickness=0,border_radius=10)
    canvas.draw_text(text="Distance & Heading",font_size=16,color=(0,0,0),xpos=1155,ypos=235)
    canvas.draw_text(text=f"Travelled: {distance_travelled:.2f}m",font_size=16,color=(84, 84, 84),xpos=1155,ypos=255)
    canvas.draw_text(text=f"From Start: {straight_distance:.2f}m",font_size=16,color=(84, 84, 84),xpos=1155,ypos=275)
    canvas.draw_text(text=f"Heading: {int(heading)}°",font_size=16,color=(84, 84, 84),xpos=1155,ypos=295)

    # placeholder for cheat sheet
    canvas.draw_rect(color="lightgray",org=(275,700),width=800,height=70,border_thickness=0,border_radius=10)
    canvas.draw_text(text="Commands:",font_size=16,color=(0,0,0),xpos=280,ypos=705)
    canvas.draw_text(text="Distance -> d",font_size=16,color=(84,84,84),xpos=370,ypos=705)

    # sending command to esp32(punte)
    odometry_data.send_serial_data_unobstructed((current_cmd + "\n").encode("ascii"))

    # fps
    canvas.set_fps(60)

    # refresh the window buffer
    canvas.refresh_window()