import json

ADULT = [[*range(18, 10, -1), *range(21, 29)], [*range(48, 40, -1), *range(31, 39)]]
CHILD = [[*range(55, 50, -1), *range(61, 66)], [*range(85, 80, -1), *range(71, 76)]]
TEETH = {str(n) for arch in ADULT + CHILD for n in arch}
PROCEDURES = ('Restauração', 'Extração', 'Implante', 'Tratamento de canal', 'Coroa', 'Prótese', 'Selante', 'Profilaxia', 'Raspagem', 'Clareamento', 'Cirurgia', 'Ajuste oclusal', 'Outro')
SURFACES = ('Dente inteiro', 'Oclusal / incisal', 'Mesial', 'Distal', 'Vestibular', 'Lingual / palatina', 'Múltiplas faces', 'Não se aplica')
QUESTIONS = {
    'Saúde geral': [
        ('treatment', 'Está em tratamento médico?'), ('medication', 'Usa medicamentos atualmente?'),
        ('allergy', 'Tem alergia a medicamentos ou materiais?'), ('anesthesia', 'Já teve reação à anestesia?'),
        ('hospital', 'Já foi hospitalizado ou fez cirurgia?'), ('bleeding', 'Tem sangramento prolongado ou alteração de coagulação?'),
        ('anticoagulant', 'Usa anticoagulantes ou antiagregantes?'), ('healing', 'Tem dificuldade de cicatrização?'),
        ('bisphosphonate', 'Usa ou usou bisfosfonatos / medicamentos para os ossos?'),
    ],
    'Condições de saúde': [
        ('heart', 'Tem doença cardíaca?'), ('pressure', 'Tem hipertensão?'), ('diabetes', 'Tem diabetes?'),
        ('respiratory', 'Tem asma ou outra doença respiratória?'), ('kidney', 'Tem doença renal?'),
        ('liver', 'Tem doença no fígado / hepatite?'), ('epilepsy', 'Tem epilepsia ou convulsões?'),
        ('thyroid', 'Tem doença da tireoide?'), ('immune', 'Tem doença ou tratamento que afeta a imunidade?'),
        ('cancer', 'Teve câncer, quimioterapia ou radioterapia?'), ('infectious', 'Tem doença infectocontagiosa?'),
        ('joint', 'Tem doença reumática ou articular?'), ('pregnant', 'Está grávida ou há possibilidade de gravidez?'),
        ('breastfeeding', 'Está amamentando?'), ('other', 'Tem outra condição de saúde relevante?'),
    ],
    'Hábitos e sintomas': [
        ('smoking', 'Fuma ou usa produtos com nicotina?'), ('alcohol', 'Consome bebidas alcoólicas?'),
        ('drugs', 'Usa outras substâncias?'), ('bruxism', 'Range ou aperta os dentes?'),
        ('snoring', 'Ronca ou tem apneia do sono?'), ('drymouth', 'Sente a boca seca?'),
        ('pain', 'Sente dor nos dentes ou na boca?'), ('sensitivity', 'Tem sensibilidade dentária?'),
        ('gumbleeding', 'A gengiva sangra?'), ('tmj', 'Tem dor, estalos ou dificuldade para abrir a boca?'),
        ('lesion', 'Percebe feridas ou alterações na boca?'), ('anxiety', 'Tem medo ou ansiedade no atendimento?'),
    ],
    'Histórico odontológico e infantil': [
        ('previous', 'Já realizou tratamento odontológico?'), ('complication', 'Teve complicação em tratamento anterior?'),
        ('prosthesis', 'Usa prótese, aparelho ou possui implantes?'), ('floss', 'Usa fio dental?'),
        ('thumb', 'Tem hábito de chupar dedo ou chupeta?'), ('bottle', 'Usa mamadeira, especialmente à noite?'),
        ('mouthbreathing', 'Respira predominantemente pela boca?'), ('trauma', 'Já sofreu trauma nos dentes ou face?'),
    ],
}
QUESTION_IDS = {key for group in QUESTIONS.values() for key, _ in group}


class ClinicalStore:
    def init_clinical(self):
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS anamnesis(patient TEXT PRIMARY KEY REFERENCES patients(id), data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS procedures(id INTEGER PRIMARY KEY AUTOINCREMENT, patient TEXT NOT NULL REFERENCES patients(id), target TEXT NOT NULL, kind TEXT NOT NULL, surface TEXT NOT NULL, status TEXT NOT NULL, body TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        ''')
        self.db.commit()

    def anamnesis(self, patient):
        row = self.db.execute('SELECT data FROM anamnesis WHERE patient=?', (patient,)).fetchone()
        return json.loads(row[0]) if row else {}

    def save_anamnesis(self, patient, data):
        if any(key not in QUESTION_IDS for key in data.get('answers', {})):
            raise ValueError('Pergunta de anamnese inválida.')
        for answer in data.get('answers', {}).values():
            if answer.get('value') not in ('Sim', 'Não', 'Não se aplica', 'Não informado'):
                raise ValueError('Resposta inválida.')
        self.db.execute('INSERT INTO anamnesis VALUES(?,?) ON CONFLICT(patient) DO UPDATE SET data=excluded.data', (patient, json.dumps(data, ensure_ascii=False)))
        self.db.commit()

    def add_procedure(self, patient, target, kind, surface, status, body):
        if target not in TEETH | {'Boca'} or kind not in PROCEDURES or surface not in SURFACES or status not in ('Planejado', 'Realizado'):
            raise ValueError('Procedimento inválido.')
        if target == 'Boca' and kind in ('Extração', 'Implante'):
            raise ValueError('Selecione um dente para registrar extração ou implante.')
        self.db.execute('INSERT INTO procedures(patient,target,kind,surface,status,body) VALUES(?,?,?,?,?,?)', (patient, target, kind, surface, status, body.strip()))
        self.db.commit()

    def procedures(self, patient, target=None):
        if target is not None:
            return self.db.execute('SELECT target,kind,surface,status,body,created FROM procedures WHERE patient=? AND target=? ORDER BY id', (patient, target)).fetchall()
        return self.db.execute('SELECT target,kind,surface,status,body,created FROM procedures WHERE patient=? ORDER BY id', (patient,)).fetchall()

    def tooth_state(self, patient, target):
        state, completed, planned = 'Dente', False, False
        for _, kind, _, status, _, _ in self.procedures(patient, target):
            if status == 'Planejado':
                planned = True
                continue
            completed = True
            if kind == 'Extração':
                state = 'Extraído'
            elif kind == 'Implante':
                state = 'Implante'
        return state, completed, planned
