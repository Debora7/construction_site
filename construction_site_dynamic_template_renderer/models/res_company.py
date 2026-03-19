import random
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _generate_construction_demo_data(self):
        res = super()._generate_construction_demo_data()
        env = self.env
        proiecte = env['project.project'].search([('is_construction_site', '=', True)])
        sablon_doc = env.ref('construction_site.demo_document_template_opis')
        for proiect in proiecte:
            toate_sarcinile = proiect.tasks
            for sarcina in toate_sarcinile:
                # Sub-sarcini
                env['project.task'].create(
                    {'name': f'Sub-sarcină pentru {sarcina.name}', 'project_id': proiect.id, 'parent_id': sarcina.id})

                # Adăugare resurse la sarcină
                sarcina.write({
                    'document_template_ids': [(4, sablon_doc.id)]
                })
                sarcina._onchange_document_templates()  # Pentru a genera parametrii OPIS
        return res
