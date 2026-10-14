import os
import sqlite3
import uuid
import zipfile
import tempfile
import shutil
from pathlib import Path


class Store:
    def __init__(self, root=None):
        self.root = Path(root or Path(os.getenv('LOCALAPPDATA', Path.home())) / 'ConsultorioDental')
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / 'exams').mkdir(exist_ok=True)
        self.db = sqlite3.connect(self.root / 'patients.sqlite')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS patients(id TEXT PRIMARY KEY, name TEXT NOT NULL, contact TEXT NOT NULL, history TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS notes(id TEXT PRIMARY KEY, patient TEXT REFERENCES patients(id), created TEXT DEFAULT CURRENT_TIMESTAMP, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS exams(id TEXT PRIMARY KEY, patient TEXT REFERENCES patients(id), name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS appointments(id TEXT PRIMARY KEY, title TEXT NOT NULL, start TEXT NOT NULL, end TEXT NOT NULL, status TEXT NOT NULL);
        ''')
        self.db.commit()

    def patients(self):
        return self.db.execute('SELECT * FROM patients ORDER BY name COLLATE NOCASE').fetchall()

    def appointments(self):
        return self.db.execute('SELECT id,title,start,end,status FROM appointments ORDER BY start').fetchall()

    def save_appointment(self, ident, title, start, end):
        from datetime import datetime
        start, end = datetime.fromisoformat(start), datetime.fromisoformat(end)
        if start.tzinfo or end.tzinfo:
            raise ValueError('Use horários locais, sem fuso explícito.')
        if not title.strip() or end <= start:
            raise ValueError('Informe o título e um horário final posterior ao início.')
        if ident and not self.db.execute('SELECT 1 FROM appointments WHERE id=?', (ident,)).fetchone():
            raise ValueError('Consulta não encontrada.')
        ident = ident or uuid.uuid4().hex
        self.db.execute("INSERT INTO appointments VALUES(?,?,?,?,'Agendada') ON CONFLICT(id) DO UPDATE SET title=excluded.title,start=excluded.start,end=excluded.end,status='Agendada'", (ident, title.strip(), start.isoformat(), end.isoformat()))
        self.db.commit()
        return ident

    def cancel_appointment(self, ident):
        self.db.execute("UPDATE appointments SET status='Cancelada' WHERE id=?", (ident,))
        self.db.commit()

    def save_patient(self, ident, name, contact, history):
        if not name.strip():
            raise ValueError('Informe o nome do paciente.')
        ident = ident or uuid.uuid4().hex
        self.db.execute('INSERT INTO patients VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,contact=excluded.contact,history=excluded.history', (ident, name.strip(), contact, history))
        self.db.commit()
        return ident

    def note(self, patient, body):
        if not body.strip():
            raise ValueError('Informe a evolução do atendimento.')
        self.db.execute('INSERT INTO notes(id,patient,body) VALUES(?,?,?)', (uuid.uuid4().hex, patient, body))
        self.db.commit()

    def attach(self, patient, source):
        ident = uuid.uuid4().hex
        target = self.root / 'exams' / ident
        shutil.copyfile(source, target)
        try:
            self.db.execute('INSERT INTO exams VALUES(?,?,?)', (ident, patient, Path(source).name))
            self.db.commit()
        except Exception:
            target.unlink()
            raise

    def backup(self, destination):
        destination = Path(destination).resolve()
        if destination.is_relative_to(self.root.resolve()):
            raise ValueError('Salve o backup fora da pasta de dados.')
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / 'patients.sqlite'
            conn = sqlite3.connect(snapshot)
            self.db.backup(conn)
            conn.close()
            temporary = destination.with_name(destination.name + '.tmp')
            try:
                with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
                    archive.writestr('format.txt', 'ConsultorioDental-1')
                    archive.write(snapshot, 'patients.sqlite')
                    for row in self.db.execute('SELECT id FROM exams'):
                        archive.write(self.root / 'exams' / row[0], 'exams/' + row[0])
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)

    def restore(self, source):
        with tempfile.TemporaryDirectory() as tmp:
            staged = Path(tmp)
            with zipfile.ZipFile(source) as archive:
                if archive.read('format.txt') != b'ConsultorioDental-1':
                    raise ValueError('Formato de backup incompatível.')
                names = archive.namelist()
                if len(names) != len(set(names)):
                    raise ValueError('Backup com entradas duplicadas.')
                for name in names:
                    if name in ('format.txt', 'patients.sqlite'):
                        continue
                    if not name.startswith('exams/') or len(name[6:]) != 32 or any(c not in '0123456789abcdef' for c in name[6:]):
                        raise ValueError('Backup contém arquivos inválidos.')
                archive.extractall(staged)
            conn = sqlite3.connect(staged / 'patients.sqlite')
            try:
                if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                    raise ValueError('Banco de dados inválido.')
                conn.execute('SELECT id,name,contact,history FROM patients').fetchall()
                conn.execute('SELECT id,patient,created,body FROM notes').fetchall()
                # Backups da primeira versão não possuem agenda local.
                conn.execute('CREATE TABLE IF NOT EXISTS appointments(id TEXT PRIMARY KEY, title TEXT NOT NULL, start TEXT NOT NULL, end TEXT NOT NULL, status TEXT NOT NULL)')
                from datetime import datetime
                for ident, title, start, end, status in conn.execute('SELECT id,title,start,end,status FROM appointments'):
                    begin, finish = datetime.fromisoformat(start), datetime.fromisoformat(end)
                    if begin.tzinfo or finish.tzinfo or finish <= begin or not title.strip() or status not in ('Agendada', 'Cancelada'):
                        raise ValueError('Consulta inválida no backup.')
                conn.commit()
                exams = conn.execute('SELECT id,patient,name FROM exams').fetchall()
                if conn.execute('PRAGMA foreign_key_check').fetchall():
                    raise ValueError('Referências inválidas no backup.')
                for ident, _, _ in exams:
                    if len(ident) != 32 or any(c not in '0123456789abcdef' for c in ident) or not (staged / 'exams' / ident).is_file():
                        raise ValueError('Exame ausente ou inválido no backup.')
            finally:
                conn.close()
            recovery = self.root.parent / ('Dental-antes-restauracao-' + uuid.uuid4().hex + '.zip')
            self.backup(recovery)
            self.db.close()
            try:
                shutil.copyfile(staged / 'patients.sqlite', self.root / 'patients.sqlite')
                shutil.rmtree(self.root / 'exams')
                shutil.copytree(staged / 'exams', self.root / 'exams') if (staged / 'exams').exists() else (self.root / 'exams').mkdir()
            except Exception:
                with zipfile.ZipFile(recovery) as archive:
                    archive.extract('patients.sqlite', self.root)
                    shutil.rmtree(self.root / 'exams', ignore_errors=True)
                    (self.root / 'exams').mkdir()
                    for name in archive.namelist():
                        if name.startswith('exams/'):
                            archive.extract(name, self.root)
                raise
            finally:
                self.db = sqlite3.connect(self.root / 'patients.sqlite')
                self.db.execute('PRAGMA foreign_keys=ON')
            return recovery
