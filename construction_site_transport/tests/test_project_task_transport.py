# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase

class TestProjectTaskTransport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id
        cls.project = cls.env['project.project'].create({'name': 'Test Project'})
        cls.task = cls.env['project.task'].create({
            'name': 'Test Task',
            'project_id': cls.project.id,
        })
        cls.vehicle_model_brand = cls.env['fleet.vehicle.model.brand'].create({'name': 'Test Brand'})
        cls.vehicle_model = cls.env['fleet.vehicle.model'].create({
            'name': 'Test Vehicle Model',
            'brand_id': cls.vehicle_model_brand.id,
        })
        cls.vehicle = cls.env['fleet.vehicle'].create({
            'name': 'Test Vehicle',
            'model_id': cls.vehicle_model.id,
            'company_id': cls.company.id,
            'sale_km_price': 2.5,
            'currency_id': cls.currency.id,
        })



    def test_transport_cost_and_price_computation(self):
        task_transport = self.env['project.task.transport'].create({
            'task_id': self.task.id,
            'transport_id': self.vehicle.id,
            'planned_kms': 100,
            'effective_kms': 60,
            'analytic_account_line_id':1
        })
        # km_cost should be equal to vehicle's sale_km_price
        self.assertEqual(task_transport.km_cost, 2.5)
        # Planned and effective cost should be negative
        self.assertEqual(task_transport.planned_cost, -250)
        self.assertEqual(task_transport.effective_cost, -150)
        # Price fields should use sale_km_price
        self.assertEqual(task_transport.price_unit, 2.5)
        self.assertEqual(task_transport.price_total_planned, 250)
        self.assertEqual(task_transport.price_total_received, 150)