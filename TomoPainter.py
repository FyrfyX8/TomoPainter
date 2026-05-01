import gp2040pico.picoinput as gp2040
from time import sleep
import json
import argparse

from math import floor, ceil

from docutils.parsers import null

parser = argparse.ArgumentParser(description='JSON from Living the Grid')
parser.add_argument('file', help="JSON file from Living the Grid")

args = parser.parse_args()

# Constant Variables
REAL_CANVAS_SIZE = (256, 256) # size of actual canvas
DEFAULT_CANVAS_POS = (129, 129) # X , Y
DEFAULT_colour_POS = (0,0,0) # Hue, Saturation, Brightness
SMOOTH_PIXEL_MAP = { # Pixel size : (Pixel offset, Position in selection menu)
    1: (0, -2),
    3: (-1, -1),
    7: (1, 0),
    13: (-5, 1),
    19: (-5, 2),
    27: (-11, 3),
}
PERFECT_PIXEL_MAP = { # Pixel size : Position in selection menu
    4: 3,
    8: 2,
    16: 1,
    32: 0
}
# Values for correction of center for different Canvas modes, determent by offset from (1,1) WIP
CANVAS_CORRECTION_VALUES = {
    "square": (0,0),
    "book": (38,0),
    "tv": (0,68),
}
STARTING_PIXEL = (1,1)
FALLBACK_LOOPS = 5 # This is used to handle skipped inputs for canvas_move and colour_move this should eliminate pixel shifts

def can_handle(d) -> bool:
    if d["source"] == "living-the-grid.gozapp.dev" and d["version"] >= 2:
        return True
    return False

# Open file and check if format is right

with open(args.file, "r", encoding="utf-8") as f:
    data = json.load(f)

if not can_handle(data):
    raise ValueError("Invalid JSON")

# Setup of needed editable Variables
default_grid_pos = DEFAULT_CANVAS_POS
preset_canvas_size = REAL_CANVAS_SIZE
canvas_pos = DEFAULT_CANVAS_POS
colour_pos = DEFAULT_colour_POS
current_colour_number = -1
brush_offset = 0

if data["version"] == 2: # Read File parameters for version 2
    max_grid_pos = (data["width"], data["height"])
    brush = data["brush"]
    canvas = data["canvas"]
    palette_raw : list[dict] = data["palette"]
    palette : list[tuple[int,int,int]]= []
    for colour in palette_raw:
        palette.append((colour["press"]["h"],colour["press"]["s"],colour["press"]["b"]))
    pixels = data["pixels"]
else:
    raise ValueError("Unsupported File version")

print("file read")

# Function definitions
def fallback_loop_value(value : float, n : int = 2) -> float: #Calculate end value * FALLBACK_LOOPS = value
    return round(value / FALLBACK_LOOPS, n)

def calibrate_default(): # Move offset for smooth Pixel sizes gets applied here
    global default_grid_pos, canvas_pos, preset_canvas_size
    goto(default_grid_pos)
    correction_x, correction_y = CANVAS_CORRECTION_VALUES[canvas["preset"]]
    default_grid_pos = (floor((REAL_CANVAS_SIZE[0] / 2 - correction_x) / brush["px"] + 1), floor((REAL_CANVAS_SIZE[1] / 2 - correction_y) / brush["px"] + 1))
    preset_canvas_size = (canvas["w"],canvas["h"])
    print(default_grid_pos)
    if brush["mode"] == "smooth":
        canvas_move(brush_offset,brush_offset,True)
    canvas_pos = default_grid_pos

def canvas_move(right : int = 0, down : int = 0, override_pixelsize : bool = False) -> None:
    global canvas_pos
    canvas_pos = (canvas_pos[0] + right, canvas_pos[1] + down)

    # account for smooth pixels pixel size since It's still the full grid.
    if brush["mode"] == "smooth" and not override_pixelsize:
        pixelsize_multiplier = brush["px"]
        right *= pixelsize_multiplier
        down *= pixelsize_multiplier

    # Makes list of needed inputs to move by x, y
    move_inputs : list[list[int]] = []
    while right != 0 or down != 0:
        move_input : list[int] = []
        if right > 0:
            right -= 1
            move_input.append(gp2040.DPAD_RIGHT)
        elif right < 0:
            move_input.append(gp2040.DPAD_LEFT)
            right += 1
        if down > 0:
            move_input.append(gp2040.DPAD_DOWN)
            down -= 1
        elif down < 0:
            move_input.append(gp2040.DPAD_UP)
            down += 1
        move_inputs.append(move_input)

    # Execute macro
    if move_inputs:
        for mi in move_inputs:
            gp2040.press_buttons(mi)
            sleep(0.05)


