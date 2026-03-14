# pratica_odoo_hospital_system

Projeto de pratica com Odoo 18 para gestao hospitalar.

## Objetivo do dia

- Integracao externa via XML-RPC com leitura de `exame_laboratorial.json`.
- Integracao interna via endpoint HTTP `POST /hospital/checkin` para check-in automatico.

## 1) Integracao externa (XML-RPC)

Arquivo do script:

- `scripts/integracao_externa_xmlrpc.py`

Arquivo de entrada (exemplo):

- `exame_laboratorial.json`

### O que o script faz

- Le o JSON de exames laboratoriais.
- Faz autenticacao no Odoo via XML-RPC.
- Cria ou atualiza paciente (`res.partner` com `is_patient=True`).
- Anexa o exame como `ir.attachment` e vincula em `laudo_ids`.

### Execucao

```bash
python3 scripts/integracao_externa_xmlrpc.py \
	--url http://localhost:8070 \
	--db <SEU_BANCO> \
	--user admin \
	--password admin \
	--json-path exame_laboratorial.json
```

## 2) Integracao interna (HTTP Controller)

Endpoint implementado:

- `POST /hospital/checkin`

Arquivo:

- `addons/hospital_mgmt/controllers/controllers.py`

### Comportamento automatico

- Recebe dados do paciente via JSON.
- Cria/atualiza paciente automaticamente.
- Busca leito livre (com filtro opcional por tipo).
- Cria agendamento imediato e confirma (`action_confirmar`).
- Retorna IDs de paciente, leito e agendamento.

### Payload JSON (exemplo)

```json
{
	"nome": "Maria Oliveira",
	"email": "maria.oliveira@example.com",
	"telefone": "+55 11 98888-7777",
	"data_nascimento": "1994-09-02",
	"sexo": "feminino",
	"tipo_sanguineo": "a+",
	"tipo_leito": "enfermaria",
	"duracao_horas": 24,
	"observacoes": "Check-in vindo de sistema de triagem."
}
```

### Chamada com curl

```bash
curl -X POST http://localhost:8070/hospital/checkin \
	-H "Content-Type: application/json" \
	-d '{
		"nome": "Maria Oliveira",
		"email": "maria.oliveira@example.com",
		"telefone": "+55 11 98888-7777",
		"tipo_leito": "enfermaria",
		"duracao_horas": 24
	}'
```

### Resposta de sucesso (exemplo)

```json
{
	"success": true,
	"message": "Check-in realizado com sucesso.",
	"paciente_id": 25,
	"leito_id": 4,
	"agendamento_id": 18,
	"data_inicio": "2026-03-13 14:00:00",
	"data_fim": "2026-03-14 14:00:00"
}
```