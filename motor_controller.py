import RPi.GPIO as GPIO

class MotorController:
    def __init__(self):
        self.PIN_A1 = 17
        self.PIN_A2 = 27
        self.PWM_PIN = 22

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN_A1, GPIO.OUT)
        GPIO.setup(self.PIN_A2, GPIO.OUT)
        GPIO.setup(self.PWM_PIN, GPIO.OUT)

        self.pwm = GPIO.PWM(self.PWM_PIN, 1000)
        self.pwm.start(0)

    def forward(self, speed):
        GPIO.output(self.PIN_A1, GPIO.HIGH)
        GPIO.output(self.PIN_A2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(speed)

    def backward(self, speed):
        GPIO.output(self.PIN_A1, GPIO.LOW)
        GPIO.output(self.PIN_A2, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(speed)

    def turn_left(self, speed):
        self.forward(speed)
        # 左だけちょっと止めるなど調整も可能

    def turn_right(self, speed):
        self.forward(speed)
        # 右だけちょっと止めるなど調整も可能

    def stop(self):
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.PIN_A1, GPIO.LOW)
        GPIO.output(self.PIN_A2, GPIO.LOW)
