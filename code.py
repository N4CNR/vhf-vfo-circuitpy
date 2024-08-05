# Copyright <2024> <N4CNR (Richard Neese) (n4cnr.ham@gmail.com)>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), 
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# CircutPython 9

# Designing a VHF VFO 6M or 2m
# CircuitPython on a Raspberry Pi Pico with an SI5351 and an ST7735 
# SPI display involves several components and functionalities. 
# Below is a step-by-step implementation plan, followed by the complete code.

# Implementation Plan:
# Setup and Initialization:

# Initialize the SPI display (ST7735).
# Initialize the SI5351.
# Set up the encoders and buttons.
# Display Functionality:

# Display the current frequency, mode (USB/LSB), RIT status, and step size.
# Encoders and Button Handling:

# Handle frequency changes with the main encoder.
# Handle RIT changes with the RIT encoder.
# Change frequency steps with the step button.
# Toggle RIT with the RIT encoder button.
# Change mode (USB/LSB) with the main encoder button.
# Board Raspi Pico, flash screen red if ptt active

# Continuously update the display based on user interactions.
# Update the SI5351 frequency output based on the current 

import time
import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_ili9341 import ILI9341
from adafruit_si5351 import SI5351
import digitalio
import rotaryio
import adafruit_debouncer

# ITU Regions and Frequency Bands
ITU_REGIONS = ['1', '2', '3']
BANDS = ['2m', '6m']
FREQUENCY_RANGES = {
    '1': {
        '2m': (144000000, 144500000),
        '6m': (50000000, 50400000)
    },
    '2': {
        '2m': (144000000, 144500000),
        '6m': (50000000, 50400000)
    },
    '3': {
        '2m': (144000000, 144500000),
        '6m': (50000000, 50400000)
    }
}

# si5351 or si570
IF_FREQUENCY = 26994100

# Initial state
current_region_index = 1
current_band_index = 0
current_region = ITU_REGIONS[current_region_index]
current_band = BANDS[current_band_index]
FREQUENCY_RANGE = FREQUENCY_RANGES[current_region][current_band]
current_frequency = FREQUENCY_RANGE[0]
DEFAULT_FREQUENCY = current_frequency

# Release any displays that may be in use
displayio.release_displays()

# Pin configuration for ILI9341 TFT Display
tft_clk = board.GP10  # sclk
tft_mosi = board.GP11  # sda
tft_reset = board.GP12  # reset
tft_dc = board.GP8  # a0
tft_cs = board.GP9  # cs

# Required for SI5351 or SI570 in future
sda = board.GP4
scl = board.GP5

# Frequency encoder +/- and select mode USB/LSB Functional
enc_a = board.GP13
enc_b = board.GP14
enc_switch = board.GP15

# Used to display Transmitting on screen
ptt_btn = board.GP2

# RIT +/- Functional
rit_enc_a = board.GP16
rit_enc_b = board.GP17
rit_enc_btn = board.GP18

# Used for button to cycle through Steps
step_switch = board.GP3

# Button to change ITU region
itu_button_pin = board.GP6  # Assign a suitable GPIO pin

# Button to change band
band_button_pin = board.GP7  # Assign a suitable GPIO pin

STEPS = [100, 1000, 10000, 100000]
MODES = ['USB', 'LSB']  # CW to be added in future
DOUBLE_PRESS_INTERVAL = 0.5  # Time interval for double press detection in seconds

# I2C setup used for SI570 or SI5351 clock chips
i2c = busio.I2C(scl, sda)

# SPI Display Pin Setup
spi = busio.SPI(clock=tft_clk, MOSI=tft_mosi)
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset)
display = ILI9341(display_bus, width=320, height=240)

# Si5351 setup
si5351 = SI5351(i2c)

