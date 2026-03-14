import json
import logging
from datetime import timedelta

from odoo import fields, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import Response, request

_logger = logging.getLogger(__name__)


class HospitalController(http.Controller):
    def _json_response(self, payload, status=200):
        return Response(
            json.dumps(payload),
            status=status,
            content_type='application/json;charset=utf-8',
        )

    @http.route('/hospital/checkin', type='http', auth='public', methods=['POST'], csrf=False)
    def hospital_checkin(self, **kwargs):
        try:
            payload = request.get_json_data() or {}
            if not payload:
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Payload JSON invalido ou vazio.',
                    },
                    status=400,
                )

            patient_model = request.env['res.partner'].sudo()
            bed_model = request.env['hospital.leito'].sudo()
            schedule_model = request.env['hospital.agendamento'].sudo()

            patient_name = payload.get('nome')
            patient_email = payload.get('email')
            patient_phone = payload.get('telefone')
            if not patient_name:
                return self._json_response(
                    {
                        'success': False,
                        'message': "Campo obrigatorio ausente: 'nome'.",
                    },
                    status=400,
                )

            patient_domain = [('is_patient', '=', True)]
            if patient_email:
                patient_domain.append(('email', '=', patient_email))
            elif patient_phone:
                patient_domain.append(('phone', '=', patient_phone))
            else:
                patient_domain.append(('name', '=', patient_name))

            patient = patient_model.search(patient_domain, limit=1)
            patient_vals = {
                'name': patient_name,
                'email': patient_email,
                'phone': patient_phone,
                'is_patient': True,
                'company_type': 'person',
                'sexo': payload.get('sexo'),
                'tipo_sanguineo': payload.get('tipo_sanguineo'),
                'data_nascimento': payload.get('data_nascimento'),
                'status_atendimento': 'em_atendimento',
            }
            patient_vals = {k: v for k, v in patient_vals.items() if v not in (None, '')}

            if patient:
                patient.write(patient_vals)
            else:
                patient = patient_model.create(patient_vals)

            bed_domain = [('status', '=', 'livre')]
            bed_type = payload.get('tipo_leito')
            if bed_type:
                bed_domain.append(('tipo', '=', bed_type))

            bed = bed_model.search(bed_domain, order='id asc', limit=1)
            if not bed:
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Nenhum leito livre disponivel para o tipo informado.',
                    },
                    status=409,
                )

            duration_hours = int(payload.get('duracao_horas', 24))
            if duration_hours <= 0:
                return self._json_response(
                    {
                        'success': False,
                        'message': "'duracao_horas' deve ser maior que zero.",
                    },
                    status=400,
                )

            data_inicio = fields.Datetime.now()
            data_fim = data_inicio + timedelta(hours=duration_hours)

            schedule = schedule_model.create({
                'paciente_id': patient.id,
                'leito_id': bed.id,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'status': 'agendado',
                'observacoes': payload.get(
                    'observacoes',
                    'Check-in automatico via endpoint /hospital/checkin.',
                ),
            })
            schedule.action_confirmar()

            return self._json_response(
                {
                    'success': True,
                    'message': 'Check-in realizado com sucesso.',
                    'paciente_id': patient.id,
                    'leito_id': bed.id,
                    'agendamento_id': schedule.id,
                    'data_inicio': fields.Datetime.to_string(data_inicio),
                    'data_fim': fields.Datetime.to_string(data_fim),
                }
            )
        except (ValidationError, UserError) as exc:
            return self._json_response(
                {
                    'success': False,
                    'message': str(exc),
                },
                status=400,
            )
        except Exception:
            _logger.exception('Erro inesperado ao processar check-in.')
            return self._json_response(
                {
                    'success': False,
                    'message': 'Erro interno ao processar check-in.',
                },
                status=500,
            )

