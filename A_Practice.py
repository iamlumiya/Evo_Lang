# Auditory - Practice

from psychopy import visual, core, event, sound, data
import random
import datetime
import os
import csv
import pandas as pd
from sys import platform
import sounddevice as sd
import soundfile as sf
import numpy as np

# Get the current working directory
current_dir = os.getcwd()

# Define the CSV file path
csv_file = os.path.join(current_dir, "stimuli.csv")

# Define directions to search for image and audio files
image_dir = os.path.join(current_dir, "image")
audio_dir = os.path.join(current_dir, "speech")

# Function to find a file in a given directory
def find_file(directory, filename):
    for root, _, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None
    
# Initialize an empty dictionary
data_dict = {}

# Read the CSV file
with open (csv_file, mode = 'r', encoding = 'utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        stimuli = row["name_s1"]
        
        # Extract just the file name
        visual_filename = os.path.basename(row["visual_s1"])
        audio_filename = os.path.basename(row["auditory_s1"])
        
        # Find the actual file paths in the specified directory
        visual_path = find_file(image_dir, visual_filename)
        audio_path = find_file(audio_dir, audio_filename)
        
        # Store in dictionary
        data_dict[stimuli] = {
            "name": row["name_s1"],
            "object": row["item_s1"],
            "visual": visual_path if visual_path else "Not found",
            "audio": audio_path if audio_path else "Not found",
            }
            
# Convert the dictionary into a DataFrame
stimuli_df = pd.DataFrame.from_dict(data_dict, orient = 'index')

# Define the directory for the audio files
word_audio = find_file(audio_dir, "word.wav")
nonword_audio = find_file(audio_dir, "daneo_converted.wav")

# Set up the window
win = visual.Window(fullscr = True, screen = 0, color = "black", units = "pix", checkTiming = False)
mouse = event.Mouse(visible = True, win = win)

# Function to show a message and wait for a mouse click
def show_message(text):
    msg = visual.TextStim(win, text = text, font = 'Arial', color = "white", height = 35, pos = (0, 0))
    msg.draw()
    win.flip()
    
    while not any(mouse.getPressed()):
        core.wait(0.1)
        
# Select 4 random images for the Learning phase and store them
all_images = stimuli_df ["visual"].dropna().tolist()
selected_images = random.sample(all_images, 4)
random.shuffle(selected_images)

# Get a list of all possible imaes that were not shown in the learning phase
unused_images = [img for img in all_images if img not in selected_images]

# Initial Presentation
# Welcome message
print("Starting Initial Presentation Phase...")
show_message("[Practice]\nPlease follow the instructions on the screen.\n\n Click the mouse to start the practice.")

# Prepare text and image components
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0, 0))

# Experiment loop
mouse = event.Mouse(visible = False, win = win)

for image_path in selected_images:
    
    keys = event.getKeys()
    if "escape" in keys:
        break

    # Display an image with the name for 2 seconds
    image_display.image = image_path
    name_audio = sound.Sound(word_audio)
    name_audio.play()
    image_display.draw()
    win.flip()
    core.wait(2)

    # Blank space
    win.flip()
    core.wait(1.5)


# End message
mouse = event.Mouse(visible = True, win = win)
show_message("Click the mouse to move to the next phase.")
print ("Completed Initial phase.")
core.wait(0.1)

event.clearEvents()

# Recognition Training
# Welcome message
print("Starting Recognition phase...")
core.wait(0.1)
show_message("Choose the correct image of the name on the screen. \n\n Click the mouse to start.")

# Define the image and text position
image_positions = [(-200, 200), (200, 200), (-200, -200), (200, -200)]

# Set the correct name to "word"
correct_name = sound.Sound(value = word_audio)
random.shuffle(selected_images)

# Prepare text and image component
image_stims = [visual.ImageStim(win, pos = pos, size = (250, 250)) for pos in image_positions]
feedback_display = visual.TextStim(win, text = "", font = 'Arial', height = 35, color = 'white', pos = (0, 0))

# Experiment
terminate_exp = False
event.clearEvents()

# Reset mouse position to center
mouse.setPos((0, -30))

