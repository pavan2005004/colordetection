import cv2
import pandas as pd
import pyttsx3
import csv
from datetime import datetime
import colorsys
# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Load color dataset
csv_path = 'colors.csv'
index = ['color', 'color_name', 'hex', 'R', 'G', 'B']
df = pd.read_csv(csv_path, names=index, header=None)

# Globals
clicked = False
r = g = b = xpos = ypos = 0
last_spoken = None

# Function to find closest named color
def get_color_name(R, G, B):
    min_dist = float('inf')
    cname = "Unknown"
    for i in range(len(df)):
        d = abs(R - int(df.loc[i, "R"])) + abs(G - int(df.loc[i, "G"])) + abs(B - int(df.loc[i, "B"]))
        if d < min_dist:
            min_dist = d
            cname = df.loc[i, "color_name"]
    return cname

# Function to get general color category


def get_basic_color(R, G, B):
    # Normalize RGB to 0-1
    r_norm, g_norm, b_norm = R / 255.0, G / 255.0, B / 255.0
    h, l, s = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    h = h * 360  # Convert to degrees

    if l < 0.1:
        return "Black"
    elif l > 0.9:
        return "White"
    elif s < 0.2:
        return "Gray"

    if 0 <= h < 20 or 340 <= h <= 360:
        return "Red"
    elif 20 <= h < 45:
        return "Orange"
    elif 45 <= h < 70:
        return "Yellow"
    elif 70 <= h < 160:
        return "Green"
    elif 160 <= h < 260:
        return "Blue"
    elif 260 <= h < 320:
        return "Purple"
    else:
        return "Unknown"


# Speak detected color
def speak(text):
    global last_spoken
    if text != last_spoken:
        engine.say(text)
        engine.runAndWait()
        last_spoken = text

# Save to CSV
def save_color(color_name, r, g, b):
    with open("detected_colors.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([color_name, r, g, b, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

# Mouse callback
def draw_function(event, x, y, flags, param):
    global b, g, r, xpos, ypos, clicked, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked = True
        xpos, ypos = x, y
        b, g, r = frame[y, x]
        b, g, r = int(b), int(g), int(r)
        cname = get_color_name(r, g, b)
        bcolor = get_basic_color(r, g, b)
        full_name = f"{bcolor} - {cname}"
        speak(full_name)
        save_color(full_name, r, g, b)

# Webcam stream
cap = cv2.VideoCapture(0)
cv2.namedWindow('Color Recognition')
cv2.setMouseCallback('Color Recognition', draw_function)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if clicked:
        # Show color info
        cv2.rectangle(frame, (20, 20), (750, 60), (b, g, r), -1)
        text = f'{get_basic_color(r, g, b)} | {get_color_name(r, g, b)}  R={r} G={g} B={b}'
        cv2.putText(frame, text, (50, 50), 2, 0.8,
                    (255, 255, 255) if r + g + b < 400 else (0, 0, 0), 2)

    cv2.imshow('Color Recognition', frame)

    if cv2.waitKey(20) & 0xFF == 27:  # Press Esc to exit
        break

cap.release()
cv2.destroyAllWindows()
