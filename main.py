import time
from gamepad_handler import GamepadHandler
from motor_controller import MotorController
from audio_player import AudioPlayer

# 初期化
gamepad = GamepadHandler()
motor = MotorController()
audio = AudioPlayer("drive_music.mp3")

music_playing = False
speed = 50  # 初期スピード（0-100）

try:
    while True:
        event = gamepad.get_event()

        if event == "FORWARD":
            motor.forward(speed)
        elif event == "BACKWARD":
            motor.backward(speed)
        elif event == "LEFT":
            motor.turn_left(speed)
        elif event == "RIGHT":
            motor.turn_right(speed)
        elif event == "STOP":
            motor.stop()
        elif event == "TOGGLE_MUSIC":
            if music_playing:
                audio.stop()
            else:
                audio.play()
            music_playing = not music_playing
        elif event == "ACCELERATE":
            speed = min(speed + 10, 100)
        elif event == "DECELERATE":
            speed = max(speed - 10, 20)

        time.sleep(0.05)

except KeyboardInterrupt:
    motor.stop()
    audio.stop()
    print("終了しました")
