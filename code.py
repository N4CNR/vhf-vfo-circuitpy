# Copyright <2024> <N4CNR (Richard Neese) (n4cnr.ham@gmail.com)>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time
import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_st7735r import ST7735R
from adafruit_si5351 import SI5351
import digitalio
import rotaryio
import adafruit_debouncer
import microcontroller

"""ITU Regions and Frequency Bands"""
ITU_REGIONS = ["1", "2", "3"]
BANDS = ["2m", "6m"]
FREQUENCY_RANGES = {
    "1": {"2m": (144000000, 144500000), "6m": (50000000, 50400000)},
    "2": {"2m": (144000000, 144500000), "6m": (50000000, 50400000)},
    "3": {"2m": (144000000, 144500000), "6m": (50000000, 50400000)},
}

IF_FREQUENCY = 26994100  # Intermediate Frequency

STEPS = [100, 1000, 10000, 100000]  # Frequency steps in Hz
MODES = ["USB", "LSB"]  # Operational modes
DOUBLE_PRESS_INTERVAL = 0.5  # Time interval for double press detection in seconds

"""Initial state"""
current_region_index = 1
current_band_index = 0
current_region = ITU_REGIONS[current_region_index]
current_band = BANDS[current_band_index]
FREQUENCY_RANGE = FREQUENCY_RANGES[current_region][current_band]
current_frequency = FREQUENCY_RANGE[0]
DEFAULT_FREQUENCY = current_frequency

"""Release any displays that may be in use"""
displayio.release_displays()

"""Pin configuration for ST7735 TFT Display"""
tft_clk, tft_mosi, tft_reset = board.GP10, board.GP11, board.GP12
tft_dc, tft_cs = board.GP8, board.GP9

"""I2C configuration for SI5351 clock chip"""
sda, scl = board.GP4, board.GP5

"""Encoder and button configuration"""
enc_a, enc_b, enc_switch = board.GP13, board.GP14, board.GP15
ptt_btn, rit_enc_a, rit_enc_b, rit_enc_btn = (
    board.GP2,
    board.GP16,
    board.GP17,
    board.GP18,
)
step_switch, itu_button, band_button = board.GP3, board.GP6, board.GP7

"""Setup I2C and SPI buses"""
i2c = busio.I2C(scl, sda)
spi = busio.SPI(clock=tft_clk, MOSI=tft_mosi)

"""Setup display"""
display_bus = displayio.FourWire(
    spi, command=tft_dc, chip_select=tft_cs, reset=tft_reset
)
display = ST7735R(display_bus, width=160, height=128, rotation=90)

"""Setup Si5351 clock generator"""
si5351 = SI5351(i2c)
# Configure PLL with initial frequency for 144 MHz
si5351.pll_a.configure_integer(24)

