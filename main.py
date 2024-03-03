import cv2
import pandas as pd
from tkinter import filedialog
import matplotlib.pyplot as plt
import colorsys

# Load the image
img_path = r'C:\Users\USER\Desktop\Year 3 semester 1\pythonProject3\color snap logo.png'
original_img = cv2.imread(img_path)

# Check if the image is loaded successfully
if original_img is None:
    print("Error: Unable to load image from path:", img_path)
else:
    print("Image loaded successfully:", img_path)

# Resize the image to a larger size
scale_percent = 150  # Adjust the scale percentage as needed
width = int(original_img.shape[1] * scale_percent / 95)
height = int(original_img.shape[0] * scale_percent / 120)
img = cv2.resize(original_img, (width, height))

# Global variables
clicked = False
r = g = b = x_pos = y_pos = 0
camera_opened = False
capture_in_progress = False

# Reading CSV file with color data
index = ["color_name", "hex", "R", "G", "B"]
csv = pd.read_csv('color_names_1200.csv', names=index, header=None)
hex_color=None

# Function to calculate the minimum distance from all colors and get the most matching color
def get_color_info(R, G, B):
    minimum = 10000
    color_info = {}
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            color_info['color_name'] = csv.loc[i, "color_name"]
            color_info['hex'] = csv.loc[i, "hex"]
            color_info['rgb'] = (int(csv.loc[i, "R"]), int(csv.loc[i, "G"]), int(csv.loc[i, "B"]))

    return color_info

# Function to handle mouse double-click events
def draw_function(event, x, y, flags, param):
    global b, g, r, x_pos, y_pos, clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked = True
        x_pos = x
        y_pos = y
        b, g, r = img[y, x]
        b = int(b)
        g = int(g)
        r = int(r)


# Click handler for the "Take Picture" button
def take_picture():
    global camera_opened, capture_in_progress, captured_image, img
    if camera_opened and not capture_in_progress:  # Check if the camera is opened and not capturing already
        capture_in_progress = True
        ret, frame = camera.read()
        if ret:
            captured_image = frame.copy()
            # Resize the captured image to a larger size
            captured_image = cv2.resize(captured_image, (800, 600))  # Adjust size as needed
            img = captured_image.copy()  # Update the 'img' variable with the captured frame
            cv2.imshow("image", img)  # Display the captured image
        else:
            print("Error: Unable to capture image")
        capture_in_progress = False  # Reset the flag after attempting to capture
        camera.release()  # Close the camera
        camera_opened = False  # Update camera state
    else:
        print("Error: Camera is not opened or capture is already in progress")


def upload_image():
    global img
    file_path = filedialog.askopenfilename()
    print("Selected file path:", file_path)  # Print the selected file path
    if file_path:
        img = cv2.imread(file_path)
        if img is not None:
            if camera_opened:
                camera.release()
                cv2.rectangle(img, (20, button_height), (20 + button_width, button_height + 50), (255, 255, 255), -1)
            # Get the dimensions of the window
            window_width = cv2.getWindowImageRect('image')[2]
            window_height = cv2.getWindowImageRect('image')[3]

            # Resize the image to fit the window size
            img = cv2.resize(img, (window_width, window_height))

            cv2.imshow("image", img)
        else:
            print("Error: Unable to load image")


# Function to generate matching colors
def generate_matching_colors(input_color, num_colors=5):
    # Convert input color to RGB
    input_rgb = tuple(int(input_color[i:i + 2], 16) / 255.0 for i in (1, 3, 5))

    # Convert RGB to HLS (Hue, Lightness, Saturation)
    input_h, input_l, input_s = colorsys.rgb_to_hls(*input_rgb)

    # Generate new colors based on variations in hue, lightness, and saturation
    matching_colors = []
    matching_color_names = []
    matching_color_rgb = []  # Store RGB values
    for i in range(num_colors):
        # Adjust hue, lightness, and saturation to create variation
        hue = (input_h + 0.1 * i) % 1.0
        lightness = min(1.0, max(0.0, input_l + 0.1 * i))
        saturation = min(1.0, max(0.0, input_s + 0.1 * i))
        # Convert HLS back to RGB
        new_rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        # Convert RGB to hexadecimal color
        new_hex = "#{:02x}{:02x}{:02x}".format(int(new_rgb[0] * 255), int(new_rgb[1] * 255), int(new_rgb[2] * 255))

        matching_colors.append(new_hex)
        matching_color_names.append(get_color_info(*[int(c * 255) for c in new_rgb])['color_name'])  # Get color name
        new_rgb = tuple(round(val * 255) for val in colorsys.hls_to_rgb(hue, lightness, saturation))
        matching_color_rgb.append(new_rgb)  # Store RGB values

    return matching_colors, matching_color_names, matching_color_rgb


