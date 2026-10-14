import tkinter as tk
from tkinter import ttk
from dental.clinical import ADULT, CHILD, PROCEDURES, SURFACES, QUESTIONS
from dental.ui import BG, PANEL, FIELD, TEXT, MUTED, ACCENT


class Anamnesis:
    def __init__(self, app, parent):
        self.app = app
        self.answers = {}
        bar = ttk.Frame(parent)
        bar.pack(fill='x', pady=(0, 12))
        ttk.Button(bar, text='Salvar anamnese', style='Accent.TButton', command=lambda: app.safe(self.save)).pack(side='left')
        ttk.Label(parent, text='Marque Sim / Não. Campos em branco ficam como “Não informado”.', style='Muted.TLabel', wraplength=500).pack(anchor='w', pady=(0, 12))
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        body = ttk.Frame(canvas)
        item = canvas.create_window(0, 0, window=body, anchor='nw')
        body.bind('<Configure>', lambda _: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda event: canvas.itemconfigure(item, width=event.width))
        def wheel(event):
            canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')
            return 'break'
        self.fields = {}
        for key, label in [('birth', 'Data de nascimento'), ('profession', 'Profissão'), ('complaint', 'Queixa principal'), ('last_visit', 'Última consulta odontológica'), ('brushing', 'Escovação: frequência diária'), ('responsible', 'Responsável (paciente infantil)'), ('doctor', 'Médico / contato'), ('emergency', 'Contato de emergência')]:
            ttk.Label(body, text=label).pack(anchor='w', pady=(8, 4))
            var = tk.StringVar()
            ttk.Entry(body, textvariable=var).pack(fill='x', pady=(0, 6))
            self.fields[key] = var
        for group, questions in QUESTIONS.items():
            ttk.Label(body, text=group, style='Section.TLabel', wraplength=500).pack(anchor='w', pady=(24, 12))
            for key, label in questions:
                card = ttk.Frame(body, padding=10, style='Card.TFrame')
                card.pack(fill='x', pady=5)
                tk.Label(card, text=label, bg=PANEL, fg=TEXT, wraplength=430, justify='left').pack(anchor='w')
                controls = ttk.Frame(card, style='Card.TFrame')
                controls.pack(fill='x', pady=8)
                answer, observation = tk.StringVar(value='Não informado'), tk.StringVar()
                for choice in ('Sim', 'Não', 'Não se aplica'):
                    ttk.Radiobutton(controls, text=choice, variable=answer, value=choice).pack(side='left', padx=(0, 8))
                tk.Label(card, text='Observação (opcional)', bg=PANEL, fg=MUTED, font=('Segoe UI', 9)).pack(anchor='w')
                ttk.Entry(card, textvariable=observation).pack(fill='x', pady=(4, 0))
                self.answers[key] = answer, observation
        ttk.Label(body, text='Observações gerais').pack(anchor='w', pady=(18, 6))
        self.observations = tk.Text(body, height=5, wrap='word')
        self.observations.pack(fill='x', pady=(0, 20))
        def bind_wheel(widget):
            widget.bind('<MouseWheel>', wheel)
            for child in widget.winfo_children():
                bind_wheel(child)
        bind_wheel(body)

    def load(self):
        data = self.app.store.anamnesis(self.app.patient) if self.app.patient else {}
        for key, var in self.fields.items():
            var.set(data.get('fields', {}).get(key, ''))
        for key, (answer, observation) in self.answers.items():
            value = data.get('answers', {}).get(key, {})
            answer.set(value.get('value', 'Não informado'))
            observation.set(value.get('observation', ''))
        self.observations.delete('1.0', 'end')
        self.observations.insert('1.0', data.get('observations', ''))

    def save(self):
        self.app.require_patient()
        self.app.store.save_anamnesis(self.app.patient, {
            'fields': {key: var.get() for key, var in self.fields.items()},
            'answers': {key: {'value': answer.get(), 'observation': obs.get()} for key, (answer, obs) in self.answers.items()},
            'observations': self.observations.get('1.0', 'end-1c'),
        })
        self.app.status.set('Anamnese salva com sucesso')


