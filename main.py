
import time
from motor_controller import MotorController
from gamepad_handler import GamepadHandler

# ===== Tunables =====
LOOP_HZ = 50.0
ACCEL_PER_SEC = 0.9     # throttle increase rate per second when A is held
BRAKE_PER_SEC = 1.2     # throttle decrease rate per second when Y is held
DRAG_PER_SEC = 1.0      # throttle natural decay toward 0 when no button held
TURN_GAIN = 0.8         # how strongly turn mixes into wheel speeds
MIN_DUTY = 25.0         # minimum duty to overcome stiction when moving (0..100)
MAX_DUTY = 100.0        # clamp
SAFETY_TIMEOUT = 1.5    # seconds since last pad read => stop

def mix(throttle: float, turn: float) -> tuple[float, float]:
    """
    Differential mixing:
      left  = throttle + turn*TURN_GAIN
      right = throttle - turn*TURN_GAIN
    Clamp to -1..1
    """
    l = throttle + turn * TURN_GAIN
    r = throttle - turn * TURN_GAIN
    l = max(-1.0, min(1.0, l))
    r = max(-1.0, min(1.0, r))
    return l, r

def to_duty(x: float) -> float:
    """Convert -1..1 speed to -100..100 duty with MIN_DUTY floor when moving."""
    if x == 0.0:
        return 0.0
    sign = 1.0 if x > 0 else -1.0
    duty = abs(x) * MAX_DUTY
    if duty < MIN_DUTY:
        duty = MIN_DUTY
    return sign * min(duty, MAX_DUTY)

def main():
    motor = MotorController(
        left_pins=(27, 22),   # Physical 13,15
        right_pins=(23, 24),  # Physical 16,18
        pwm_freq=1000
    )
    pad = GamepadHandler()

    if pad.pad is None:
        print("⚠️  No gamepad detected. Pair/connect your controller, then try again.")
        return

    throttle = 0.0  # -1..1
    last_time = time.monotonic()
    last_pad_time = last_time

    try:
        while True:
            now = time.monotonic()
            dt = now - last_time
            last_time = now

            st = pad.read()
            if st.connected:
                last_pad_time = now

            # Update throttle based on A/Y
            if st.a_pressed:
                throttle += ACCEL_PER_SEC * dt
            elif st.y_pressed:
                throttle -= BRAKE_PER_SEC * dt
            else:
                # natural decay toward 0 (coast)
                if throttle > 0:
                    throttle = max(0.0, throttle - DRAG_PER_SEC * dt)
                elif throttle < 0:
                    throttle = min(0.0, throttle + DRAG_PER_SEC * dt)

            # Clamp
            throttle = max(-1.0, min(1.0, throttle))

            # Safety timeout
            if now - last_pad_time > SAFETY_TIMEOUT:
                motor.stop()
                throttle = 0.0
                time.sleep(1.0 / LOOP_HZ)
                continue

            # Differential mixing
            left_norm, right_norm = mix(throttle, st.turn)

            # Convert to duty cycle
            left_dc = to_duty(left_norm)
            right_dc = to_duty(right_norm)

            motor.drive(left_dc, right_dc)

            time.sleep(max(0.0, 1.0 / LOOP_HZ - (time.monotonic() - now)))
    except KeyboardInterrupt:
        pass
    finally:
        motor.cleanup()

if __name__ == "__main__":
    main()
