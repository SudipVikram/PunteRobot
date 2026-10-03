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
# actual width of the robot{l: 0.105m (10.5 cm), b: 0.11m (11 cm)}
# since 1m = 150px, in visualizer l = 0.105*150 = 15.75px, b = 0.11*150 = 16.5px
robot_world_width = 15.75
robot_world_height = 16.5
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
WHEEL_BASE = 0.11  # 11 cms  # wheel to wheel distance = 110mm = 0.11m

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
path_points = []        # list of (world_x, world_y) in meters
path_on_screen = []     # list of (screen_x, world_y) in pixels
MIN_DISTANCE_BETWEEN_POINTS = 0.03  # 3 cm
last_path_point_x = 0.0
last_path_point_y = 0.0
live_trail_flag = False

#=====================
# WAYPOINT FOLLOWING
#=====================
saved_path = []             # holds path points of loaded path from file
is_following = False        # flag that tells that the robot is in following mode
current_target_index = 0    # next point in the path the robot is heading towards


#===============
# WALL
#===============
walls = []          # list of ((x1,y1),(x2,y2))  # holds collection of coordinates for a wall
is_wall = False     # flag to check if the wall object has been constructed        

#=====================================
# MISSION PLANNING FOR PATH A TO B
#=====================================
mission_file = "mission.json"  # file to save the mission plan
start_point = None             # (x,y) in meters
goal_point = None              # (x,y) in meters
planned_path = []              # list of (x,y) in meters for the computed path
mission = []                   # list of ((x1,y1),(x2,y2))  # holds collection of coordinates for a mission path
is_mission = False             # the mission flag