def colour_move(h : int = 0, s : int = 0, b : int = 0) -> None: # h and s value cant be changed at the same time!!!
    global colour_pos
    colour_pos = (colour_pos[0] + h, colour_pos[1] + s, colour_pos[2] + b)

    # Makes list of needed inputs to move by h, s, b.
    colour_inputs : list[list[int]] = []
    while h != 0 or s != 0 or b != 0:
        colour_input: list[int] = []
        if h > 0:
            h -= 1
            colour_input.append(gp2040.ZR)
        elif h < 0:
            colour_input.append(gp2040.ZL)
            h += 1
        if s > 0:
            s -= 1
            colour_input.append(gp2040.DPAD_RIGHT)
        elif s < 0:
            colour_input.append(gp2040.DPAD_LEFT)
            s += 1
        elif b > 0:
            colour_input.append(gp2040.DPAD_UP)
            b -= 1
        elif b < 0:
            colour_input.append(gp2040.DPAD_DOWN)
            b += 1
        colour_inputs.append(colour_input)

    if colour_inputs:
        for ci in colour_inputs:
            gp2040.press_buttons(ci)
            sleep(0.05)

def goto(pos_xy : tuple[int,int]) -> None: # Move to Position (X, Y)
    canvas_move(pos_xy[0] - canvas_pos[0], pos_xy[1] - canvas_pos[1])


def set_colour(colour_hsb : tuple[int,int,int]) -> None: # Sets colour to (H, S, B) can only be used outside any other menü
    gp2040.press_buttons([gp2040.Y])
    sleep(0.2)
    gp2040.press_buttons([gp2040.Y])
    sleep(0.2)
    gp2040.press_buttons([gp2040.R])
    colour_move(colour_hsb[0] - colour_pos[0], colour_hsb[1] - colour_pos[1], colour_hsb[2] - colour_pos[2])
    gp2040.press_buttons([gp2040.B])
    sleep(0.3)

# Starting macro to print the image from JSON File
print("Enter the Canvas without giving any inputs and navigate to the Change Grip/Order menu.")
print("Make sure that no Joycons are conneted to the Switch")
input("Press Enter to continue...")

print("Connecting to Switch...")
gp2040.connect()
input("press enter to continue...")
# Opening Tomodatchi Live LTD
gp2040.press_buttons([gp2040.A])
sleep(2)
gp2040.press_buttons([gp2040.B])
sleep(1.5)
gp2040.press_buttons([gp2040.HOME])
sleep(1)

# Sececting Brush and applying offset if needed
for i in range(2):
    gp2040.press_buttons([gp2040.X])
    sleep(0.1)
match brush["mode"]:
    case "smooth":
        gp2040.press_buttons([gp2040.DPAD_DOWN])
        sleep(0.1)
        brush_offset, loops = SMOOTH_PIXEL_MAP.get(brush["px"],(None,None))
        if (brush_offset, loops) == (None,None):
            raise ValueError("Brush Size unsupported for smooth mode.")
        print("here")
        if loops < 0:
            for i in range(abs(loops)):
                gp2040.press_buttons([gp2040.DPAD_LEFT])
                sleep(0.1)
        elif loops > 0:
            for i in range(abs(loops)):
                gp2040.press_buttons([gp2040.DPAD_RIGHT])
                sleep(0.1)

    case "pixel":
        for i in range(2):
            gp2040.press_buttons([gp2040.DPAD_UP])
            sleep(0.1)
        gp2040.press_buttons([gp2040.DPAD_RIGHT])
        sleep(0.1)
        gp2040.press_buttons([gp2040.A])
        sleep(0.1)
        for i in range(2):
            gp2040.press_buttons([gp2040.DPAD_DOWN])
            sleep(0.1)
        loops = PERFECT_PIXEL_MAP.get(brush["px"], None)
        if loops is None:
            raise ValueError("Brush Size unsupported for mode Pixel-perfect")
        if loops != 0:
            for i in range(abs(loops)):
                gp2040.press_buttons([gp2040.DPAD_LEFT])
                sleep(0.1)

gp2040.press_buttons([gp2040.A])
sleep(0.1)
gp2040.press_buttons([gp2040.B])
sleep(0.5)
calibrate_default()
sleep(2)
print("brush type and size set.")

# Calculate Colour to Position Matrix

picture_matrix : list[list[tuple[int,int]]] = [[] for _ in palette_raw]
pos_x, pos_y = (0,0)
for pixel_row in pixels:
    pos_y += 1
    pos_x = 0
    pixel: int | None
    for pixel in pixel_row:
        pos_x += 1
        if pixel is None:
            continue
        picture_matrix[pixel].append((pos_x,pos_y))

print(len(picture_matrix))

# Test
"""
goto((1,1))
gp2040.press_buttons([gp2040.A])
sleep(0.2)
goto(max_grid_pos)
gp2040.press_buttons([gp2040.A])
sleep(0.2)

"""

# GOTO all positions of colour i and place a pixel there
for i in range(len(picture_matrix)):
    set_colour(palette[i])
    for pos in picture_matrix[i]:
        print(pos)
        goto(pos)
        sleep(0.1)
        gp2040.press_buttons([gp2040.A])
        sleep(0.1)