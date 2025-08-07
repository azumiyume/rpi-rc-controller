import pygame

class GamepadHandler:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.pad = pygame.joystick.Joystick(0)
        self.pad.init()

    def get_event(self):
        pygame.event.pump()
        x_axis = self.pad.get_axis(0)
        y_axis = self.pad.get_axis(1)

        if y_axis < -0.5:
            return "FORWARD"
        elif y_axis > 0.5:
            return "BACKWARD"
        elif x_axis < -0.5:
            return "LEFT"
        elif x_axis > 0.5:
            return "RIGHT"
        elif self.pad.get_button(1):  # ○ボタン
            return "TOGGLE_MUSIC"
        elif self.pad.get_button(5):  # R1
            return "ACCELERATE"
        elif self.pad.get_button(4):  # L1
            return "DECELERATE"
        else:
            return "STOP"