class Odontogram:
    def __init__(self, app):
        app.require_patient()
        self.app, self.target = app, 'Boca'
        self.window = tk.Toplevel(app.window)
        self.window.title('Odontograma — ' + app.name.get())
        self.window.configure(bg=BG)
        self.window.geometry('1120x860')
        self.window.minsize(900, 700)
        self.window.transient(app.window)
        self.window.grab_set()
        body = ttk.Frame(self.window, padding=20)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text='Odontograma e evolução', style='Title.TLabel').pack(anchor='w')
        ttk.Label(body, text='Clique no dente • Verde: realizado • Amarelo: planejado • X: extraído • Parafuso: implante', style='Muted.TLabel').pack(anchor='w', pady=(8, 12))
        self.dentition = tk.StringVar(value='Adulto')
        bar = ttk.Frame(body)
        bar.pack(fill='x')
        for mode in ('Adulto', 'Infantil'):
            ttk.Radiobutton(bar, text=mode, variable=self.dentition, value=mode, command=self.draw).pack(side='left', padx=(0, 16))
        ttk.Button(bar, text='Boca / procedimento geral', command=lambda: self.select('Boca')).pack(side='right')
        self.canvas = tk.Canvas(body, bg=PANEL, height=260, highlightthickness=0)
        self.canvas.pack(fill='x', pady=12)
        self.canvas.bind('<Configure>', lambda _: self.draw())
        self.label = tk.StringVar()
        ttk.Label(body, textvariable=self.label, style='Section.TLabel').pack(anchor='w', pady=(0, 8))
        form = ttk.Frame(body)
        form.pack(fill='x')
        self.kind, self.surface, self.status = tk.StringVar(value=PROCEDURES[0]), tk.StringVar(value='Não se aplica'), tk.StringVar(value='Realizado')
        for col, (label, var, choices) in enumerate([('Procedimento', self.kind, PROCEDURES), ('Face / região', self.surface, SURFACES), ('Situação', self.status, ('Realizado', 'Planejado'))]):
            form.columnconfigure(col, weight=1)
            ttk.Label(form, text=label).grid(row=0, column=col, sticky='w', padx=(0, 12))
            ttk.Combobox(form, textvariable=var, values=choices, state='readonly').grid(row=1, column=col, sticky='ew', padx=(0, 12), pady=6)
        ttk.Label(body, text='Descrição / observação do procedimento (opcional)').pack(anchor='w', pady=(8, 4))
        self.description = tk.Text(body, height=3, wrap='word')
        self.description.pack(fill='x')
        ttk.Button(body, text='Registrar procedimento', style='Accent.TButton', command=lambda: app.safe(self.save)).pack(anchor='w', pady=12)
        self.history = tk.Text(body, height=6, wrap='word', state='disabled')
        self.history.pack(fill='both', expand=True)
        self.select('Boca')

    def select(self, target):
        self.target = target
        self.surface.set('Não se aplica' if target == 'Boca' else 'Dente inteiro')
        if target == 'Boca' and self.kind.get() in ('Extração', 'Implante'):
            self.kind.set('Outro')
        self.label.set('Boca — procedimentos gerais' if target == 'Boca' else 'Dente ' + target + ' — numeração FDI')
        self.history.configure(state='normal')
        self.history.delete('1.0', 'end')
        for _, kind, surface, status, body, created in self.app.store.procedures(self.app.patient, target):
            self.history.insert('end', f'{created} UTC • {status}\n{kind} • {surface}\n{body}\n\n')
        self.history.configure(state='disabled')
        self.draw()

    def save(self):
        self.app.store.add_procedure(self.app.patient, self.target, self.kind.get(), self.surface.get(), self.status.get(), self.description.get('1.0', 'end-1c'))
        self.description.delete('1.0', 'end')
        self.select(self.target)
        self.app.show_records()

    def draw(self):
        canvas = self.canvas
        canvas.delete('all')
        arches = ADULT if self.dentition.get() == 'Adulto' else CHILD
        width = max(canvas.winfo_width(), 840)
        cell = (width - 32) / len(arches[0])
        for row, arch in enumerate(arches):
            for column, number in enumerate(arch):
                target = str(number)
                state, completed, planned = self.app.store.tooth_state(self.app.patient, target)
                x, y = 16 + cell * (column + .5), 58 + row * 122
                tag = 'tooth' + target
                border = ACCENT if completed else '#efbf66' if planned else '#4f6078'
                if self.target == target:
                    canvas.create_rectangle(x-cell/2+2, y-40, x+cell/2-2, y+62, fill='#294354', outline='', tags=tag)
                canvas.create_oval(x-21, y-30, x+21, y+39, outline=border, width=3, tags=tag)
                if state == 'Implante':
                    canvas.create_rectangle(x-12, y-22, x+12, y-5, fill='#edf2fa', outline='#afc0d5', tags=tag)
                    canvas.create_polygon(x-8,y-3,x+8,y-3,x+5,y+28,x,y+35,x-5,y+28, fill='#a8b7cc', outline='#edf2fa', tags=tag)
                    for offset in range(0, 28, 5):
                        canvas.create_line(x-9,y+offset,x+9,y+offset-3, fill=FIELD, width=2, tags=tag)
                else:
                    digit = number % 10
                    primary = number // 10 >= 5
                    molar = digit >= (4 if primary else 6)
                    if molar:
                        points = [x-15,y-23,x-5,y-27,x,y-21,x+5,y-27,x+15,y-23,x+17,y-8,x+11,y+30,x+6,y+34,x,y+10,x-6,y+34,x-11,y+30,x-17,y-8]
                    elif digit == 3:
                        points = [x-12,y-16,x,y-29,x+12,y-16,x+10,y,x+5,y+22,x,y+35,x-5,y+22,x-10,y]
                    else:
                        points = [x-12,y-23,x,y-26,x+12,y-23,x+13,y-7,x+7,y+18,x,y+35,x-7,y+18,x-13,y-7]
                    canvas.create_polygon(*points, smooth=True, fill='#dce5f0', outline='#93a7c0', width=2, tags=tag)
                    if state == 'Extraído':
                        canvas.create_line(x-17,y-25,x+17,y+32, fill='#ff788a', width=4, tags=tag)
                        canvas.create_line(x+17,y-25,x-17,y+32, fill='#ff788a', width=4, tags=tag)
                canvas.create_text(x,y+53,text=target,fill=TEXT,font=('Segoe UI',11,'bold'),tags=tag)
                canvas.tag_bind(tag, '<Button-1>', lambda _, tooth=target: self.select(tooth))
                canvas.tag_bind(tag, '<Enter>', lambda _: canvas.configure(cursor='hand2'))
                canvas.tag_bind(tag, '<Leave>', lambda _: canvas.configure(cursor=''))
