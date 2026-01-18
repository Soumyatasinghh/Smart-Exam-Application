# SmartExam — Full Multi-Section Exam Simulator (Part 1)
import tkinter as tk
from tkinter import ttk, messagebox
import csv, os, time
from datetime import datetime

# -----------------------------
# Configuration
# -----------------------------
APP_TITLE = "SmartExam - Multi-Section"
EXAM_DURATION_MINUTES = 30
RESULTS_CSV = "results.csv"

SECTIONS = {
    "Aptitude": [
        {"q": "If 3x + 2 = 11, what is x?", "opts": ["2", "3", "9", "11"], "a": 1},
        {"q": "What is 15% of 200?", "opts": ["20", "30", "25", "35"], "a": 1},
        {"q": "If train A runs at 60 km/hr and B at 40 km/hr, ratio speed A:B?", "opts": ["3:2", "2:3", "6:4", "4:3"], "a": 0},
        {"q": "What is the LCM of 6 and 8?", "opts": ["24", "48", "12", "18"], "a": 0},
        {"q": "Solve: 7 * 8 - 5", "opts": ["51", "56", "45", "50"], "a": 0},
    ],
    "Reasoning": [
        {"q": "Find the next: 2, 4, 8, 16, ?", "opts": ["20", "24", "32", "18"], "a": 2},
        {"q": "If ALL = 3 letters, then BALL = ?", "opts": ["4", "5", "3", "2"], "a": 0},
        {"q": "Which does not belong: Dog, Cat, Car, Cow?", "opts": ["Dog", "Cat", "Car", "Cow"], "a": 2},
        {"q": "If A=1, B=2 then Z=?", "opts": ["26", "25", "27", "24"], "a": 0},
        {"q": "Which is opposite of 'ascend'?", "opts": ["Rise", "Drop", "Climb", "Descend"], "a": 3},
    ],
    "Coding": [
        {"q": "Which language uses 'def' to define a function?", "opts": ["Java", "C++", "Python", "Ruby"], "a": 2},
        {"q": "What does HTML stand for?", "opts": ["Hyperlink Text Markup Language", "HyperText Markup Language", "Home Tool Markup Language", "HyperText Makeup Language"], "a": 1},
        {"q": "Which symbol starts a single-line comment in Java?", "opts": ["//", "/*", "#", "<!--"], "a": 0},
        {"q": "Which keyword is used to create a class in Java?", "opts": ["func", "class", "def", "new"], "a": 1},
        {"q": "What is the output of: print(2+3*4) in Python?", "opts": ["20", "14", "10", "24"], "a": 1},
    ]
}

