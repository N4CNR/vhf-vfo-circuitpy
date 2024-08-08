# VHF VFO for CircuitPython on Raspberry Pi Pico
##### Copyright (C) 2024 Richard Neese (N4CNR)
Contact: n4cnr.ham@gmail.com



## Description:
 Designing a VHF VFO (Variable Frequency Oscillator) for 6M or 2M bands using CircuitPython on a Raspberry Pi Pico with an SI5351 frequency generator and an ST7735 SPI display. This project involves setting up components and handling various functionalities such as frequency changes, mode switching, and user interface through encoders and buttons.

## Implementation Plan:
### 1. Setup and Initialization:
- Initialize the SPI display (ST7735).
- Initialize the SI5351 frequency generator.
- Set up encoders and buttons.

## 2. Display Functionality:
- Display the current frequency, mode (USB/LSB), RIT status, and step size.

## 3. Encoders and Button Handling:
- **Main encoder:** Handle frequency changes.
- **RIT encoder:** Handle RIT (Receiver Incremental Tuning) changes.
- **Step button:** Change frequency steps.
- **RIT encoder button:** Toggle RIT.
- **Main encoder button:** Change mode (USB/LSB).
- Flash the screen red if PTT (Push-to-Talk) is active.

## 4. Continuous Update:
- Continuously update the display and the SI5351 output based on user interactions.

# Parts Needed:
### 1. Raspberry Pi Pico: [Product 4883](https://www.adafruit.com/product/4883) or [Product 5525](https://www.adafruit.com/product/5525)
### 2. SI5351 Breakout Board: [Product 2045](https://www.adafruit.com/product/2045)
### 3. KY-040 Rotary Encoder Module Knob with Push Button
### 4. LCD Display: [Product 358](https://www.adafruit.com/product/358)
### 5. Breakout Breadboard: [Example on eBay](https://www.ebay.com/itm/203042162648)
### 6. Additional buttons for changing modes

# *Instructions:*
1. Download the latest CircuitPython for Raspberry Pi Pico: https://circuitpython.org/board/raspberry_pi_pico/

3. Copy the UF2 file to the Raspberry Pi Pico.

# Additional Notes:
#### - The main encoder also changes the mode (USB/LSB).
#### - The button on the RIT encoder toggles RIT.
#### - A button is needed for step/region/band selection (band selection is for 2M/6M operation).

# License
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

- The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Contributing:
Create a pull request or send us an email (as specified above) and we will do our best to get back to you.
