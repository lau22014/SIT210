import tkinter as tk
import RPi.GPIO as GPIO 


# Use Broadcom GPIO numbering.
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# pin mapping for each room.
LED_PINS = {
    "living": 17,   # GPIO17 - Living Room
    "bathroom": 27, # GPIO27 - Bathroom
    "closet": 22,   # GPIO22 - Closet
}


def setup_gpio():
    """Initialize all LED pins as outputs and set them OFF."""
    for pin in LED_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)


def turn_all_off():
    """Turn OFF all LEDs."""
    for pin in LED_PINS.values():
        GPIO.output(pin, GPIO.LOW)


def turn_on_only(room_key):
    """Turn ON only the selected room LED, turn others OFF."""
    turn_all_off()
    GPIO.output(LED_PINS[room_key], GPIO.HIGH)


class LedControlApp:
    """Tkinter GUI application for 3-LED room control."""

    def __init__(self, root):
        self.root = root
        self.root.title("Home LED Control")
        self.root.geometry("420x310")
        self.root.resizable(False, False)

        # color palette.
        self.colors = {
            "bg": "#f3f6fb",
            "panel": "#ffffff",
            "title": "#1f2937",
            "text": "#334155",
            "accent": "#0ea5e9",
            "accent_active": "#0284c7",
            "button": "#ef4444",
            "button_active": "#dc2626",
        }

        self.root.configure(bg=self.colors["bg"])

        # Selected room; empty at start means all LEDs are OFF.
        self.selected_room = tk.StringVar(value="")

        self._build_ui()

        # Handle window close button safely.
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def _build_ui(self):
        """Create and style the GUI widgets."""
        container = tk.Frame(
            self.root,
            bg=self.colors["panel"],
            bd=0,
            highlightthickness=0,
            padx=28,
            pady=24,
        )
        container.place(relx=0.5, rely=0.5, anchor="center", width=360, height=250)

        title = tk.Label(
            container,
            text="Room LED Controller",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors["title"],
            bg=self.colors["panel"],
        )
        title.pack(pady=(0, 18))

        # Radio buttons: only one can be selected at a time.
        radio_style = {
            "font": ("Segoe UI", 12),
            "fg": self.colors["text"],
            "bg": self.colors["panel"],
            "activeforeground": self.colors["title"],
            "activebackground": self.colors["panel"],
            "selectcolor": self.colors["panel"],
            "anchor": "w",
            "padx": 4,
            "pady": 5,
        }

        tk.Radiobutton(
            container,
            text="Living Room",
            variable=self.selected_room,
            value="living",
            command=self.on_room_selected,
            **radio_style,
        ).pack(fill="x")

        tk.Radiobutton(
            container,
            text="Bathroom",
            variable=self.selected_room,
            value="bathroom",
            command=self.on_room_selected,
            **radio_style,
        ).pack(fill="x")

        tk.Radiobutton(
            container,
            text="Closet",
            variable=self.selected_room,
            value="closet",
            command=self.on_room_selected,
            **radio_style,
        ).pack(fill="x")

        exit_button = tk.Button(
            container,
            text="Exit",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["button"],
            fg="#ffffff",
            activebackground=self.colors["button_active"],
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.exit_app,
        )
        exit_button.pack(pady=(18, 0), anchor="e")

    def on_room_selected(self):
        """Apply LED state based on selected radio option."""
        room_key = self.selected_room.get()
        if room_key in LED_PINS:
            turn_on_only(room_key)

    def exit_app(self):
        """Turn off LEDs, release GPIO, and close GUI."""
        turn_all_off()
        GPIO.cleanup()
        self.root.destroy()


def main():
    """Program entry point."""
    setup_gpio()

    root = tk.Tk()
    app = LedControlApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
