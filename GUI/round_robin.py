"""
Round Robin CPU Scheduling Simulator
Operating Systems Course Project
Built with Python & Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import copy
import math

# ══════════════════════════════════════════════
#  COLOR PALETTE & DESIGN TOKENS
# ══════════════════════════════════════════════
COLORS = {
    "bg_dark": "#0f0f1a",
    "bg_card": "#1a1a2e",
    "bg_input": "#16213e",
    "bg_table": "#0a0a15",
    "accent": "#e94560",
    "accent_hover": "#ff6b81",
    "accent2": "#533483",
    "accent3": "#0f3460",
    "text": "#eaeaea",
    "text_dim": "#8892b0",
    "text_bright": "#ffffff",
    "success": "#00d2d3",
    "warning": "#feca57",
    "border": "#2a2a4a",
    "gantt_colors": [
        "#e94560", "#00d2d3", "#feca57", "#a29bfe",
        "#fd79a8", "#55efc4", "#fdcb6e", "#74b9ff",
        "#ff7675", "#81ecec", "#fab1a0", "#dfe6e9",
    ],
}

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 10)
FONT_GANTT = ("Consolas", 8)


# ══════════════════════════════════════════════
#  ROUND ROBIN ALGORITHM
# ══════════════════════════════════════════════
class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start_time = -1
        self.finish_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1


def round_robin(processes, quantum):
    """Execute Round Robin scheduling and return results."""
    procs = [Process(p.pid, p.arrival, p.burst) for p in processes]
    n = len(procs)
    time = 0
    queue = []
    gantt = []  # list of (pid, start, end)
    completed = 0
    visited = [False] * n

    # Sort by arrival time
    procs.sort(key=lambda p: (p.arrival, p.pid))

    # Add processes arriving at time 0
    for i, p in enumerate(procs):
        if p.arrival <= time:
            queue.append(i)
            visited[i] = True

    while completed < n:
        if not queue:
            # CPU idle — jump to next arrival
            next_arrival = min(p.arrival for p in procs if p.remaining > 0)
            gantt.append(("idle", time, next_arrival))
            time = next_arrival
            for i, p in enumerate(procs):
                if p.arrival <= time and not visited[i]:
                    queue.append(i)
                    visited[i] = True
            continue

        idx = queue.pop(0)
        p = procs[idx]

        if p.response_time == -1:
            p.response_time = time - p.arrival

        exec_time = min(quantum, p.remaining)
        gantt.append((p.pid, time, time + exec_time))
        time += exec_time
        p.remaining -= exec_time

        # Check for new arrivals during this burst
        for i, proc in enumerate(procs):
            if not visited[i] and proc.arrival <= time:
                queue.append(i)
                visited[i] = True

        if p.remaining > 0:
            queue.append(idx)
        else:
            completed += 1
            p.finish_time = time
            p.turnaround_time = p.finish_time - p.arrival
            p.waiting_time = p.turnaround_time - p.burst

    return procs, gantt


# ══════════════════════════════════════════════
#  GUI APPLICATION
# ══════════════════════════════════════════════
class RoundRobinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Round Robin CPU Scheduler — OS Project")
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.state("zoomed")
        self.root.minsize(1100, 700)

        self.processes = []
        self.pid_counter = 1

        self._build_ui()

    # ── UI BUILDING ──────────────────────────
    def _build_ui(self):
        # Main container
        main = tk.Frame(self.root, bg=COLORS["bg_dark"])
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # ── HEADER ──
        header = tk.Frame(main, bg=COLORS["bg_dark"])
        header.pack(fill="x", pady=(0, 10))

        tk.Label(
            header, text="⏱  Round Robin CPU Scheduler",
            font=FONT_TITLE, fg=COLORS["accent"], bg=COLORS["bg_dark"]
        ).pack(side="left")

        tk.Label(
            header, text="Operating Systems Project",
            font=FONT_BODY, fg=COLORS["text_dim"], bg=COLORS["bg_dark"]
        ).pack(side="right", padx=10)

        # ── TOP SECTION: Input + Process Table ──
        top = tk.Frame(main, bg=COLORS["bg_dark"])
        top.pack(fill="x", pady=5)

        self._build_input_panel(top)
        self._build_process_table(top)

        # ── BOTTOM SECTION: Gantt + Results ──
        bottom = tk.Frame(main, bg=COLORS["bg_dark"])
        bottom.pack(fill="both", expand=True, pady=5)

        self._build_gantt_panel(bottom)
        self._build_results_panel(bottom)

    def _card(self, parent, **pack_opts):
        """Create a styled card frame."""
        card = tk.Frame(
            parent, bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        card.pack(**pack_opts)
        return card

    def _build_input_panel(self, parent):
        card = self._card(parent, side="left", fill="y", padx=(0, 10), pady=5)

        tk.Label(
            card, text="Add Process", font=FONT_HEADING,
            fg=COLORS["text_bright"], bg=COLORS["bg_card"]
        ).pack(pady=(15, 10), padx=20)

        fields = tk.Frame(card, bg=COLORS["bg_card"])
        fields.pack(padx=20, pady=5)

        # Arrival Time
        tk.Label(fields, text="Arrival Time", font=FONT_SMALL,
                 fg=COLORS["text_dim"], bg=COLORS["bg_card"]).grid(row=0, column=0, sticky="w")
        self.entry_arrival = tk.Entry(
            fields, font=FONT_BODY, width=10,
            bg=COLORS["bg_input"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat",
            highlightbackground=COLORS["border"], highlightthickness=1
        )
        self.entry_arrival.grid(row=1, column=0, padx=(0, 8), pady=3, ipady=4)
        self.entry_arrival.insert(0, "0")

        # Burst Time
        tk.Label(fields, text="Burst Time", font=FONT_SMALL,
                 fg=COLORS["text_dim"], bg=COLORS["bg_card"]).grid(row=0, column=1, sticky="w")
        self.entry_burst = tk.Entry(
            fields, font=FONT_BODY, width=10,
            bg=COLORS["bg_input"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat",
            highlightbackground=COLORS["border"], highlightthickness=1
        )
        self.entry_burst.grid(row=1, column=1, padx=(0, 0), pady=3, ipady=4)

        # Time Quantum
        tk.Label(fields, text="Time Quantum", font=FONT_SMALL,
                 fg=COLORS["text_dim"], bg=COLORS["bg_card"]).grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.entry_quantum = tk.Entry(
            fields, font=FONT_BODY, width=10,
            bg=COLORS["bg_input"], fg=COLORS["text"],
            insertbackground=COLORS["text"], relief="flat",
            highlightbackground=COLORS["border"], highlightthickness=1
        )
        self.entry_quantum.grid(row=3, column=0, padx=(0, 8), pady=3, ipady=4)
        self.entry_quantum.insert(0, "2")

        # Buttons
        btn_frame = tk.Frame(card, bg=COLORS["bg_card"])
        btn_frame.pack(pady=10, padx=20, fill="x")

        self._make_btn(btn_frame, "➕ Add", COLORS["accent3"], self._add_process).pack(fill="x", pady=2)
        self._make_btn(btn_frame, "▶  Run Scheduler", COLORS["accent"], self._run_scheduler).pack(fill="x", pady=2)
        self._make_btn(btn_frame, "🗑  Clear All", COLORS["accent2"], self._clear_all).pack(fill="x", pady=2)
        self._make_btn(btn_frame, "📋 Load Example", "#0a6e5c", self._load_example).pack(fill="x", pady=2)

    def _make_btn(self, parent, text, color, cmd):
        btn = tk.Button(
            parent, text=text, font=FONT_BODY,
            bg=color, fg=COLORS["text_bright"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text_bright"],
            relief="flat", cursor="hand2", command=cmd, pady=6
        )
        return btn

    def _build_process_table(self, parent):
        card = self._card(parent, side="left", fill="both", expand=True, pady=5)

        tk.Label(
            card, text="Process Queue", font=FONT_HEADING,
            fg=COLORS["text_bright"], bg=COLORS["bg_card"]
        ).pack(pady=(15, 5), padx=15, anchor="w")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
                        background=COLORS["bg_table"],
                        foreground=COLORS["text"],
                        fieldbackground=COLORS["bg_table"],
                        font=FONT_BODY,
                        rowheight=30)
        style.configure("Dark.Treeview.Heading",
                        background=COLORS["bg_input"],
                        foreground=COLORS["accent"],
                        font=FONT_HEADING)
        style.map("Dark.Treeview", background=[("selected", COLORS["accent3"])])

        cols = ("pid", "arrival", "burst")
        self.proc_tree = ttk.Treeview(
            card, columns=cols, show="headings",
            style="Dark.Treeview", height=8
        )
        self.proc_tree.heading("pid", text="PID")
        self.proc_tree.heading("arrival", text="Arrival Time")
        self.proc_tree.heading("burst", text="Burst Time")
        for c in cols:
            self.proc_tree.column(c, anchor="center", width=100)
        self.proc_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _build_gantt_panel(self, parent):
        card = self._card(parent, side="top", fill="x", pady=(0, 5))

        tk.Label(
            card, text="Gantt Chart", font=FONT_HEADING,
            fg=COLORS["text_bright"], bg=COLORS["bg_card"]
        ).pack(pady=(10, 0), padx=15, anchor="w")

        self.gantt_canvas = tk.Canvas(
            card, bg=COLORS["bg_table"], height=100,
            highlightthickness=0
        )
        self.gantt_canvas.pack(fill="x", padx=15, pady=(5, 15))

    def _build_results_panel(self, parent):
        card = self._card(parent, side="top", fill="both", expand=True, pady=5)

        tk.Label(
            card, text="Results", font=FONT_HEADING,
            fg=COLORS["text_bright"], bg=COLORS["bg_card"]
        ).pack(pady=(10, 5), padx=15, anchor="w")

        cols = ("pid", "arrival", "burst", "finish", "waiting", "turnaround", "response")
        self.result_tree = ttk.Treeview(
            card, columns=cols, show="headings",
            style="Dark.Treeview", height=6
        )
        headings = ["PID", "Arrival", "Burst", "Finish", "Waiting", "Turnaround", "Response"]
        for c, h in zip(cols, headings):
            self.result_tree.heading(c, text=h)
            self.result_tree.column(c, anchor="center", width=95)
        self.result_tree.pack(fill="both", expand=True, padx=15, pady=(0, 5))

        self.stats_label = tk.Label(
            card, text="", font=FONT_MONO,
            fg=COLORS["success"], bg=COLORS["bg_card"], justify="left"
        )
        self.stats_label.pack(pady=(0, 10), padx=15, anchor="w")

    # ── ACTIONS ──────────────────────────────
    def _add_process(self):
        try:
            arrival = int(self.entry_arrival.get())
            burst = int(self.entry_burst.get())
            if burst <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter valid positive integers.")
            return

        pid = f"P{self.pid_counter}"
        self.pid_counter += 1
        self.processes.append(Process(pid, arrival, burst))
        self.proc_tree.insert("", "end", values=(pid, arrival, burst))
        self.entry_burst.delete(0, "end")

    def _load_example(self):
        self._clear_all()
        examples = [(0, 5), (1, 3), (2, 8), (4, 6)]
        for arr, bur in examples:
            pid = f"P{self.pid_counter}"
            self.pid_counter += 1
            self.processes.append(Process(pid, arr, bur))
            self.proc_tree.insert("", "end", values=(pid, arr, bur))
        self.entry_quantum.delete(0, "end")
        self.entry_quantum.insert(0, "3")

    def _clear_all(self):
        self.processes.clear()
        self.pid_counter = 1
        for item in self.proc_tree.get_children():
            self.proc_tree.delete(item)
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.gantt_canvas.delete("all")
        self.stats_label.config(text="")

    def _run_scheduler(self):
        if not self.processes:
            messagebox.showwarning("No Processes", "Add at least one process.")
            return
        try:
            quantum = int(self.entry_quantum.get())
            if quantum <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Quantum", "Time Quantum must be a positive integer.")
            return

        results, gantt = round_robin(self.processes, quantum)
        self._draw_gantt(gantt)
        self._show_results(results)

    # ── DRAWING ──────────────────────────────
    def _draw_gantt(self, gantt):
        canvas = self.gantt_canvas
        canvas.delete("all")
        canvas.update_idletasks()

        if not gantt:
            return

        cw = canvas.winfo_width() - 30
        total_time = gantt[-1][2]
        if total_time == 0:
            return

        unit = cw / total_time
        y_top, y_bot = 15, 65
        pid_set = sorted(set(g[0] for g in gantt if g[0] != "idle"))
        color_map = {pid: COLORS["gantt_colors"][i % len(COLORS["gantt_colors"])]
                     for i, pid in enumerate(pid_set)}
        color_map["idle"] = COLORS["border"]

        for pid, start, end in gantt:
            x1 = 15 + start * unit
            x2 = 15 + end * unit
            color = color_map.get(pid, COLORS["border"])

            canvas.create_rectangle(x1, y_top, x2, y_bot, fill=color, outline=COLORS["bg_dark"], width=1)
            mid_x = (x1 + x2) / 2
            label = pid if pid != "idle" else "—"
            canvas.create_text(mid_x, (y_top + y_bot) / 2, text=label,
                               font=FONT_GANTT, fill=COLORS["text_bright"])

        # Time labels
        times_drawn = set()
        for pid, start, end in gantt:
            for t in (start, end):
                if t not in times_drawn:
                    x = 15 + t * unit
                    canvas.create_text(x, y_bot + 14, text=str(t),
                                       font=FONT_GANTT, fill=COLORS["text_dim"])
                    times_drawn.add(t)

    def _show_results(self, results):
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        results.sort(key=lambda p: p.pid)
        for p in results:
            self.result_tree.insert("", "end", values=(
                p.pid, p.arrival, p.burst,
                p.finish_time, p.waiting_time,
                p.turnaround_time, p.response_time
            ))

        n = len(results)
        avg_wt = sum(p.waiting_time for p in results) / n
        avg_tat = sum(p.turnaround_time for p in results) / n
        avg_rt = sum(p.response_time for p in results) / n

        self.stats_label.config(
            text=f"  Avg Waiting Time = {avg_wt:.2f}   |   "
                 f"Avg Turnaround Time = {avg_tat:.2f}   |   "
                 f"Avg Response Time = {avg_rt:.2f}"
        )


# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app = RoundRobinApp(root)
    root.mainloop()
