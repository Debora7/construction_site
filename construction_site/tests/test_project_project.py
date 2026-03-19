# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase

class TestProjectProject(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.category = cls.env['project.category'].create({'name': 'Test Category'})
        cls.project = cls.env['project.project'].create({
            'name': 'Test Construction Project',
            'is_construction_site': True,
            'partner_id': cls.partner.id,
            'category_id': cls.category.id,
        })

    def test_site_management_task_created(self):
        management_task = self.env['project.task'].search([
            ('project_id', '=', self.project.id),
            ('site_management', '=', True)
        ])
        self.assertTrue(management_task, "Site management task should be created for construction site projects.")

    def test_destroy_management_task_on_unset_construction_site(self):
        self.project.write({'is_construction_site': False})
        management_task = self.env['project.task'].search([
            ('project_id', '=', self.project.id),
            ('site_management', '=', True)
        ])
        self.assertFalse(management_task, "Site management task should be removed when project is no longer a construction site.")

    def test_pricelist_computed_from_partner(self):
        pricelist = self.env['product.pricelist'].create({'name': 'Test Pricelist'})
        self.partner.property_product_pricelist = pricelist.id
        project = self.env['project.project'].create({
            'name': 'Test Project 2',
            'partner_id': self.partner.id,
        })
        self.assertEqual(project.pricelist_id, pricelist, "Pricelist should be computed from partner.")

    def test_consume_products_raises_on_multiple(self):
        project2 = self.env['project.project'].create({'name': 'Another Project'})
        with self.assertRaises(Exception):
            (self.project + project2).consumeProducts()