import os
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
from google import genai
from google.genai import types
from PIL import ImageGrab

# Initialisiere den Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Modernere, dunkle Farbpalette
BG_DARK = "#181818"
BG_PANEL = "#222222"
BG_INPUT = "#2d2d2d"
TEXT_COLOR = "#e0e0e0"
ACCENT_COLOR = "#007acc"
BTN_RESET = "#333333"


class GeminiAssistantApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Gemini Sidebar")

    # Bildschirmgröße ermitteln, um die Sidebar exakt rechts anzudocken
    screen_width = self.root.winfo_screenwidth()
    screen_height = self.root.winfo_screenheight()
    sidebar_width = 400
    sidebar_height = screen_height - 60  # Puffer oben/unten

    # Geometrie: Breite x Höhe + X-Position + Y-Position (Rechter Rand)
    self.root.geometry(
        f"{sidebar_width}x{sidebar_height}+{screen_width - sidebar_width - 10}+30"
    )

    self.root.configure(bg=BG_DARK)

    # Unter Linux: Als Utility-Fenster definieren, damit die Tastatur funktioniert,
    # aber keine störende Windows-Titelleiste angezeigt wird.
    try:
      self.root.attributes("-type", "utility")
    except Exception:
      # Fallback falls das Betriebssystem das Attribut nicht unterstützt
      self.root.overrideredirect(True)

    # Damit das Fenster im Vordergrund bleibt
    self.root.attributes("-topmost", True)

    # Fokus direkt auf das Eingabefeld lenken
    self.root.after(100, lambda: self.entry_field.focus_set())
    self.root.bind(
        "<Button-1>", lambda event: self.entry_field.focus_set()
    )

    # --- Header mit Schließen-Button ---
    header_frame = tk.Frame(root, bg=BG_DARK, height=40)
    header_frame.pack(fill=tk.X, padx=15, pady=(10, 0))
    header_frame.pack_propagate(False)

    lbl_title = tk.Label(
        header_frame,
        text="GEMINI ASSISTANT",
        font=("Segoe UI", 10, "bold"),
        bg=BG_DARK,
        fg="#888888",
    )
    lbl_title.pack(side=tk.LEFT)

    close_btn = tk.Button(
        header_frame,
        text="✕ Schließen",
        command=self.root.destroy,
        bg="#2d2d2d",
        fg="#ff5555",
        font=("Segoe UI", 9),
        relief=tk.FLAT,
        cursor="hand2",
        padx=8,
        pady=2,
    )
    close_btn.pack(side=tk.RIGHT)

    # --- Chat-Verlauf ---
    self.chat_history = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        state=tk.DISABLED,
        bg=BG_PANEL,
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
        font=("Segoe UI", 10),
        bd=0,
        highlightthickness=0,
    )
    self.chat_history.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

    # --- Unterer Bereich: Eingabe & Funktions-Buttons ---
    bottom_frame = tk.Frame(root, bg=BG_DARK)
    bottom_frame.pack(padx=15, pady=(0, 15), fill=tk.X)

    # Eingabefeld
    self.entry_field = tk.Entry(
        bottom_frame,
        font=("Segoe UI", 11),
        bg=BG_INPUT,
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
        relief=tk.FLAT,
    )
    self.entry_field.pack(fill=tk.X, ipady=8, padx=0, pady=(0, 10))
    self.entry_field.bind("<Return>", lambda event: self.send_message())

    # Steuerungs-Buttons (Reset, Screenshot, Senden) nebeneinander
    btn_layout_frame = tk.Frame(bottom_frame, bg=BG_DARK)
    btn_layout_frame.pack(fill=tk.X)

    reset_btn = tk.Button(
        btn_layout_frame,
        text="🔄",
        command=self.reset_chat,
        bg=BTN_RESET,
        fg=TEXT_COLOR,
        font=("Segoe UI", 11),
        relief=tk.FLAT,
        cursor="hand2",
        width=4,
    )
    reset_btn.pack(side=tk.LEFT, padx=(0, 5))

    screenshot_btn = tk.Button(
        btn_layout_frame,
        text="📸 Screenshot",
        command=self.analyze_screenshot,
        bg=BTN_RESET,
        fg=TEXT_COLOR,
        font=("Segoe UI", 10),
        relief=tk.FLAT,
        cursor="hand2",
    )
    screenshot_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    send_button = tk.Button(
        btn_layout_frame,
        text="Senden",
        command=self.send_message,
        bg=ACCENT_COLOR,
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief=tk.FLAT,
        cursor="hand2",
        padx=10,
    )
    send_button.pack(side=tk.RIGHT)

    # Chat initialisieren
    self.init_chat_session()

  def init_chat_session(self):
    self.chat = client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=(
                "Du bist ein hilfreicher Desktop-Assistent. "
                "Wenn der Nutzer möchte, dass du einen Terminal-Befehl ausführen sollst, "
                "antworte im Format: EXECUTE: [befehl]. "
                "Erkläre kurz, was der Befehl tut, bevor du ihn ausgibst."
            )
        ),
    )
    self.append_chat(
        "System", "Sidebar bereit. Wie kann ich dir helfen?"
    )

  def reset_chat(self):
    if messagebox.askyesno(
        "Chat zurücksetzen", "Möchtest du den Chat leeren?"
    ):
      self.chat_history.config(state=tk.NORMAL)
      self.chat_history.delete("1.0", tk.END)
      self.chat_history.config(state=tk.DISABLED)
      self.init_chat_session()

  def append_chat(self, sender, message):
    self.chat_history.config(state=tk.NORMAL)
    self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
    self.chat_history.config(state=tk.DISABLED)
    self.chat_history.see(tk.END)

  def send_message(self):
    user_text = self.entry_field.get().strip()
    if not user_text:
      return

    self.entry_field.delete(0, tk.END)
    self.append_chat("Du", user_text)

    try:
      response = self.chat.send_message(user_text)
      reply = response.text
      self.append_chat("Gemini", reply)

      if "EXECUTE:" in reply:
        self.handle_command_execution(reply)

    except Exception as e:
      self.append_chat("Fehler", str(e))

  def handle_command_execution(self, text):
    try:
      lines = text.split("\n")
      command_line = next((line for line in lines if "EXECUTE:" in line), None)
      if command_line:
        command = command_line.split("EXECUTE:")[1].strip()

        confirm = messagebox.askyesno(
            "Terminal-Befehl bestätigen",
            f"Das LLM möchte folgenden Befehl ausführen:\n\n{command}\n\nMöchtest du das erlauben?",
        )

        if confirm:
          result = subprocess.run(
              command, shell=True, capture_output=True, text=True, encoding="utf-8"
          )
          output = result.stdout if result.returncode == 0 else result.stderr
          self.append_chat(
              "System",
              f"Befehl ausgeführt:\n--- Ausgabe ---\n{output or 'Keine Ausgabe'}",
          )
        else:
          self.append_chat("System", "Befehl vom Benutzer abgebrochen.")
    except Exception as e:
      self.append_chat("Fehler bei der Befehlsausführung", str(e))

  def analyze_screenshot(self):
    try:
      screenshot = ImageGrab.grab()
      self.append_chat("System", "Screenshot aufgenommen. Analysiere...")
      self.root.update()

      response = client.models.generate_content(
          model="gemini-3.5-flash-lite",
          contents=[
              screenshot,
              "Analysiere diesen Screenshot. Was ist darauf zu sehen und gibt es etwas Wichtiges?",
          ],
      )

      self.append_chat("Gemini (Analyse)", response.text)
    except Exception as e:
      self.append_chat("Fehler", f"Screenshot fehlgeschlagen: {e}")


if __name__ == "__main__":
  if not os.environ.get("GEMINI_API_KEY"):
    print("Warnung: GEMINI_API_KEY Umgebungsvariable ist nicht gesetzt!")

  root = tk.Tk()
  app = GeminiAssistantApp(root)
  root.mainloop()
