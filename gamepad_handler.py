
import os
import pygame
from dataclasses import dataclass

# Allow pygame to init without a display (headless SSH)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

DEADZONE = 0.15  # ignore tiny stick noise

@dataclass
class PadState:
    turn: float          # -1..1 (left stick X)
    a_pressed: bool
    y_pressed: bool
    connected: bool

class GamepadHandler:
    """
    Pygame-based gamepad reader.
    Defaults target a Switch-like controller:
      - A button index tends to be 1
      - Y button index tends to be 2
    If your controller mapping differs, tweak A_BUTTON_IDX / Y_BUTTON_IDX below
    or run this file directly to print button indices.
    """
    # Default mapping suitable for many Switch-style pads on Linux
    A_BUTTON_IDX = 1
    Y_BUTTON_IDX = 2
    # Axis indices for left stick (common layout)
    AXIS_LEFT_X = 0
    AXIS_LEFT_Y = 1

    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.pad = None
        if pygame.joystick.get_count() > 0:
            self.pad = pygame.joystick.Joystick(0)
            self.pad.init()

    def read(self) -> PadState:
        if self.pad is None:
            return PadState(turn=0.0, a_pressed=False, y_pressed=False, connected=False)

        pygame.event.pump()

        # Left stick X for steering
        turn = 0.0
        try:
            turn = self.pad.get_axis(self.AXIS_LEFT_X)
        except Exception:
            turn = 0.0

        # Deadzone
        if abs(turn) < DEADZONE:
            turn = 0.0

        def btn(idx: int) -> bool:
            try:
                return bool(self.pad.get_button(idx))
            except Exception:
                return False

        a_pressed = btn(self.A_BUTTON_IDX)
        y_pressed = btn(self.Y_BUTTON_IDX)

        return PadState(turn=float(turn), a_pressed=a_pressed, y_pressed=y_pressed, connected=True)

if __name__ == "__main__":
    # Simple tester to find your A/Y indices.
    import time
    gh = GamepadHandler()
    if gh.pad is None:
        print("No gamepad detected. Pair/connect your controller and try again.")
        raise SystemExit(1)
    print("Press buttons; Ctrl+C to exit. Observing A idx=%d, Y idx=%d"
          % (GamepadHandler.A_BUTTON_IDX, GamepadHandler.Y_BUTTON_IDX))
    try:
        while True:
            st = gh.read()
            print(f"turn={st.turn:+.2f}  A={st.a_pressed}  Y={st.y_pressed}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
