# vhf-vfo-circuitpy
 vhf vfo wtiten in circuitpython for raspi pi pico
 
 
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
