"""Tema e organização da interface desktop, sem dependências externas."""
import tkinter as tk
from tkinter import ttk

BG = '#10151f'
PANEL = '#192230'
FIELD = '#222e40'
TEXT = '#edf2fa'
MUTED = '#a8b7cc'
ACCENT = '#53d6c4'


def theme(window):
    window.configure(bg=BG)
    window.option_add('*Font', ('Segoe UI', 11))
    window.option_add('*Text.background', FIELD)
    window.option_add('*Text.foreground', TEXT)
    window.option_add('*Text.insertBackground', TEXT)
    window.option_add('*Text.selectBackground', '#345b70')
    window.option_add('*Text.relief', 'flat')
    window.option_add('*Text.padX', 12)
    window.option_add('*Text.padY', 12)
    style = ttk.Style(window)
    style.theme_use('clam')
    style.configure('.', background=BG, foreground=TEXT, font=('Segoe UI', 11))
    style.configure('TFrame', background=BG)
    style.configure('Card.TFrame', background=PANEL)
    style.configure('TLabel', background=BG, foreground=TEXT)
    style.configure('Muted.TLabel', foreground=MUTED)
    style.configure('Title.TLabel', font=('Segoe UI', 25, 'bold'))
    style.configure('Section.TLabel', font=('Segoe UI', 15, 'bold'))
    style.configure('TButton', background=FIELD, foreground=TEXT, borderwidth=0, padding=(16, 11))
    style.map('TButton', background=[('active', '#30435b')], foreground=[('disabled', MUTED)])
    style.configure('Accent.TButton', background=ACCENT, foreground=BG, font=('Segoe UI', 11, 'bold'))
    style.map('Accent.TButton', background=[('active', '#86e8da')])
    style.configure('Danger.TButton', foreground='#ffb2b9')
    style.configure('Nav.TButton', padding=(18, 15), anchor='w', background=PANEL)
    style.configure('Active.Nav.TButton', background='#254350', foreground=ACCENT)
    style.configure('TEntry', fieldbackground=FIELD, foreground=TEXT, insertcolor=TEXT, bordercolor=FIELD, padding=10)
    style.map('TEntry', fieldbackground=[('focus', FIELD)], bordercolor=[('focus', ACCENT)])
    style.configure('Treeview', background=PANEL, fieldbackground=PANEL, foreground=TEXT, borderwidth=0, rowheight=42)
    style.map('Treeview', background=[('selected', '#294c60')], foreground=[('selected', '#ffffff')])
    style.configure('Treeview.Heading', background=FIELD, foreground=MUTED, padding=(10, 12), font=('Segoe UI', 10, 'bold'), relief='flat')
    style.map('Treeview.Heading', background=[('active', '#30435b')])
    style.configure('TNotebook', background=BG, borderwidth=0)
    style.configure('TNotebook.Tab', background=FIELD, foreground=MUTED, padding=(20, 12))
    style.map('TNotebook.Tab', background=[('selected', PANEL)], foreground=[('selected', ACCENT)])
    style.configure('Vertical.TScrollbar', background=FIELD, troughcolor=BG, borderwidth=0, arrowcolor=MUTED)
    style.configure('TRadiobutton', background=BG, foreground=TEXT, padding=5)
    style.map('TRadiobutton', background=[('active', FIELD)], indicatorcolor=[('selected', ACCENT), ('!selected', FIELD)])
    style.configure('TCombobox', fieldbackground=FIELD, foreground=TEXT, arrowcolor=TEXT, padding=8)
    style.map('TCombobox', fieldbackground=[('readonly', FIELD)], foreground=[('readonly', TEXT)], selectbackground=[('readonly', FIELD)], selectforeground=[('readonly', TEXT)])
    window.option_add('*TCombobox*Listbox.background', FIELD)
    window.option_add('*TCombobox*Listbox.foreground', TEXT)


def button(parent, label, action, app, style='TButton'):
    widget = ttk.Button(parent, text=label, command=lambda: app.safe(action), style=style)
    widget.pack(side='left', padx=(0, 8))
    return widget