for correct_image in selected_images:
    
    keys = event.getKeys()
    if "escape" in keys:
        core.quit()
    
    # Select 3 distractor images from images not shown earlier
    distractor_images = random.sample(unused_images, 3)
    
    # Create the final list for 4 images (1 shown + 3 not shown)
    image_paths = distractor_images + [correct_image]
    random.shuffle(image_paths)

    # Display images
    for stim, img_path in zip(image_stims, image_paths):
        stim.setImage(img_path)
        stim.draw()
        
    win.flip()
    core.wait(1)

    # Display an object name with four images
    name_audio = sound.Sound(word_audio)
    name_audio.play()
    for stim in image_stims:
        stim.draw()
        
    win.flip()

    # 6. Wait for participants to response by clicking
    responseTimer = core.Clock()
    responseTimer.reset()

    start_time = core.getTime()
    response_given = False
    selected_image = None

    while core.getTime() - start_time < 5:
        if "escape" in event.getKeys():
            break
            
        mouse_clicks = mouse.getPressed()
        if mouse_clicks[0]:
            for i, stim in enumerate(image_stims):
                if stim.contains(mouse):
                    selected_image = image_paths[i]
                    response_given = True
                    break
                    
        if response_given:
            break
                        
        core.wait(0.1)

    # Provide feedback
    if not response_given:
        feedback_display.setText("Too Slow")
    elif selected_image == correct_image:
        feedback_display.setText("Correct")
    else:
        feedback_display.setText("Incorrect")
        
    feedback_display.draw()
    win.flip()
    core.wait(1.5)

    # Blank screen
    win.flip()
    core.wait(1.5)

    # Reset the mouse position to the center
    mouse.setPos((0, -30))

    event.clearEvents()

# End message
show_message("Click the mouse to move to the next phase.")
print("Completed Recognition phase.")
core.wait(0.1)

# Initial Presentation
# Welcome message
print("Starting second Initial Phase...")

# Prepare text and image components
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0, 0))

# Experiment loop
mouse = event.Mouse(visible = False, win = win)

for image_path in selected_images:
    
    keys = event.getKeys()
    if "escape" in keys:
        break

    # Display an image with the name for 2 seconds
    image_display.image = image_path
    name_audio = sound.Sound(word_audio)
    name_audio.play()
    image_display.draw()
    win.flip()
    core.wait(2)

    # Blank space
    win.flip()
    core.wait(1.5)

# End message
mouse = event.Mouse(visible = True, win = win)
show_message("Click the mouse to move to the next phase.")
print ("Completed second Initial phase.")
core.wait(0.1)

event.clearEvents()

# Name learning
# Welcome message
print("Starting Naming phase...")
show_message("Choose the correct name for the image on the screen. \n\n Click the mouse to start.")

# Define the text position
number_positions = [(-200, 200), (200, 200), (200, -200), (-200, -200)]

# Prepare text and image components
number_stims= [visual.TextStim(win, text = f"({i+1})", font = "Arial", height = 35, color = "white", pos = number_positions[i]) for i in range(4)]
image_display = visual.ImageStim(win, image = None, size = (250, 250), pos = (0, 0))
feedback_display = visual.TextStim(win, text = "", font = 'Arial', height = 35, color = "white", pos = (0, 0))

# Experiment
terminate_exp = False
event.clearEvents()
random.shuffle(selected_images)

# Reset mouse position to center
mouse.setPos((0, 0))

nonword_sound = sound.Sound(nonword_audio)
correct_name = sound.Sound(word_audio)

