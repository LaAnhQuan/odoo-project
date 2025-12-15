from odoo import api, fields, models, _
import calendar
from datetime import date, timedelta


class HrMonthlyAttendanceGrid(models.Model):
    """Model để hỗ trợ hiển thị grid view của chấm công tháng"""
    _name = "hr.monthly.attendance.grid"
    _description = "Monthly Attendance Grid View"
    _order = "year desc, month desc, employee_id"

    name = fields.Char(string="Hiển thị", compute="_compute_name", store=True)
    
    employee_id = fields.Many2one(
        "hr.employee",
        string="Nhân viên",
        required=True,
        index=True,
        ondelete="cascade",
    )
    
    employee_name = fields.Char(
        related="employee_id.name",
        string="Tên nhân viên",
        store=True,
    )
    
    mans = fields.Char(
        related="employee_id.mans",
        string="MANS",
        store=True,
        index=True,
    )
    
    month = fields.Selection(
        [(str(i), f"Tháng {i}") for i in range(1, 13)],
        string="Tháng",
        required=True,
        index=True,
    )
    
    year = fields.Integer(
        string="Năm",
        required=True,
        default=lambda self: fields.Date.today().year,
        index=True,
    )
    
    department_id = fields.Many2one(
        "hr.department",
        related="employee_id.department_id",
        string="Phòng ban",
        store=True,
        index=True,
    )
    
    company_id = fields.Many2one(
        "res.company",
        related="employee_id.company_id",
        string="Công ty",
        store=True,
        index=True,
    )
    
    monthly_sheet_id = fields.Many2one(
        "hr.monthly.attendance",
        string="Bảng công tháng",
        ondelete="cascade",
        index=True,
    )
    
    # Các trường cho từng ngày trong tháng (1-31)
    day_01 = fields.Char(string="01")
    day_02 = fields.Char(string="02")
    day_03 = fields.Char(string="03")
    day_04 = fields.Char(string="04")
    day_05 = fields.Char(string="05")
    day_06 = fields.Char(string="06")
    day_07 = fields.Char(string="07")
    day_08 = fields.Char(string="08")
    day_09 = fields.Char(string="09")
    day_10 = fields.Char(string="10")
    day_11 = fields.Char(string="11")
    day_12 = fields.Char(string="12")
    day_13 = fields.Char(string="13")
    day_14 = fields.Char(string="14")
    day_15 = fields.Char(string="15")
    day_16 = fields.Char(string="16")
    day_17 = fields.Char(string="17")
    day_18 = fields.Char(string="18")
    day_19 = fields.Char(string="19")
    day_20 = fields.Char(string="20")
    day_21 = fields.Char(string="21")
    day_22 = fields.Char(string="22")
    day_23 = fields.Char(string="23")
    day_24 = fields.Char(string="24")
    day_25 = fields.Char(string="25")
    day_26 = fields.Char(string="26")
    day_27 = fields.Char(string="27")
    day_28 = fields.Char(string="28")
    day_29 = fields.Char(string="29")
    day_30 = fields.Char(string="30")
    day_31 = fields.Char(string="31")
    
    # Tổng kết - Đồng bộ với hr.monthly.attendance.line
    worked_days = fields.Float(
        string="Ngày công thực tế",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày công thực tế (W, X - đã tính thứ 7 = 0.5)",
    )
    
    paid_leave_days = fields.Float(
        string="Ngày nghỉ hưởng lương",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày phép hưởng lương (P, P/2)",
    )
    
    unpaid_leave_days = fields.Float(
        string="Ngày nghỉ không lương",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày không lương (KO, KO/2)",
    )
    
    overtime_hours = fields.Float(
        string="Giờ làm thêm",
        compute="_compute_totals",
        store=True,
        help="Tổng giờ làm thêm",
    )
    
    total_paid_days = fields.Float(
        string="Tổng ngày công tính lương",
        compute="_compute_totals",
        store=True,
        help="Ngày công thực tế + Ngày nghỉ hưởng lương",
    )
    
    # Giữ lại để backward compatible
    total_workdays = fields.Float(
        related="worked_days",
        string="Công",
        store=False,
        readonly=True,
    )
    
    total_work_hours = fields.Float(
        related="overtime_hours",
        string="Tổng giờ công",
        store=False,
        readonly=True,
    )
    
    _sql_constraints = [
        (
            "grid_unique_employee_month_year",
            "unique (employee_id, month, year)",
            "Mỗi nhân viên chỉ có một bản ghi grid cho mỗi tháng.",
        ),
    ]
    
    @api.depends("employee_id", "month", "year")
    def _compute_name(self):
        for rec in self:
            if rec.employee_id and rec.month and rec.year:
                rec.name = f"{rec.employee_id.name} - {rec.month}/{rec.year}"
            else:
                rec.name = "Grid chấm công"
    
    @api.depends(
        "day_01", "day_02", "day_03", "day_04", "day_05", "day_06", "day_07",
        "day_08", "day_09", "day_10", "day_11", "day_12", "day_13", "day_14",
        "day_15", "day_16", "day_17", "day_18", "day_19", "day_20", "day_21",
        "day_22", "day_23", "day_24", "day_25", "day_26", "day_27", "day_28",
        "day_29", "day_30", "day_31",
        "month", "year"
    )
    def _compute_totals(self):
        """Tính tổng các loại ngày công chi tiết
        
        Quy tắc:
        - Thứ 7 (code W/X): 0.5 ngày công
        - Chủ nhật (code W/X): Không tính
        - P/P2: Phép (hưởng lương)
        - KO/KO2: Không lương
        """
        code_to_value = {
            "P": 1.0,
            "P2": 0.5,
            "P/2": 0.5,
            "KO": 1.0,
            "KO2": 0.5,
            "KO/2": 0.5,
            "OFF": 0.0,
        }
        
        for rec in self:
            # Reset tất cả
            worked_days = 0.0      # Ngày công thực tế (W, X)
            paid_leave = 0.0       # Ngày nghỉ hưởng lương (P, P/2)
            unpaid_leave = 0.0     # Ngày nghỉ không lương (KO, KO/2)
            overtime_hours = 0.0   # Giờ làm thêm
            
            if not rec.month or not rec.year:
                rec.worked_days = 0.0
                rec.paid_leave_days = 0.0
                rec.unpaid_leave_days = 0.0
                rec.overtime_hours = 0.0
                rec.total_paid_days = 0.0
                continue
            
            month_int = int(rec.month)
            last_day = calendar.monthrange(rec.year, month_int)[1]
            
            # Duyệt qua tất cả các ngày có trong tháng
            for day_num in range(1, last_day + 1):
                field_name = f"day_{day_num:02d}"
                value = getattr(rec, field_name, None)
                
                if not value:
                    continue
                
                # Parse value: có thể là "W", "P", "KO/2", "W (8h)", etc.
                code = value.split()[0] if value else ""
                code = code.strip().upper()
                
                # Kiểm tra ngày trong tuần
                try:
                    current_date = date(rec.year, month_int, day_num)
                    is_saturday = current_date.weekday() == 5  # Thứ 7
                    is_sunday = current_date.weekday() == 6    # Chủ nhật
                except:
                    is_saturday = False
                    is_sunday = False
                
                # Tính ngày công theo loại code
                if code in ["W", "X"]:
                    # Ngày công thực tế (đi làm)
                    if is_sunday:
                        # Chủ nhật không tính công
                        day_value = 0.0
                    elif is_saturday:
                        # Thứ 7 chỉ tính 0.5 công
                        day_value = 0.5
                    else:
                        # Các ngày thường tính đủ 1.0
                        day_value = 1.0
                    worked_days += day_value
                    
                elif code in ["P", "P2", "P/2"]:
                    # Ngày nghỉ hưởng lương (Phép)
                    day_value = code_to_value.get(code, 1.0)
                    paid_leave += day_value
                    
                elif code in ["KO", "KO2", "KO/2"]:
                    # Ngày nghỉ không lương
                    day_value = code_to_value.get(code, 1.0)
                    unpaid_leave += day_value
                    
                elif code == "OFF":
                    # Nghỉ - không tính
                    pass
                
                # Nếu có format "Xh" trong value, extract giờ làm thêm
                if "h" in value.lower() and "(" in value:
                    try:
                        # Format: "W (8h)" hoặc "W (10h)"
                        hours_str = value.split("(")[1].split(")")[0].strip()
                        hours = float(hours_str.replace("h", "").replace("H", ""))
                        # Nếu > 8h thì tính overtime (giờ làm thêm)
                        if hours > 8:
                            overtime_hours += (hours - 8)
                    except:
                        pass
            
            # Tổng ngày công tính lương = Ngày công thực tế + Ngày nghỉ hưởng lương
            total_paid = worked_days + paid_leave
            
            rec.worked_days = worked_days
            rec.paid_leave_days = paid_leave
            rec.unpaid_leave_days = unpaid_leave
            rec.overtime_hours = overtime_hours
            rec.total_paid_days = total_paid
    
    def action_sync_from_daily(self):
        """Đồng bộ dữ liệu từ hr.daily.attendance"""
        self.ensure_one()
        
        if not self.month or not self.year:
            return
        
        month_int = int(self.month)
        last_day = calendar.monthrange(self.year, month_int)[1]
        date_from = date(self.year, month_int, 1)
        date_to = date(self.year, month_int, last_day)
        
        # Lấy tất cả chấm công ngày của nhân viên trong tháng
        daily_records = self.env["hr.daily.attendance"].search([
            ("employee_id", "=", self.employee_id.id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ])
        
        # Map code hiển thị
        code_display = {
            "W": "W",
            "P": "P",
            "P2": "P/2",
            "KO": "KO",
            "KO2": "KO/2",
            "OFF": "OFF",
        }
        
        # Cập nhật từng ngày
        for daily in daily_records:
            day_num = daily.date.day
            field_name = f"day_{day_num:02d}"
            
            # Format: "Code (Xh / Yh)" hoặc chỉ "Code"
            code = code_display.get(daily.attendance_code, daily.attendance_code)
            
            if daily.work_hours > 0:
                display_value = f"{code} ({daily.work_hours:.0f}h)"
            else:
                display_value = code
            
            setattr(self, field_name, display_value)
        
        return True
    
    @api.model
    def sync_all_from_monthly_sheet(self, sheet_id):
        """
        Tạo/cập nhật tất cả grid records từ một monthly attendance sheet
        """
        sheet = self.env["hr.monthly.attendance"].browse(sheet_id)
        if not sheet.exists():
            return False
        
        # Lấy tất cả nhân viên từ line_ids
        employees = sheet.line_ids.mapped("employee_id")
        
        for employee in employees:
            # Tìm hoặc tạo grid record
            grid = self.search([
                ("employee_id", "=", employee.id),
                ("month", "=", sheet.month),
                ("year", "=", sheet.year),
            ])
            
            if not grid:
                grid = self.create({
                    "employee_id": employee.id,
                    "month": sheet.month,
                    "year": sheet.year,
                    "monthly_sheet_id": sheet.id,
                })
            else:
                grid.monthly_sheet_id = sheet.id
            
            # Sync dữ liệu
            grid.action_sync_from_daily()
        
        return True
    
    def action_open_daily_records(self):
        """Mở form xem chi tiết các bản ghi chấm công ngày"""
        self.ensure_one()
        
        if not self.month or not self.year:
            return
        
        month_int = int(self.month)
        last_day = calendar.monthrange(self.year, month_int)[1]
        date_from = date(self.year, month_int, 1)
        date_to = date(self.year, month_int, last_day)
        
        return {
            "type": "ir.actions.act_window",
            "name": f"Chấm công ngày - {self.employee_name}",
            "res_model": "hr.daily.attendance",
            "view_mode": "list,form",
            "domain": [
                ("employee_id", "=", self.employee_id.id),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
            ],
            "context": {
                "default_employee_id": self.employee_id.id,
            },
        }
