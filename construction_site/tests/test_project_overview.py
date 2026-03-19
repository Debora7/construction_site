# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase

class TestProjectOverview(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.project = cls.env['project.project'].create({
            'name': 'Test Project',
            'is_construction_site': True,
        })
        cls.analytic = cls.project.auto_account_id
        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'company_id': cls.company.id,
        })
        cls.purchase_order_line = cls.env['purchase.order.line'].create({
            'order_id': cls.purchase_order.id,
            'product_id': cls.env['product.product'].create({'name': 'Test Product', 'type': 'consu'}).id,
            'product_uom_qty': 1,
            'price_unit': 10,
            'name': 'Test POL',
            # 'auto_analytic_id': cls.analytic.id,
        })

    def test_compute_purchase_order_ids_for_non_construction_site(self):
        self.project.is_construction_site = False
        self.project._computePurchaseOrder()
        self.assertIn(self.purchase_order, self.project.purchase_order_ids)