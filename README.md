# Consultório Dental — primeira versão

Aplicativo desktop para Windows com interface nativa Tkinter. Cadastro, anamnese, evoluções e anexos ficam em `%LOCALAPPDATA%\ConsultorioDental`. Prontuários e agenda funcionam sem internet. Nenhum dado é enviado à nuvem.

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

Esta é uma versão inicial: sem odontograma gráfico, login próprio, criptografia integrada ou controle de conflitos. Validar a interface e o executável no Windows antes do uso clínico.
