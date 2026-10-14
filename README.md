# Consultório Dental — primeira versão

Aplicativo desktop para Windows com interface nativa Tkinter. Cadastro, anamnese, evoluções e anexos ficam em `%LOCALAPPDATA%\ConsultorioDental`. Prontuários e agenda funcionam sem internet. Nenhum dado é enviado à nuvem.

## Login local

No primeiro uso, crie seu usuário e senha (mínimo de 8 caracteres). O acesso fica neste computador, com hash PBKDF2-SHA256; não há senha padrão ou conta na internet. **Sair / bloquear** encerra a sessão. O login não criptografa o banco ou os exames. Guarde a senha: esta versão não oferece recuperação automática. O backup clínico não transporta o login nem substitui a senha do computador de destino.

## Anamnese e odontograma

Na ficha do paciente, abra **Anamnese**. São 44 perguntas em quatro categorias, com Sim, Não e Não se aplica e observações opcionais, além de dados básicos e queixa principal. Nenhuma resposta é preenchida automaticamente como Não. Salve a ficha antes de sair ou trocar de paciente. Este formulário deve ser revisado pelo profissional conforme seu protocolo clínico.

Em **Evolução → Odontograma / procedimento**, alterne entre os 32 dentes permanentes e os 20 decíduos, com numeração FDI. Clique em um dente para registrar procedimento, face, situação e descrição. Use **Boca / procedimento geral** para intervenções sem dente específico. O desenho recebe contorno verde após um procedimento realizado; procedimentos planejados ficam em amarelo. Extração realizada recebe X e implante realizado recebe desenho de parafuso. Os desenhos são esquemáticos, com formas distintas para grupos dentários. Todos os registros ficam no histórico do paciente e no backup. As faces são selecionadas em lista; esta versão não pinta cada face separadamente. O histórico é cumulativo; não há edição ou exclusão de registros clínicos nesta versão.

Backups anteriores continuam compatíveis; as novas tabelas são criadas ao restaurar, preservando o histórico antigo. Atualizar o EXE mantém os dados locais existentes.

## Aparência e navegação

Interface escura com menu lateral para Pacientes, Agenda e Backup. A lista de pacientes possui busca por nome ou contato; a ficha divide Cadastro, Evoluções e Exames em abas. Para atualizar o executável, gere-o novamente com `build-windows.bat` e substitua somente o EXE; os dados continuam na pasta local do usuário.

## Executar e gerar o EXE no Windows

Instale Python 3.12 para Windows (incluindo Tcl/Tk e o launcher `py`). Execute `build-windows.bat`. O resultado será `dist\ConsultorioDental.exe`, que abre uma janela própria. O EXE precisa ser gerado e validado no Windows; não foi produzido pelo ambiente Linux.

Para executar diretamente durante desenvolvimento:

```powershell
py -3 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

## Agenda local

Abra a aba **Agenda** e use **Criar consulta**, **Alterar selecionada** ou **Cancelar selecionada**. Informe data no formato DD/MM/AAAA e horários HH:MM. Cancelamentos permanecem visíveis no histórico. Os horários usam a hora local do computador. Não há contas, configuração de Google ou conexão com a internet para utilizar o programa.

A agenda fica no mesmo banco dos prontuários e acompanha o backup. Não há compartilhamento automático entre computadores nem bloqueio de horários sobrepostos nesta versão.

## Backup de todos os pacientes

Use **Backup de TODOS os pacientes** para criar um único `.dentalbackup` com todos os pacientes, prontuários, exames e consultas. Transfira o arquivo e use **Restaurar backup** no outro computador. A restauração substitui os dados e preserva um backup anterior ao lado da pasta de dados. Backups anteriores sem agenda continuam compatíveis; sua restauração deixa a agenda vazia.

O arquivo não é criptografado nesta versão. Proteja o computador e o dispositivo de backup, por exemplo com BitLocker. Faça backups regulares e teste a restauração antes de usar dados reais. Não há sincronização de prontuários entre computadores.

## Validação

```sh
python -m unittest discover -s tests -v
```

Esta é uma versão inicial: sem criptografia integrada ou controle de conflitos. Validar a interface e o executável no Windows antes do uso clínico.
