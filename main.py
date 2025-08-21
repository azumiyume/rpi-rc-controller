import time
from motor_controller import MotorController
from gamepad_handler import GamepadHandler

# ===== Tunables =====
LOOP_HZ = 75.0
ACCEL_PER_SEC = 1.5     # ↑ 立ち上がり加速を強める
BRAKE_PER_SEC = 1.2
DRAG_PER_SEC = 1.0
TURN_GAIN = 0.6         # ↓ 片輪が弱り過ぎないよう少し下げる
TURN_DEADBAND = 0.05    # 微小なヨー入力を無視して左右差の発生を抑える

MIN_DUTY = 65.0         # ↑ 始動用の底上げ（まずは 65、必要なら 70→75）
MAX_DUTY = 100.0

# 始動キック
KICK_MS = 150           # 100〜200ms で調整
KICK_DUTY = 100.0

SAFETY_TIMEOUT = 1.5

def mix(throttle: float, turn: float) -> tuple[float, float]:
    """Differential mixing with small deadband on turn."""
    t = 0.0 if abs(turn) < TURN_DEADBAND else turn
    l = throttle + t * TURN_GAIN
    r = throttle - t * TURN_GAIN
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
        pwm_freq=1000         # 1kHz 推奨
    )
    pad = GamepadHandler()

    if pad.pad is None:
        print("No gamepad detected. Pair/connect your controller, then try again.")
        return

    throttle = 0.0  # -1..1
    last_time = time.monotonic()
    last_pad_time = last_time

    # 始動キック管理（左右独立）
    left_prev_dc = 0.0
    right_prev_dc = 0.0
    left_kick_until = 0.0
    right_kick_until = 0.0

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
                left_prev_dc = right_prev_dc = 0.0  # 状態リセット
                time.sleep(1.0 / LOOP_HZ)
                continue

            # Differential mixing
            left_norm, right_norm = mix(throttle, st.turn)

            # Convert to duty cycle (±100)
            left_dc_cmd = to_duty(left_norm)
            right_dc_cmd = to_duty(right_norm)

            # --- 始動キック判定（停止→非0 で発火） ---
            if left_prev_dc == 0.0 and left_dc_cmd != 0.0:
                left_kick_until = now + KICK_MS / 1000.0
            if right_prev_dc == 0.0 and right_dc_cmd != 0.0:
                right_kick_until = now + KICK_MS / 1000.0

            # キック適用（時間内は100%固定、符号はコマンドに合わせる）
            if now < left_kick_until:
                left_dc = KICK_DUTY if left_dc_cmd >= 0 else -KICK_DUTY
            else:
                left_dc = left_dc_cmd

            if now < right_kick_until:
                right_dc = KICK_DUTY if right_dc_cmd >= 0 else -KICK_DUTY
            else:
                right_dc = right_dc_cmd

            # 出力
            print(
                f"turn={st.turn:+.2f}  fwd={st.a_pressed}  back={st.y_pressed} "
                f"thr={throttle:+.2f}  L={left_dc:+.0f}% R={right_dc:+.0f}%"
            )
            motor.drive(left_dc, right_dc)

            # 次回用に保持
            left_prev_dc = 0.0 if left_dc == 0.0 else left_dc
            right_prev_dc = 0.0 if right_dc == 0.0 else right_dc

            # ループ周期調整
            sleep_rem = 1.0 / LOOP_HZ - (time.monotonic() - now)
            if sleep_rem > 0:
                time.sleep(sleep_rem)

    except KeyboardInterrupt:
        pass
    finally:
        motor.cleanup()

if __name__ == "__main__":
    main()
