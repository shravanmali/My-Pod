# My-Pod Hardware Pinout (ESP32-S3-WROOM-1 N16R8)

> **Board:** ESP32-S3-WROOM-1 N16R8 (16MB Flash, 8MB Octal PSRAM, Dual USB-C)  
> **Important:** Do **NOT** use **GPIO 26–37** (reserved for internal Flash/Octal PSRAM) or **GPIO 19–20** (USB-OTG).

---

## 1. Waveshare 1.69" ST7789V2 LCD (240x280)

| LCD Pin | ESP32-S3 Pin | Notes |
|---|---|---|
| `VCC` | `3V3` | **3.3V only** |
| `GND` | `GND` | Common ground |
| `DIN` (MOSI) | `GPIO 11` | SPI2 MOSI |
| `CLK` (SCK) | `GPIO 12` | SPI2 Clock |
| `CS` | `GPIO 10` | Chip Select |
| `DC` | `GPIO 9` | Data / Command |
| `RST` | `GPIO 14` | Display Reset |
| `BL` | `GPIO 13` | Backlight (PWM for dimming) |

---

## 2. KY-040 Rotary Encoder

| KY-040 Pin | ESP32-S3 Pin | Notes |
|---|---|---|
| `+` | `3V3` | **Use 3.3V** (never 5V on ESP32 GPIO) |
| `GND` | `GND` | Common ground |
| `CLK` | `GPIO 4` | Encoder A |
| `DT` | `GPIO 5` | Encoder B |
| `SW` | `GPIO 6` | Center click (active LOW) |

---

## 3. Bezel Action Buttons (Active LOW, Internal Pull-Up)

| Button | ESP32-S3 Pin | Other Leg |
|---|---|---|
| `VOL` (Hold + Wheel) | `GPIO 15` | `GND` |
| `SEEK` (Hold + Wheel) | `GPIO 16` | `GND` |
| `HOME` (Jump Home) | `GPIO 17` | `GND` |

---

## 4. Feedback & Sensors

| Component | ESP32-S3 Pin | Notes |
|---|---|---|
| **15mm Piezo Buzzer (`+`)** | `GPIO 7` | PWM click tone (`-` to `GND`) |
| **5mm LDR Sensor** | `GPIO 1` | ADC1_CH0 (with 10kΩ resistor divider) |
| **1027 Coin Motor** | `GPIO 8` *(via transistor)* | **Never connect directly to GPIO** |
