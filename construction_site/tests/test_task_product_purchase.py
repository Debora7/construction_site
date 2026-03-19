from odoo.tests import TransactionCase

class TestTaskProductPurchase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.user.company_id
        cls.partner = cls.env['res.partner'].create({'name': 'Test Partner'})
        cls.project = cls.env['project.project'].create({'name': 'Test Project'})
        cls.task = cls.env['project.task'].create({'name': 'Test Task', 'project_id': cls.project.id})
        cls.product = cls.env['product.product'].create({'name': 'Test Product', 'type': 'consu'})
        cls.purchase_order = cls.env['purchase.order'].create({
            'partner_id': cls.partner.id,
            'company_id': cls.company.id,
        })
        cls.purchase_order_line = cls.env['purchase.order.line'].create({
            'order_id': cls.purchase_order.id,
            'product_id': cls.product.id,
            'product_uom_qty': 10,
            'price_unit': 100,
            'name': 'Test POL',
        })
        cls.task_product = cls.env['project.task.product'].create({
            'task_id': cls.task.id,
            'product_id': cls.product.id,
            'planned_qty': 10,
        })

    def test_create_purchase_fragment(self):
        purchase_fragment = self.env['project.task.product.purchase'].create({
            'task_product_id': self.task_product.id,
            'purchase_order_line_id': self.purchase_order_line.id,
            'planned_qty': 5,
        })
        self.assertEqual(purchase_fragment.task_id, self.task)
        self.assertEqual(purchase_fragment.project_id, self.project)
        self.assertEqual(purchase_fragment.state, self.purchase_order.state)