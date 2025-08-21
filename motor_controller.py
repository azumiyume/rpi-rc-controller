
import RPi.GPIO as GPIO
from typing import Tuple

class MotorController:
    """
    Dual DC motor controller for two TA7291P drivers (2-wheel drive).
    Each motor uses 2 GPIO pins (IN1, IN2). Speed is controlled by PWM
    on one of the IN pins while the other is held LOW, and direction is
    determined by which pin receives PWM.
    """
    def __init__(
        self,
        left_pins: Tuple[int, int] = (27, 22),   # Physical pins 13(GPIO27),15(GPIO22)
        right_pins: Tuple[int, int] = (23, 24),  # Physical pins 16(GPIO23),18(GPIO24)
        pwm_freq: int = 1000
    ) -> None:
        self.left_in1, self.left_in2 = left_pins
        self.right_in1, self.right_in2 = right_pins
        self.freq = pwm_freq

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in (self.left_in1, self.left_in2, self.right_in1, self.right_in2):
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        # Software PWM on each IN pin so we can drive either direction with PWM
        self.pwm_left_in1 = GPIO.PWM(self.left_in1, self.freq)
        self.pwm_left_in2 = GPIO.PWM(self.left_in2, self.freq)
        self.pwm_right_in1 = GPIO.PWM(self.right_in1, self.freq)
        self.pwm_right_in2 = GPIO.PWM(self.right_in2, self.freq)

        for pwm in (self.pwm_left_in1, self.pwm_left_in2, self.pwm_right_in1, self.pwm_right_in2):
            pwm.start(0.0)

    def _apply_channel(self, speed_percent: float, pwm_pos, pwm_neg) -> None:
        """
        Drive a single motor channel.
        speed_percent: -100..100 (sign = direction, magnitude = duty)
        """
        # Clamp
        if speed_percent > 100.0:
            speed_percent = 100.0
        elif speed_percent < -100.0:
            speed_percent = -100.0

        if speed_percent > 0:
            # Forward: positive pin PWM, negative pin LOW
            pwm_neg.ChangeDutyCycle(0.0)
            pwm_pos.ChangeDutyCycle(speed_percent)
        elif speed_percent < 0:
            # Reverse: negative pin PWM, positive pin LOW
            pwm_pos.ChangeDutyCycle(0.0)
            pwm_neg.ChangeDutyCycle(abs(speed_percent))
        else:
            # Stop: both LOW
            pwm_pos.ChangeDutyCycle(0.0)
            pwm_neg.ChangeDutyCycle(0.0)

    def drive(self, left_percent: float, right_percent: float) -> None:
        """Set left/right motor speeds (-100..100)."""
        self._apply_channel(left_percent, self.pwm_left_in1, self.pwm_left_in2)
        self._apply_channel(right_percent, self.pwm_right_in1, self.pwm_right_in2)

    def stop(self) -> None:
        self.drive(0.0, 0.0)

    def cleanup(self) -> None:
        try:
            self.stop()
        finally:
            for pwm in (self.pwm_left_in1, self.pwm_left_in2, self.pwm_right_in1, self.pwm_right_in2):
                pwm.stop()
            GPIO.cleanup()

    def __del__(self):
        # Best-effort cleanup
        try:
            self.cleanup()
        except Exception:
            pass
