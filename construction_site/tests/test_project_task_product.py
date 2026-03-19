# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase
from odoo import fields


class TestProjectTaskProduct(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.product = cls.env['product.product'].create({'name': 'Test Product', 'type': 'consu'})

        # Project și task
        cls.project = cls.env['project.project'].create({'name': 'Test Project', 'invoice_method': 'planned'})
        cls.task = cls.env['project.task'].create({'name': 'Test Task', 'project_id': cls.project.id})

        # Consum location
        cls.consume_loc = cls.env['stock.location'].create({'name': 'Consume'})
        cls.project.write({'consume_loc_id': cls.consume_loc.id})

        # Task product
        cls.task_product = cls.env['project.task.product'].create({
            'task_id': cls.task.id,
            'product_id': cls.product.id,
            'planned_qty': 5,
        })

        # Purchase order și line
        cls.picking_type = cls.env['stock.picking.type'].search([], limit=1)
        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'company_id': cls.company.id,
            'picking_type_id': cls.picking_type.id,
        })
        cls.purchase_order_line = cls.env['purchase.order.line'].create({
            'order_id': cls.purchase_order.id,
            'product_id': cls.product.id,
            'product_uom_qty': 5,
            'price_unit': 10,
            'name': 'Test POL',
        })
        cls.task_product_purchase = cls.env['project.task.product.purchase'].create({
            'task_product_id': cls.task_product.id,
            'purchase_order_line_id': cls.purchase_order_line.id,
            'planned_qty': 5
        })

    def test_create_sets_planned_date_to_task_date(self):
        task = self.env['project.task'].create({
            'name': 'Task',
            'planned_date_begin': fields.Date.today(),
            'project_id': self.project.id,
        })
        vals = {
            'task_id': task.id,
            'product_id': self.product.id,
            'planned_qty': 5,
        }
        product_line = self.env['project.task.product'].with_context(default_task_id=task.id).create(vals)
        self.assertEqual(product_line.planned_date, task.planned_date_begin.date())

    def test_compute_requested_state_variants(self):
        product_line = self.env['project.task.product'].create({
            'task_id': self.task.id,
            'product_id': self.product.id,
            'planned_qty': 10,
        })

        # requested_qty < planned_qty → hipo_request
        product_line.write({'requested_qty': 5})
        self.assertEqual(product_line.requested_state, 'hipo_request')

        # requested_qty == planned_qty → fix_request
        product_line.write({'requested_qty': 10})
        self.assertEqual(product_line.requested_state, 'fix_request')

        # requested_qty > planned_qty → hiper_request
        product_line.write({'requested_qty': 15})
        self.assertEqual(product_line.requested_state, 'hiper_request')

        # planned_qty = 0 → no_plan
        product_line.write({'requested_qty': 5, 'planned_qty': 0})
        self.assertEqual(product_line.requested_state, 'no_plan')

    def test_unlink_triggers_incrementParentTask(self):
        product_line = self.env['project.task.product'].create({
            'task_id': self.task.id,
            'product_id': self.product.id,
            'planned_qty': 1,
        })
        self.assertTrue(product_line.unlink())

    def test_write_triggers_incrementParentTask(self):
        product_line = self.env['project.task.product'].create({
            'task_id': self.task.id,
            'product_id': self.product.id,
            'planned_qty': 1,
        })
        product_line.write({'planned_qty': 2})
        self.assertEqual(product_line.planned_qty, 2)

    def test_launch_replenishment_raises_without_warehouse_or_location(self):
        product_line = self.env['project.task.product'].create({
            'task_id': self.task.id,
            'product_id': self.product.id,
            'planned_qty': 1,
        })
        with self.assertRaises(Exception):
            product_line.launch_replenishment(1, replenishment=None, wh=None, location=None)

    # def test_qtyAchieved_returns_qty_by_invoice_method(self):
    #     move = self.env['stock.move'].create({
    #         'name': 'Test Move',
    #         'product_id': self.product.id,
    #         'product_uom_qty': 3,
    #         'quantity': 3,
    #         'product_uom': self.product.uom_id.id,
    #         'location_id': self.env.ref('stock.stock_location_stock').id,
    #         'location_dest_id': self.consume_loc.id,
    #         'state': 'done',
    #         'task_id': self.task.id,
    #     })
    #     self.task_product.stock_move_ids = [(4, move.id)]
    #     self.project.write({'invoice_method': 'consume'})
    #     self.assertEqual(self.task_product.qtyAchieved(), 3)

    #     self.purchase_order_line.write({'qty_received': 2})
    #     self.project.write({'invoice_method': 'received'})
    #     self.task_product._compute_in_quantities()  # recompute pentru a actualiza received_qty
    #     self.assertEqual(self.task_product.qtyAchieved(), 2)

    #     self.project.write({'invoice_method': 'planned'})
    #     self.assertEqual(self.task_product.qtyAchieved(), 5)