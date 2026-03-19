# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase
from odoo.exceptions import UserError

class TestProjectWarehouse(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['project.category'].create({
            'name': 'Test Category',
            'project_sequence_id': cls.env['ir.sequence'].create({'name': 'Test Seq'}).id,
        })
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.supply_warehouse = cls.env['stock.warehouse'].create({'name': 'Supply WH', 'code': 'SWH'})
        cls.consume_loc = cls.env['stock.location'].create({'name': 'Consume Loc', 'usage': 'internal'})
        cls.consume_type = cls.env['stock.picking.type'].create({'name': 'Consume Type', 'sequence_code': 'SPT'})
        cls.project = cls.env['project.project'].create({
            'name': 'Test Project',
            'category_id': cls.category.id,
            'supply_warehouse_id': cls.supply_warehouse.id,
            'consume_loc_id': cls.consume_loc.id,
            'consume_type_id': cls.consume_type.id,
            'partner_id': cls.partner.id,
        })

    def test_create_logistic_creates_warehouse(self):
        self.project.createLogistic()
        self.assertTrue(self.project.warehouse_id)
        self.assertTrue(self.project.warehouse_id.is_construction_site)
        self.assertEqual(self.project.warehouse_id.project_id, self.project)
        self.assertIn('[%s]' % self.project.warehouse_id.code, self.project.name)

    def test_create_logistic_missing_category_raises(self):
        project = self.env['project.project'].create({
            'name': 'No Category',
            'supply_warehouse_id': self.supply_warehouse.id,
            'consume_loc_id': self.consume_loc.id,
            'consume_type_id': self.consume_type.id,
            'partner_id': self.partner.id,
        })
        with self.assertRaises(UserError):
            project.createLogistic()

    def test_unlink_construction_warehouse_with_project_raises(self):
        self.project.createLogistic()
        warehouse = self.project.warehouse_id
        with self.assertRaises(UserError):
            warehouse.unlink()

    # def test_unlink_non_construction_warehouse(self):
    #     wh = self.env['stock.warehouse'].create({'name': 'Normal WH', 'code': 'NWH'})
    #     wh.unlink()
    #     self.assertFalse(self.env['stock.warehouse'].search([('name', '=', 'Normal WH')]))