# Function to plot colors
def plot_colors(colors, color_names, rgb_values, figsize=(10,2)):
    num_colors = len(colors)
    fig, ax = plt.subplots(1, num_colors, figsize=figsize)
    # Extract RGB values of the first color
    third_color_rgb = rgb_values[3]
    sum_rgb = sum(third_color_rgb)

    for i, (color, color_name, rgb) in enumerate(zip(colors, color_names, rgb_values)):
        rgb_color = tuple(int(color[i:i+2], 16) / 255.0 for i in (1, 3, 5))
        rect = plt.Rectangle((0, 0), 1, 1, color=rgb_color)
        ax[i].add_patch(rect)  # Corrected line
        ax[i].axis('off')
        # Use the sum of RGB values of the first color to determine text color for all colors
        if sum_rgb >= 300 :
            ax[i].text(0.5, 0.5, f'{color_name}\nR={rgb[0]} G={rgb[1]} B={rgb[2]}', horizontalalignment='center',
                       verticalalignment='center', fontsize=10, color='black')
        else:
            ax[i].text(0.5, 0.5, f'{color_name}\nR={rgb[0]} G={rgb[1]} B={rgb[2]}', horizontalalignment='center',
                       verticalalignment='center', fontsize=10, color='white')


    plt.tight_layout()
    plt.show()


def generate_matching_button_clicked():
    global clicked, r, g, b, hex_color
    if hex_color:  # Check if a color is selected

        clicked = True

        # Use the RGB values from the selected pixel for generating matching colors
        matching_colors, matching_color_names, rgb_values = generate_matching_colors(hex_color)

        # Plot the matching colors
        plot_colors(matching_colors, matching_color_names, rgb_values)


# Create a window and set mouse callback
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_function)

# Main loop
while True:
    # Initialize camera if opened
    if camera_opened:
        if not capture_in_progress:
            ret, frame = camera.read()
            if ret:
                img = frame.copy()
                cv2.putText(img, 'Press "Take Picture" to capture', (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (255, 0, 0), 2, cv2.LINE_AA)

    # Draw the buttons regardless of camera state
    button_height = img.shape[0] - 80  # Adjust the button height as needed
    button_width = 200  # Adjust the button width as needed
    cv2.rectangle(img, (20, button_height), (210, button_height + 50), (255, 255, 255), -1)
    cv2.putText(img, 'Take Picture', (50, button_height + 35), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 0), 1, cv2.LINE_AA)

    cv2.rectangle(img, (240, button_height), (440, button_height + 50), (255, 255, 255), -1)
    cv2.putText(img, 'Upload Image', (260, button_height + 35), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 0), 1, cv2.LINE_AA)
    # Draw "Generate Matching Colors" button only if the camera is not opened
    if not camera_opened:
        cv2.rectangle(img, (460, button_height), (770, button_height + 50), (255, 255, 255), -1)
        cv2.putText(img, 'Generate Matching Colors', (470, button_height + 35), cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (0, 0, 0), 1, cv2.LINE_AA)

    # Display the image
    if img is not None:
        cv2.imshow("image", img)
        cv2.rectangle(img, (460, button_height), (770, button_height + 50), (255, 255, 255), -1)
        cv2.putText(img, 'Generate Matching Colors', (470, button_height + 35), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 0), 1, cv2.LINE_AA)

    # Check if a button is clicked
    if clicked:
        if 20 <= x_pos <= 220 and button_height <= y_pos <= button_height + 50:
            if not camera_opened:
                camera = cv2.VideoCapture(0)
                camera_opened = True
            elif not capture_in_progress:
                take_picture()
        elif 240 <= x_pos <= 440 and button_height <= y_pos <= button_height + 50:
            upload_image()
        elif 460 <= x_pos <= 770 and button_height <= y_pos <= button_height + 50:
            generate_matching_button_clicked()
        else:
            # cv2.rectangle(image, start point, endpoint, color, thickness)-1 fills entire rectangle
            cv2.rectangle(img, (20, 20), (750, 60), (b, g, r), -1)

            # Get color information including RGB values
            color_info = get_color_info(r, g, b)
            hex_color=color_info['hex']

            # Creating text string to display (Color name and RGB values)
            text = f"{color_info['color_name']} R={color_info['rgb'][0]}" \
                   f" G={color_info['rgb'][1]} B={color_info['rgb'][2]}"

            # cv2.putText(img,text,start,font(0-7),fontScale,color,thickness,lineType )
            cv2.putText(img, text, (50, 50), 2, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

            # For very light colours we will display text in black colour
            if r + g + b >= 600:
                cv2.putText(img, text, (50, 50), 2, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
            pass
        clicked = False

    # Break the loop when user hits 'esc' key
    if cv2.waitKey(20) & 0xFF == 27:
        break

# Release camera and destroy all windows
if camera_opened:
    camera.release()
cv2.destroyAllWindows()
