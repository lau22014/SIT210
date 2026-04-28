import tkinter as tk
import RPi.GPIO as GPIO

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED mapping
LED_PINS = {
    "living": 17,
    "bathroom": 27,
    "closet": 22,
}

# Setup all pins
def setup_gpio():
    for pin in LED_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

# Turn off all LEDs
def turn_all_off():
    for pin in LED_PINS.values():
        GPIO.output(pin, GPIO.LOW)

class LedControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LED Control")
        self.root.geometry("380x280")
        self.root.configure(bg="#f3f6fb")

        # Checkbox variables
        self.living_var = tk.BooleanVar()
        self.bathroom_var = tk.BooleanVar()
        self.closet_var = tk.BooleanVar()

        self.build_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def build_ui(self):
        frame = tk.Frame(self.root, bg="#ffffff", bd=2, relief="ridge", padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(
            frame,
            text="Room LED Control",
            font=("Segoe UI", 14, "bold"),
            fg="#0ea5e9",
            bg="#ffffff"
        )
        title.pack(pady=(0, 10))

        style = {
            "font": ("Segoe UI", 11),
            "fg": "#334155",
            "bg": "#ffffff",
            "activeforeground": "#0ea5e9",
            "activebackground": "#ffffff",
            "selectcolor": "#e0f2fe",
            "anchor": "w",
            "padx": 5,
            "pady": 5,
        }

        tk.Checkbutton(frame, text="Living Room", variable=self.living_var,
                       command=self.update_leds, **style).pack(fill="x")

        tk.Checkbutton(frame, text="Bathroom", variable=self.bathroom_var,
                       command=self.update_leds, **style).pack(fill="x")

        tk.Checkbutton(frame, text="Closet", variable=self.closet_var,
                       command=self.update_leds, **style).pack(fill="x")

        tk.Button(
            frame,
            text="Exit",
            font=("Segoe UI", 11, "bold"),
            bg="#ef4444",
            fg="white",
            activebackground="#b91c1c",
            bd=0,
            padx=10,
            pady=5,
            command=self.exit_app
        ).pack(pady=10)

    def update_leds(self):
        GPIO.output(LED_PINS["living"], GPIO.HIGH if self.living_var.get() else GPIO.LOW)
        GPIO.output(LED_PINS["bathroom"], GPIO.HIGH if self.bathroom_var.get() else GPIO.LOW)
        GPIO.output(LED_PINS["closet"], GPIO.HIGH if self.closet_var.get() else GPIO.LOW)

    def exit_app(self):
        turn_all_off()
        GPIO.cleanup()
        self.root.destroy()

def main():
    setup_gpio()
    root = tk.Tk()
    app = LedControlApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