def table(parent, columns, headings, widths):
    frame = ttk.Frame(parent)
    frame.pack(fill='both', expand=True)
    tree = ttk.Treeview(frame, columns=columns, show='headings', selectmode='browse')
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')
    for col, heading, width in zip(columns, headings, widths):
        tree.heading(col, text=heading)
        tree.column(col, width=width, minwidth=70)
    return tree


def build(app):
    window = app.window
    theme(window)
    window.title('Consultório Dental')
    window.geometry('1240x820')
    window.minsize(1000, 680)
    sidebar = tk.Frame(window, bg=PANEL, width=210)
    sidebar.pack(side='left', fill='y')
    sidebar.pack_propagate(False)
    tk.Label(sidebar, text='DENTAL', bg=PANEL, fg=ACCENT, font=('Segoe UI', 23, 'bold')).pack(anchor='w', padx=24, pady=(32, 0))
    tk.Label(sidebar, text='Seu consultório, organizado', bg=PANEL, fg=MUTED, font=('Segoe UI', 9)).pack(anchor='w', padx=24, pady=(4, 36))
    content = ttk.Frame(window, padding=28)
    content.pack(side='left', fill='both', expand=True)
    pages = {name: ttk.Frame(content) for name in ('Pacientes', 'Agenda', 'Backup')}
    nav = {}
    def navigate(name):
        for key, page in pages.items():
            page.pack_forget()
            nav[key].configure(style='Active.Nav.TButton' if key == name else 'Nav.TButton')
        pages[name].pack(fill='both', expand=True)
    for name in pages:
        nav[name] = ttk.Button(sidebar, text='Prontuários' if name == 'Pacientes' else name, style='Nav.TButton', command=lambda n=name: navigate(n))
        nav[name].pack(fill='x', padx=12, pady=4)
    tk.Label(sidebar, text='●  Dados neste computador\nFuncionamento offline', bg=PANEL, fg=MUTED, justify='left', font=('Segoe UI', 10)).pack(side='bottom', anchor='w', padx=24, pady=26)
    ttk.Button(sidebar, text='Sair / bloquear', style='Nav.TButton', command=app.logout).pack(side='bottom', fill='x', padx=12, pady=12)
    def heading(page, title, description):
        ttk.Label(page, text=title, style='Title.TLabel').pack(anchor='w')
        ttk.Label(page, text=description, style='Muted.TLabel', wraplength=760).pack(anchor='w', pady=(6, 22))
    patients = pages['Pacientes']
    heading(patients, 'Pacientes', 'Encontre um paciente ou abra uma nova ficha para começar.')
    body = ttk.Frame(patients)
    body.pack(fill='both', expand=True)
    directory = ttk.Frame(body, width=300)
    directory.pack(side='left', fill='both', padx=(0, 22))
    directory.pack_propagate(False)
    button(directory, '+ Novo paciente', app.new, app, 'Accent.TButton').pack(side='top', fill='x', pady=(0, 14))
    app.search = tk.StringVar()
    ttk.Label(directory, text='Buscar por nome ou contato', style='Muted.TLabel').pack(anchor='w', pady=(0, 6))
    ttk.Entry(directory, textvariable=app.search).pack(fill='x', pady=(0, 14))
    app.list = table(directory, ('name', 'contact'), ('Paciente', 'Contato'), (170, 100))
    app.list.bind('<<TreeviewSelect>>', app.select)
    app.search.trace_add('write', lambda *_: app.reload())
    detail = ttk.Frame(body)
    detail.pack(side='left', fill='both', expand=True)
    app.patient_heading = tk.StringVar(value='Nova ficha')
    ttk.Label(detail, textvariable=app.patient_heading, style='Section.TLabel', wraplength=540).pack(anchor='w', pady=(0, 16))
    notebook = ttk.Notebook(detail)
    notebook.pack(fill='both', expand=True)
    app.patient_tabs = notebook
    registration, anamnesis, evolution, exams = [ttk.Frame(notebook, padding=18) for _ in range(4)]
    for page, title in [(registration, 'Cadastro'), (anamnesis, 'Anamnese'), (evolution, 'Evolução'), (exams, 'Exames')]:
        notebook.add(page, text=title)
    from dental.clinical_ui import Anamnesis
    app.anamnesis_form = Anamnesis(app, anamnesis)
    app.name, app.contact = tk.StringVar(), tk.StringVar()
    for label, var in [('Nome completo', app.name), ('Telefone / contato', app.contact)]:
        ttk.Label(registration, text=label).pack(anchor='w', pady=(0, 6))
        ttk.Entry(registration, textvariable=var).pack(fill='x', pady=(0, 18))
    ttk.Label(registration, text='Anamnese e histórico de saúde').pack(anchor='w', pady=(0, 6))
    app.history = tk.Text(registration, height=8, wrap='word')
    app.history.pack(fill='both', expand=True, pady=(0, 18))
    bar = ttk.Frame(registration)
    bar.pack(fill='x')
    button(bar, 'Salvar cadastro', app.save, app, 'Accent.TButton')
    bar = ttk.Frame(evolution)
    bar.pack(fill='x', pady=(0, 16))
    button(bar, 'Odontograma / procedimento', app.odontogram, app, 'Accent.TButton')
    button(bar, 'Nota geral', app.note, app)
    app.records = tk.Text(evolution, height=12, state='disabled', wrap='word')
    app.records.pack(fill='both', expand=True)
    bar = ttk.Frame(exams)
    bar.pack(fill='x', pady=(0, 16))
    button(bar, '+ Anexar exame', app.attach, app, 'Accent.TButton')
    button(bar, 'Abrir selecionado', app.open_exam, app)
    app.exams = table(exams, ('file',), ('Arquivo anexado',), (360,))
    app.exams.bind('<Double-1>', lambda _: app.safe(app.open_exam))
    agenda = pages['Agenda']
    heading(agenda, 'Agenda', 'Consultas salvas localmente. Selecione uma consulta para editar ou cancelar.')
    bar = ttk.Frame(agenda)
    bar.pack(fill='x', pady=(0, 20))
    button(bar, '+ Nova consulta', lambda: app.edit_event(False), app, 'Accent.TButton')
    button(bar, 'Alterar', lambda: app.edit_event(True), app)
    button(bar, 'Cancelar consulta', app.cancel_event, app, 'Danger.TButton')
    button(bar, 'Atualizar', app.refresh_events, app)
    app.event_list = table(agenda, ('start', 'end', 'title', 'status'), ('Início', 'Fim', 'Paciente / consulta', 'Situação'), (160, 160, 280, 110))
    app.event_list.tag_configure('cancelled', foreground='#b38c95')
    app.event_list.bind('<Double-1>', lambda _: app.safe(lambda: app.edit_event(True)))
    backup = pages['Backup']
    heading(backup, 'Backup e transferência', 'Todos os pacientes, prontuários, exames e consultas em um único arquivo.')
    for title, description, label, action, style in [
        ('Salvar uma cópia completa', 'Escolha uma pasta, pendrive ou HD externo para guardar seu arquivo de backup.', 'Salvar backup completo', app.backup, 'Accent.TButton'),
        ('Restaurar neste computador', 'A restauração substitui os dados atuais. Uma cópia anterior é preservada automaticamente.', 'Escolher arquivo para restaurar', app.restore, 'TButton'),
    ]:
        card = ttk.Frame(backup, padding=24, style='Card.TFrame')
        card.pack(fill='x', pady=(0, 18))
        tk.Label(card, text=title, bg=PANEL, fg=TEXT, font=('Segoe UI', 15, 'bold')).pack(anchor='w')
        tk.Label(card, text=description, bg=PANEL, fg=MUTED, wraplength=700, justify='left').pack(anchor='w', pady=(10, 20))
        ttk.Button(card, text=label, style=style, command=lambda a=action: app.safe(a)).pack(anchor='w')
    ttk.Label(backup, text='O arquivo de backup não é criptografado. Guarde-o em um local seguro.', style='Muted.TLabel').pack(anchor='w', pady=8)
    app.status = tk.StringVar(value='Tudo pronto • Dados salvos neste computador')
    ttk.Label(content, textvariable=app.status, style='Muted.TLabel').pack(side='bottom', fill='x', pady=(18, 0))
    navigate('Pacientes')
