# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase
from odoo import fields
from odoo.exceptions import ValidationError


class TestPurchase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.project = cls.env['project.project'].create({'name': 'Test Project', 'is_construction_site': True})
        cls.task = cls.env['project.task'].create({'name': 'Test task', 'project_id': cls.project.id})
        cls.product = cls.env['product.product'].create({'name': 'Test Product', 'type': 'consu'})
        cls.picking_type = cls.env['stock.picking.type'].search([], limit=1)
        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'company_id': cls.company.id,
            'picking_type_id': cls.picking_type.id,
            'project_id': cls.project.id,
            'task_id': cls.task.id
        })
        cls.route = cls.env['stock.route'].search([], limit=1)

    def test_project_construction_computed_fields(self):
        task = self.env['project.task'].create({'name': 'Task', 'project_id': self.project.id})
        task_product = self.env['project.task.product'].create({
            'task_id': task.id,
            'product_id': self.product.id,
            'planned_qty': 1,
        })
        pol = self.env['purchase.order.line'].create({
            'order_id': self.purchase_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 10,
            'name': 'Test POL',
            'task_product_ids': [(0, 0, {'task_product_id': task_product.id, 'planned_qty': 1})],
        })
        self.purchase_order._project_construction()
        self.assertEqual(self.purchase_order.construction_project_count, 1)
        self.assertIn(self.project, self.purchase_order.construction_project_ids)

    def test_onchange_project_id_sets_order_line_project(self):
        pol = self.env['purchase.order.line'].create({
            'order_id': self.purchase_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 10,
            'name': 'Test POL',
        })
        self.purchase_order.project_id = self.project.id
        self.purchase_order.onclick_project_id()
        self.assertEqual(pol.project_id, self.project)

    def test_action_view_projects_returns_action(self):
        task = self.env['project.task'].create({
            'name': 'Task',
            'project_id': self.project.id,
        })
        task_product = self.env['project.task.product'].create({
            'task_id': task.id,
            'product_id': self.product.id,
            'planned_qty': 1,
        })

        pol = self.env['purchase.order.line'].create({
            'order_id': self.purchase_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 10,
            'name': 'Test POL',
            'task_product_ids': [(0, 0, {'task_product_id': task_product.id, 'planned_qty': 1})],
        })

        self.purchase_order._project_construction()

        action = self.purchase_order.action_view_projects()

        self.assertIn(self.project.id, action['domain'][0][2])

    def test_message_post_propagates_to_procurements(self):
        # Create a procurement linked to the project
        procurement = self.env['project.site.procurement'].create({
            'project_id': self.project.id,
        })

        pol = self.env['purchase.order.line'].create({
            'order_id': self.purchase_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 10,
            'name': 'Test POL',
        })

        pol.procurement_ids = [(4, procurement.id)]

        msg = self.purchase_order.message_post(body="Test message")
        self.assertTrue(msg, "Message was not created on the purchase order")

        msgs = procurement.message_ids.filtered(lambda m: "Test message" in m.body)
        self.assertTrue(msgs, "Message was not propagated to procurement")

    # def test_button_confirm_pushes_product_to_task(self):
    #     route = self.env['stock.route'].create({'name': 'Test Route'})
    #     warehouse = self.env['stock.warehouse'].search([], limit=1)
    #     warehouse.write({
    #         'resupply_route_ids': [(6, 0, route.id)],
    #     })
    #     self.project.warehouse_id = warehouse
    #     pol = self.env['purchase.order.line'].create({
    #         'order_id': self.purchase_order.id,
    #         'product_id': self.product.id,
    #         'product_uom_qty': 1,
    #         'price_unit': 10,
    #         'name': 'Test POL',
    #         'task_id': self.task.id
    #     })
    #     self.purchase_order.button_confirm()
    #     self.assertTrue(pol.task_product_ids, "Product was not pushed to the task")

    def test_get_destination_location_with_task_location(self):
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        location = warehouse.lot_stock_id
        project = self.env['project.project'].create(
            {'name': 'Project2', 'is_construction_site': True, 'warehouse_id': warehouse.id})
        task = self.env['project.task'].create({'name': 'Task', 'project_id': project.id, 'location_id': location.id})
        po = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'picking_type_id': self.picking_type.id,
            'project_id': project.id,
        })
        pol = self.env['purchase.order.line'].create({
            'order_id': po.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 10,
            'name': 'Test POL',
            'task_id': task.id,
        })
        loc = po._get_destination_location()
        self.assertEqual(loc, location.id)

    # def test_get_destination_location_raises_on_multiple_locations(self):
    #     warehouse = self.env['stock.warehouse'].search([], limit=1)

    #     # Create two distinct internal locations
    #     location1 = self.env['stock.location'].create({
    #         'name': 'Location 1',
    #         'usage': 'internal',
    #     })
    #     location2 = self.env['stock.location'].create({
    #         'name': 'Location 2',
    #         'usage': 'internal',
    #     })

    #     project = self.env['project.project'].create({
    #         'name': 'Project3',
    #         'is_construction_site': True,
    #         'warehouse_id': warehouse.id,
    #     })

    #     task1 = self.env['project.task'].create({
    #         'name': 'Task1',
    #         'project_id': project.id,
    #         'location_id': location1.id,
    #     })
    #     task2 = self.env['project.task'].create({
    #         'name': 'Task2',
    #         'project_id': project.id,
    #         'location_id': location2.id,
    #     })

    #     po = self.env['purchase.order'].create({
    #         'partner_id': self.partner.id,
    #         'company_id': self.company.id,
    #         'picking_type_id': self.picking_type.id,
    #         'project_id': project.id,
    #     })

    #     self.env['purchase.order.line'].create({
    #         'order_id': po.id,
    #         'product_id': self.product.id,
    #         'product_uom_qty': 1,
    #         'price_unit': 10,
    #         'name': 'Test POL1',
    #         'task_id': task1.id,
    #     })
    #     self.env['purchase.order.line'].create({
    #         'order_id': po.id,
    #         'product_id': self.product.id,
    #         'product_uom_qty': 1,
    #         'price_unit': 10,
    #         'name': 'Test POL2',
    #         'task_id': task2.id,
    #     })

    #     with self.assertRaises(ValidationError):
    #         po._get_destination_location()

    # def test_prepare_purchase_order_line_from_procurement_sets_task_fields(self):
    #     task = self.env['project.task'].create({
    #         'name': 'Task',
    #         'project_id': self.project.id
    #     })

    #     analytic = self.project.auto_account_id

    #     task_product = self.env['project.task.product'].create({
    #         'task_id': task.id,
    #         'product_id': self.product.id,
    #         'planned_qty': 1,
    #     })

    #     self.purchase_order.partner_id = self.partner

    #     supplierinfo = self.env['product.supplierinfo'].create({
    #         'partner_id': self.partner.id,
    #         'product_tmpl_id': self.product.product_tmpl_id.id,
    #     })
    #     values = {
    #         'task_product_id': task_product,
    #         'procurement_ids': [],
    #         'supplier': supplierinfo,
    #     }

    #     res = self.env['purchase.order.line']._prepare_purchase_order_line_from_procurement(
    #         product_id=self.product,
    #         product_qty=1,
    #         product_uom=self.product.uom_id,
    #         location_dest_id=self.purchase_order._get_destination_location(),
    #         name='Test POL',
    #         origin=self.purchase_order.name,
    #         company_id=self.company,
    #         values=values,
    #         po=self.purchase_order
    #     )

    #     self.assertEqual(res['task_id'], task.id)

    #     self.assertIn('task_product_ids', res)
    #     task_product_vals = res['task_product_ids'][0][2]  # (0, 0, dict)
    #     self.assertEqual(task_product_vals['task_product_id'], task_product.id)
    #     self.assertEqual(task_product_vals['planned_qty'], task_product.planned_qty)
    #     self.assertEqual(task_product_vals['warehouse_id'], self.purchase_order.picking_type_id.warehouse_id.id)

    #     self.assertIn('analytic_distribution', res)
    #     self.assertIn(analytic.id, res['analytic_distribution'])
    #     self.assertEqual(res['analytic_distribution'][analytic.id], 100)

    def test_prepare_account_move_line_includes_task_id(self):
        pol = self.env['purchase.order.line'].create({
            'order_id': self.purchase_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': 10,
            'name': 'Test POL',
            'task_id': self.task.id,
        })
        res = pol._prepare_account_move_line()
        self.assertEqual(res['task_id'], self.task.id)
