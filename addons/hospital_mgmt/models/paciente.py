from odoo import models, fields


class HospitalPaciente(models.Model):
    _name = 'hospital.paciente'
    _description = 'Paciente'

    name = fields.Char(string='Nome do Paciente', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Telefone')
    data_nascimento = fields.Date(string='Data de Nascimento')
    sexo = fields.Selection([
        ('masculino', 'Masculino'),
        ('feminino', 'Feminino'),
        ('outro', 'Outro'),
    ], string='Sexo')
    
    tipo_sanguineo = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'), ('o+', 'O+'), ('o-', 'O-'),
    ], string='Tipo Sanguíneo')

    alergias = fields.Text(string='Alergias')
    historico_clinico = fields.Text(string='Histórico Clínico')
    diagnostico = fields.Text(string='Diagnóstico')
    prescricao = fields.Text(string='Prescrição')
    observacoes = fields.Text(string='Observações')

    status_atendimento = fields.Selection([
        ('em_atendimento', 'Em Atendimento'),
        ('internado', 'Internado'),
        ('alta', 'Alta'),
    ], string='Status do Atendimento', default='em_atendimento', required=True)

    leito_id = fields.Many2one(
        'hospital.leito',
        string='Leito',
        help='Leito associado ao paciente.',
    )