for correct_image in selected_images:

    keys = event.getKeys()
    if "escape" in keys:
        break
    
    # Display an image
    image_display.image = correct_image
    image_display.draw()
    win.flip()
    core.wait(2)
    
    # Display numbers on the screen
    for stim in number_stims:
        stim.draw()
    
    image_display.draw()
    win.flip()
    
    # Shuffle the position of names and numbers for each trial
    distractor_names = [nonword_sound] * 3
    name_choices = distractor_names + [correct_name]
    random.shuffle(name_choices)
    
    # Ensure correct pairing of number to name
    number_to_name = {i: name_choices[i] for i in range(4)}

    # Listening phase and Wait for the response
    responseTimer = core.Clock()
    mouse.clickReset()
    
    # Enable mouse-clicking during playback
    response_given = False
    selected_number = None
    
    for i in range(4):
        # Flash the corresponding number
        for stim in number_stims:
            stim.setColor("white")
        
        number_stims[i].setColor("yellow")
        
        # Draw updated numbers and image
        for stim in number_stims:
            stim.draw()
        image_display.draw()
        win.flip()
        
        # Play audio
        name_choices[i].play()
        core.wait(1)
        
        # Allow mouse-click responses while audio is playing
        start_time = core.getTime()
        
        while core.getTime() - start_time < 1:
            mouse_clicks = mouse.getPressed()
            
            if mouse_clicks[0]:
                mouse_x, mouse_y = mouse.getPos()
                
                for j, stim in enumerate(number_stims):
                    stim_x, stim_y = stim.pos
                    box_width = stim.height * 3
                    box_height = stim.height
                    
                    new_width = box_width * 1.5
                    new_height = box_height * 1.5
                    
                    left_bound = stim_x - new_width / 2
                    right_bound = stim_x + new_width / 2
                    top_bound = stim_y + new_height / 2
                    bottom_bound = stim_y - new_height / 2
                    
                    if left_bound <= mouse_x <= right_bound and bottom_bound <= mouse_y <= top_bound:
                        selected_number = name_choices[i]
                        response_given = True
                        break
                        
                        # Stop audio immediately and exit the loop
                        name_choices[i].stop()
                        break
                    
            if response_given:
                break
        if response_given:
            break
                    
    # Reset the last stimulus after all audios are played
    for stim in number_stims:
        stim.setColor("white")
        stim.draw()
    image_display.draw()
    win.flip()
    
    # Response timewindow(5s) after last audio finishes
    if not response_given:
        timeout = 5
        start_time = core.getTime()
        while core.getTime() - start_time < timeout:
            buttons, times = mouse.getPressed(getTime = True)
            
            if buttons[0]:
                for i, stim in enumerate(number_stims):
                    if stim.contains(mouse):
                        selected_number = i
                        response_given = True
                        break
            if response_given:
                break
            core.wait(0.1)
            
    # Provide feedback
    if not response_given:
        feedback_display.setText("Too Slow")
    elif selected_number == correct_name:
        feedback_display.setText("Correct")
    else:
        feedback_display.setText("Incorrect")
        
    feedback_display.draw()
    win.flip()
    core.wait(1.5)

    # Blank screen
    win.flip()
    core.wait(1)

    # Reset mouse position to the center
    mouse.setPos((0, 0))

    event.clearEvents()

# Close the window after the experiment
print("Completed Name phase.")
mouse = event.Mouse(visible = False, win = win)

def show_message(text):
    msg = visual.TextStim(win, text = text, font = 'Arial', color = "white", height = 35, pos = (0, 0))
    msg.draw()
    win.flip()
    
    while True:
        keys = event.getKeys()
        if "space" in keys:
            break
        core.wait(0.1)

show_message("You've completed the practice for learning phases. \n\nYou can take a short break.\n\n After the break, press the space bar to start the Testing phase.")

# Testing phase
print("Starting Testing phase - Auditory Comprehension...")
show_message("[Practice - Testing Phase]\n Press LEFT arrow key if match, RIGHT arrow key if mismatch when \"?\" appears on the screen. \n\nPress the space bar to start.")

# Generate a balanced block of trials with randomized match/mismatch
def create_block():
    match_images = selected_images[:2]
    mismatch_images = selected_images[2:]
    
    match_trials = [{'name': word_audio, 'image': img, 'match': True} for img in match_images]
    mismatch_trials = [{'name': nonword_audio, 'image': img, 'match': False} for img in mismatch_images]
    
    # Combine and shuffle the block
    block_trials = match_trials + mismatch_trials
    random.shuffle(block_trials)
    
    return block_trials
    
# Prepare text and image components
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', height = 35, pos = (0, 0))
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0, 0))
response_wait = visual.TextStim(win, text = "?", font = 'Arial', color = 'yellow', height = 35, pos = (0, 0))

