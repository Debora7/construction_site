# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase

class TestProjectTaskEmployee(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id
        cls.department = cls.env['hr.department'].create({'name': 'Test Department'})
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Test Employee',
            'department_id': cls.department.id,
            'hourly_cost': 100,
            'currency_id': cls.currency.id,
            'company_id': cls.company.id,
        })
        cls.project = cls.env['project.project'].create({'name': 'Test Project'})
        cls.task = cls.env['project.task'].create({
            'name': 'Test Task',
            'project_id': cls.project.id,
        })

    def test_create_task_employee_and_compute_costs(self):
        task_employee = self.env['project.task.employee'].create({
            'task_id': self.task.id,
            'employee_id': self.employee.id,
            'hr_department_id': self.department.id,
            'planned_hours': 5,
        })
        task_employee._compute_planned_cost()
        self.assertEqual(task_employee.planned_cost, -500)
        task_employee.manual_effective_hours = 2
        task_employee._compute_effective_cost()
        self.assertEqual(task_employee.effective_hours, 2)
        self.assertEqual(task_employee.effective_cost, -200)

    def test_onchange_hr_department_id(self):
        task_employee = self.env['project.task.employee'].new({
            'task_id': self.task.id,
            'employee_id': self.employee.id,
            'hr_department_id': self.department.id,
        })
        res = task_employee._change_departament()
        self.assertIn('domain', res)
        self.assertIn('employee_id', res['domain'])

    def test_onchange_employee_id_sets_department(self):
        task_employee = self.env['project.task.employee'].new({
            'task_id': self.task.id,
            'employee_id': self.employee.id,
        })
        task_employee._change_employee()
        self.assertEqual(task_employee.hr_department_id, self.department)