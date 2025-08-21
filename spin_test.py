# spin_test.py
import time, RPi.GPIO as GPIO
LEFT_IN1, LEFT_IN2 = 27, 22   # 物理13,15
RIGHT_IN1, RIGHT_IN2 = 23, 24 # 物理16,18

GPIO.setmode(GPIO.BCM)
for p in (LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2):
    GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)

pL1 = GPIO.PWM(LEFT_IN1, 1000); pL2 = GPIO.PWM(LEFT_IN2, 1000)
pR1 = GPIO.PWM(RIGHT_IN1, 1000); pR2 = GPIO.PWM(RIGHT_IN2, 1000)
for p in (pL1,pL2,pR1,pR2): p.start(0)

try:
    print("LEFT FWD 50%")
    pL2.ChangeDutyCycle(0); pL1.ChangeDutyCycle(50)  # 左前進
    time.sleep(2)
    print("LEFT REV 50%")
    pL1.ChangeDutyCycle(0); pL2.ChangeDutyCycle(50)  # 左後退
    time.sleep(2)

    print("RIGHT FWD 50%")
    pR2.ChangeDutyCycle(0); pR1.ChangeDutyCycle(50)  # 右前進
    time.sleep(2)
    print("RIGHT REV 50%")
    pR1.ChangeDutyCycle(0); pR2.ChangeDutyCycle(50)  # 右後退
    time.sleep(2)
finally:
    for p in (pL1,pL2,pR1,pR2): p.stop()
    GPIO.cleanup()
    print("DONE")