while True:
    # canvas background
    canvas.background_color("white")

    # grid
    canvas.grid()   # with default grid sizes
    
    # numbering the grid
    canvas.snake_pattern()

    # crosshair in the origin
    canvas.draw_text(text="+",font_size=20,color="blue",xpos=(canvas.wwidth//2)-3,ypos=(canvas.wheight//2)-17)

    #=================
    # ODOMETRY DATA
    #=================
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

    #===============
    # KEY STROKES
    #===============
    current_cmd = "S"   # stopping is the default command unless another key is pressed

    if canvas.left_pressed:
        current_cmd = "L"
    if canvas.right_pressed:
        current_cmd = "R"
    if canvas.up_pressed:
        current_cmd = "F"
    if canvas.down_pressed:
        current_cmd = "B"
    if canvas.minus_key_pressed:  # slow motor speed by 5
        current_cmd = "-"
    if canvas.plus_key_pressed:   # increase motor speed by 5
        current_cmd = "+"
    if canvas.d_key_pressed:      # draws a line from origin to center of robot
        #canvas.draw_line(start=(canvas.wwidth//2,canvas.wheight//2),end=(screen_x,screen_y),color="black",width=1)
        # drawing a dotted line instead of a straight line
        canvas.draw_dotted_line(start=(canvas.wwidth//2,canvas.wheight//2), end=(screen_x,screen_y), color="gray", width=1)
        current_cmd = "d"
    if canvas.t_key_pressed or live_trail_flag:      # activate the green trail
        #====== GREEN TRAIL =======
        # the actual path taken by the robot
        if len(path_on_screen) > 1:
            for point in path_on_screen:
                canvas.draw_circle(center=point,radius=2,color=(0,255,100))
    if canvas.l_key_pressed:
        if live_trail_flag:
            live_trail_flag = False
            current_cmd = "t"
        else:
            live_trail_flag = True
            current_cmd = "l"
    if canvas.mouse_clicked: # on mouse click we will save the point as path point
        world_x_clicked = (canvas.mouse_x - 675) / scale
        world_y_clicked = (375-canvas.mouse_y) / scale

        path_on_screen.append((canvas.mouse_x,canvas.mouse_y))
        path_points.append((world_x_clicked,world_y_clicked))

    if canvas.s_key_pressed:  # when s key is pressed save path
        current_cmd = "s"
        import json
        with open("saved_trail.json","w") as f:
            json.dump(path_points, f)
        print(f"Saved {len(path_points)} path points to saved_trail.json")

    #======== wall =======
    # when w key is pressed, we save the wall points
    if canvas.w_key_pressed and len(path_points) >= 2:
        current_cmd = "w"
        for i in range(len(path_points) - 1):
            p1 = list(path_points[i])
            p2 = list(path_points[i+1])
            walls.append([p1,p2])

        import json
        with open("walls.json","w") as w:
            json.dump(walls, w, indent=2)

        print(f"{len(walls)} Wall coordinates saved to walls.json")

    # when o key is pressed, the walls are constructed as objects
    if canvas.o_key_pressed:
        current_cmd = "o"
        is_wall = not is_wall   # toggle

        try:
            import json
            with open("walls.json", "r") as f:
                walls = json.load(f)
                print(f"Loaded {len(walls)} wall coordinates from walls.json")
        except:
            print("Couldn't load walls.json")

        canvas.o_key_pressed = False  # reset the flag

    if is_wall:
        for (x1,y1), (x2,y2) in walls:
            sx1 = 675 + int(x1 * scale)
            sy1 = 375 - int(y1 * scale)
            sx2 = 675 + int(x2 * scale)
            sy2 = 375 - int(y2 * scale)
            canvas.draw_line(start=(sx1,sy1), end=(sx2,sy2), color=(0,0,0), width=2)

    #====================================
    # MISSION PLANNING FROM PATH A TO B
    #====================================
    # we must know that everytime a left click happens, the coordinates automatically get saved as a start point
    if canvas.mouse_clicked: # on mouse click we will save the point as start point
        wx = (canvas.mouse_x - 675) / scale
        wy = (375-canvas.mouse_y) / scale
        start_point = (wx,wy)
        print(f"Start point set at: {start_point}")
        canvas.mouse_clicked = False  # reset the flag

    if canvas.right_mouse_clicked: # on right mouse click we will save the point as goal point
        wx = (canvas.mouse_x - 675) / scale
        wy = (375-canvas.mouse_y) / scale
        goal_point = (wx,wy)
        print(f"Goal point set at: {goal_point}")
        canvas.right_mouse_clicked = False  # reset the flag

    if canvas.m_key_pressed and start_point and goal_point:  # when m key is pressed, the mission path is saved
        current_cmd = "m"
        is_mission = not is_mission   # toggle

        import json
        data = {
            "start": list(start_point),
            "goal": list(goal_point),
            "path": []
        }
        with open(mission_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Mission data saved to {mission_file}")
        canvas.m_key_pressed = False  # reset the flag

    # upon pressing "p", we load the mission data 
    # and plan the path
    if canvas.p_key_pressed:
        current_cmd = "p"
        try:
            import json
            with open("mission.json", "r") as f:
                mission_data = json.load(f)
                start_point = tuple(mission_data["start"])
                goal_point = tuple(mission_data["goal"])
                planned_path = mission_data["path"]
                is_mission = True
                print(f"Loaded mission data from mission.json")
        except:
            print("Couldn't load mission.json")

        canvas.p_key_pressed = False  # reset the flag

    if is_mission:
        # drawing the start point
        sx = 675 + int(start_point[0] * scale)
        sy = 375 - int(start_point[1] * scale)
        canvas.draw_circle(color=(0, 200, 0), center=(sx, sy), radius=6)    # green
        # drawing the goal point
        gx = 675 + int(goal_point[0] * scale)
        gy = 375 - int(goal_point[1] * scale)
        canvas.draw_circle(color=(200, 0, 0), center=(gx, gy), radius=6)    # red


    #==========================
    # waypoint line following
    if canvas.b_key_pressed:
        try:
            import json
            with open("saved_trail.json", "r") as f:
                saved_path = json.load(f)
                print(f"Loaded {len(saved_path)} path points from saved_trail.json")

            is_following = True
            current_target_index = 0
        except:
            print("Couldn't load saved_trail.json")

    # drawing the path in blue
    if saved_path:
        for i in range(1, len(saved_path)):
            # getting the real world points into screen coordinates
            x1 = 675 + int(saved_path[i-1][0] * scale)
            y1 = 375 - int(saved_path[i-1][1] * scale)
            canvas.draw_circle(color=(0,0,255),center=(x1,y1),radius=2)

    #===== Line Following/Path Following logic ======
    if is_following and saved_path:
        target_x, target_y = saved_path[current_target_index]

        # vector from robot to target
        dx = target_x - world_x
        dy = target_y - world_y

        # distance to target
        distance_to_target = math.hypot(dx,dy)

        # desired heading to face the target
        desired_heading = math.degrees(math.atan2(dy,dx))

        # heading error
        error = (desired_heading - heading + 180) % 360 - 180   # shortest angle

        # deciding the command based on heading error
        TURN_THRESHOLD = 10     # degrees - can tune this value for accuracy

        if abs(error) < TURN_THRESHOLD:
            current_cmd = "F"   # go forward if it is facing roughly the right way
        elif error > 0:
            current_cmd = "L"   # need to turn left
        else:
            current_cmd = "R"   # need to turn right

        # check if the robot reached the current target
        if distance_to_target < 0.03:       # within 3cm(Can be tuned)
            current_target_index += 1
            if current_target_index >= len(saved_path):
                is_following = False        # we assume the target has been reached
                current_cmd = "s"           # last hop is a stop
                print("Path Following Completed!")
            else:
                current_cmd = "s"


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
    canvas.draw_text(text="Travel trail -> t", font_size=16,color=(84,84,84),xpos=480,ypos=705)
    canvas.draw_text(text="Live trail -> l", font_size=16,color=(84,84,84),xpos=610,ypos=705)
    canvas.draw_text(text="Save path -> s", font_size=16,color=(84,84,84),xpos=720,ypos=705)

    # sending command to esp32(punte)
    odometry_data.send_serial_data_unobstructed((current_cmd + "\n").encode("ascii"))

    # fps
    canvas.set_fps(60)

    # refresh the window buffer
    canvas.refresh_window()