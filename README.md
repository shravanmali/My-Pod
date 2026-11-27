# mypod

A retro, handcrafted DIY music player inspired by the classic Apple iPod, built with modern components, an IPS display, physical rotary scroll wheel with haptic feedback, and a layered wooden MDF body.

## Features
- **Display:** 1.69" 240x280 IPS color screen (ST7789)
- **Navigation:** Physical 360-degree rotary encoder with push-button select
- **Haptics & Audio:** Vibration motor pulse on every wheel tick + acoustic click
- **Audio Output:** Bluetooth wireless audio + 3.5mm wired headphone jack
- **Enclosure:** Layered 2.1mm MDF wood sandwich chassis (pocket sized)
- **Sensors:** LDR ambient light sensor for automatic screen dimming
- **Power:** Li-Po rechargeable battery with USB-C charging board and slide switch

## Project Roadmap
1. **Virtual UI & Simulator:** Build and test the 240x280 screen UI and rotary menu navigation in Python.
2. **ESP32-S3 Hardware Prototype:** Wire up the screen, encoder, haptics, and test controls on breadboard.
3. **MDF Wooden Enclosure:** Cut and layer the 6 sheets of 2.1mm MDF to form the pocket body.
4. **Raspberry Pi Zero 2 W Core & Custom PCB:** Integrate the final compute core, I2S DAC, and carrier PCB.
5. **Final Polish:** Assemble, varnish the wood, and load albums.

## Quick Start

### 1. Desktop Simulator
```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install pygame
.\.venv\Scripts\python.exe simulator.py
```
* **Controls:** Wheel / `Up`/`Down` = Scroll • `Enter`/`Space` = Select • `V` + Wheel = Volume • `S` + Wheel = Seek • `H` = Home • `R` = 1:1 Real Size • `Backspace` = Back

### 2. ESP32-S3 Hardware Prototype (MicroPython)
1. Wire the Waveshare 1.69" LCD and KY-040 encoder using [esp32/PINOUT.md](esp32/PINOUT.md).
2. Upload the firmware files and run (replace `COM6` with your port):
```bash
.\.venv\Scripts\mpremote.exe connect COM6 fs cp esp32/st7789_fb.py :st7789_fb.py + fs cp esp32/main.py :main.py + reset
```
