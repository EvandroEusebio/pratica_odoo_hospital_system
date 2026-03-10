from odoo import models, fields


class HospitalLeito(models.Model):
     _name = 'hospital.leito'
     _description = 'Leito Hospitalar'

     name = fields.Char(string='Nome do Leito', required=True)
     status = fields.Selection(
          [
               ('livre', 'Livre'),
               ('ocupado', 'Ocupado'),
               ('manutencao', 'Manutenção'),
               ('alta', 'Alta'),
          ],
          string='Status',
          default='livre',
          required=True,
     )
     tipo = fields.Selection(
          [
               ('uti', 'UTI'),
               ('enfermaria', 'Enfermaria'),
               ('privado', 'Privado'),
          ],
          string='Tipo de Leito',
          required=True,
     )
     observacao = fields.Text(string='Observações')

