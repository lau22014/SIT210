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


class LedControlApp:
    """Tkinter GUI application for 3-LED room control."""
    def __init__(self, root):
        self.root = root
        self.root.title("Home LED Control")
        self.root.geometry("520x560")
        self.root.resizable(False, False)

        # color palette.
        self.colors = {
            "bg": "#eef3f8",
            "panel": "#ffffff",
            "card": "#f8fafc",
            "card_border": "#d5deea",
            "card_selected": "#b9d7ff",
            "title": "#0f172a",
            "text": "#334155",
            "accent": "#0ea5e9",
            "accent_active": "#0284c7",
            "button": "#ef4444",
            "button_active": "#dc2626",
        }

        self.root.configure(bg=self.colors["bg"])

        # Selected room; empty at start means all LEDs are OFF.
        self.selected_room = tk.StringVar(value="living")
        self.brightness_vars = {
            "living": tk.IntVar(value=100),
            "bathroom": tk.IntVar(value=100),
            "closet": tk.IntVar(value=100),
        }
        self.room_cards = {}
        self.room_value_labels = {}

        # Create one PWM channel per LED pin.
        self.pwm_channels = {}
        for pin in LED_PINS.values():
            pwm = GPIO.PWM(pin, 1000)
            pwm.start(0)
            self.pwm_channels[pin] = pwm

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
        container.place(relx=0.5, rely=0.5, anchor="center", width=470, height=500)

        title = tk.Label(
            container,
            text="Room LED Controller",
            font=("Segoe UI", 18, "bold"),
            fg=self.colors["title"],
            bg=self.colors["panel"],
        )
        title.pack(anchor="w", pady=(0, 2))

        subtitle = tk.Label(
            container,
            text="Select a room and drag its slider to set LED brightness",
            font=("Segoe UI", 10),
            fg="#64748b",
            bg=self.colors["panel"],
        )
        subtitle.pack(anchor="w", pady=(0, 14))

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

        controls_frame = tk.Frame(container, bg=self.colors["panel"])
        controls_frame.pack(fill="both", expand=True)
        
        self._build_room_control(controls_frame, "Living Room", "living", radio_style)
        self._build_room_control(controls_frame, "Bathroom", "bathroom", radio_style)
        self._build_room_control(controls_frame, "Closet", "closet", radio_style)

        self._refresh_room_cards()

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
        exit_button.pack(pady=(14, 0), anchor="e")

    def _build_room_control(self, parent, label, room_key, radio_style):
        """Build one radio button and one slider for a room."""
        card = tk.Frame(
            parent,
            bg=self.colors["card"],
            highlightthickness=1,
            highlightbackground=self.colors["card_border"],
            highlightcolor=self.colors["card_border"],
            padx=12,
            pady=10,
        )
        card.pack(fill="x", pady=(0, 10))
        self.room_cards[room_key] = card

        header = tk.Frame(card, bg=self.colors["card"])
        header.pack(fill="x")
        tk.Radiobutton(
            header,
            text=label,
            variable=self.selected_room,
            value=room_key,
            command=self.on_room_selected,
            **radio_style,
        ).pack(side="left")

        value_label = tk.Label(
            header,
            text=f"{self._get_room_duty(room_key)}%",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["accent_active"],
            bg=self.colors["card"],
        )
        value_label.pack(side="right")
        self.room_value_labels[room_key] = value_label

        tk.Scale(
            card,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.brightness_vars[room_key],
            command=lambda _value, key=room_key: self.on_brightness_changed(key),
            bg=self.colors["card"],
            fg=self.colors["text"],
            highlightthickness=0,
            bd=0,
            troughcolor="#dbeafe",
            activebackground=self.colors["accent"],
            length=370,
            showvalue=False,
        ).pack(fill="x", pady=(2, 0))

    def _refresh_room_cards(self):
        """Highlight selected room card for better visual feedback."""
        selected_room = self.selected_room.get()
        for room_key, card in self.room_cards.items():
            border = self.colors["card_selected"] if room_key == selected_room else self.colors["card_border"]
            card.configure(highlightbackground=border, highlightcolor=border)

    def on_room_selected(self):
        """Update active output when selected room changes."""
        self._refresh_room_cards()
        self._apply_output_state()

    def on_brightness_changed(self, room_key):
        """Apply brightness in real time if this room is selected."""
        self.room_value_labels[room_key].configure(text=f"{self._get_room_duty(room_key)}%")
        if self.selected_room.get() == room_key:
            self._apply_output_state()

    def turn_led_off(self):
        """Force all PWM outputs to zero duty cycle."""
        for pin in LED_PINS.values():
            self.pwm_channels[pin].ChangeDutyCycle(0)

    def _get_room_duty(self, room_key):
        """Get clamped duty cycle for one room slider."""
        return max(0, min(100, int(self.brightness_vars[room_key].get())))

    def _apply_output_state(self):
        """Route selected room slider value to the selected LED only."""
        selected_room = self.selected_room.get()

        for room_key, pin in LED_PINS.items():
            if room_key == selected_room:
                self.pwm_channels[pin].ChangeDutyCycle(self._get_room_duty(room_key))
            else:
                self.pwm_channels[pin].ChangeDutyCycle(0)

    def exit_app(self):
        """Turn off LEDs, release GPIO, and close GUI."""
        self.turn_led_off()

        for pwm in self.pwm_channels.values():
            pwm.stop()

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
