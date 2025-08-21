import os
import pygame
from dataclasses import dataclass

# ヘッドレスSSHでもpygame初期化できるように
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

# ===== チューニング =====
DEADZONE = 0.05         # デッドゾーン（D-Padは±1.0なので小さめでOK）
INVERT_TURN = False     # 左右が逆なら True にする
USE_HAT_FALLBACK = True # 軸が0の時にhat(0)のXを使う保険

@dataclass
class PadState:
    turn: float          # -1..1（左: -1, 右: +1）
    a_pressed: bool
    y_pressed: bool
    connected: bool

class GamepadHandler:
    """
    Joy-Con (R) 横持ちの実測（あなたの jstest 結果）に合わせたマッピング：
      - Buttons: A=0, X=1, B=2, Y=3
      - D-Pad:   左右=Axis 4（-32767/32767）, 上下=Axis 5
    """
    # --- あなたの実測に合わせる ---
    FORWARD_BUTTON_IDX = 1  
    BACKWARD_BUTTON_IDX = 2   

    # 「向き」はD-Pad左右を turn として使う
    AXIS_TURN = 4      # D-Pad 左右（±1.0に正規化される）
    AXIS_TURN_ALT = None  # 予備軸があれば指定（例: 0 や 2 など）。通常は不要。

    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.pad = None
        if pygame.joystick.get_count() > 0:
            self.pad = pygame.joystick.Joystick(0)
            self.pad.init()

    def _read_axis(self, idx: int) -> float:
        try:
            return float(self.pad.get_axis(idx))
        except Exception:
            return 0.0

    def _read_button(self, idx: int) -> bool:
        try:
            return bool(self.pad.get_button(idx))
        except Exception:
            return False

    def read(self) -> PadState:
        if self.pad is None:
            return PadState(turn=0.0, a_pressed=False, y_pressed=False, connected=False)

        pygame.event.pump()

        # 1) まず指定の軸から turn を読む（D-Pad左右=Axis 4）
        turn = self._read_axis(self.AXIS_TURN)

        # 2) 補助軸の値が必要なら加味（通常は未使用）
        if self.AXIS_TURN_ALT is not None and abs(turn) < DEADZONE:
            alt = self._read_axis(self.AXIS_TURN_ALT)
            if abs(alt) > abs(turn):
                turn = alt

        # 3) 軸が0なら HAT(X) の値（-1,0,1）を保険で使う
        if USE_HAT_FALLBACK and abs(turn) < DEADZONE:
            try:
                if self.pad.get_numhats() > 0:
                    hat_x, _ = self.pad.get_hat(0)
                    turn = float(hat_x)
            except Exception:
                pass

        # 4) デッドゾーン適用
        if abs(turn) < DEADZONE:
            turn = 0.0

        # 5) 方向反転
        if INVERT_TURN:
            turn = -turn

        a_pressed = self._read_button(self.FORWARD_BUTTON_IDX)
        y_pressed = self._read_button(self.BACKWARD_BUTTON_IDX)

        return PadState(turn=turn, a_pressed=a_pressed, y_pressed=y_pressed, connected=True)

if __name__ == "__main__":
    import time
    gh = GamepadHandler()
    if gh.pad is None:
        print("No gamepad detected. Pair/connect your controller and try again.")
        raise SystemExit(1)

    print(f"Using Joy-Con (R) mapping: X={GamepadHandler.FORWARD_BUTTON_IDX}, B={GamepadHandler.BACKWARD_BUTTON_IDX}, TURN_AXIS={GamepadHandler.AXIS_TURN}")
    try:
        while True:
            st = gh.read()
            print(f"turn={st.turn:+.2f}  X={st.a_pressed}  B={st.y_pressed}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
