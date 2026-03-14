import argparse
import base64
import json
from datetime import datetime
from pathlib import Path
import xmlrpc.client


def parse_args():
    parser = argparse.ArgumentParser(
        description='Importa exames laboratoriais do JSON para o Odoo via XML-RPC.'
    )
    parser.add_argument('--url', default='http://localhost:8070', help='URL base do Odoo.')
    parser.add_argument('--db', default='odoo_db', help='Nome do banco de dados do Odoo.')
    parser.add_argument('--username', default='admin', help='Usuario de acesso ao Odoo.')
    parser.add_argument('--password', default='odoo', help='Senha do usuario Odoo.')
    parser.add_argument(
        '--json-path',
        default='exame_laboratorial.json',
        help='Caminho para o arquivo JSON com os exames.',
    )
    return parser.parse_args()


def load_exams(json_path):
    data = json.loads(Path(json_path).read_text(encoding='utf-8'))
    if isinstance(data, dict) and isinstance(data.get('exames'), list):
        return data['exames']
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    raise ValueError('Formato invalido para o arquivo de exames.')


def authenticate(url, db, username, password):
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise RuntimeError('Falha na autenticacao. Verifique URL, banco e credenciais.')
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return uid, models


def find_patient(models, db, uid, password, exam):
    domain = [['is_patient', '=', True]]
    if exam.get('email'):
        domain.append(['email', '=', exam['email']])
    elif exam.get('telefone'):
        domain.append(['phone', '=', exam['telefone']])
    else:
        domain.append(['name', '=', exam['nome']])

    result = models.execute_kw(
        db,
        uid,
        password,
        'res.partner',
        'search_read',
        [domain],
        {'fields': ['id'], 'limit': 1},
    )
    return result[0]['id'] if result else None


def upsert_patient(models, db, uid, password, exam):
    if not exam.get('nome'):
        raise ValueError("Cada exame precisa do campo obrigatorio 'nome'.")

    patient_id = find_patient(models, db, uid, password, exam)
    vals = {
        'name': exam.get('nome'),
        'email': exam.get('email'),
        'phone': exam.get('telefone'),
        'data_nascimento': exam.get('data_nascimento'),
        'sexo': exam.get('sexo'),
        'tipo_sanguineo': exam.get('tipo_sanguineo'),
        'diagnostico': exam.get('diagnostico'),
        'observacoes': exam.get('observacoes'),
        'is_patient': True,
        'company_type': 'person',
    }
    vals = {key: value for key, value in vals.items() if value not in (None, '')}

    if patient_id:
        models.execute_kw(db, uid, password, 'res.partner', 'write', [[patient_id], vals])
        return patient_id

    return models.execute_kw(db, uid, password, 'res.partner', 'create', [vals])


def attach_exam(models, db, uid, password, patient_id, exam):
    file_name = f"exame_laboratorial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    content = json.dumps(exam, ensure_ascii=False, indent=2).encode('utf-8')
    attachment_id = models.execute_kw(
        db,
        uid,
        password,
        'ir.attachment',
        'create',
        [{
            'name': file_name,
            'type': 'binary',
            'datas': base64.b64encode(content).decode('ascii'),
            'mimetype': 'application/json',
            'res_model': 'res.partner',
            'res_id': patient_id,
        }],
    )

    models.execute_kw(
        db,
        uid,
        password,
        'res.partner',
        'write',
        [[patient_id], {'laudo_ids': [(4, attachment_id)]}],
    )

    message = (
        f"Exame laboratorial importado via XML-RPC. "
        f"Diagnostico: {exam.get('diagnostico', 'Nao informado')}."
    )
    models.execute_kw(
        db,
        uid,
        password,
        'res.partner',
        'message_post',
        [[patient_id]],
        {'body': message},
    )

    return attachment_id


def main():
    args = parse_args()
    exams = load_exams(args.json_path)
    uid, models = authenticate(args.url, args.db, args.username, args.password)

    print(f'Autenticado com sucesso. UID: {uid}')
    print(f'Total de exames lidos: {len(exams)}')

    for exam in exams:
        patient_id = upsert_patient(models, args.db, uid, args.password, exam)
        attachment_id = attach_exam(models, args.db, uid, args.password, patient_id, exam)
        print(
            'Exame importado com sucesso '
            f'| paciente_id={patient_id} '
            f'| attachment_id={attachment_id}'
        )


if __name__ == '__main__':
    main()