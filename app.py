from tkinter import *
from tkinter import ttk
from chat import get_response
import tkinter.font as tkFont

# Claude-inspired color scheme
BG_PRIMARY = "#FFFFFF"
BG_SECONDARY = "#F5F5F5"
USER_MSG_BG = "#10A37F"
BOT_MSG_BG = "#E8E8E8"
TEXT_DARK = "#0D0D0D"
TEXT_LIGHT = "#FFFFFF"
HEADER_BG = "#FFFFFF"
BORDER_COLOR = "#ECECEC"
ACCENT_COLOR = "#10A37F"


class ScrollableFrame(Frame):
    """A frame that can scroll its contents"""
    def __init__(self, container, **kwargs):
        super().__init__(container, **kwargs)
        
        self.canvas = Canvas(self, bg=BG_PRIMARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, bg=BG_PRIMARY)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class ChatApplication:
    def __init__(self):
        self.window = Tk()
        self.window.title("Aura - Mental Health Companion")
        self.window.geometry("900x700")
        self.window.configure(bg=BG_PRIMARY)
        
        # Configure fonts
        self.font_header = tkFont.Font(family="Segoe UI", size=14, weight="bold")
        self.font_user_msg = tkFont.Font(family="Segoe UI", size=10)
        self.font_bot_msg = tkFont.Font(family="Segoe UI", size=10)
        
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        # Top Header
        header_frame = Frame(self.window, bg=HEADER_BG, height=70)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # App title and description
        title_label = Label(
            header_frame,
            text="Aura",
            font=self.font_header,
            bg=HEADER_BG,
            fg=TEXT_DARK
        )
        title_label.pack(pady=12, padx=20, anchor="w")

        # Divider line
        divider = Frame(self.window, bg=BORDER_COLOR, height=1)
        divider.pack(fill="x", padx=0)

        # Main chat area with scrolling
        self.scrollable_frame = ScrollableFrame(self.window, bg=BG_PRIMARY)
        self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self.messages_frame = self.scrollable_frame.scrollable_frame

        # Bottom input area
        input_frame = Frame(self.window, bg=BG_PRIMARY)
        input_frame.pack(fill="x", padx=20, pady=20)

        # Message entry box with modern styling
        entry_frame = Frame(input_frame, bg=BG_SECONDARY, highlightthickness=1, highlightbackground=BORDER_COLOR)
        entry_frame.pack(fill="x", side="left", expand=True, padx=(0, 10))

        self.msg_entry = Entry(
            entry_frame,
            bg=BG_SECONDARY,
            fg=TEXT_DARK,
            font=self.font_user_msg,
            relief=FLAT,
            border=0
        )
        self.msg_entry.pack(fill="both", ipady=12, padx=16, pady=12)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)
        self.msg_entry.bind("<Shift-Return>", lambda e: None)  # Allow newlines with Shift+Enter

        # Send button with styling
        send_button = Button(
            input_frame,
            text="Send",
            font=self.font_user_msg,
            bg=ACCENT_COLOR,
            fg=TEXT_LIGHT,
            relief=FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=lambda: self._on_enter_pressed(None),
            activebackground="#0E8F6F",
            activeforeground=TEXT_LIGHT
        )
        send_button.pack(side="left")

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get().strip()
        if msg:
            self._insert_message(msg, "You")

    def _insert_message(self, msg, sender):
        if not msg:
            return

        self.msg_entry.delete(0, END)

        # User message
        self._add_message_bubble(msg, "user")

        # Get bot response
        bot_response = get_response(msg)
        
        # Bot message
        self._add_message_bubble(bot_response, "bot")

        # Scroll to bottom
        self.scrollable_frame.canvas.yview_moveto(1.0)

    def _add_message_bubble(self, text, sender):
        """Create a message bubble styled like Claude"""
        
        # Determine styling based on sender
        if sender == "user":
            bubble_bg = USER_MSG_BG
            text_color = TEXT_LIGHT
            anchor_position = "e"  # Right align
            padx = (60, 20)
        else:
            bubble_bg = BOT_MSG_BG
            text_color = TEXT_DARK
            anchor_position = "w"  # Left align
            padx = (20, 60)

        # Message container
        msg_container = Frame(self.messages_frame, bg=BG_PRIMARY)
        msg_container.pack(fill="x", padx=20, pady=8)

        # Bubble frame
        bubble_frame = Frame(msg_container, bg=bubble_bg, highlightthickness=0)
        bubble_frame.pack(anchor=anchor_position, padx=padx, pady=0, fill="x", expand=False, side="right" if sender == "user" else "left")

        # Message text with word wrap
        msg_label = Label(
            bubble_frame,
            text=text,
            font=self.font_bot_msg if sender == "bot" else self.font_user_msg,
            bg=bubble_bg,
            fg=text_color,
            wraplength=400,
            justify="left",
            padx=16,
            pady=12
        )
        msg_label.pack(fill="both", expand=True)


# Run the Application
if __name__ == "__main__":
    app = ChatApplication()
    app.run()
