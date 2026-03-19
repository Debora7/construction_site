import random
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    def _generate_construction_demo_data(self):
        res = super()._generate_construction_demo_data()
        env = self.env

        # Departments
        dept_construction = env.ref('construction_site_employee.hr_department_construction', raise_if_not_found=False)
        dept_management = env.ref('construction_site_employee.hr_department_management', raise_if_not_found=False)

        # Employees
        employees = env['hr.employee'].search([], limit=10)
        for emp in employees:
            emp.hourly_cost = random.uniform(20, 60)
            emp.sale_hour_price = random.uniform(80, 150)
            if not emp.department_id and dept_construction:
                emp.department_id = dept_construction.id

        # Project tasks
        tasks = env['project.task'].search([], limit=30)
        for task in tasks:
            # Assign 1-2 employees per task
            assigned_emps = random.sample(employees, min(len(employees), random.randint(1, 2)))
            for emp in assigned_emps:
                env['project.task.employee'].create({
                    'task_id': task.id,
                    'employee_id': emp.id,
                    'hr_department_id': emp.department_id.id if emp.department_id else False,
                    'planned_hours': random.uniform(10, 40),
                })

        _logger.info("Employee and project.task.employee demo data generated for construction site.")
        return res