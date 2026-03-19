# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase

class TestProjectTask(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env['stock.warehouse'].search([], limit=1)
        cls.location = cls.warehouse.lot_stock_id
        cls.project = cls.env['project.project'].create({
            'name': 'Test Project',
            'warehouse_id': cls.warehouse.id,
        })
        cls.task = cls.env['project.task'].create({
            'name': 'Test Task',
            'project_id': cls.project.id,
        })

    def test_get_current_location_returns_task_location(self):
        location = self.env['stock.location'].create({'name': 'Task Location'})
        self.task.location_id = location.id
        self.assertEqual(self.task.get_current_location(), location.id)

    def test_get_current_location_returns_parent_location(self):
        parent_location = self.env['stock.location'].create({'name': 'Parent Location'})
        parent_task = self.env['project.task'].create({
            'name': 'Parent Task',
            'project_id': self.project.id,
            'location_id': parent_location.id,
        })
        self.task.location_id = False
        self.task.parent_id = parent_task.id
        self.assertEqual(self.task.get_current_location(), parent_location.id)

    def test_get_current_location_returns_project_warehouse_location(self):
        self.task.location_id = False
        self.task.parent_id = False
        self.assertEqual(self.task.get_current_location(), self.location.id)