"""Setup display groups and elements"""
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(160, 128, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000  # Black background
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

text_area = label.Label(
    terminalio.FONT, scale=1, text="Initializing...", color=0xFFFFFF, x=10, y=20
)
splash.append(text_area)

transmitting_label = label.Label(
    terminalio.FONT, scale=1, text="Transmitting", color=0xFFFF00, x=50, y=95
)
splash.append(transmitting_label)
transmitting_label.hidden = True  # Initially hidden

"""Setup S-meter"""
smeter_text = label.Label(
    terminalio.FONT, scale=1, text="S:", color=0x00FF00, x=20, y=5
)
splash.append(smeter_text)

smeter_bar = displayio.Bitmap(100, 10, 10)  # Create a bar graph
smeter_palette = displayio.Palette(10)
for i in range(10):
    smeter_palette[i] = (i * 28, 255 - i * 28, 0)  # Gradient from green to red
smeter_sprite = displayio.TileGrid(smeter_bar, pixel_shader=smeter_palette, x=50, y=0)
splash.append(smeter_sprite)

"""Setup Blue Transmitting Bar"""
blue_bar_bitmap = displayio.Bitmap(160, 10, 1)
blue_bar_palette = displayio.Palette(1)
blue_bar_palette[0] = 0xFF0000
blue_bar = displayio.TileGrid(
    blue_bar_bitmap, pixel_shader=blue_bar_palette, x=0, y=115
)
splash.append(blue_bar)
blue_bar.hidden = True  # Initially hidden

"""Encoder and button setup"""
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

itu_button = digitalio.DigitalInOut(itu_button)
itu_button.direction = digitalio.Direction.INPUT
itu_button.pull = digitalio.Pull.UP

band_button = digitalio.DigitalInOut(band_button)
band_button.direction = digitalio.Direction.INPUT
band_button.pull = digitalio.Pull.UP

"""Configure Debouncers"""
freq_switch_debounced = adafruit_debouncer.Debouncer(freq_switch)
ptt_button_debounced = adafruit_debouncer.Debouncer(ptt_button)
rit_switch_debounced = adafruit_debouncer.Debouncer(rit_switch)
step_button_debounced = adafruit_debouncer.Debouncer(step_button)
itu_button_debounced = adafruit_debouncer.Debouncer(itu_button)
band_button_debounced = adafruit_debouncer.Debouncer(band_button)

"""State variables"""
current_step_index = 2  # Default step to 10000 Hz
current_mode = MODES[0]  # Defaults to USB
rit_enabled = False  # RIT Disabled by default
rit_value = 0  # Default RIT to 0 when Disabled
transmit_mode = False  # Track the transmit mode


def initialize_nvm():
    """Initialize NVM with default settings if no settings are found."""
    global current_region_index, current_band_index, current_frequency
    nvm_data = microcontroller.nvm[:8]
    if nvm_data == bytes([0xFF] * 8):  # NVM is empty
        save_to_nvm()
    else:
        current_region_index = nvm_data[0]
        current_band_index = nvm_data[1]
        current_frequency = int.from_bytes(nvm_data[2:6], 'big')
        if current_region_index >= len(ITU_REGIONS):
            current_region_index = 0
        if current_band_index >= len(BANDS):
            current_band_index = 0
        FREQUENCY_RANGE = FREQUENCY_RANGES[ITU_REGIONS[current_region_index]][BANDS[current_band_index]]


def save_to_nvm():
    """Save the current settings to NVM."""
    data = bytearray(8)
    data[0] = current_region_index
    data[1] = current_band_index
    data[2:6] = current_frequency.to_bytes(4, 'big')
    microcontroller.nvm[:8] = data


def update_display():
    """Update the display with the current frequency, mode, and other parameters."""
    display_frequency = (
        current_frequency + rit_value if rit_enabled else current_frequency
    )
    text = f" \n"
    text += f"     {current_mode} {display_frequency / 1000:.1f} MHz\n"
    text += f" \n"
    text += f" Step: {STEPS[current_step_index]} Hz\n"
    text += f" RIT: {'ON' if rit_enabled else 'OFF'} {rit_value / 1000:.1f} kHz \n"
    text += " \n"
    text += f"Band:{current_band}            ITU:{current_region} \n"
    text_area.text = text
    transmitting_label.hidden = ptt_button.value  # Show transmitting if PTT is pressed
    blue_bar.hidden = ptt_button.value  # Show red bar if PTT is pressed


def set_frequency(frequency):
    """Set the frequency on the Si5351."""
    pll_frequency = frequency + IF_FREQUENCY
    # Configure the PLL and Clock outputs
    si5351.pll_a.configure_integer(pll_frequency // 8000000)
    si5351.clock_0.configure_integer(si5351.pll_a, pll_frequency // 8000000)
    si5351.clock_1.configure_integer(si5351.pll_a, pll_frequency // 8000000)
    si5351.outputs_enabled = True


def change_mode():
    """Change the mode between USB and LSB."""
    global current_mode
    current_mode = MODES[(MODES.index(current_mode) + 1) % len(MODES)]
    save_to_nvm()


def change_step():
    """Cycle through the frequency steps."""
    global current_step_index
    current_step_index = (current_step_index + 1) % len(STEPS)


def change_itu_region():
    """Cycle through the ITU regions."""
    global current_region_index, current_region, FREQUENCY_RANGE, current_frequency
    current_region_index = (current_region_index + 1) % len(ITU_REGIONS)
    current_region = ITU_REGIONS[current_region_index]
    FREQUENCY_RANGE = FREQUENCY_RANGES[current_region][current_band]
    current_frequency = FREQUENCY_RANGE[0]
    set_frequency(current_frequency)
    save_to_nvm()


def change_band():
    """Cycle through the frequency bands."""
    global current_band_index, current_band, FREQUENCY_RANGE, current_frequency
    current_band_index = (current_band_index + 1) % len(BANDS)
    current_band = BANDS[current_band_index]
    FREQUENCY_RANGE = FREQUENCY_RANGES[current_region][current_band]
    current_frequency = FREQUENCY_RANGE[0]
    set_frequency(current_frequency)
    save_to_nvm()


def handle_freq_encoder():
    """Handle frequency encoder changes."""
    global current_frequency
    position = freq_encoder.position
    if position != 0:
        step = STEPS[current_step_index]
        current_frequency += position * step
        current_frequency = max(
            min(current_frequency, FREQUENCY_RANGE[1]), FREQUENCY_RANGE[0]
        )
        freq_encoder.position = 0
        set_frequency(current_frequency)
        save_to_nvm()


def handle_rit_encoder():
    """Handle RIT encoder changes."""
    global rit_value
    position = rit_encoder.position
    if rit_enabled and position != 0 and not transmit_mode:
        rit_value += position * 100
        rit_value = max(min(rit_value, 9900), -9900)
        rit_encoder.position = 0


def update_smeter(level):
    """Update the S-meter display."""
    level = min(max(level, 0), 9)  # Ensure level is between 0 and 9
    smeter_text.text = f"S: {level}"
    smeter_text.color = (level * 28, 255 - level * 28, 0)
    for x in range(100):
        smeter_bar[x, 0] = min(x // 10, level)  # Update bar graph


# Main loop
initialize_nvm()
while True:
    """Update debouncers"""
    freq_switch_debounced.update()
    rit_switch_debounced.update()
    step_button_debounced.update()
    ptt_button_debounced.update()
    itu_button_debounced.update()
    band_button_debounced.update()

    """Handle encoder and button inputs"""
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

    """Simulate S-meter level for testing purposes (random value between 0 and 9)"""
    smeter_level = time.monotonic() % 10
    update_smeter(int(smeter_level))

    update_display()
    time.sleep(0.1)  # Small delay to avoid excessive CPU usage
