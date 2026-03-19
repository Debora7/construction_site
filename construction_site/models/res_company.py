from odoo import models, fields, _
import random
import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_force_qty = fields.Boolean(string=_("Construction - Purchase Force Qty"), help=_("Generate purchase from procurment regardless supply warehouse stock."))

    def _generate_construction_demo_data(self):
        """
        Funcția chemată din XML pentru a genera datele demo complexe pentru toate modulele de șantier.
        """
        if self.env.company.id != self.id:
            # Rulează funcția doar pentru compania principală pentru a evita duplicarea
            return

        _logger.info("Pornire generare date demo complete pentru șantiere...")
        env = self.env

        # --- PREGĂTIRE DATE DE BAZĂ ---
        Partener = env['res.partner']
        clienti_demo = Partener.search([('is_company', '=', True)], limit=2)
        furnizori_demo = Partener.search([('is_company', '=', True), ('id', 'not in', clienti_demo.ids)], limit=2)

        # Referințe către datele statice din XML
        materiale = env['product.product'].search([('id', 'in', [
            env.ref('construction_site.product_product_cement').id,
            env.ref('construction_site.product_product_rebar').id,
            env.ref('construction_site.product_product_gravel').id,
            env.ref('construction_site.product_product_bricks').id
        ])])



        # Asigurare furnizori pentru materiale
        for mat in materiale:
            if not mat.seller_ids:
                mat.write({'seller_ids': [
                    (0, 0, {'partner_id': random.choice(furnizori_demo).id, 'price': random.uniform(10, 200)})]})

        proiecte = env['project.project'].search([])
        for proiect in proiecte:
            # --- FLUXURI POST-CREARE ---

            sarcini_alese = random.sample(proiect.tasks.ids, min(len(proiect.tasks), 2))
            for sarcina_id in sarcini_alese:
                sarcina = env['project.task'].browse(sarcina_id)

                # Aprovizionare
                aprov = env['project.site.procurement'].create({'project_id': proiect.id, 'task_id': sarcina.id,
                                                                'procurement_type': random.choice(
                                                                    ['in_site', 'in_supply_warehouse'])})
                aprov.load_materials_planned()
                aprov.executeProcurement()

        # Procesare finală comenzi de achiziție
        achizitii = env['purchase.order'].search([('project_id', 'in', proiecte.ids)])
        for achizitie in achizitii.filtered(lambda p: p.state == 'draft'):
            achizitie.button_confirm()
            for picking in achizitie.picking_ids:
                picking.move_ids.write({'quantity': picking.move_ids.product_uom_qty})
                picking.button_validate()
            achizitie.action_create_invoice().action_post()

        _logger.info("Generarea datelor demo complete a fost finalizată cu succes.")
        return True