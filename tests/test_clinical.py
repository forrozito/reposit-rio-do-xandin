import tempfile
import unittest
from pathlib import Path
from dental.store import Store
from dental.auth import Auth
from dental.clinical import TEETH


class ClinicalTests(unittest.TestCase):
    def test_teeth_anamnesis_and_backup(self):
        self.assertEqual(len(TEETH), 52)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = Store(root / 'source')
            patient = store.save_patient(None, 'Paciente', '', '')
            other = store.save_patient(None, 'Outro', '', '')
            data = {'answers': {'allergy': {'value': 'Sim', 'observation': 'Látex'}}, 'observations': 'Observação'}
            store.save_anamnesis(patient, data)
            store.add_procedure(patient, '11', 'Extração', 'Dente inteiro', 'Planejado', '')
            self.assertEqual(store.tooth_state(patient, '11'), ('Dente', False, True))
            store.add_procedure(patient, '11', 'Extração', 'Dente inteiro', 'Realizado', 'Extração')
            self.assertEqual(store.tooth_state(patient, '11')[0], 'Extraído')
            store.add_procedure(patient, '11', 'Implante', 'Dente inteiro', 'Realizado', '')
            self.assertEqual(store.tooth_state(patient, '11')[0], 'Implante')
            store.add_procedure(patient, '55', 'Restauração', 'Oclusal / incisal', 'Realizado', '')
            store.add_procedure(patient, 'Boca', 'Profilaxia', 'Não se aplica', 'Realizado', '')
            self.assertEqual(store.procedures(other), [])
            self.assertEqual(store.anamnesis(other), {})
            backup = root / 'backup.dentalbackup'
            store.backup(backup)
            restored = Store(root / 'target')
            restored.restore(backup)
            self.assertEqual(restored.anamnesis(patient), data)
            self.assertEqual(restored.procedures(patient), store.procedures(patient))
            self.assertEqual(restored.tooth_state(patient, '55'), ('Dente', True, False))
            store.db.close()
            restored.db.close()

    def test_reject_invalid_procedure(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(tmp)
            patient = store.save_patient(None, 'Paciente', '', '')
            for target in ('99', 'Boca'):
                with self.assertRaises(ValueError):
                    store.add_procedure(patient, target, 'Extração', 'Dente inteiro', 'Realizado', '')
            self.assertEqual(store.procedures(patient), [])
            store.db.close()

    def test_restore_legacy_backup_creates_clinical_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = Store(root / 'source')
            patient = store.save_patient(None, 'Paciente antigo', '', 'Histórico preservado')
            store.db.executescript('DROP TABLE anamnesis; DROP TABLE procedures;')
            backup = root / 'old.dentalbackup'
            store.backup(backup)
            target = Store(root / 'target')
            target.restore(backup)
            self.assertEqual(target.patients()[0][3], 'Histórico preservado')
            self.assertEqual(target.anamnesis(patient), {})
            target.add_procedure(patient, '11', 'Restauração', 'Dente inteiro', 'Realizado', '')
            self.assertEqual(target.tooth_state(patient, '11'), ('Dente', True, False))
            target.db.close()
            store.db.close()

    def test_local_login_and_backup_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = Store(root / 'source')
            auth = Auth(store.root)
            auth.create('dentista', 'senha-de-teste')
            self.assertTrue(auth.verify('dentista', 'senha-de-teste'))
            self.assertFalse(auth.verify('dentista', 'incorreta'))
            self.assertFalse(auth.verify('outro', 'senha-de-teste'))
            self.assertNotIn('senha-de-teste', auth.path.read_text())
            backup = root / 'backup.dentalbackup'
            store.backup(backup)
            import zipfile
            with zipfile.ZipFile(backup) as archive:
                self.assertNotIn('login.json', archive.namelist())
            store.db.close()
