"""
This is a library by Beyond Apogee, Nepal tailored
for the school-level students that we educate in our
robotics program.
@ developer: Beyond Apogee
@ author: Sudip Vikram Adhikari
@ version: 1.0
@ license: MIT
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import json
import sys
import math
import os
import serial
#import pyautogui


class sajilocv:
    def __init__(self, config_path="config.json"):
        self.mp = mp  # Store MediaPipe module
        self.time = time  # Store Time module
        self.load_config(config_path)  # Load user settings
        # default settings if the config file isn't found
        self.camera_index = 0
        self.max_num_hands = 1
        self.static_image_mode = False
        self.model_complexity = 1
        self.min_detection_confidence = 0.7
        self.min_tracking_confidence = 0.7
        self.frame_rate = 30
        self.wcam = 640
        self.hcam = 480

    def load_config(self, config_path):
        """Loads settings from a JSON file."""
        try:
            with open(config_path, 'r') as file:
                config = json.load(file)
                self.camera_index = config.get("camera_index", 0)
                self.max_num_hands = config.get("max_num_hands", 1)
                self.static_image_mode = config.get("static_image_mode", False)
                self.model_complexity = config.get("model_complexity", 1)
                self.min_detection_confidence = config.get("min_detection_confidence", 0.7)
                self.min_tracking_confidence = config.get("min_tracking_confidence", 0.7)
                self.frame_rate = config.get("frame_rate", 30)
                self.wCam = config.get("wCam", 640)
                self.hCam = config.get("hCam", 480)
        except FileNotFoundError:
            print("Config file not found. Using default settings.")

    def get_name(self):
        return "SajiloCV"

    def get_version(self):
        return "1.0"

    def get_author(self):
        return "Sudip Vikram Adhikari"

    def get_license(self):
        return "MIT"

    def get_description(self):
        return "A library for computer vision tasks written by Sudip Vikram Adhikari @ Beyond Apogee"

    def get_github_link(self):
        return "https://github.com/SudipVikram/SajiloCV"

    def get_documentation_link(self):
        return "https://github.com/SudipVikram/SajiloCV/blob/main/README.md"

    # Creating a class for hand tracking
    class hand_tracking:
        def __init__(self, outer_instance):
            self.outer = outer_instance  # Reference to the outer class
            self.cap = cv2.VideoCapture(self.outer.camera_index)  # Use user-defined camera
            self.cap.set(cv2.CAP_PROP_FPS, self.outer.frame_rate)  # Set frame rate

            self.imgRGB = None  # Initialize image storage
            self.results = None
            self.img = None
            self.finger_tips = [4,8,12,16,20]

            self.pTime = 0 # previous time(initialized to 0)

            if not self.cap.isOpened():
                print(f"Failed to open camera {self.outer.camera_index}, retrying...")

            # MediaPipe Hands setup
            self.mpHands = self.outer.mp.solutions.hands
            self.hands = self.mpHands.Hands(
                static_image_mode=self.outer.static_image_mode,
                model_complexity=self.outer.model_complexity,
                max_num_hands=self.outer.max_num_hands,
                min_detection_confidence=self.outer.min_detection_confidence,
                min_tracking_confidence=self.outer.min_tracking_confidence
            )
            self.mpDraw = self.outer.mp.solutions.drawing_utils

        # destructor
        def __del__(self, outer_instance):
            if self.cap.isOpened():
                self.cap.release()
                cv2.destroyAllWindows()

        ''' The following methods are for dynamic settings. Updating
        the values on runtime '''
        # updating the maximum number of hands to track
        def update_max_hands(self, new_max_hands):
            """Updates the maximum number of hands to track dynamically."""
            # Validate max_num_hands: it must be an integer between 1 and 2
            if not isinstance(new_max_hands, int) or not (1 <= new_max_hands <= 2):
                print("Error: 'max_num_hands' must be an integer in the range [1, 2].")
                sys.exit()
            # Update max_num_hands and retain all other previously set values
            self.hands = self.mpHands.Hands(
                static_image_mode=self.outer.static_image_mode,
                model_complexity=self.outer.model_complexity,
                max_num_hands=new_max_hands,
                min_detection_confidence=self.outer.min_detection_confidence,
                min_tracking_confidence=self.outer.min_tracking_confidence
            )
            self.outer.max_num_hands = new_max_hands
            print(f"Updated max num of hands to {new_max_hands}")

        # updating the minimum detection confidence
        def update_min_detection_confidence(self, min_detection_confidence):
            """Updates the minimum detection confidence dynamically."""
            # Validate min_detection_confidence: it must be a float between 0.0 and 1.0
            if not isinstance(min_detection_confidence, float) or not (0.0 <= min_detection_confidence <= 1.0):
                print("Error: 'min_detection_confidence' must be a float in the range [0.0, 1.0].")
                sys.exit()
            # Update min_detection_confidence and retain all other previously set values
            self.hands = self.mpHands.Hands(
                static_image_mode=self.outer.static_image_mode,
                model_complexity=self.outer.model_complexity,
                max_num_hands=self.outer.max_num_hands,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=self.outer.min_tracking_confidence
            )
            self.outer.min_detection_confidence = min_detection_confidence
            print(f"Updated min detection confidence to {min_detection_confidence}")

        # updating the minimum tracking confidence
        def update_min_tracking_confidence(self, min_tracking_confidence):
            """Updates the minimum tracking confidence dynamically."""
            # Validate min_tracking_confidence: it must be a float between 0.0 and 1.0
            if not isinstance(min_tracking_confidence, float) or not (0.0 <= min_tracking_confidence <= 1.0):
                print("Error: 'min_tracking_confidence' must be a float in the range [0.0, 1.0].")
                sys.exit()
            # Update min_tracking_confidence and retain all other previously set values
            self.hands = self.mpHands.Hands(
                static_image_mode=self.outer.static_image_mode,
                model_complexity=self.outer.model_complexity,
                max_num_hands=self.outer.max_num_hands,
                min_detection_confidence=self.outer.min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence
            )
            self.outer.min_tracking_confidence = min_tracking_confidence
            print(f"Updated min tracking confidence to {min_tracking_confidence}")

        # updating the frame rate
        def update_frame_rate(self, frame_rate):
            """Updates the frame rate dynamically."""
            # Validate frame_rate: it must be a positive integer within the range [1, 240]
            if not isinstance(frame_rate, int) or not (1 <= frame_rate <= 240):
                print("Error: 'frame_rate' must be an integer in the range [1, 240].")
                sys.exit()  # Terminate the program if the input is invalid
            self.cap.set(cv2.CAP_PROP_FPS, frame_rate)
            self.outer.frame_rate = frame_rate
            print(f"Updated frame rate to {frame_rate}")

        # updating the static image mode(boolean)
        def update_static_image_mode(self, static_image_mode):
            """Updates the static image mode dynamically."""
            # Validate input for static_image_mode
            if not isinstance(static_image_mode, bool):
                print("Error: 'static_image_mode' must be a boolean value (True or False).")
                sys.exit()  # Terminate the program if the input is invalid
            # Update static_image_mode and retain all other previously set values
            self.hands = self.mpHands.Hands(
                static_image_mode=static_image_mode,
                model_complexity=self.outer.model_complexity,
                max_num_hands=self.outer.max_num_hands,
                min_detection_confidence=self.outer.min_detection_confidence,
                min_tracking_confidence=self.outer.min_tracking_confidence
            )
            self.outer.static_image_mode = static_image_mode
            print(f"Updated static image mode to {static_image_mode}")

        # updating the model complexity
        def update_model_complexity(self, model_complexity):
            """Updates the model complexity dynamically."""
            # Validate input for model_complexity
            if not isinstance(model_complexity, int) or model_complexity not in [0, 1, 2]:
                print("Error: 'model_complexity' must be an integer (0, 1, or 2).")
                sys.exit()  # Terminate the program if the input is invalid
            # Update model_complexity and retain all other previously set values
            self.hands = self.mpHands.Hands(
                static_image_mode=self.outer.static_image_mode,
                model_complexity=model_complexity,
                max_num_hands=self.outer.max_num_hands,
                min_detection_confidence=self.outer.min_detection_confidence,
                min_tracking_confidence=self.outer.min_tracking_confidence
            )
            self.outer.model_complexity = model_complexity
            print(f"Updated model complexity to {model_complexity}")

        # camera number if there are more than one camera
        def update_camera_index(self, camera_index):
            """Updates the camera index dynamically."""
            # Validate camera_index: it must be a non-negative integer
            if not isinstance(camera_index, int) or camera_index < 0:
                print("Error: 'camera_index' must be a non-negative integer.")
                sys.exit()
            self.camera_index = camera_index
            print(f"Updated camera index to {camera_index}")

        # updating the video output width and height
        def update_video_output(self, wcam, hcam):
            # Validation: Ensure width and height are integers
            if not isinstance(wcam, int) or not isinstance(hcam, int):
                raise ValueError("Width (wcam) and height (hcam) must be integers.")

            # Validation: Ensure width and height are positive
            if wcam < 640 or hcam < 480:
                raise ValueError("Width (wcam) and height (hcam) must be positive values.")

            # Optional Validation: Set a maximum reasonable value for resolution
            if wcam > 1920 or hcam > 1080:
                raise ValueError("Width (wcam) and height (hcam) must be less than or equal to 8000.")

            self.outer.wcam = wcam
            self.outer.hcam = hcam

            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,self.outer.wcam)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,self.outer.hcam)
            print(f"Updated video output to {wcam}x{hcam}")
        ''' updating dynamic settings ends here '''

        # initializing hands and reading from the captured image
        def track_hands(self):
            success, self.img = self.cap.read()
            if not success or self.img is None:
                print("Failed to capture frame, retrying...")
                return

            self.imgRGB = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            self.results = self.hands.process(self.imgRGB)  # Process frame

        # printing just the landmark coordinates on the terminal
        def print_landmarks(self):
            if self.results and self.results.multi_hand_landmarks:
                for handLms in self.results.multi_hand_landmarks:
                    for id, lm in enumerate(handLms.landmark):
                        print(f"Landmark for {id}: {lm.x}, {lm.y}, {lm.z}")

        # printing the landmark pixels on the terminal
        def print_landmarks_in_pixels(self):
            if self.results and self.results.multi_hand_landmarks:
                for handLms in self.results.multi_hand_landmarks:
                    for id, lm in enumerate(handLms.landmark):
                        h, w, c = self.img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        print(f"Landmark Pixels for {id}: {cx}, {cy}")

        # showing hand landmark as points
        def show_hand_landmarks(self):
            if self.results and self.results.multi_hand_landmarks:
                for landmarks in self.results.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(self.img, landmarks)

        # showing hand connections as lines connecting the points
        def show_hand_connections(self):
            if self.results and self.results.multi_hand_landmarks:
                for landmarks in self.results.multi_hand_landmarks:
                    self.mpDraw.draw_landmarks(self.img, landmarks, self.mpHands.HAND_CONNECTIONS)

        ''' really important functions starts here'''
        # displaying the video on screen
        def display_video(self):
            if self.img is None:
                print("Image is not ready yet, retrying...")
                return
            cv2.imshow("Image", self.img)

            # Allow both ESC and 'q' as quit options
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):  # 27 is the ASCII code for ESC, ord('q') is for 'q'
                self.release_camera()
                sys.exit()  # Ensures the entire program exits

        # destructor that can be called upon
        def release_camera(self):
            if self.cap.isOpened():
                self.cap.release()
                cv2.destroyAllWindows()
        ''' important functions ends here '''

        ''' functions for drawing on the image starts here '''
        # circle a landmark with radius and color
        def circle_landmark(self, landmark_id=None, radius=15, color=(255, 0, 255)):
            """
            Circles a hand landmark on the image.

            Parameters:
                landmark_id (int | None): ID of the landmark to circle (0-21). If None, all landmarks are circled.
                radius (int): Radius of the circle. Must be greater than 0.
                color (tuple): Color of the circle in BGR format, must be a tuple of three integers (0-255).
            """
            # Validate landmark_id
            if landmark_id is not None:  # If specified, ensure it's valid
                if not isinstance(landmark_id, int) or landmark_id < 0 or landmark_id > 21:
                    print("Error: 'landmark_id' must be an integer in the range [0, 21], or None.")
                    return

            # Validate radius
            if not isinstance(radius, int) or radius <= 0:
                print("Error: 'radius' must be a positive integer.")
                return

            # Validate color
            if not (isinstance(color, tuple) and len(color) == 3 and
                    all(isinstance(c, int) and 0 <= c <= 255 for c in color)):
                print("Error: 'color' must be a tuple of three integers in the range [0, 255].")
                return

            # Check if results are available
            if self.results and self.results.multi_hand_landmarks:
                for handLms in self.results.multi_hand_landmarks:
                    for id, lm in enumerate(handLms.landmark):
                        # If landmark_id is None, draw for all landmarks
                        if landmark_id is None or id == landmark_id:
                            h, w, c = self.img.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            cv2.circle(self.img, (cx, cy), radius, color, cv2.FILLED)

        # line across two landmarks
        def line_across_landmarks(self, hand_no=0, landmark_ids=(4,8), color=(255, 0, 255), thickness=2,rcircle=5,center=False):
            # validating hand_no
            if hand_no < 0 or hand_no > 1:
                return "Error: 'hand_no' must be an integer in the range [0, 1]."

            # Validate landmark_ids
            lmOne, lmTwo = landmark_ids

            # Check if both lmOne and lmTwo are within the valid range [0, 21]
            if (not isinstance(lmOne, int) or not isinstance(lmTwo, int)) or not (
                    0 <= lmOne <= 21 and 0 <= lmTwo <= 21):
                print("Error: 'landmark_ids' must be integers in the range [0, 21].")
                return

            # Validate radius
            if not isinstance(rcircle, int) or rcircle <= 0:
                print("Error: 'radius' must be a positive integer.")
                return

            # Validate color
            if not (isinstance(color, tuple) and len(color) == 3 and
                    all(isinstance(c, int) and 0 <= c <= 255 for c in color)):
                print("Error: 'color' must be a tuple of three integers in the range [0, 255].")
                return

            # Validate thickness (ensure it is a positive integer)
            if not isinstance(thickness, int):
                raise ValueError(f"'thickness' must be an integer, got {type(thickness).__name__} instead.")
            elif thickness < 1 or thickness > 10:
                raise ValueError(
                    f"'thickness' must be between {1} and {10}, got {thickness} instead."
                )

            lmList = self.find_hand_position(hand_no,draw=False)
            if lmList is not None:
                if len(lmList) >= lmOne and len(lmList) >= lmTwo:
                    #print(lmList[lmOne], lmList[lmTwo])

                    x1,y1 = lmList[lmOne][1], lmList[lmOne][2]
                    x2,y2 = lmList[lmTwo][1], lmList[lmTwo][2]
                    cx, cy = (x1+x2)//2, (y1+y2)//2     # finding out the center of the line

                    # drawing circles on the landmarks
                    cv2.circle(self.img, (x1,y1), rcircle, color, cv2.FILLED)
                    cv2.circle(self.img, (x2,y2), rcircle, color, cv2.FILLED)

                    # drawing a line across the landmarks
                    cv2.line(self.img, (x1,y1), (x2,y2), color, thickness)

                    if center:
                        # drawing a circle on the center of the line
                        cv2.circle(self.img, (cx,cy), rcircle, color, cv2.FILLED)

        # finding the length between two landmarks
        def length_across_landmarks(self, hand_no=0, landmark_ids=(4,8)):
            # validating hand_no
            if hand_no < 0 or hand_no > 1:
                return "Error: 'hand_no' must be an integer in the range [0, 1]."

            lmList = self.find_hand_position(hand_no,draw=False)
            # Validate landmark_ids
            lmOne, lmTwo = landmark_ids

            # Check if both lmOne and lmTwo are within the valid range [0, 21]
            if (not isinstance(lmOne, int) or not isinstance(lmTwo, int)) or not (
                    0 <= lmOne <= 21 and 0 <= lmTwo <= 21):
                print("Error: 'landmark_ids' must be integers in the range [0, 21].")
                return
            if lmList is not None:
                if len(lmList) >= lmOne and len(lmList) >= lmTwo:
                    x1, y1 = lmList[lmOne][1], lmList[lmOne][2]
                    x2, y2 = lmList[lmTwo][1], lmList[lmTwo][2]

                    length = math.hypot(x2 - x1, y2 - y1)
                    return length

        # center across two landmarks
        def center_across_landmarks(self, hand_no=0, landmark_ids=(4,8), rcircle=5,color=(255, 0, 255)):
            # validating hand_no
            if hand_no < 0 or hand_no > 1:
                return "Error: 'hand_no' must be an integer in the range [0, 1]."

            # Validate radius
            if not isinstance(rcircle, int) or rcircle <= 0:
                print("Error: 'radius' must be a positive integer.")
                return

            # Validate color
            if not (isinstance(color, tuple) and len(color) == 3 and
                    all(isinstance(c, int) and 0 <= c <= 255 for c in color)):
                print("Error: 'color' must be a tuple of three integers in the range [0, 255].")
                return

            lmList = self.find_hand_position(hand_no,draw=False)
            # Validate landmark_ids
            lmOne, lmTwo = landmark_ids

            # Check if both lmOne and lmTwo are within the valid range [0, 21]
            if (not isinstance(lmOne, int) or not isinstance(lmTwo, int)) or not (
                    0 <= lmOne <= 21 and 0 <= lmTwo <= 21):
                print("Error: 'landmark_ids' must be integers in the range [0, 21].")
                return
            if lmList is not None:
                if len(lmList) >= lmOne and len(lmList) >= lmTwo:
                    x1, y1 = lmList[lmOne][1], lmList[lmOne][2]
                    x2, y2 = lmList[lmTwo][1], lmList[lmTwo][2]
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # finding out the center of the line

                    # drawing a circle on the center of the line
                    cv2.circle(self.img, (cx, cy), rcircle, color, cv2.FILLED)


        # displaying the frame rate on the screen
        def display_frame_rate(self, text="Frame Rate: ", org=(30, 50), font="plain", font_scale=2, color=(0, 0, 255),
                               thickness=2):
            # Input validation
            max_font_scale = 10,  # Maximum font scale allowed
            min_thickness = 1,  # Minimum thickness allowed
            max_thickness = 10,  # Maximum thickness allowed
            window_size=(1920, 1080)  # Expecting

            # Ensure `window_size` is a tuple of two positive integers
            if not isinstance(window_size, tuple) or len(window_size) != 2 or not all(
                    isinstance(i, int) and i > 0 for i in window_size):
                raise ValueError(f"'window_size' must be a tuple of two positive integers, got {window_size} instead.")

            # Unpack window dimensions
            window_width, window_height = window_size

            # Validate text (ensure it is a string)
            if not isinstance(text, str):
                raise ValueError(f"'text' must be a string, got {type(text).__name__} instead.")

            # Validate org (ensure it is a tuple of two positive integers and in range)
            if not isinstance(org, tuple) or len(org) != 2 or not all(isinstance(i, int) and i >= 0 for i in org):
                raise ValueError(f"'org' must be a tuple of two non-negative integers, got {org} instead.")

            # Check if `org` fits within the window dimensions
            x, y = org
            if x >= window_width or y >= window_height:
                raise ValueError(
                    f"'org' values must fit within the window dimensions ({window_width}x{window_height}), got ({x}, {y}) instead."
                )

            # Check if `org` fits within the window dimensions
            x, y = org
            if x >= window_width or y >= window_height:
                raise ValueError(
                    f"'org' values must fit within the window dimensions ({window_width}x{window_height}), got {org} instead."
                )

            # Validate font (ensure it is a string and matches allowed font types)
            allowed_fonts = {"simplex", "plain", "duplex", "complex", "triplex", "script_simplex", "script_complex"}
            if not isinstance(font, str) or font.lower() not in allowed_fonts:
                raise ValueError(f"'font' must be one of {allowed_fonts}, got '{font}' instead.")

            if isinstance(max_font_scale, tuple):
                if len(max_font_scale) == 1:  # A tuple like (10,) can be unpacked
                    max_font_scale = max_font_scale[0]
                else:
                    raise ValueError(
                        f"'max_font_scale' must be a single integer or float, got an invalid tuple: {max_font_scale}")

            # Validate font_scale
            if not (isinstance(font_scale, int) or isinstance(font_scale, float)) or font_scale <= 0:
                raise ValueError(f"'font_scale' must be a positive number, got {font_scale}.")

            # Validate max_font_scale
            if not isinstance(max_font_scale, (int, float)):
                raise ValueError(
                    f"'max_font_scale' must be an integer or float, got {max_font_scale} ({type(max_font_scale).__name__}).")

            # Check that font_scale does not exceed max_font_scale
            if font_scale > max_font_scale:
                raise ValueError(f"'font_scale' cannot exceed the maximum value of {max_font_scale}, got {font_scale}.")

            # Validate color (ensure it is a tuple of 3 integers within the range 0-255)
            if not isinstance(color, tuple) or len(color) != 3 or not all(
                    isinstance(c, int) and 0 <= c <= 255 for c in color):
                raise ValueError(f"'color' must be a tuple of three integers between 0 and 255, got {color} instead.")

            # Unpack min_thickness if it's a tuple
            if isinstance(min_thickness, tuple):
                if len(min_thickness) == 1:  # Single value tuple (e.g., (1,))
                    min_thickness = min_thickness[0]
                else:
                    raise ValueError(f"'min_thickness' must be a single integer, got invalid tuple: {min_thickness}")

            # Unpack max_thickness if it's a tuple
            if isinstance(max_thickness, tuple):
                if len(max_thickness) == 1:  # Single value tuple (e.g., (10,))
                    max_thickness = max_thickness[0]
                else:
                    raise ValueError(f"'max_thickness' must be a single integer, got invalid tuple: {max_thickness}")

            # Validate thickness (ensure it is a positive integer)
            if not isinstance(thickness, int):
                raise ValueError(f"'thickness' must be an integer, got {type(thickness).__name__} instead.")
            elif thickness < min_thickness or thickness > max_thickness:
                raise ValueError(
                    f"'thickness' must be between {min_thickness} and {max_thickness}, got {thickness} instead."
                )

            """
            Displays the frame rate on the image with custom font style, position, and appearance.

            :param text: The text to display.
            :param org: The position of the text in the frame (x, y).
            :param font: The user-friendly font name (default is "plain").
                         Supported values: "simplex", "plain", "duplex", "complex", "triplex",
                                          "script_simplex", "script_complex".
            :param font_scale: The scale factor for the font size.
            :param color: The color of the text in BGR format.
            :param thickness: The thickness of the text stroke.
            """
            # Mapping user-friendly font names to OpenCV constants
            font_mapping = {
                "simplex": cv2.FONT_HERSHEY_SIMPLEX,
                "plain": cv2.FONT_HERSHEY_PLAIN,
                "duplex": cv2.FONT_HERSHEY_DUPLEX,
                "complex": cv2.FONT_HERSHEY_COMPLEX,
                "triplex": cv2.FONT_HERSHEY_TRIPLEX,
                "script_simplex": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                "script_complex": cv2.FONT_HERSHEY_SCRIPT_COMPLEX
            }

            # Retrieve the actual font constant from the mapping, default to "plain" if invalid font
            font_type = font_mapping.get(font.lower(), cv2.FONT_HERSHEY_PLAIN)

            # Draw the text on the image
            cv2.putText(self.img, f"{text} {self.outer.frame_rate}", org, font_type, font_scale, color, thickness)

        # displaying text on the screen
        def display_text(self, text="Your Text: ", org=(30, 110), font="plain", font_scale=2, color=(0, 0, 255),
                               thickness=2):
            # Input validation
            max_font_scale = 10,  # Maximum font scale allowed
            min_thickness = 1,  # Minimum thickness allowed
            max_thickness = 10,  # Maximum thickness allowed
            window_size = (1920, 1080)  # Expecting

            # Ensure `window_size` is a tuple of two positive integers
            if not isinstance(window_size, tuple) or len(window_size) != 2 or not all(
                    isinstance(i, int) and i > 0 for i in window_size):
                raise ValueError(
                    f"'window_size' must be a tuple of two positive integers, got {window_size} instead.")

            # Unpack window dimensions
            window_width, window_height = window_size

            # Validate text (ensure it is a string)
            if not isinstance(text, str):
                raise ValueError(f"'text' must be a string, got {type(text).__name__} instead.")

            # Validate org (ensure it is a tuple of two positive integers and in range)
            if not isinstance(org, tuple) or len(org) != 2 or not all(isinstance(i, int) and i >= 0 for i in org):
                raise ValueError(f"'org' must be a tuple of two non-negative integers, got {org} instead.")

            # Check if `org` fits within the window dimensions
            x, y = org
            if x >= window_width or y >= window_height:
                raise ValueError(
                    f"'org' values must fit within the window dimensions ({window_width}x{window_height}), got ({x}, {y}) instead."
                )

            # Check if `org` fits within the window dimensions
            x, y = org
            if x >= window_width or y >= window_height:
                raise ValueError(
                    f"'org' values must fit within the window dimensions ({window_width}x{window_height}), got {org} instead."
                )

            # Validate font (ensure it is a string and matches allowed font types)
            allowed_fonts = {"simplex", "plain", "duplex", "complex", "triplex", "script_simplex", "script_complex"}
            if not isinstance(font, str) or font.lower() not in allowed_fonts:
                raise ValueError(f"'font' must be one of {allowed_fonts}, got '{font}' instead.")

            if isinstance(max_font_scale, tuple):
                if len(max_font_scale) == 1:  # A tuple like (10,) can be unpacked
                    max_font_scale = max_font_scale[0]
                else:
                    raise ValueError(
                        f"'max_font_scale' must be a single integer or float, got an invalid tuple: {max_font_scale}")

            # Validate font_scale
            if not (isinstance(font_scale, int) or isinstance(font_scale, float)) or font_scale <= 0:
                raise ValueError(f"'font_scale' must be a positive number, got {font_scale}.")

            # Validate max_font_scale
            if not isinstance(max_font_scale, (int, float)):
                raise ValueError(
                    f"'max_font_scale' must be an integer or float, got {max_font_scale} ({type(max_font_scale).__name__}).")

            # Check that font_scale does not exceed max_font_scale
            if font_scale > max_font_scale:
                raise ValueError(
                    f"'font_scale' cannot exceed the maximum value of {max_font_scale}, got {font_scale}.")

            # Validate color (ensure it is a tuple of 3 integers within the range 0-255)
            if not isinstance(color, tuple) or len(color) != 3 or not all(
                    isinstance(c, int) and 0 <= c <= 255 for c in color):
                raise ValueError(
                    f"'color' must be a tuple of three integers between 0 and 255, got {color} instead.")

            # Unpack min_thickness if it's a tuple
            if isinstance(min_thickness, tuple):
                if len(min_thickness) == 1:  # Single value tuple (e.g., (1,))
                    min_thickness = min_thickness[0]
                else:
                    raise ValueError(
                        f"'min_thickness' must be a single integer, got invalid tuple: {min_thickness}")

            # Unpack max_thickness if it's a tuple
            if isinstance(max_thickness, tuple):
                if len(max_thickness) == 1:  # Single value tuple (e.g., (10,))
                    max_thickness = max_thickness[0]
                else:
                    raise ValueError(
                        f"'max_thickness' must be a single integer, got invalid tuple: {max_thickness}")

            # Validate thickness (ensure it is a positive integer)
            if not isinstance(thickness, int):
                raise ValueError(f"'thickness' must be an integer, got {type(thickness).__name__} instead.")
            elif thickness < min_thickness or thickness > max_thickness:
                raise ValueError(
                    f"'thickness' must be between {min_thickness} and {max_thickness}, got {thickness} instead."
                )

            """
            Displays a text on the image with custom font style, position, and appearance.

            :param text: The text to display.
            :param org: The position of the text in the frame (x, y).
            :param font: The user-friendly font name (default is "plain").
                         Supported values: "simplex", "plain", "duplex", "complex", "triplex",
                                          "script_simplex", "script_complex".
            :param font_scale: The scale factor for the font size.
            :param color: The color of the text in BGR format.
            :param thickness: The thickness of the text stroke.
            """
            # Mapping user-friendly font names to OpenCV constants
            font_mapping = {
                "simplex": cv2.FONT_HERSHEY_SIMPLEX,
                "plain": cv2.FONT_HERSHEY_PLAIN,
                "duplex": cv2.FONT_HERSHEY_DUPLEX,
                "complex": cv2.FONT_HERSHEY_COMPLEX,
                "triplex": cv2.FONT_HERSHEY_TRIPLEX,
                "script_simplex": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                "script_complex": cv2.FONT_HERSHEY_SCRIPT_COMPLEX
            }

            # Retrieve the actual font constant from the mapping, default to "plain" if invalid font
            font_type = font_mapping.get(font.lower(), cv2.FONT_HERSHEY_PLAIN)

            # Draw the text on the image
            cv2.putText(self.img, f"{text}", org, font_type, font_scale, color, thickness)

        # displays the real frames per second value
        def display_real_fps(self):
            cTime = time.time()  # Current time
            fps = 1 / (cTime - self.pTime)  # Calculate frames per second
            self.pTime = cTime  # Update previous time to the current time

            # Draw the text on the image
            cv2.putText(self.img, f"real FPS {int(fps)}", (30,80), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 2)
            print(f"FPS: {int(fps)}")  # Display FPS
            time.sleep(0.03)

        # drawing a rectangle in the image
        def draw_rectangle(self,start=(50, 150),end=(85, 400),fill=False, color=(0, 255, 0), thickness=2):
            # validation
            # Validate 'start' and 'end'
            if not isinstance(start, tuple) or not isinstance(end, tuple) or len(start) != 2 or len(end) != 2:
                raise ValueError("Invalid inputs: 'start' and 'end' must be tuples of two integers (x, y).")
            if not all(isinstance(coord, int) for coord in start + end):
                raise ValueError("Invalid inputs: 'start' and 'end' must contain integer coordinates.")

            # Validate 'fill'
            if not isinstance(fill, bool):
                raise ValueError("Invalid input: 'fill' must be a boolean.")

            # Validate 'color'
            if not isinstance(color, tuple) or len(color) != 3 or not all(
                    isinstance(c, int) and 0 <= c <= 255 for c in color):
                raise ValueError("Invalid input: 'color' must be a tuple of three integers between 0 and 255.")

            # Validate 'thickness'
            if not isinstance(thickness, int) or thickness < 0:
                raise ValueError("Invalid input: 'thickness' must be a non-negative integer.")

            # checking whether it is asking to fill the rectangle or not
            if fill:
                cv2.rectangle(self.img, start, end, color, cv2.FILLED)
            else:
                cv2.rectangle(self.img, start, end, color, thickness)

        # draw a vertical slider in the image
        def draw_vertical_slider(self,start=(50, 150),end=(85, 400),val=150, color=(0, 255, 0), thickness=2):
            # validating
            # Validate 'start' and 'end'
            if not isinstance(start, tuple) or not isinstance(end, tuple) or len(start) != 2 or len(end) != 2:
                raise ValueError("Invalid inputs: 'start' and 'end' must be tuples of two integers (x, y).")
            if not all(isinstance(coord, int) for coord in start + end):
                raise ValueError("Invalid inputs: 'start' and 'end' must contain integer coordinates.")

            # Validate 'val'
            if not isinstance(val, (int, float)):
                raise ValueError("Invalid input: 'val' must be an integer or a float.")

            # Validate 'color'
            if not isinstance(color, tuple) or len(color) != 3 or not all(
                    isinstance(c, int) and 0 <= c <= 255 for c in color):
                raise ValueError("Invalid input: 'color' must be a tuple of three integers between 0 and 255.")

            # Validate 'thickness'
            if not isinstance(thickness, int) or thickness <= 0:
                raise ValueError("Invalid input: 'thickness' must be a positive integer.")

            # drawing the outer bar
            self.draw_rectangle(start,end,fill=False,color=color,thickness=thickness)
            # slider
            x, y = start
            cv2.rectangle(self.img, (x,int(val)), end, color, cv2.FILLED)


        ''' functions for drawing on the image ends here '''

        ''' functions on hand positions starts here '''
        def find_hand_position(self, hand_no=0, draw=True):
            # validating handNo
            if hand_no < 0 or hand_no > 1:
                print("Error: 'handNo' must be a non-negative integer less than or equal to 1.")
                return
            lmsList = []  # list of landmarks
            # Check if self.results is not None and contains hand landmarks
            if self.results and self.results.multi_hand_landmarks:
                # Ensure handNo is within the range of detected hands
                if hand_no < len(self.results.multi_hand_landmarks):
                    myHand = self.results.multi_hand_landmarks[hand_no]
                    for id, lm in enumerate(myHand.landmark):
                        h, w, c = self.img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmsList.append([id, cx, cy])
                        if draw:
                           cv2.circle(self.img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                else:
                    print(f"Error: Hand number {hand_no} is out of bounds.")
                # we will return the values of the landmarks
                return lmsList
            else:
                print("No hand landmarks detected.")

        def determine_hand_position(self,hand_no=0):
            # getting the hand position
            lmList = self.find_hand_position(hand_no=0, draw=False)
            if lmList and len(lmList) != 0:
                fingers = []
                # for detecting the thumb(since it is a special case). Right hand
                if(lmList[self.finger_tips[0]][1] > lmList[self.finger_tips[0] - 1][1]):
                    fingers.append(1)
                else:
                    fingers.append(0)
                # for detecting the four fingers without the thumb
                for id in range(1,5):
                    if(lmList[self.finger_tips[id]][2] < lmList[self.finger_tips[id]-2][2]):
                        fingers.append(1)
                    else:
                        fingers.append(0)
                return fingers

        ''' function on hand positions ends here '''

        ''' function to find the landmark position starts here '''
        def find_landmark_position(self, hand_no=0, landmark_id=0, draw=False, color=(255, 0, 0)):
            lmList = self.find_hand_position(hand_no=hand_no,draw=False)
            if lmList and len(lmList) > landmark_id:
                id, xpos, ypos = lmList[landmark_id]
                if draw:
                    cv2.circle(self.img, (xpos, ypos), 5, color=color, thickness=cv2.FILLED)
                return xpos, ypos
            else:
                return None, None
        ''' function to find the landmark position ends here '''

    ''' class for manipulating the microcontroller '''
    class ucontroller:
        def __init__(self,outer_instance,port="COM0",baudrate=9600,timeout=None):
            self.outer = outer_instance
            self.port = port
            self.baudrate = baudrate
            self.timeout = timeout
            self.conn = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            if self.conn:
                time.sleep(2) # wait 2 secs for the serial connection to initialize
            else:
                raise Exception("Error: Unable to connect to the controller.")

        ''' function to send serial data to arduino starts here '''
        def send_serial_data(self,data=None):
            if data is not None:
                self.conn.write(bytes(data))
            else:
                self.conn.write(b'0')
        ''' function to send serial data to arduino ends here '''

        ''' function to send serial data to arduino without any obstruction starts here '''
        def send_serial_data_unobstructed(self, data=None):
            if data is None:
                return  # do nothing — better than sending garbage

            try:
                # Optional: add small timeout if your serial lib supports it
                self.conn.write(data)
                self.conn.flush()  # try to push data out immediately
            except Exception as e:
                print("Serial write error:", e)
                # Optional: try to reconnect or flag error
        ''' function to send serial data to arduino without any obstruction ends here '''

        ''' function to receive serial data from arduino starts here '''
        def receive_serial_data(self):
            if self.conn.in_waiting > 0:
                try:
                    data = self.conn.readline().decode('utf-8').strip()
                    return data
                except Exception as e:
                    print(f"Error reading serial data: {e}")
                    return None
            return None
        ''' function to receive serial data from arduino ends here '''
    # Creating a class for tools
    class tools:
        def __init__(self, outer_instance,other_instance=None):
            self.outer = outer_instance # reference to the outer class
            self.other_instance = other_instance # reference to hand tracking class
            self.dir_path = ""  # path of the directory
            self.overlay_list = []   # list to store images for overlays

        # finding the range of two numbers w.r.t. the object/finger position
        def find_range(self, length=100, min=150, max=400, lmin=20, lmax=100, order="ascending"):
            if length < 0:
                print("Error: 'length' must be a positive integer.")
                return
            if min > max:
                print("Error: 'min' must be less than or equal to 'max'.")
                return
            if min < 0:
                print("Error: 'min' must be a positive integer.")
            if lmin > lmax:
                print("Error: 'lmin' must be less than or equal to 'lmax'.")
                return
            if lmin < 0:
                print("Error: 'lmin' must be a positive integer.")
            # validating inputs
            try:
                # Validate 'order' - must be a non-empty string
                if not isinstance(order, str) or order.strip() == "":
                    raise ValueError("Invalid 'order': Must be a non-empty string.")

                # Validate 'min', 'max', 'lmin', 'lmax' - must all be int or float
                for field, value in [("min", min), ("max", max), ("lmin", lmin), ("lmax", lmax)]:
                    if not isinstance(value, (int, float)):
                        raise ValueError(f"Invalid '{field}': Must be an integer or floating-point number.")
                        return True
            except ValueError as e:
                print(f"Validation Error: {e}")
                return False

            if order == "descending":
                range_val = np.interp(length,[lmin,lmax],[max,min])
            elif order == "ascending":
                range_val = np.interp(length, [lmin, lmax], [min, max])
            return range_val

        # list out files from a directory
        def print_dir_list(self, dir_path):
            if not os.path.isdir(dir_path):
                print(f"Error: '{dir_path}' is not a valid directory path.")
                return
            print("Files in directory:")
            for file in os.listdir(dir_path):
                print(file)

        # return the list of files from a directory
        def find_dir_list(self, dir_path):
            if not os.path.isdir(dir_path):
                print(f"Error: '{dir_path}' is not a valid directory path.")
                return
            self.dir_path = dir_path
            return os.listdir(dir_path)

        # load images from a directory into the program
        def load_images_from_dir(self, dir_path):
            if not os.path.isdir(dir_path):
                print(f"Error: '{dir_path}' is not a valid directory path.")
                return
            self.dir_path = dir_path
            imgList = os.listdir(dir_path)
            self.overlay_list = []  # redeclaring to get rid of previous values
            for indivImg in imgList:
                if indivImg.endswith(".png") or indivImg.endswith(".jpg"):
                    indivImg = cv2.imread(f'{dir_path}/{indivImg}')
                    self.overlay_list.append(indivImg)
                else:
                    print(f"Skipping file '{indivImg}': File type not supported.")
            return len(self.overlay_list)

        # function to overlay an image
        def overlay_image(self,org=(0,0),img_num=0):
            x, y = org
            h, w, c = self.overlay_list[img_num].shape
            if x == 0 or y == 0:
                self.other_instance.img[0:h,0:w] = self.overlay_list[img_num]
            else:
                self.other_instance.img[y:h+y,x:w+x] = self.overlay_list[img_num]

        # save files from a directory
        def save_files(self, filename="output.jpg"):
            if not isinstance(filename, str):
                print("Error: 'filename' must be a string.")
                return
            try:
                cv2.imwrite(filename, self.outer.img)
                print(f"Image saved as '{filename}'.")
            except Exception as e:
                print(f"Error saving file: {e}")

    ''''# Creating a class for hand tracking
    class AutoGUI:
            def __init__(self, outer_instance):
                self.outer = outer_instance  # Reference to the outer class

            #functions on volume control starts here
            def increase_volume(self,steps=5):
                for _ in range(steps):
                    pyautogui.press("volumeup")
                    time.sleep(0.1)  # Small delay between key presses to ensure smooth handling

            # Decrease Volume
            def decrease_volume(self,steps=5):
                for _ in range(steps):
                    pyautogui.press("volumedown")
                    time.sleep(0.1)

            # Mute/Unmute Volume
            def mute_volume(self):
                pyautogui.press("volumemute")
            function on volume control ends here '''