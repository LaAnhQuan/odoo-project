from odoo import fields, models

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    mans = fields.Char(string="MANS (Mã nhân viên)", index=True)
