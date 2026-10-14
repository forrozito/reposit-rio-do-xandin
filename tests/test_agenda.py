import tempfile
import unittest
from dental.store import Store


class AgendaTests(unittest.TestCase):
    def test_create_edit_cancel_and_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(tmp)
            ident = store.save_appointment(None, 'Consulta Ana', '2026-10-15T09:00:00', '2026-10-15T10:00:00')
            store.save_appointment(ident, 'Retorno Ana', '2026-10-16T11:00:00', '2026-10-16T12:00:00')
            store.cancel_appointment(ident)
            store.db.close()
            store = Store(tmp)
            self.assertEqual(store.appointments(), [(ident, 'Retorno Ana', '2026-10-16T11:00:00', '2026-10-16T12:00:00', 'Cancelada')])
            store.db.close()

    def test_invalid_appointment_preserves_existing_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(tmp)
            ident = store.save_appointment(None, 'Consulta', '2026-10-15T09:00:00', '2026-10-15T10:00:00')
            before = store.appointments()
            for title, start, end in [('', '2026-10-15T09:00:00', '2026-10-15T10:00:00'), ('Consulta', '2026-10-15T11:00:00', '2026-10-15T10:00:00'), ('Consulta', 'data inválida', '2026-10-15T10:00:00')]:
                with self.assertRaises(ValueError):
                    store.save_appointment(ident, title, start, end)
                self.assertEqual(store.appointments(), before)
            store.db.close()
