from odoo import api, fields, models

ATTENDANCE_CODE_MAP = [
    ("W", "Công (mặc định)"),
    ("P", "Phép"),
    ("P2", "Phép nửa ngày"),
    ("KO", "Không lương"),
    ("KO2", "Không lương nửa ngày"),
    ("OFF", "Nghỉ"),
]


class HrDailyAttendance(models.Model):
    _name = "hr.daily.attendance"
    _description = "Daily Attendance (per employee per day)"
    _order = "date desc, employee_id"
    _rec_name = "name"

    # Hiển thị
    name = fields.Char(string="Hiển thị", compute="_compute_name", store=True)

    employee_id = fields.Many2one(
        "hr.employee",
        string="Nhân viên",
        required=True,
        index=True,
    )

    # MANS lấy từ employee
    mans = fields.Char(
        string="MANS",
        related="employee_id.mans",
        store=True,
        index=True,
        readonly=True,
    )

    date = fields.Date(
        string="Ngày",
        required=True,
        index=True,
    )

    attendance_code = fields.Selection(
        ATTENDANCE_CODE_MAP,
        string="Ký hiệu",
        default="W",
        required=True,
        index=True,
    )

    workday_value = fields.Float(
        string="Giá trị ngày công",
        compute="_compute_workday_value",
        store=True,
    )

    check_in = fields.Datetime(string="Đăng nhập")
    check_out = fields.Datetime(string="Đăng xuất")

    work_hours = fields.Float(
        string="Thời gian làm việc (giờ)",
        compute="_compute_work_hours",
        store=True,
    )

    overtime_hours = fields.Float(string="Giờ làm thêm", default=0.0)

    note = fields.Char(string="Ghi chú")

    monthly_sheet_id = fields.Many2one(
        "hr.monthly.attendance",
        string="Bảng công tháng",
        ondelete="set null",
        index=True,
    )
    monthly_line_id = fields.Many2one(
        "hr.monthly.attendance.line",
        string="Dòng bảng công tháng",
        ondelete="set null",
        index=True,
    )

    company_id = fields.Many2one(
        "res.company",
        related="employee_id.company_id",
        store=True,
        index=True,
        readonly=True,
    )
    department_id = fields.Many2one(
        "hr.department",
        related="employee_id.department_id",
        store=True,
        index=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "daily_unique_employee_date",
            "unique (employee_id, date)",
            "Mỗi nhân viên chỉ được có một bản ghi chấm công trong một ngày.",
        ),
    ]

    @api.depends("attendance_code")
    def _compute_workday_value(self):
        mapping = {
            "W": 1.0,
            "P": 1.0,
            "P2": 0.5,
            "KO": 0.0,
            "KO2": 0.5,
            "OFF": 0.0,
        }
        for rec in self:
            rec.workday_value = mapping.get(rec.attendance_code or "W", 1.0)

    @api.depends("check_in", "check_out")
    def _compute_work_hours(self):
        for rec in self:
            if rec.check_in and rec.check_out and rec.check_out > rec.check_in:
                delta = rec.check_out - rec.check_in
                rec.work_hours = delta.total_seconds() / 3600.0
            else:
                rec.work_hours = 0.0

    @api.depends("employee_id", "date", "check_in", "check_out")
    def _compute_name(self):
        """
        Nếu có checkin/checkout: "Tên (09:00 → 12:00)"
        Nếu không: "Tên - YYYY-MM-DD"
        """
        for rec in self:
            emp_name = rec.employee_id.name or "Chấm công"
            if rec.check_in and rec.check_out:
                start = fields.Datetime.context_timestamp(rec, rec.check_in).strftime("%H:%M")
                end = fields.Datetime.context_timestamp(rec, rec.check_out).strftime("%H:%M")
                rec.name = f"{emp_name} ({start} → {end})"
            else:
                rec.name = f"{emp_name} - {rec.date}" if rec.date else emp_name
