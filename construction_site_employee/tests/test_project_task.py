# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase

class TestProjectTaskEmployeeCost(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id
        cls.department = cls.env['hr.department'].create({'name': 'Test Department'})
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
            'department_id': cls.department.id,
            'hourly_cost': 50,
            'currency_id': cls.currency.id,
            'company_id': cls.company.id,
        })
        cls.project = cls.env['project.project'].create({'name': 'Test Project'})
        cls.task = cls.env['project.task'].create({
            'name': 'Test Task',
            'project_id': cls.project.id,
        })

    def test_employee_cost_computation(self):
        task_employee = self.env['project.task.employee'].create({
            'task_id': self.task.id,
            'employee_id': self.employee.id,
            'hr_department_id': self.department.id,
            'planned_hours': 4,
            'manual_effective_hours': 2,
        })
        task_employee._compute_planned_cost()
        task_employee._compute_effective_cost()
        self.task._compute_employee_cost()
        self.assertEqual(self.task.employee_planned_cost, -200)
        self.assertEqual(self.task.employee_cost, -100)
        # Check that _sumCost and _sumPlannedCost include employee costs
        planned = self.task._sumPlannedCost()
        actual = self.task._sumCost()
        self.assertIn(self.task.employee_planned_cost, [planned, actual])
        self.assertIn(self.task.employee_cost, [planned, actual])