# -----------------------------
# CSV saving
# -----------------------------
def save_results_csv(name, roll, per_section_scores, total_score, total_questions, time_taken_seconds):
    header = ["Timestamp", "Name", "Roll", "Section", "Score", "TotalQuestions", "TimeTakenSeconds"]
    now = datetime.now().isoformat(sep=' ', timespec='seconds')
    file_exists = os.path.isfile(RESULTS_CSV)
    try:
        with open(RESULTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists: writer.writerow(header)
            for sec, (score, total) in per_section_scores.items():
                writer.writerow([now, name, roll, sec, score, total, int(time_taken_seconds)])
            writer.writerow([now, name, roll, "Overall", total_score, total_questions, int(time_taken_seconds)])
    except Exception as e:
        print("Failed to save CSV:", e)

# -----------------------------
# Main App
# -----------------------------
class SmartExamApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.state("zoomed")
        self.resizable(True, True)

        # Styles
        self.style = ttk.Style(self)
        try: self.style.theme_use('clam')
        except: pass
        self._setup_styles()

        # State
        self.student_name, self.student_roll = "", ""
        self.duration_seconds = EXAM_DURATION_MINUTES*60
        self.remaining_seconds = self.duration_seconds
        self.timer_job = None
        self.start_time = None
        self.sections = list(SECTIONS.keys())
        self.current_section = self.sections[0]
        self.section_state = {sec: {"current_q":0, "selected":[None]*len(SECTIONS[sec]), "flagged":[False]*len(SECTIONS[sec])} for sec in self.sections}

        # Build UI frames
        self._build_login_frame()
        self._build_section_select_frame()
        self._build_exam_frame()
        self._build_review_frame()
        self.show_frame('login')

    # -----------------------------
    # Styles
    # -----------------------------
    def _setup_styles(self):
        self.style.configure('Header.TLabel', background='#1565c0', foreground='white', font=('Segoe UI', 18, 'bold'))
        self.style.configure('Card.TFrame', background='white')
        self.style.configure('Q.TLabel', background='white', foreground='#212121', font=('Segoe UI', 14, 'bold'))
        self.style.configure('Opt.TRadiobutton', background='white', font=('Segoe UI', 12))
        self.style.configure('Primary.TButton', font=('Segoe UI', 11, 'bold'))
        self.style.map('Primary.TButton', background=[('!active','#1976d2'), ('active','#1565c0')])
        self.style.configure('TProgressbar', thickness=16)

    # -----------------------------
    # Login Frame
    # -----------------------------
    def _build_login_frame(self):
        self.login_frame = ttk.Frame(self, padding=16)
        header = ttk.Label(self.login_frame, text=APP_TITLE, style='Header.TLabel', anchor='center')
        header.pack(fill='x', pady=(0,12))
        card = ttk.Frame(self.login_frame, style='Card.TFrame', padding=20)
        card.pack(fill='both', expand=True)
        ttk.Label(card, text="Welcome to SmartExam", font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(4,6))
        ttk.Label(card, text="Enter details to begin the exam.", font=('Segoe UI', 11)).pack(anchor='w', pady=(0,12))
        form = ttk.Frame(card)
        form.pack(anchor='w', pady=6)
        ttk.Label(form, text="Full name:", font=('Segoe UI', 11)).grid(row=0, column=0, sticky='w')
        self.entry_name = ttk.Entry(form, width=40, font=('Segoe UI', 11))
        self.entry_name.grid(row=0, column=1, padx=(6,0), pady=6)
        ttk.Label(form, text="Roll/ID:", font=('Segoe UI', 11)).grid(row=1, column=0, sticky='w')
        self.entry_roll = ttk.Entry(form, width=25, font=('Segoe UI', 11))
        self.entry_roll.grid(row=1, column=1, padx=(6,0), pady=6, sticky='w')
        ttk.Label(card, text=f"Total Duration: {EXAM_DURATION_MINUTES} minutes", font=('Segoe UI', 10, 'italic')).pack(anchor='w', pady=(8,0))
        btn_row = ttk.Frame(card)
        btn_row.pack(fill='x', pady=(16,0))
        ttk.Button(btn_row, text="Start Exam", style='Primary.TButton', command=self._on_start).pack(side='left')
        ttk.Button(btn_row, text="Instructions", command=self._show_instructions).pack(side='left', padx=8)

    # -----------------------------
    # Section Selection Frame
    # -----------------------------
    def _build_section_select_frame(self):
        self.section_select_frame = ttk.Frame(self, padding=10)
        header = ttk.Label(self.section_select_frame, text="Select Sections", style='Header.TLabel')
        header.pack(fill='x', pady=(0,12))
        card = ttk.Frame(self.section_select_frame, style='Card.TFrame', padding=12)
        card.pack(fill='both', expand=True)
        ttk.Label(card, text="Choose sections to take (default: all):", font=('Segoe UI', 11)).pack(anchor='w', pady=(4,6))
        self.section_vars = {}
        for sec in self.sections:
            var = tk.IntVar(value=1)
            ttk.Checkbutton(card, text=sec, variable=var).pack(anchor='w', pady=4)
            self.section_vars[sec] = var
        ttk.Button(card, text="Continue", style='Primary.TButton', command=self._on_section_confirm).pack(pady=(12,0))

    # -----------------------------
    # Exam Frame (UI only)
    # -----------------------------
    def _build_exam_frame(self):
        self.exam_frame = ttk.Frame(self, padding=8)
        header = ttk.Frame(self.exam_frame)
        header.pack(fill='x', pady=(0,6))
        self.lbl_title = ttk.Label(header, text=APP_TITLE, style='Header.TLabel')
        self.lbl_title.pack(side='left', fill='x', expand=True)
        self.lbl_timer = ttk.Label(header, text="00:00", font=('Consolas', 14, 'bold'), foreground='red')
        self.lbl_timer.pack(side='right')

        content = ttk.Frame(self.exam_frame)
        content.pack(fill='both', expand=True)

        # Left card: question
        left = ttk.Frame(content, style='Card.TFrame', padding=12)
        left.pack(side='left', fill='both', expand=True, padx=(0,8))

        top_row = ttk.Frame(left)
        top_row.pack(fill='x')
        ttk.Label(top_row, text="Section:", font=('Segoe UI', 10)).pack(side='left')
        self.section_combo = ttk.Combobox(top_row, values=self.sections, state='readonly', width=18)
        self.section_combo.current(0)
        self.section_combo.pack(side='left', padx=(6,12))
        ttk.Button(top_row, text="Switch Section", command=self._switch_section).pack(side='left')
        self.lbl_qcounter = ttk.Label(top_row, text="Question 1/1")
        self.lbl_qcounter.pack(side='right')

        self.lbl_question = ttk.Label(left, text="", style='Q.TLabel', wraplength=620, justify='left')
        self.lbl_question.pack(anchor='w', pady=(8,10))

        self.answer_var = tk.IntVar(value=-1)
        self.opt_buttons = []
        for i in range(4):
            rb = ttk.Radiobutton(left, text="", variable=self.answer_var, value=i, style='Opt.TRadiobutton')
            rb.pack(anchor='w', pady=6)
            self.opt_buttons.append(rb)

        action = ttk.Frame(left)
        action.pack(fill='x', pady=(12,0))
        self.btn_prev = ttk.Button(action, text="Previous", command=self._prev_q)
        self.btn_prev.pack(side='left')
        self.btn_next = ttk.Button(action, text="Next", command=self._next_q)
        self.btn_next.pack(side='left', padx=(6,0))
        self.flag_btn = ttk.Button(action, text="Flag for review", command=self._toggle_flag)
        self.flag_btn.pack(side='left', padx=(6,0))
        self.btn_submit = ttk.Button(action, text="Submit Exam", style='Primary.TButton', command=self._submit_exam)
        self.btn_submit.pack(side='right')

        # Right sidebar
        right = ttk.Frame(content, padding=(8,4))
        right.pack(side='right', fill='y')
        ttk.Label(right, text="Section Progress", font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        self.progress_bar = ttk.Progressbar(right, orient='vertical', length=300, mode='determinate', maximum=5)
        self.progress_bar.pack(pady=(8,12))
        ttk.Label(right, text="Flagged Questions", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(8,2))
        self.flagged_listbox = tk.Listbox(right, height=8, width=28)
        self.flagged_listbox.pack()
        self.flagged_listbox.bind("<Double-Button-1>", self._jump_to_flagged)
        ttk.Separator(right, orient='horizontal').pack(fill='x', pady=8)
        ttk.Label(right, text="Sections", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(6,2))
        self.sections_listbox = tk.Listbox(right, height=5, width=28)
        for sec in self.sections: self.sections_listbox.insert(tk.END, sec)
        self.sections_listbox.selection_set(0)
        self.sections_listbox.pack()
        ttk.Button(right, text="Go to Section", command=self._goto_section_from_list).pack(pady=(6,0))
        ttk.Button(right, text="Review Answers", command=self._open_review).pack(pady=(12,0))

    # -----------------------------
# Part 2 — Exam Logic, Timer, Review, Submission
# -----------------------------

    # -----------------------------
    # Frame Navigation
    # -----------------------------
    def show_frame(self, name):
        for widget in self.winfo_children(): widget.place_forget()
        if name == 'login': self.login_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        elif name == 'section_select': self.section_select_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        elif name == 'exam': self.exam_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        elif name == 'review': self.review_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    # -----------------------------
    # Actions: Login -> Start Exam
    # -----------------------------
    def _on_start(self):
        name = self.entry_name.get().strip()
        roll = self.entry_roll.get().strip()
        if not name or not roll:
            messagebox.showwarning("Missing", "Please enter both name and roll/ID.")
            return
        self.student_name = name
        self.student_roll = roll
        self.show_frame('section_select')

    def _on_section_confirm(self):
        selected = [sec for sec, var in self.section_vars.items() if var.get()==1]
        if not selected:
            messagebox.showwarning("Select", "Select at least one section.")
            return
        self.sections = selected
        self.current_section = self.sections[0]
        # Reset per-section state
        self.section_state = {sec: {"current_q":0, "selected":[None]*len(SECTIONS[sec]), "flagged":[False]*len(SECTIONS[sec])} for sec in self.sections}
        # Update combo & sidebar
        self.section_combo['values'] = self.sections
        self.section_combo.set(self.current_section)
        self.sections_listbox.delete(0, tk.END)
        for sec in self.sections: self.sections_listbox.insert(tk.END, sec)
        self.progress_bar['maximum'] = len(SECTIONS[self.current_section])
        # Start timer
        self.start_time = time.time()
        self.remaining_seconds = self.duration_seconds
        self.show_frame('exam')
        self._update_question_ui()
        self._tick()

    # -----------------------------
    # Timer
    # -----------------------------
    def _format_time(self, seconds):
        m, s = divmod(seconds, 60)
        return f"{int(m):02d}:{int(s):02d}"

    def _tick(self):
        if self.remaining_seconds <= 0:
            self.lbl_timer.config(text="00:00")
            messagebox.showinfo("Time's up", "Time is over. The exam will be submitted automatically.")
            self._submit_exam()
            return
        # warning if less than 5 minutes
        if self.remaining_seconds <= 300: self.lbl_timer.config(foreground='red')
        self.lbl_timer.config(text=self._format_time(self.remaining_seconds))
        self.remaining_seconds -= 1
        self.timer_job = self.after(1000, self._tick)

    # -----------------------------
    # Question Navigation
    # -----------------------------
    def _update_question_ui(self):
        sec = self.current_section
        state = self.section_state[sec]
        qidx = state['current_q']
        qdata = SECTIONS[sec][qidx]
        self.lbl_question.config(text=qdata['q'])
        for i, opt in enumerate(qdata['opts']): self.opt_buttons[i].config(text=opt)
        sel = state['selected'][qidx]
        self.answer_var.set(sel if sel is not None else -1)
        self.lbl_qcounter.config(text=f"Question {qidx+1} / {len(SECTIONS[sec])}")
        self.progress_bar['maximum'] = len(SECTIONS[sec])
        self.progress_bar['value'] = qidx+1
        self.flag_btn.config(text="Unflag" if state['flagged'][qidx] else "Flag for review")
        self._update_flagged_list()

    def _record_selection(self):
        sel = self.answer_var.get()
        self.section_state[self.current_section]['selected'][self.section_state[self.current_section]['current_q']] = None if sel==-1 else sel

    def _next_q(self):
        self._record_selection()
        sec = self.current_section
        if self.section_state[sec]['current_q'] < len(SECTIONS[sec])-1:
            self.section_state[sec]['current_q'] += 1
            self._update_question_ui()
        else:
            messagebox.showinfo("End", "You reached the end of this section.")

    def _prev_q(self):
        self._record_selection()
        sec = self.current_section
        if self.section_state[sec]['current_q'] > 0:
            self.section_state[sec]['current_q'] -= 1
            self._update_question_ui()

    # -----------------------------
    # Flag Questions
    # -----------------------------
    def _toggle_flag(self):
        sec = self.current_section
        idx = self.section_state[sec]['current_q']
        self.section_state[sec]['flagged'][idx] = not self.section_state[sec]['flagged'][idx]
        self._update_flagged_list()
        self.flag_btn.config(text="Unflag" if self.section_state[sec]['flagged'][idx] else "Flag for review")

    def _update_flagged_list(self):
        self.flagged_listbox.delete(0, tk.END)
        for sec in self.sections:
            for i, f in enumerate(self.section_state[sec]['flagged']):
                if f:
                    qtext = SECTIONS[sec][i]['q']
                    display = f"{sec} - Q{i+1}: {qtext[:40]}{'...' if len(qtext)>40 else ''}"
                    self.flagged_listbox.insert(tk.END, display)

    def _jump_to_flagged(self, event):
        sel = self.flagged_listbox.curselection()
        if not sel: return
        text = self.flagged_listbox.get(sel[0])
        try:
            parts = text.split(" - ")
            sec = parts[0]
            qnum = int(parts[1].split(":")[0][1:]) - 1
            if sec in self.sections:
                self.current_section = sec
                self.section_combo.set(sec)
                self.section_state[sec]['current_q'] = qnum
                self._update_question_ui()
        except: pass

    # -----------------------------
    # Section Switching
    # -----------------------------
    def _switch_section(self):
        sec = self.section_combo.get()
        if sec in self.sections:
            self.current_section = sec
            self._update_question_ui()

    def _goto_section_from_list(self):
        sel = self.sections_listbox.curselection()
        if sel:
            sec = self.sections_listbox.get(sel[0])
            self.current_section = sec
            self.section_combo.set(sec)
            self._update_question_ui()

    # -----------------------------
    # Review & Submit
    # -----------------------------
    def _build_review_frame(self):
        self.review_frame = ttk.Frame(self, padding=8)
        header = ttk.Label(self.review_frame, text="Review Answers", style='Header.TLabel')
        header.pack(fill='x', pady=(0,8))
        canvas = tk.Canvas(self.review_frame, borderwidth=0, background='#f7f7f7')
        frame = ttk.Frame(canvas)
        vsb = ttk.Scrollbar(self.review_frame, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.create_window((0,0), window=frame, anchor='nw')
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self.review_container = frame
        bottom = ttk.Frame(self.review_frame)
        bottom.pack(fill='x', pady=(8,0))
        ttk.Button(bottom, text="Save Results to CSV", command=self._save_results_prompt).pack(side='left')
        ttk.Button(bottom, text="Back to Exam", command=lambda: self.show_frame('exam')).pack(side='right')

    def _open_review(self):
        for w in self.review_container.winfo_children(): w.destroy()
        for sec in self.sections:
            frame = ttk.Frame(self.review_container, style='Card.TFrame', padding=8)
            frame.pack(fill='x', padx=6, pady=6)
            ttk.Label(frame, text=f"Section: {sec}", font=('Segoe UI', 11, 'bold')).pack(anchor='w')
            state = self.section_state[sec]
            for i, q in enumerate(SECTIONS[sec]):
                user = state['selected'][i]
                correct = q['a']
                ttk.Label(frame, text=f"Q{i+1}. {q['q']}", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(6,0))
                for j, opt in enumerate(q['opts']):
                    prefix, fg = "   ", "#000"
                    if j==correct: prefix, fg = "✔ ", "#2e7d32"
                    if user is not None and j==user and user!=correct: prefix, fg = "✖ ", "#c62828"
                    ttk.Label(frame, text=f"{prefix}{opt}", foreground=fg).pack(anchor='w', padx=8)
        self.show_frame('review')

    def _submit_exam(self):
        self._record_selection()
        if self.timer_job: self.after_cancel(self.timer_job); self.timer_job=None
        per_section_scores = {}
        total_score, total_questions = 0,0
        for sec in self.sections:
            score = sum(1 for i,q in enumerate(SECTIONS[sec]) if self.section_state[sec]['selected'][i]==q['a'])
            per_section_scores[sec] = (score, len(SECTIONS[sec]))
            total_score += score
            total_questions += len(SECTIONS[sec])
        time_taken = time.time() - (self.start_time if self.start_time else time.time())
        save_results_csv(self.student_name, self.student_roll, per_section_scores, total_score, total_questions, time_taken)
        pct = int((total_score/total_questions)*100 if total_questions>0 else 0)
        msg = f"Exam submitted.\n\nName: {self.student_name}\nRoll: {self.student_roll}\nTotal Score: {total_score}/{total_questions}\nPercentage: {pct}%\nTime taken: {int(time_taken)}s\n\nResults saved to {RESULTS_CSV}\n\nOpen review?"
        if messagebox.askyesno("Submitted", msg): self._open_review()
        else: messagebox.showinfo("Saved", f"Results saved to {RESULTS_CSV}."); self._reset_to_login()

    def _save_results_prompt(self): messagebox.showinfo("Saved", f"Results are in {RESULTS_CSV}")

    def _reset_to_login(self):
        if self.timer_job: self.after_cancel(self.timer_job); self.timer_job=None
        self.student_name, self.student_roll = "", ""
        self.entry_name.delete(0, tk.END)
        self.entry_roll.delete(0, tk.END)
        self.section_state = {sec: {"current_q":0, "selected":[None]*len(SECTIONS[sec]), "flagged":[False]*len(SECTIONS[sec])} for sec in self.sections}
        self.remaining_seconds = self.duration_seconds
        self.show_frame('login')

    def _show_instructions(self):
        messagebox.showinfo("Instructions", "1. Fill name and roll.\n2. Select sections.\n3. Switch sections via dropdown or sidebar.\n4. Flag questions to review.\n5. Timer is shared across sections. Good luck!")

# -----------------------------
# Launch App
# -----------------------------
def main():
    app = SmartExamApp()
    app.mainloop()

if __name__=="__main__":
    main()
