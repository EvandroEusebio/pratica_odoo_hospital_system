from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string='É Paciente', default=False, index=True)
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
    ], string='Status do Atendimento')

    leito_id = fields.Many2one(
        'hospital.leito',
        string='Leito',
        help='Leito associado ao paciente.',
    )

    laudo_ids = fields.Many2many(
        'ir.attachment',
        'res_partner_laudo_rel',
        'partner_id',
        'attachment_id',
        string='Laudos e Exames',
    )