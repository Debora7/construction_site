# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase
from odoo import fields

class TestProductProduct(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.category = cls.env['product.category'].create({'name': 'Test Category'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu',
            'categ_id': cls.category.id,
        })
        cls.project = cls.env['project.project'].create({'name': 'Test Project'})
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'currency_id': cls.env.ref('base.EUR').id,
        })
        cls.site_procurement = cls.env['project.site.procurement'].create({
            'project_id': cls.project.id,
        })
        cls.project.pricelist_id = cls.pricelist.id

    def test_get_domain_locations_adds_task_id_to_domain(self):
        task = self.env['project.task'].create({'name': 'Task', 'project_id': self.project.id})
        with self.env.cr.savepoint():
            domains = self.product.with_context(task=task.id)._get_domain_locations()
            self.assertIn(('task_id', '=', task.id), domains[1])
            self.assertIn(('task_id', '=', task.id), domains[2])

    def test_select_seller_creates_supplierinfo_when_missing(self):
        self.product.seller_ids.unlink()
        self.site_procurement.project_id.pricelist_id = self.pricelist
        supp = self.product.with_context(procurement_source_id=self.site_procurement.id)._select_seller(
            partner_id=self.partner, quantity=1)
        self.assertTrue(supp)
        self.assertEqual(supp.partner_id, self.partner)
        self.assertEqual(supp.currency_id, self.pricelist.currency_id)
        self.assertEqual(supp.product_uom_id, self.product.uom_id)
        self.assertEqual(supp.product_tmpl_id, self.product.product_tmpl_id)