# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase
from odoo import fields
from datetime import datetime


class TestProcurementGroupStockRule(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.project = cls.env['project.project'].create({'name': 'Test Project'})
        cls.task = cls.env['project.task'].create({'name': 'Test Task', 'project_id': cls.project.id})
        cls.product = cls.env['product.product'].create({'name': 'Test Product', 'type': 'consu'})
        cls.picking_type = cls.env['stock.picking.type'].search([], limit=1)
        cls.route = cls.env['stock.route'].create({
            'name': 'Test Route',
            'company_id': cls.company.id,
        })
        cls.location_src = cls.env['stock.location'].create({
            'name': 'Test Source Location',
            'usage': 'internal',
            'company_id': cls.company.id,
        })

        cls.location_dest = cls.env['stock.location'].create({
            'name': 'Test Destination Location',
            'usage': 'internal',
            'company_id': cls.company.id,
        })

        cls.rule = cls.env['stock.rule'].create({
            'name': 'Test Rule',
            'action': 'pull',
            'picking_type_id': cls.picking_type.id,
            'location_dest_id': cls.picking_type.default_location_dest_id.id,
            'route_id': cls.route.id,
        })

    def test_get_stock_move_values_includes_task_id(self):
        values = {
            'task_id': self.task,
            'date_planned': datetime.now(),
        }
        res = self.rule._get_stock_move_values(
            self.product,
            1,
            self.product.uom_id,
            self.location_src,
            'Test Move',
            'Origin',
            self.company.id,
            values
        )

        self.assertEqual(res['task_id'], self.task)

    def test_get_stock_move_values_includes_task_product_ids_from_int(self):
        # Creează task product
        task_product = self.env['project.task.product'].create({
            'task_id': self.task.id,
            'product_id': self.product.id,
            'planned_qty': 1,
        })

        values = {
            'task_product_id': task_product.id,
            'date_planned': datetime.now(),
        }

        res = self.rule._get_stock_move_values(
            self.product,
            1,
            self.product.uom_id,
            self.location_src,
            'Test Move',
            'Origin',
            self.company.id,
            values
        )
        self.assertIn('task_product_ids', res)
        self.assertTrue(any(tp[1] == task_product.id for tp in res['task_product_ids']))

    def test_get_stock_move_values_includes_task_product_ids_from_list(self):
        task_product = self.env['project.task.product'].create({
            'task_id': self.task.id,
            'product_id': self.product.id,
            'planned_qty': 1,
        })
        values = {
            'task_product_ids': [(4, task_product.id)],
            'date_planned': datetime.now(),
        }
        res = self.rule._get_stock_move_values(
            self.product,
            1,
            self.product.uom_id,
            self.location_src,
            'Test Move',
            'Origin',
            self.company.id,
            values
        )
        self.assertIn('task_product_ids', res)
        self.assertTrue(any(tp[1] == task_product.id for tp in res['task_product_ids']))

    def test_update_purchase_order_line_sets_task_fields(self):
        task_product = self.env['project.task.product'].create({
            'task_id': self.task.id,
            'product_id': self.product.id,
            'planned_qty': 2,
        })

        supplierinfo = self.env['product.supplierinfo'].create({
            'partner_id': self.partner.id,
            'product_tmpl_id': self.product.product_tmpl_id.id,
        })

        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'picking_type_id': self.picking_type.id,
        })

        purchase_order_line = self.env['purchase.order.line'].create({
            'order_id': purchase_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 2,
            'price_unit': 10,
            'name': 'Test POL',
        })

        values = {
            'task_product_id': task_product,
            'supplier': supplierinfo,
        }

        res = self.rule._update_purchase_order_line(
            self.product,
            2,
            self.product.uom_id,
            self.company.id,
            values,
            purchase_order_line
        )

    def test_push_prepare_move_copy_values_copies_task_fields(self):
        task_product = self.env['project.task.product'].create({
            'task_id': self.task.id,
            'product_id': self.product.id,
            'planned_qty': 1,
        })
        move = self.env['stock.move'].create({
            # 'name': 'Move',
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
            'task_id': self.task.id,
            'task_product_ids': [(6, 0, [task_product.id])],
            'location_id': self.location_src.id,
            'location_dest_id': self.location_dest.id
        })
        res = self.rule._push_prepare_move_copy_values(move, fields.Date.today())
        self.assertEqual(res['task_id'], self.task.id)
        self.assertIn('task_product_ids', res)