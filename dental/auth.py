"""Login local. O hash fica separado dos dados clínicos e dos backups."""
import hashlib
import hmac
import json
import os
import secrets
import tkinter as tk
from tkinter import ttk, messagebox
from dental.ui import theme


class Auth:
    def __init__(self, root):
        self.path = root / 'login.json'

    def exists(self):
        return self.path.exists()

    def create(self, username, password):
        if self.exists():
            raise ValueError('O usuário local já foi criado.')
        if not username.strip() or len(password) < 8:
            raise ValueError('Informe um usuário e uma senha com pelo menos 8 caracteres.')
        salt = secrets.token_bytes(32)
        data = {'username': username.strip(), 'salt': salt.hex(), 'hash': hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000).hex()}
        with self.path.open('x', encoding='utf-8') as handle:
            json.dump(data, handle)
        if os.name != 'nt':
            self.path.chmod(0o600)

    def verify(self, username, password):
        data = json.loads(self.path.read_text(encoding='utf-8'))
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(data['salt']), 600000).hex()
        return hmac.compare_digest(actual, data['hash']) and username.strip() == data['username']


def login(window, auth, on_success):
    theme(window)
    window.title('Consultório Dental — Login')
    window.geometry('520x560')
    frame = ttk.Frame(window, padding=40)
    frame.pack(fill='both', expand=True)
    setup = not auth.exists()
    ttk.Label(frame, text='DENTAL', style='Title.TLabel').pack(anchor='w', pady=(0, 12))
    ttk.Label(frame, text='Crie seu acesso local' if setup else 'Bem-vindo de volta', style='Section.TLabel').pack(anchor='w', pady=(0, 24))
    username, password, confirm = tk.StringVar(), tk.StringVar(), tk.StringVar()
    first = None
    for label, variable, secret in [('Usuário', username, False), ('Senha', password, True)] + ([('Confirmar senha', confirm, True)] if setup else []):
        ttk.Label(frame, text=label).pack(anchor='w', pady=(0, 6))
        entry = ttk.Entry(frame, textvariable=variable, show='•' if secret else '')
        entry.pack(fill='x', pady=(0, 16))
        first = first or entry
    attempts = [0]
    submit = None
    def enter(_=None):
        if str(submit['state']) == 'disabled':
            return
        try:
            if setup:
                if password.get() != confirm.get():
                    raise ValueError('As senhas não coincidem.')
                auth.create(username.get(), password.get())
            elif not auth.verify(username.get(), password.get()):
                attempts[0] += 1
                password.set('')
                if attempts[0] >= 5:
                    submit.configure(state='disabled')
                    window.after(30000, lambda: (submit.configure(state='normal'), attempts.__setitem__(0, 0)))
                raise ValueError('Usuário ou senha incorretos.' + (' Aguarde 30 segundos.' if attempts[0] >= 5 else ''))
            password.set('')
            confirm.set('')
            window.unbind('<Return>')
            frame.destroy()
            on_success()
        except Exception as error:
            messagebox.showerror('Acesso local', str(error), parent=window)
    submit = ttk.Button(frame, text='Criar acesso e entrar' if setup else 'Entrar', style='Accent.TButton', command=enter)
    submit.pack(fill='x', pady=10)
    ttk.Label(frame, text='Sem conta na internet. Este login protege o acesso pelo programa; não criptografa os arquivos.', style='Muted.TLabel', wraplength=420).pack(anchor='w', pady=16)
    window.bind('<Return>', enter)
    first.focus_set()
