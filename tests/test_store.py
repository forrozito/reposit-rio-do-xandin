import tempfile
import unittest
import zipfile
from pathlib import Path
from dental.store import Store


class StoreTests(unittest.TestCase):
    def test_full_backup_restore_and_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = Store(root / 'source')
            first = source.save_patient(None, 'Ana', '123', 'Histórico A')
            second = source.save_patient(None, 'Bruno', '456', 'Histórico B')
            source.note(first, 'Procedimento realizado')
            source.note(second, 'Retorno')
            appointment = source.save_appointment(None, 'Ana — consulta', '2026-10-15T09:00:00', '2026-10-15T10:00:00')
            source.cancel_appointment(appointment)
            exam = root / 'exame.pdf'
            exam.write_bytes(b'%PDF-exame-teste')
            source.attach(second, exam)
            backup = root / 'all.dentalbackup'
            source.backup(backup)
            target = Store(root / 'target')
            target.save_patient(None, 'Anterior', '', '')
            recovery = target.restore(backup)
            self.assertEqual(source.patients(), target.patients())
            self.assertEqual(source.appointments(), target.appointments())
            self.assertEqual(target.db.execute('SELECT COUNT(*) FROM notes').fetchone()[0], 2)
            ident = target.db.execute('SELECT id FROM exams').fetchone()[0]
            self.assertEqual((target.root / 'exams' / ident).read_bytes(), exam.read_bytes())
            target.restore(recovery)
            self.assertEqual(target.patients()[0][1], 'Anterior')
            self.assertEqual(target.appointments(), [])
            source.db.close()
            target.db.close()

    def test_reject_invalid_backup_without_losing_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = Store(root / 'data')
            store.save_patient(None, 'Preservado', '', '')
            backup = root / 'invalid.zip'
            with zipfile.ZipFile(backup, 'w') as archive:
                archive.writestr('format.txt', 'ConsultorioDental-1')
                archive.writestr('../escape', 'bad')
            with self.assertRaises(ValueError):
                store.restore(backup)
            self.assertEqual(store.patients()[0][1], 'Preservado')
            self.assertFalse((root / 'escape').exists())
            store.db.close()


if __name__ == '__main__':
    unittest.main()
