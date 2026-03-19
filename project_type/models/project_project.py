from odoo import fields, models, _, api
import logging

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = "project.project"

    category_id = fields.Many2one(
        comodel_name="project.category",
        string=_("Project Type"),
        copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        for project in projects:
            if project.category_id.project_task_type_ids:
                project.type_ids = [(6, 0, project.category_id.project_task_type_ids.ids)]
        return projects

    def write(self, vals):
        projects = super().write(vals)
        if 'category_id' in vals:
            for project in self:
                if project.category_id:
                    new_stages = project.category_id.project_task_type_ids.ids
                    if set(project.type_ids.ids) != set(new_stages):
                        project.type_ids = [(6, 0, new_stages)]
        return projects