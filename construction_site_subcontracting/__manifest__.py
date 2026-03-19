# -*- coding: utf-8 -*-
{
  'name':'Construction site subcontracting',
  'description': "",
  'version':'19.0.0.0.0',
  'author':'Dakai SOFT',
  'website': 'https://dakai.ro',
  'maintainers': ["adrian-dks"],
  'license': 'OPL-1',
  'installable': True,
  'data': [
    'security/ir.model.access.csv',
    'views/project_view.xml',
    'reports/report_subcontracting.xml',
    'reports/project_cost_structure.xml',
    ],
  'category': '',
  'depends': ['construction_site','smart_contract'],
}
