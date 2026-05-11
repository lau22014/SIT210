import json
import threading
import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import font as tkfont
 
# --- Config ---
LED_GREEN  = 17
LED_YELLOW = 27
LED_RED    = 22
BUZZER     = 18
 
MQTT_BROKER = "localhost"
MQTT_PORT   = 1883
MQTT_TOPIC  = "home/kitchen/sensors"
 
# --- GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in [LED_GREEN, LED_YELLOW, LED_RED, BUZZER]:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
 
sensor_data = {"temp": 0.0, "smoke": 0, "level": 0}
 
def set_outputs(level):
    GPIO.output(LED_GREEN,  GPIO.HIGH if level == 0 else GPIO.LOW)
    GPIO.output(LED_YELLOW, GPIO.HIGH if level == 1 else GPIO.LOW)
    GPIO.output(LED_RED,    GPIO.HIGH if level == 2 else GPIO.LOW)
    GPIO.output(BUZZER,     GPIO.HIGH if level == 2 else GPIO.LOW)
 
# --- MQTT ---
def on_message(client, userdata, msg):
    global sensor_data
    try:
        sensor_data = json.loads(msg.payload.decode())
        set_outputs(sensor_data.get("level", 0))
    except Exception as e:
        print(f"Parse error: {e}")
 
def start_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC)
    client.loop_forever()
 
# --- Theme ---
BG       = "#f2f2f5"
CARD_BG  = "#ffffff"
TEXT_DIM = "#aaaaaa"
TEXT_ON  = "#1a1a1a"
 
LEVEL = {
    0: {"color": "#00a87a", "label": "SAFE"},
    1: {"color": "#e0900a", "label": "WARNING"},
    2: {"color": "#e02020", "label": "FIRE ALARM"},
}

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Fire Alarm Monitor")
        self.root.geometry("600x360")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._blink = True
        self._build()
        self._refresh()
 
    def _build(self):
        f_label  = tkfont.Font(family="Courier New", size=10)
        f_status = tkfont.Font(family="Courier New", size=42, weight="bold")
        f_value  = tkfont.Font(family="Courier New", size=32, weight="bold")
        f_unit   = tkfont.Font(family="Courier New", size=13)
        f_time   = tkfont.Font(family="Courier New", size=9)
 
        # Status box (top half)
        self.status_frame = tk.Frame(self.root, bg=CARD_BG)
        self.status_frame.pack(fill="x", padx=24, pady=(24, 12))
 
        self.lbl_status = tk.Label(self.status_frame, text="SAFE",
                                   font=f_status, bg=CARD_BG,
                                   fg=LEVEL[0]["color"], pady=24)
        self.lbl_status.pack()
 
        # Bottom row: temp + smoke
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=24)
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)
 
        # Temp card
        temp_card = tk.Frame(row, bg=CARD_BG)
        temp_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
 
        tk.Label(temp_card, text="TEMPERATURE", font=f_label,
                 bg=CARD_BG, fg=TEXT_DIM).pack(anchor="w", padx=20, pady=(16, 0))
        temp_row = tk.Frame(temp_card, bg=CARD_BG)
        temp_row.pack(anchor="w", padx=20, pady=(4, 16))
        self.lbl_temp = tk.Label(temp_row, text="--", font=f_value,
                                 bg=CARD_BG, fg=TEXT_ON)
        self.lbl_temp.pack(side="left")
        tk.Label(temp_row, text=" C", font=f_unit,
                 bg=CARD_BG, fg=TEXT_DIM).pack(side="left", anchor="s", pady=(0, 6))
 
        # Smoke card
        smoke_card = tk.Frame(row, bg=CARD_BG)
        smoke_card.grid(row=0, column=1, sticky="nsew")
 
        tk.Label(smoke_card, text="SMOKE LEVEL", font=f_label,
                 bg=CARD_BG, fg=TEXT_DIM).pack(anchor="w", padx=20, pady=(16, 0))
        smoke_row = tk.Frame(smoke_card, bg=CARD_BG)
        smoke_row.pack(anchor="w", padx=20, pady=(4, 16))
        self.lbl_smoke = tk.Label(smoke_row, text="--", font=f_value,
                                  bg=CARD_BG, fg=TEXT_ON)
        self.lbl_smoke.pack(side="left")
        tk.Label(smoke_row, text=" RAW", font=f_unit,
                 bg=CARD_BG, fg=TEXT_DIM).pack(side="left", anchor="s", pady=(0, 6))
 
        # Timestamp
        self.lbl_time = tk.Label(self.root, text="", font=f_time,
                                 bg=BG, fg=TEXT_DIM)
        self.lbl_time.pack(anchor="e", padx=28, pady=(10, 0))
        
    def _refresh(self):
        d   = sensor_data
        lvl = d.get("level", 0)
        col = LEVEL[lvl]["color"]
 
        # Blink label on fire alarm
        self._blink = not self._blink
        show = LEVEL[lvl]["label"] if lvl != 2 or self._blink else ""
        self.lbl_status.config(text=show, fg=col)
        self.status_frame.config(bg=CARD_BG)
 
        temp  = d.get("temp",  0)
        smoke = d.get("smoke", 0)
 
        self.lbl_temp.config( text=f"{temp:.1f}",
                              fg="#ff3b3b" if temp  >= 50  else TEXT_ON)
        self.lbl_smoke.config(text=f"{smoke}",
                              fg="#f5a623" if smoke >= 600 else TEXT_ON)
 
        self.lbl_time.config(text=time.strftime("%H:%M:%S"))
        self.root.after(500, self._refresh)
 
def build_ui():
    root = tk.Tk()
    Dashboard(root)
    root.mainloop()
    GPIO.cleanup()
 
if __name__ == "__main__":
    threading.Thread(target=start_mqtt, daemon=True).start()
    build_ui()
 
