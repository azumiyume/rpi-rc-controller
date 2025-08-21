
# Raspberry Pi RC Car (2-wheel, TA7291P x2) — Gamepad Control

## Wiring (BCM numbers)
- Left motor (TA7291P #1): IN1=GPIO27 (physical 13), IN2=GPIO22 (physical 15)
- Right motor (TA7291P #2): IN1=GPIO23 (physical 16), IN2=GPIO24 (physical 18)
- Speed is controlled by PWM on one input while the other is LOW.

## Controls
- Left stick (X): steering (left/right)
- A button (hold): accelerate forward
- Y button (hold): accelerate backward
- Releasing all buttons: natural slow-down to stop
- Failsafe: if the gamepad isn't read for 1.5s, motors stop

## Pair your controller (Bluetooth)
On Raspberry Pi:
```bash
sudo apt update
sudo apt install -y python3-pygame joystick bluez bluez-tools
sudo systemctl enable --now bluetooth
bluetoothctl
# in bluetoothctl:
power on
agent on
default-agent
pairable on
discoverable on
scan on         # put your controller into pairing mode
# wait for MAC address XX:XX:XX:XX:XX:XX to appear
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
exit
```
Check it shows up as `/dev/input/js0`:
```bash
ls /dev/input/js0 && sudo jstest /dev/input/js0
```
If you're using a Switch-style pad and it misbehaves, try loading the kernel module:
```bash
sudo modprobe hid-nintendo
```

## Deploy from Windows and run on the Pi
1. Copy files to Pi (example):
   ```bash
   scp -r motor_controller.py gamepad_handler.py main.py requirements.txt pi@raspberrypi.local:~/rc_car/
   ```
2. SSH to the Pi:
   ```bash
   ssh pi@raspberrypi.local
   cd ~/rc_car
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   # (RPi.GPIO is typically preinstalled; if not: sudo apt install -y python3-rpi.gpio)
   python main.py
   ```

## Adjust button indices
If A/Y buttons don't match, run:
```bash
python gamepad_handler.py
```
and press buttons to see which indices toggle. Then update `A_BUTTON_IDX` / `Y_BUTTON_IDX` in `gamepad_handler.py`.

## Notes
- PWM frequency defaults to 1 kHz; increase if motors whine (e.g., 15–20 kHz).
- `MIN_DUTY` in `main.py` helps overcome stiction; tune for your motors.
- Keep some buttons unused for future features (music, mirror ball, etc.).
