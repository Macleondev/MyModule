# -*- coding: utf-8 -*-
{
    'name': "My Module",
    'summary': """Un módulo Odoo simple para consumir una API externa (JSONPlaceholder).""",
    'description': """
        Este módulo demuestra cómo integrar una API externa en Odoo,
        creando un modelo para almacenar los datos recibidos y
        una vista para visualizarlos.
    """,
    'author': "MacleonDev",
    'website': "http://www.macleondev.com",
    'category': 'Integración',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/api_view.xml',  
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}