# Display setup
splash = displayio.Group()
display.root_group = (splash)
color_bitmap = displayio.Bitmap(320, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000  # Black background

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

text_area = label.Label(terminalio.FONT, scale=2, text="Initializing...", color=0xFFFFFF, x=10, y=20)
splash.append(text_area)

# Flashes bottom of screen above red bar when PTT is activated
transmitting_label = label.Label(terminalio.FONT, scale=2, text="Transmitting", color=0xFFFF00, x=100, y=210)
splash.append(transmitting_label)
transmitting_label.hidden = True  # Initially hidden

# S-meter setup - repositioned in the upper left corner
smeter_text = label.Label(terminalio.FONT, scale=2, text="S:", color=0x00FF00, x=10, y=10)
splash.append(smeter_text)

# S-meter bar graph
smeter_bar_palette = displayio.Palette(2)
smeter_bar_palette[0] = 0x000000  # Background color
smeter_bar_palette[1] = 0x00FF00  # Bar color

smeter_bar_bitmap = displayio.Bitmap(90, 20, 2)
smeter_bar = displayio.TileGrid(smeter_bar_bitmap, pixel_shader=smeter_bar_palette, x=50, y=10)
splash.append(smeter_bar)

# Add red bar at the bottom Flashes when PTT is activated
red_bar_bitmap = displayio.Bitmap(320, 20, 1)
red_bar_palette = displayio.Palette(1)
red_bar_palette[0] = 0xFF0000
red_bar = displayio.TileGrid(red_bar_bitmap, pixel_shader=red_bar_palette, x=0, y=220)
splash.append(red_bar)
red_bar.hidden = True  # Initially hidden

# Encoders setup
freq_encoder = rotaryio.IncrementalEncoder(enc_a, enc_b)
freq_switch = digitalio.DigitalInOut(enc_switch)
freq_switch.direction = digitalio.Direction.INPUT
freq_switch.pull = digitalio.Pull.UP

ptt_button = digitalio.DigitalInOut(ptt_btn)
ptt_button.direction = digitalio.Direction.INPUT
ptt_button.pull = digitalio.Pull.UP

rit_encoder = rotaryio.IncrementalEncoder(rit_enc_a, rit_enc_b)
rit_switch = digitalio.DigitalInOut(rit_enc_btn)
rit_switch.direction = digitalio.Direction.INPUT
rit_switch.pull = digitalio.Pull.UP

step_button = digitalio.DigitalInOut(step_switch)
step_button.direction = digitalio.Direction.INPUT
step_button.pull = digitalio.Pull.UP

itu_button = digitalio.DigitalInOut(itu_button_pin)
itu_button.direction = digitalio.Direction.INPUT
itu_button.pull = digitalio.Pull.UP

band_button = digitalio.DigitalInOut(band_button_pin)
band_button.direction = digitalio.Direction.INPUT
band_button.pull = digitalio.Pull.UP

# Debouncers
freq_switch_debounced = adafruit_debouncer.Debouncer(freq_switch)
ptt_button_debounced = adafruit_debouncer.Debouncer(ptt_button)
rit_switch_debounced = adafruit_debouncer.Debouncer(rit_switch)
step_button_debounced = adafruit_debouncer.Debouncer(step_button)
itu_button_debounced = adafruit_debouncer.Debouncer(itu_button)
band_button_debounced = adafruit_debouncer.Debouncer(band_button)

# Initial state
current_frequency = DEFAULT_FREQUENCY
current_step_index = 2  # Default step to 10000 Hz
current_mode = MODES[0] # Defaults to USB
rit_enabled = False # Rit Disabled by default
rit_value = 0 # Default rit to 0 when Disabled AKA Reset Rit
transmit_mode = False # Track the transmit mode

def update_display():
    display_frequency = current_frequency + rit_value if rit_enabled else current_frequency
    text = f" \n"
    text += " \n"   
    text += f"     {current_mode} {display_frequency / 1000:.1f} MHz\n"
    text += f" \n"
    text += f" Step: {STEPS[current_step_index]} Hz\n"
    text += f" RIT: {'ON' if rit_enabled else 'OFF'} {rit_value / 1000:.1f} kHz \n"
    text += " \n"
    text += f" Band: {current_band}   ITU: {current_region} \n"
    text_area.text = text
    transmitting_label.hidden = ptt_button.value  # Show transmitting if PTT is pressed
    red_bar.hidden = ptt_button.value  # Show red bar if PTT is pressed

def set_frequency(frequency):
    pll_frequency = frequency + IF_FREQUENCY # Add logic to set the frequency on the Si5351

def change_mode():
    global current_mode
    current_mode = MODES[(MODES.index(current_mode) + 1) % len(MODES)]

def change_step():
    global current_step_index
    current_step_index = (current_step_index + 1) % len(STEPS)

def change_itu_region():
    global current_region_index, current_region, FREQUENCY_RANGE, current_frequency
    current_region_index = (current_region_index + 1) % len(ITU_REGIONS)
    current_region = ITU_REGIONS[current_region_index]
    FREQUENCY_RANGE = FREQUENCY_RANGES[current_region][current_band]
    current_frequency = FREQUENCY_RANGE[0]
    set_frequency(current_frequency)

def change_band():
    global current_band_index, current_band, FREQUENCY_RANGE, current_frequency
    current_band_index = (current_band_index + 1) % len(BANDS)
    current_band = BANDS[current_band_index]
    FREQUENCY_RANGE = FREQUENCY_RANGES[current_region][current_band]
    current_frequency = FREQUENCY_RANGE[0]
    set_frequency(current_frequency)

def handle_freq_encoder():
    global current_frequency
    position = freq_encoder.position
    if position != 0:
        step = STEPS[current_step_index]
        current_frequency += position * step
        if current_frequency < FREQUENCY_RANGE[0]:
            current_frequency = FREQUENCY_RANGE[0]
        if current_frequency > FREQUENCY_RANGE[1]:
            current_frequency = FREQUENCY_RANGE[1]
        freq_encoder.position = 0
        set_frequency(current_frequency)

def handle_rit_encoder():
    global rit_value
    position = rit_encoder.position
    if rit_enabled and position != 0 and not transmit_mode:
        rit_value += position * 100
        if rit_value < -9900:
            rit_value = -9900
        if rit_value > 9900:
            rit_value = 9900
        rit_encoder.position = 0

def update_smeter(level):
    # Update the S-meter display
    level = min(max(level, 0), 9)  # Ensure level is between 0 and 9
    smeter_text.text = f"S: {level}"
    for i in range(90):
        for j in range(20):
            smeter_bar_bitmap[i, j] = 1 if i < level * 10 else 0

# Main loop
while True:
    freq_switch_debounced.update()
    rit_switch_debounced.update()
    step_button_debounced.update()
    ptt_button_debounced.update()
    itu_button_debounced.update()
    band_button_debounced.update()

    handle_freq_encoder()
    handle_rit_encoder()

    if ptt_button_debounced.fell:
        transmit_mode = True
    if ptt_button_debounced.rose:
        transmit_mode = False

    if freq_switch_debounced.fell:
        change_mode()

    if rit_switch_debounced.fell:
        rit_enabled = not rit_enabled
        if not rit_enabled:
            rit_value = 0

    if step_button_debounced.fell:
        change_step()

    if itu_button_debounced.fell:
        change_itu_region()

    if band_button_debounced.fell:
        change_band()

    # Simulate S-meter level for testing purposes (random value between 0 and 9)
    smeter_level = time.monotonic() % 10
    update_smeter(int(smeter_level))

    update_display()
    time.sleep(0.1)  # Small delay to avoid excessive CPU usage
