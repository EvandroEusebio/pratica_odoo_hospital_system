from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class HospitalAgendamento(models.Model):
    _name = 'hospital.agendamento'
    _description = 'Agendamento de Leito'
    _order = 'data_inicio desc'

    name = fields.Char(
        string='Referência',
        compute='_compute_name',
        store=True,
    )

    paciente_id = fields.Many2one(
        'res.partner',
        string='Paciente',
        domain=[('is_patient', '=', True)],
        required=True,
    )

    leito_id = fields.Many2one(
        'hospital.leito',
        string='Leito',
        required=True,
    )

    data_inicio = fields.Datetime(string='Início', required=True)
    data_fim = fields.Datetime(string='Fim', required=True)

    status = fields.Selection(
        [
            ('agendado', 'Agendado'),
            ('em_uso', 'Em Uso'),
            ('concluido', 'Concluído'),
            ('cancelado', 'Cancelado'),
        ],
        string='Status',
        default='agendado',
        required=True,
    )

    observacoes = fields.Text(string='Observações')

    # ──────────────────────────────────────────────
    # Compute
    # ──────────────────────────────────────────────

    @api.depends('paciente_id', 'leito_id', 'data_inicio')
    def _compute_name(self):
        for rec in self:
            if rec.paciente_id and rec.leito_id and rec.data_inicio:
                rec.name = (
                    f"{rec.paciente_id.name} – "
                    f"{rec.leito_id.name} – "
                    f"{rec.data_inicio.strftime('%d/%m/%Y %H:%M')}"
                )
            else:
                rec.name = 'Novo Agendamento'

    # ──────────────────────────────────────────────
    # Constraints
    # ──────────────────────────────────────────────

    @api.constrains('data_inicio', 'data_fim')
    def _check_datas(self):
        for rec in self:
            if rec.data_fim <= rec.data_inicio:
                raise ValidationError(
                    "A data/hora de fim deve ser posterior à data/hora de início."
                )

    @api.constrains('leito_id', 'data_inicio', 'data_fim', 'status')
    def _check_disponibilidade(self):
        for rec in self:
            if rec.status not in ('agendado', 'em_uso'):
                continue
            conflitos = self.search([
                ('id', '!=', rec.id),
                ('leito_id', '=', rec.leito_id.id),
                ('status', 'in', ['agendado', 'em_uso']),
                ('data_inicio', '<', rec.data_fim),
                ('data_fim', '>', rec.data_inicio),
            ])
            if conflitos:
                raise ValidationError(
                    f"O leito '{rec.leito_id.name}' já possui um agendamento "
                    f"conflitante no período solicitado."
                )

    # ──────────────────────────────────────────────
    # Manual actions (buttons)
    # ──────────────────────────────────────────────

    def action_confirmar(self):
        for rec in self:
            rec.status = 'em_uso'
            rec.leito_id.status = 'ocupado'
            rec.paciente_id.leito_id = rec.leito_id
            rec.paciente_id.status_atendimento = 'internado'

    def _check_unpaid_invoices(self):
        """Verifica se o paciente possui faturas não pagas."""
        for rec in self:
            unpaid_invoices = self.env['account.move'].search([
                ('partner_id', '=', rec.paciente_id.id),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('state', '=', 'posted'),
            ])
            if unpaid_invoices:
                invoice_refs = ', '.join([inv.name for inv in unpaid_invoices])
                raise UserError(
                    f"Não é possível dar alta ao paciente {rec.paciente_id.name}. "
                    f"Existem faturas não pagas: {invoice_refs}"
                )

    def action_liberar(self):
        """Libera o leito e registra a alta do paciente."""
        for rec in self:
            # Valida se há faturas não pagas
            rec._check_unpaid_invoices()
            
            rec.status = 'concluido'
            rec.leito_id.status = 'livre'
            rec.paciente_id.leito_id = False
            rec.paciente_id.status_atendimento = 'alta'

    def action_cancelar(self):
        for rec in self:
            if rec.status == 'em_uso':
                rec.leito_id.status = 'livre'
            rec.status = 'cancelado'

    # ──────────────────────────────────────────────
    # Cron
    # ──────────────────────────────────────────────

    @api.model
    def _cron_atualizar_status_leitos(self):
        """Atualiza automaticamente o status dos leitos conforme horário agendado."""
        now = fields.Datetime.now()

        # Iniciar ocupações cujo horário de início já passou
        agendamentos_iniciar = self.search([
            ('status', '=', 'agendado'),
            ('data_inicio', '<=', now),
        ])
        agendamentos_iniciar.action_confirmar()

        # Finalizar ocupações cujo horário de fim já passou
        agendamentos_finalizar = self.search([
            ('status', '=', 'em_uso'),
            ('data_fim', '<=', now),
        ])
        agendamentos_finalizar.action_liberar()
