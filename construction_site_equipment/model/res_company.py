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
        echipamente = env.ref('construction_site_equipment.equipment_excavator') | env.ref('construction_site_equipment.equipment_crane')

        for proiect in proiecte:
            toate_sarcinile = proiect.tasks
            for sarcina in toate_sarcinile:
                # Sub-sarcini
                env['project.task'].create(
                    {'name': f'Sub-sarcină pentru {sarcina.name}', 'project_id': proiect.id, 'parent_id': sarcina.id})

                # Adăugare resurse la sarcină
                sarcina.write({
                    'task_equipment_ids': [(0, 0, {'equipment_id': e_id, 'planned_hours': random.uniform(10, 50)}) for
                                           e_id in echipamente.ids]
                })

        return res
