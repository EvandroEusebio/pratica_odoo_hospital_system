{
    'name': "Hospital Management",
    'summary': "Gestão de leitos e prontuários usando contatos do Odoo",
    'description': """
Módulo para gerenciamento hospitalar com foco em:
- Leitos com fluxo visual por status (kanban: Livre → Ocupado → Alta)
- Cadastro de pacientes usando contatos do Odoo com campos clínicos (prontuário)
    """,
    'author': "Hospital Team",
    'website': "https://example.com",
    'category': 'Healthcare',
    'version': '1.2.0',

    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

