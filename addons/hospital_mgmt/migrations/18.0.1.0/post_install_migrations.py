# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    Adicionar as colunas necessárias ao modelo res.partner.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Atualizar o registry para reconhecer os novos campos
    env['res.partner']._prepare_setup()
