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
        vehicul = env.ref('construction_site.fleet_vehicle_truck')
        for proiect in proiecte:
            toate_sarcinile = proiect.tasks
            for sarcina in toate_sarcinile:
                # Sub-sarcini
                env['project.task'].create(
                    {'name': f'Sub-sarcină pentru {sarcina.name}', 'project_id': proiect.id, 'parent_id': sarcina.id})

                # Adăugare resurse la sarcină
                sarcina.write({
                    'task_transport_ids': [
                        (0, 0, {'transport_id': vehicul.id, 'planned_kms': random.uniform(50, 300)})],
                })

        return res
