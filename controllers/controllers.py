# -*- coding: utf-8 -*-
# from odoo import http


# class MoHrMonthlyAttendance(http.Controller):
#     @http.route('/mo_hr_monthly_attendance/mo_hr_monthly_attendance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mo_hr_monthly_attendance/mo_hr_monthly_attendance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mo_hr_monthly_attendance.listing', {
#             'root': '/mo_hr_monthly_attendance/mo_hr_monthly_attendance',
#             'objects': http.request.env['mo_hr_monthly_attendance.mo_hr_monthly_attendance'].search([]),
#         })

#     @http.route('/mo_hr_monthly_attendance/mo_hr_monthly_attendance/objects/<model("mo_hr_monthly_attendance.mo_hr_monthly_attendance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mo_hr_monthly_attendance.object', {
#             'object': obj
#         })

