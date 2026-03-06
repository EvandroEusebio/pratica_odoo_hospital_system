from odoo import models, fields

class HospitalLeito(models.Model):
     _name = 'hospital.leito'
     _description = 'Hospital Leito'
     
     name = fields.Char(string='Nome do Leito', required=True)
          
     status = fields.Selection([('livre', 'Livre'), ('ocupado', 'Ocupado'), ('manuntencao', 'Manuntencao')], string='Status', default='livre')
     
     tipo = fields.Selection([('uti', 'UTI'), ('enfermaria', 'Enfermaria'), ('privado', 'Privado')], string='Tipo de leito', required=True)

