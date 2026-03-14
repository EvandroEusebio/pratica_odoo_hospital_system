from odoo import models, api
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = 'crm.lead'          # estendendo o modelo padrão do CRM

    @api.constrains('stage_id')
    def _check_stage_requires_confirmed_quotation(self):
        """Bloqueia avanço de estágio se a cotação não estiver confirmada"""
        for lead in self:
            # o nome do estágio
            if lead.stage_id.name in ['Sala de espera', 'Atendimento / exames', 'laudos / Resultados', 'Tratamento/acompanhamento', 'Alta']:
                # Procura se existe pelo menos 1 Pedido de Venda confirmado
                # 1. Verifica se existe pelo menos 1 Pedido de Venda confirmado
                sale_orders = self.env['sale.order'].search([
                    ('opportunity_id', '=', lead.id),
                    ('state', 'in', ('sale', 'done'))
                ])

                if not sale_orders:
                    raise ValidationError(
                        "❌ Não é possível avançar!\n\n"
                        "É obrigatório ter uma Cotação confirmada primeiro."
                    )
            # 2. Verifica se pelo menos UMA fatura está PAGA
                has_paid_invoice = False
                for order in sale_orders:
                    for invoice in order.invoice_ids:           # faturas ligadas ao pedido
                        if invoice.payment_state == 'paid' or invoice.state == 'posted' and invoice.payment_state in ('paid', 'in_payment'):
                            has_paid_invoice = True
                            break
                    if has_paid_invoice:
                        break

                if not has_paid_invoice:
                    raise ValidationError(
                        "❌ Não é possível avançar para o estágio 'Encaminhado'!\n\n"
                        "É obrigatório ter pelo menos UMA fatura PAGA.\n"
                        "Registre o pagamento primeiro."
                    )
    def write(self, vals):
        """Depois que o estágio muda com sucesso, marca o contacto como Paciente"""
        res = super().write(vals)

        # Só age se o estágio foi alterado
        if 'stage_id' in vals:
            new_stage_name = self.env['crm.stage'].browse(vals['stage_id']).name

            if new_stage_name in ['Sala de espera', 'Atendimento / exames', 'laudos / Resultados', 'Tratamento/acompanhamento', 'Alta']:
                for lead in self:
                    if lead.partner_id:
                        lead.partner_id.is_patient = True
                        lead.partner_id.status_atendimento = "em_atendimento";
                        # Mensagem no chatter do contacto (opcional)
                        lead.partner_id.message_post(
                            body="✅ Lead avançou para " + new_stage_name + ". Agora marcado como Paciente."
                        )

        return res