# Generate block trials
trials = create_block()

# Experiment loop
terminate_exp = False
event.clearEvents()

for trial in trials:
    if "escape" in event.getKeys(keyList = ["escape"]):
        terminate_exp = True
        break
    
    played_name = trial['name']
    displayed_image = trial['image']
    is_match = trial['match']
    
    # Each trial begins with a fixation cross (500ms)
    fixation_display.draw()
    win.flip()
    core.wait(.5)
    
    # Audio play with a fixation cross (200ms)
    name_audios = sound.Sound(played_name, stopTime = 0.9)
    name_audios.play()
    fixation_display.draw()
    win.flip()
    core.wait(.9)
    
    # Visual display of the object either matching or not matching that name
    image_display.setImage(displayed_image)
    image_display.draw()
    win.flip()
    core.wait(.2)
    
    # Blank screen (800ms)
    win.flip()
    core.wait(.8)
    
   # Response window (3000ms max)
    response_wait.draw()
    win.flip()
    event.clearEvents()

    responseTimer =  core.Clock()
    responseTimer.reset()
    response = None
    rt = None
                
    while responseTimer.getTime() < 3:
        # Check for early exit during the experiment
        keys = event.getKeys(keyList = ["escape", "left", "right"])
            
        if "escape" in keys:
            terminate_exp = True
            break 
                
        if "left" in keys:
            response = "match"
            rt = responseTimer.getTime()
            break
        elif "right" in keys:
            response = "mismatch"
            rt = responseTimer.getTime()
            break

    if terminate_exp:
        break

    # 1-sec blank screen
    win.flip()
    core.wait(1)
    
# End message
print("Completed Visual Comprehension Phase.")
show_message("Press the space bar to move to the next phase.")
core.wait(.1)    
    

# Spoken production
print("Starting Spoken Production...")
core.wait(0.1)
show_message("Speak the correct name aloud when \"?\" turns green.\n\n Press the space bar to start.")

# Prepare text and image component
fixation_display = visual.TextStim(win, text = "+", font = 'Arial', color = 'white', height = 35, pos = (0,0))
image_display = visual.ImageStim(win, image = None, size = [250, 250], pos = (0, 0))
response_wait = visual.TextStim(win, text = "?", font = 'Arial', color = 'white', height = 35, pos = (0,0))

# Define the folder path inside the save directory
output_folder_path = os.path.join(current_dir, "response")
folder_path = os.path.join(output_folder_path, "practice")
os.makedirs(folder_path, exist_ok = True)

# Record settings
fs = 44100
duration = 3

# Experiment loop
random.shuffle(selected_images)
counter = 1
terminate_exp = False

for image in selected_images:
    if terminate_exp:
        break
        
    # Display fixation cross
    fixation_display.draw()
    win.flip()
    core.wait(0.5)
    
    # Display the image (2000ms)
    image_display.image = correct_image
    image_display.draw()
    win.flip()
    core.wait(2)
    
    audio_filename = os.path.join(folder_path, f"practice_sp_{counter}.wav")

    
    # Wait for the response (3000ms) + record the voice
    # Set default color to white
    response_wait.color = 'white'
    response_wait.draw()
    win.flip()
    
    # Change color to green when recording starts
    response_wait.color = [-0.61, 0.61, -0.61]
    response_wait.draw()
    win.flip()
    
    # Start recording
    response_start = core.getTime()
    recording = sd.rec(int(duration* fs), samplerate = fs, channels = 1, dtype = "int16")
    sd.wait()
    response_end = core.getTime()
    
    sf.write(audio_filename, recording, fs)
    
    # Change color to red for 0.2 seconds after recording finishes
    response_wait.color = 'red'
    response_wait.draw()
    win.flip()
    core.wait(0.2)
    
    # Stop recording
    core.wait(3)
    
    # Blank space (1000ms)
    fixation_display.draw()
    win.flip()
    core.wait(1)
    
    # Increment the counter for the next file
    counter += 1
    
    event.clearEvents()

# End message
print("Completed Written Production Phase.")
show_message("You've completed all the practice for the testing phase.\n Press the space bar to exit.")

win.close()
core.quit()