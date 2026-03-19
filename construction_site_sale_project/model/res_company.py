from odoo import models, fields, _
from odoo.exceptions import UserError
import random
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    def _generate_construction_demo_data(self):
        res = super()._generate_construction_demo_data()
        env = self.env
        Partener = env['res.partner']
        produs_serviciu = env.ref('construction_site.product_template_construction_service').product_variant_id
        clienti_demo = Partener.search([('is_company', '=', True)], limit=2)
        categorie_proiect = env.ref('construction_site.project_category_rezidential')
        materiale = env['product.product'].search([('id', 'in', [
            env.ref('construction_site.product_product_cement').id,
            env.ref('construction_site.product_product_rebar').id,
            env.ref('construction_site.product_product_gravel').id,
            env.ref('construction_site.product_product_bricks').id
        ])])
        consume_location = env.ref('construction_site.consume_location')
        consume_type_id = env.ref('construction_site.picking_type_consume')

        # --- VÂNZĂRI & CREARE PROIECTE ---
        comenzi_de_confirmat = []
        for i in range(20):
            client = random.choice(clienti_demo)
            order_lines = []

            # Linia principală
            order_lines.append(
                (0, 0, {
                    'product_id': produs_serviciu.id,
                    'name': f'Management Șantier {i + 1}',
                    'product_uom_qty': 1
                })
            )

            # Obiective + Servicii aferente
            for j in range(10):
                # Secțiune Obiectiv
                order_lines.append(
                    (0, 0, {
                        'display_type': 'line_section',
                        'name': f'Obiectiv {j + 1}'
                    })
                )

                # Serviciu aferent
                order_lines.append(
                    (0, 0, {
                        'product_id': produs_serviciu.id,
                        'name': f'Detalii Obiectiv {j + 1}',
                        'product_uom_qty': random.randint(20, 100),
                        'price_unit': round(random.uniform(50, 500), 2)  # rotunjit la 2 zecimale
                    })
                )

            # Crearea comenzii
            comanda = env['sale.order'].create({
                'partner_id': client.id,
                'obiectiv': f'Complex Rezidențial Demo {i + 1}',
                'order_line': order_lines
            })
            if i < 17:
                comenzi_de_confirmat.append(comanda)

        for comanda in comenzi_de_confirmat:
            comanda.action_confirm()

        proiecte = env['project.project'].search([('sale_order_id', 'in', [so.id for so in comenzi_de_confirmat])])
        proiecte.write({'category_id': categorie_proiect.id})  # Asignează o categorie
        _logger.info(f"S-au creat și confirmat {len(proiecte)} proiecte.")

        # --- DETALIERE PROIECTE (SARCINI, RESURSE, ETC.) ---
        for proiect in proiecte:
            pricelists = env['product.pricelist'].search([], limit=1)
            if pricelists:
                proiect.write({
                    'consume_loc_id': consume_location.id,
                    'consume_type_id': consume_type_id.id,
                    'partner_id': proiect.sale_order_id.partner_id.id,
                    'pricelist_id': pricelists.id,
                })
            else:
                # Handle case when no pricelist exists
                raise UserError("No pricelist found. Please configure at least one pricelist.")

            proiect.createLogistic()
            toate_sarcinile = proiect.tasks
            for sarcina in toate_sarcinile:
                # Sub-sarcini
                env['project.task'].create(
                    {'name': f'Sub-sarcină pentru {sarcina.name}', 'project_id': proiect.id, 'parent_id': sarcina.id})

                # Adăugare resurse la sarcină
                sarcina.write({
                    'task_product_ids': [(0, 0, {'product_id': p_id, 'planned_qty': random.uniform(10, 200)}) for p_id
                                         in random.sample(materiale.ids, min(len(materiale), 4))],
                })
                # Consum și Facturare
                wiz_consum = env['project.task.product.consume.wizard'].with_context(default_task_id=sarcina.id).create(
                    {})
                for linie in wiz_consum.product_ids:
                    linie.quantity = linie.max_limit * random.uniform(0.4, 0.8)
                wiz_consum.execute()

                wiz_factura = env['project.site.invoice'].with_context(default_task_id=sarcina.id).create({
                    'project_id':proiect.id,
                })
                wiz_factura.executeInvoicing()
                if wiz_factura.invoice_id:
                    wiz_factura.invoice_id.action_post()

        return res
