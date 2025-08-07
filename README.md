**プログラム開発環境**

開発PC：Windows + VSCode

通信方法：SSHでRaspberry Piに接続（VSCodeのRemote-SSH推奨）

実行環境：Raspberry Pi 4（Raspbian OS）

**2. 機体構成**

3輪ラジコン：前輪2つが駆動輪

モータードライバ（例：L298Nなど）

モーター制御用ピン：GPIOでPWM制御

スピーカー：USBスピーカーか3.5mmジャック経由

ゲームパッド：USB接続 or Bluetooth接続（例：PS4コントローラー）

**操作仕様（ゲームパッド）**

操作	動作

左スティック前	前進

左スティック後	後退

左スティック右	右折

左スティック左	左折

○ボタン	再生／停止トグル

R1ボタン	加速

L1ボタン	減速

🧠 ソフト構成（概要）
plaintext
コピーする
編集する
main.py
├─ gamepad_handler.py（ゲームパッド入力）
├─ motor_controller.py（GPIO制御）
├─ audio_player.py（音楽再生）
└─ constants.py（ピン番号、設定値など）


