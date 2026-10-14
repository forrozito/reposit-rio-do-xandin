import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dental.store import Store


class App:
    def __init__(self, window):
        self.window, self.store, self.patient = window, Store(), None
        from dental.ui import build
        build(self)
        self.reload()
        self.refresh_events()

    def safe(self, action):
        try:
            action()
        except Exception as error:
            messagebox.showerror('Não foi possível concluir', str(error))

    def reload(self):
        self.list.delete(*self.list.get_children())
        query = self.search.get().strip().casefold()
        for ident, name, contact, _ in self.store.patients():
            if query and query not in (name + ' ' + contact).casefold():
                continue
            self.list.insert('', 'end', iid=ident, values=(name, contact))

    def new(self):
        self.patient = None
        self.list.selection_remove(*self.list.selection())
        self.patient_heading.set('Nova ficha')
        self.patient_tabs.select(0)
        self.name.set('')
        self.contact.set('')
        self.history.delete('1.0', 'end')
        self.show_records()

    def select(self, _=None):
        selected = self.list.selection()
        if not selected:
            return
        self.patient = selected[0]
        row = self.store.db.execute('SELECT name,contact,history FROM patients WHERE id=?', (self.patient,)).fetchone()
        if row is None:
            return
        self.patient_heading.set(row[0])
        self.name.set(row[0])
        self.contact.set(row[1])
        self.history.delete('1.0', 'end')
        self.history.insert('1.0', row[2])
        self.show_records()

    def save(self):
        self.patient = self.store.save_patient(self.patient, self.name.get(), self.contact.get(), self.history.get('1.0', 'end-1c'))
        self.search.set('')
        self.reload()
        self.list.selection_set(self.patient)
        self.patient_heading.set(self.name.get().strip())
        self.status.set('Cadastro salvo com sucesso')

    def require_patient(self):
        if not self.patient:
            raise ValueError('Selecione ou salve um paciente primeiro.')

    def show_records(self):
        self.records.config(state='normal')
        self.records.delete('1.0', 'end')
        for created, body in self.store.db.execute('SELECT created,body FROM notes WHERE patient=? ORDER BY created', (self.patient,)):
            self.records.insert('end', created + ' UTC\n' + body + '\n\n')
        self.records.config(state='disabled')
        self.exams.delete(*self.exams.get_children())
        for ident, name in self.store.db.execute('SELECT id,name FROM exams WHERE patient=?', (self.patient,)):
            self.exams.insert('', 'end', iid=ident, values=(name,))

    def note(self):
        self.require_patient()
        dialog = tk.Toplevel(self.window)
        dialog.title('Evolução do atendimento')
        dialog.configure(bg='#10151f')
        text = tk.Text(dialog, width=65, height=16)
        text.pack(padx=12, pady=12)
        def save():
            self.store.note(self.patient, text.get('1.0', 'end-1c'))
            self.show_records()
            dialog.destroy()
        ttk.Button(dialog, text='Salvar', command=lambda: self.safe(save)).pack(pady=8)
        dialog.transient(self.window)
        dialog.grab_set()

    def attach(self):
        self.require_patient()
        path = filedialog.askopenfilename(title='Selecionar exame')
        if path:
            self.store.attach(self.patient, path)
            self.show_records()

    def open_exam(self):
        selected = self.exams.selection()
        if not selected:
            return
        ident = selected[0]
        name = self.store.db.execute('SELECT name FROM exams WHERE id=?', (ident,)).fetchone()[0]
        import tempfile, shutil
        from pathlib import Path
        path = Path(tempfile.mkdtemp(prefix='dental-exame-')) / Path(name).name
        shutil.copyfile(self.store.root / 'exams' / ident, path)
        if sys.platform == 'win32':
            os.startfile(path)
        else:
            subprocess.Popen(['xdg-open', str(path)])

    def backup(self):
        path = filedialog.asksaveasfilename(defaultextension='.dentalbackup', filetypes=[('Backup completo', '*.dentalbackup')])
        if path:
            self.store.backup(path)
            messagebox.showinfo('Backup', 'Todos os pacientes, prontuários, exames e consultas foram salvos. Guarde o arquivo em local seguro; ele não é criptografado.')

    def restore(self):
        path = filedialog.askopenfilename(filetypes=[('Backup completo', '*.dentalbackup')])
        if path and messagebox.askyesno('Restaurar', 'Substituir TODOS os dados locais pelo backup? Uma cópia de segurança dos dados atuais será preservada.'):
            recovery = self.store.restore(path)
            self.new()
            self.reload()
            self.refresh_events()
            messagebox.showinfo('Restaurado', 'Dados restaurados. Cópia anterior: ' + str(recovery))

    def refresh_events(self):
        self.events = {row[0]: row for row in self.store.appointments()}
        self.event_list.delete(*self.event_list.get_children())
        from datetime import datetime
        for ident, title, start, end, status in self.events.values():
            self.event_list.insert('', 'end', iid=ident, values=(
                datetime.fromisoformat(start).strftime('%d/%m/%Y %H:%M'),
                datetime.fromisoformat(end).strftime('%d/%m/%Y %H:%M'),
                title, status), tags=('cancelled',) if status == 'Cancelada' else ())

    def selected_event(self):
        selected = self.event_list.selection()
        if not selected:
            raise ValueError('Selecione um agendamento.')
        return selected[0]

    def edit_event(self, editing):
        from datetime import datetime, timedelta
        ident = self.selected_event() if editing else None
        now = datetime.now().replace(second=0, microsecond=0)
        event = self.events[ident] if ident else (None, 'Consulta odontológica', now.isoformat(), (now + timedelta(hours=1)).isoformat(), 'Agendada')
        start, end = datetime.fromisoformat(event[2]), datetime.fromisoformat(event[3])
        dialog = tk.Toplevel(self.window)
        dialog.title('Alterar consulta' if editing else 'Nova consulta')
        dialog.configure(bg='#10151f')
        fields = []
        for label, value in [('Paciente / título', event[1]), ('Data (DD/MM/AAAA)', start.strftime('%d/%m/%Y')), ('Início (HH:MM)', start.strftime('%H:%M')), ('Fim (HH:MM)', end.strftime('%H:%M'))]:
            ttk.Label(dialog, text=label).pack(anchor='w', padx=16, pady=(10, 0))
            var = tk.StringVar(value=value)
            ttk.Entry(dialog, textvariable=var, width=45).pack(padx=16)
            fields.append(var)
        ttk.Label(dialog, text='Horários locais do computador. Salvar reativa uma consulta cancelada.').pack(padx=16, pady=12)
        def save():
            title, date, start_time, end_time = [var.get().strip() for var in fields]
            try:
                start = datetime.strptime(date + ' ' + start_time, '%d/%m/%Y %H:%M')
                end = datetime.strptime(date + ' ' + end_time, '%d/%m/%Y %H:%M')
            except ValueError:
                raise ValueError('Informe uma data válida (DD/MM/AAAA) e horários no formato HH:MM.')
            self.store.save_appointment(ident, title, start.isoformat(), end.isoformat())
            self.refresh_events()
            dialog.destroy()
        ttk.Button(dialog, text='Salvar consulta', command=lambda: self.safe(save)).pack(pady=12)
        dialog.transient(self.window)
        dialog.grab_set()

    def cancel_event(self):
        ident = self.selected_event()
        if messagebox.askyesno('Cancelar consulta', 'Marcar esta consulta como cancelada? Ela continuará no histórico.'):
            self.store.cancel_appointment(ident)
            self.refresh_events()


if __name__ == '__main__':
    window = tk.Tk()
    App(window)
    window.mainloop()
