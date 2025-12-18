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
        string="Công",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày công thực tế (W, X - đã tính thứ 7 = 0.5)",
    )
    
    paid_leave_days = fields.Float(
        string="Phép",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày phép hưởng lương (P, P/2)",
    )
    
    unpaid_leave_days = fields.Float(
        string="Không lương",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày không lương (KO, KO/2)",
    )
    
    maternity_days = fields.Float(
        string="Thai sản",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày nghỉ thai sản (TS, TS/2)",
    )
    
    holiday_days = fields.Float(
        string="Lễ",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày nghỉ lễ (L, L/2)",
    )
    
    bereavement_days = fields.Float(
        string="Hiếu",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày nghỉ hiếu (H, H/2)",
    )
    
    wedding_days = fields.Float(
        string="Hỷ",
        compute="_compute_totals",
        store=True,
        help="Tổng số ngày nghỉ hỷ (HY, HY/2)",
    )
    
    overtime_hours = fields.Float(
        string="Giờ làm thêm",
        compute="_compute_totals",
        store=True,
        help="Tổng giờ làm thêm",
    )
    
    total_paid_days = fields.Float(
        string="Tổng ngày công",
        compute="_compute_totals",
        store=True,
        help="Tổng ngày công tính lương",
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
        - TS/TS2: Thai sản
        - L/L2: Lễ
        - H/H2: Hiếu
        - HY/HY2: Hỷ
        """
        code_to_value = {
            "P": 1.0, "P2": 0.5, "P/2": 0.5,
            "KO": 1.0, "KO2": 0.5, "KO/2": 0.5,
            "TS": 1.0, "TS2": 0.5, "TS/2": 0.5,
            "L": 1.0, "L2": 0.5, "L/2": 0.5,
            "H": 1.0, "H2": 0.5, "H/2": 0.5,
            "HY": 1.0, "HY2": 0.5, "HY/2": 0.5,
            "OFF": 0.0,
        }
        
        for rec in self:
            # Reset tất cả
            worked_days = 0.0      # Ngày công thực tế (W, X)
            paid_leave = 0.0       # Ngày nghỉ phép (P, P/2)
            unpaid_leave = 0.0     # Ngày nghỉ không lương (KO, KO/2)
            maternity = 0.0        # Thai sản (TS, TS/2)
            holiday = 0.0          # Lễ (L, L/2)
            bereavement = 0.0      # Hiếu (H, H/2)
            wedding = 0.0          # Hỷ (HY, HY/2)
            overtime_hours = 0.0   # Giờ làm thêm
            
            if not rec.month or not rec.year:
                rec.worked_days = 0.0
                rec.paid_leave_days = 0.0
                rec.unpaid_leave_days = 0.0
                rec.maternity_days = 0.0
                rec.holiday_days = 0.0
                rec.bereavement_days = 0.0
                rec.wedding_days = 0.0
                rec.overtime_hours = 0.0
                rec.total_paid_days = 0.0
                continue
            
            month_int = int(rec.month)
            last_day = calendar.monthrange(rec.year, month_int)[1]
            
            # Duyệt qua tất cả các ngày có trong tháng
            for day_num in range(1, last_day + 1):
                field_name = f"day_{day_num:02d}"
                value = getattr(rec, field_name, None)
                
                # Nếu không có value hoặc rỗng, bỏ qua (không tính gì cả)
                if not value or not value.strip():
                    continue
                
                # Parse value: có thể là "W", "P", "KO/2", "W (8h)", etc.
                code = value.split()[0] if value else ""
                code = code.strip().upper()
                
                # Nếu là OFF (nghỉ), bỏ qua không tính
                if code == "OFF":
                    continue
                
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
                    
                elif code == "P":
                    # Nghỉ phép cả ngày - chỉ tính vào phép, không tính công
                    paid_leave += 1.0
                    
                elif code in ["P2", "P/2"]:
                    # Nghỉ phép nửa ngày - tính cả công và phép
                    worked_days += 0.5  # Nửa ngày làm việc
                    paid_leave += 0.5    # Nửa ngày nghỉ phép
                    
                elif code == "KO":
                    # Nghỉ không lương cả ngày
                    unpaid_leave += 1.0
                    
                elif code in ["KO2", "KO/2"]:
                    # Nghỉ không lương nửa ngày - vẫn tính nửa công
                    worked_days += 0.5
                    unpaid_leave += 0.5
                    
                elif code == "TS":
                    # Nghỉ thai sản cả ngày
                    maternity += 1.0
                    
                elif code in ["TS2", "TS/2"]:
                    # Nghỉ thai sản nửa ngày
                    worked_days += 0.5
                    maternity += 0.5
                    
                elif code == "L":
                    # Nghỉ lễ cả ngày
                    holiday += 1.0
                    
                elif code in ["L2", "L/2"]:
                    # Nghỉ lễ nửa ngày
                    worked_days += 0.5
                    holiday += 0.5
                    
                elif code == "H":
                    # Nghỉ hiếu cả ngày
                    bereavement += 1.0
                    
                elif code in ["H2", "H/2"]:
                    # Nghỉ hiếu nửa ngày
                    worked_days += 0.5
                    bereavement += 0.5
                    
                elif code == "HY":
                    # Nghỉ hỷ cả ngày
                    wedding += 1.0
                    
                elif code in ["HY2", "HY/2"]:
                    # Nghỉ hỷ nửa ngày
                    worked_days += 0.5
                    wedding += 0.5
                
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
            
            # Tổng ngày công = CHỈ công thực tế (KHÔNG tính phép và không lương)
            # Phép và Không lương được tính riêng, không vào tổng công
            total_paid = worked_days + maternity + holiday + bereavement + wedding
            
            rec.worked_days = worked_days
            rec.paid_leave_days = paid_leave
            rec.unpaid_leave_days = unpaid_leave
            rec.maternity_days = maternity
            rec.holiday_days = holiday
            rec.bereavement_days = bereavement
            rec.wedding_days = wedding
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
    
    def update_cell_value(self, day, value):
        """Cập nhật giá trị của một ô trong grid và đồng bộ vào database
        
        Args:
            day (int): Ngày trong tháng (1-31)
            value (str): Giá trị mới (VD: "P", "KO", "W", "TS", "L", "H", "HY", etc.)
        
        Returns:
            dict: Thông tin cập nhật bao gồm totals mới
        """
        self.ensure_one()
        
        if not 1 <= day <= 31:
            return {"error": "Ngày không hợp lệ"}
        
        if not self.month or not self.year:
            return {"error": "Thiếu thông tin tháng/năm"}
        
        field_name = f"day_{day:02d}"
        
        # Cập nhật giá trị trong grid
        setattr(self, field_name, value)
        
        # Đồng bộ vào hr.daily.attendance
        month_int = int(self.month)
        target_date = date(self.year, month_int, day)
        
        # Map code hiển thị sang attendance_code
        code_map = {
            "X": "X", "W": "X",
            "P": "P", "P/2": "P2",
            "KO": "KO", "KO/2": "KO2",
            "TS": "TS", "TS/2": "TS2",
            "L": "L", "L/2": "L2",
            "H": "H", "H/2": "H2",
            "HY": "HY", "HY/2": "HY2",
            "OFF": "OFF",
            "": "OFF",  # Xóa = OFF
        }
        
        # Parse value để lấy code
        code = value.split()[0] if value else ""
        attendance_code = code_map.get(code.upper(), "X")
        
        # Tìm hoặc tạo daily record
        Daily = self.env["hr.daily.attendance"]
        daily = Daily.search([
            ("employee_id", "=", self.employee_id.id),
            ("date", "=", target_date),
        ], limit=1)
        
        # Nếu chọn xóa hoặc OFF
        if not value or not value.strip() or attendance_code == "OFF":
            if daily:
                # Xóa record trong daily attendance
                daily.unlink()
        else:
            # Có giá trị
            if daily:
                # Cập nhật
                daily.write({"attendance_code": attendance_code})
            else:
                # Tạo mới
                Daily.create({
                    "employee_id": self.employee_id.id,
                    "date": target_date,
                    "attendance_code": attendance_code,
                    "monthly_sheet_id": self.monthly_sheet_id.id if self.monthly_sheet_id else False,
                })
        
        # Trigger recompute totals
        self._compute_totals()
        
        # Cập nhật lại monthly attendance line nếu có
        if self.monthly_sheet_id:
            self._sync_totals_to_monthly_line()
        
        # Trả về thông tin mới
        return {
            "success": True,
            "totals": {
                "worked_days": self.worked_days,
                "paid_leave_days": self.paid_leave_days,
                "unpaid_leave_days": self.unpaid_leave_days,
                "maternity_days": self.maternity_days,
                "holiday_days": self.holiday_days,
                "bereavement_days": self.bereavement_days,
                "wedding_days": self.wedding_days,
                "overtime_hours": self.overtime_hours,
                "total_paid_days": self.total_paid_days,
            }
        }
    
    def _sync_totals_to_monthly_line(self):
        """Đồng bộ tổng kết từ grid vào monthly attendance line"""
        self.ensure_one()
        
        if not self.monthly_sheet_id:
            return
        
        # Tìm line tương ứng
        Line = self.env["hr.monthly.attendance.line"]
        line = Line.search([
            ("sheet_id", "=", self.monthly_sheet_id.id),
            ("employee_id", "=", self.employee_id.id),
        ], limit=1)
        
        if line:
            line.write({
                "worked_days": self.worked_days,
                "paid_leave_days": self.paid_leave_days,
                "unpaid_leave_days": self.unpaid_leave_days,
                "overtime_hours": self.overtime_hours,
            })
    
    def action_open_monthly_sheet(self):
        """Mở bảng chấm công tháng chính"""
        self.ensure_one()
        
        if self.monthly_sheet_id:
            return {
                "type": "ir.actions.act_window",
                "name": "Bảng chấm công tháng",
                "res_model": "hr.monthly.attendance",
                "res_id": self.monthly_sheet_id.id,
                "view_mode": "form",
                "target": "current",
            }
        else:
            # Tìm hoặc tạo monthly sheet
            Sheet = self.env["hr.monthly.attendance"]
            sheet = Sheet.search([
                ("month", "=", self.month),
                ("year", "=", self.year),
                ("company_id", "=", self.company_id.id),
            ], limit=1)
            
            if sheet:
                return {
                    "type": "ir.actions.act_window",
                    "name": "Bảng chấm công tháng",
                    "res_model": "hr.monthly.attendance",
                    "res_id": sheet.id,
                    "view_mode": "form",
                    "target": "current",
                }
            else:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": "Thông báo",
                        "message": "Chưa có bảng chấm công tháng cho kỳ này",
                        "type": "warning",
                    },
                }
    
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
    
    @api.model
    def save_grid_changes(self, records_data, month, year, department_id=False):
        """
        Lưu tất cả thay đổi từ grid view
        
        Args:
            records_data: List các record data với thông tin đã thay đổi
            month: Tháng
            year: Năm
            department_id: ID phòng ban (optional)
        
        Returns:
            dict: {"success": True/False, "message": "..."}
        """
        try:
            Employee = self.env["hr.employee"]
            not_found_employees = []  # Danh sách nhân viên không tìm thấy
            
            for record_data in records_data:
                record_id = record_data.get("id")
                
                # Nếu là record mới (ID âm)
                if record_id and record_id < 0:
                    # Lấy thông tin nhân viên
                    mans = (record_data.get("mans") or "").strip()
                    employee_name = (record_data.get("employee_name") or "").strip()
                    
                    # Bắt buộc phải có MANS hoặc tên
                    if not mans and not employee_name:
                        continue
                    
                    # Tìm nhân viên - ưu tiên theo MANS
                    employee = False
                    
                    if mans:
                        # Tìm theo MANS (chính xác)
                        employee = Employee.search([("mans", "=", mans)], limit=1)
                    
                    if not employee and employee_name:
                        # Tìm theo tên (không phân biệt hoa thường)
                        employee = Employee.search([("name", "=ilike", employee_name)], limit=1)
                    
                    # VALIDATION: Nếu không tìm thấy -> BÁO LỖI
                    if not employee:
                        if mans and employee_name:
                            not_found_employees.append(f"MANS: '{mans}', Tên: '{employee_name}'")
                        elif mans:
                            not_found_employees.append(f"MANS: '{mans}'")
                        else:
                            not_found_employees.append(f"Tên: '{employee_name}'")
                        continue  # Bỏ qua record này, không tạo
                    
                    # Tạo grid record mới với employee đã tìm thấy
                    grid_vals = {
                        "employee_id": employee.id,
                        "month": str(month),
                        "year": year,
                    }
                    
                    # Thêm dữ liệu các ngày
                    for day in range(1, 32):
                        field_name = f"day_{day:02d}"
                        if field_name in record_data:
                            grid_vals[field_name] = record_data[field_name]
                    
                    self.create(grid_vals)
                
                # Nếu là record đã tồn tại
                elif record_id and record_id > 0:
                    grid = self.browse(record_id)
                    if not grid.exists():
                        continue
                    
                    # Cập nhật thông tin nhân viên nếu có thay đổi
                    employee_vals = {}
                    if "mans" in record_data and record_data["mans"] != grid.mans:
                        employee_vals["mans"] = record_data["mans"]
                    if "employee_name" in record_data and record_data["employee_name"] != grid.employee_name:
                        employee_vals["name"] = record_data["employee_name"]
                    
                    if employee_vals and grid.employee_id:
                        grid.employee_id.write(employee_vals)
                    
                    # Cập nhật dữ liệu các ngày
                    grid_vals = {}
                    for day in range(1, 32):
                        field_name = f"day_{day:02d}"
                        if field_name in record_data:
                            grid_vals[field_name] = record_data[field_name]
                    
                    if grid_vals:
                        grid.write(grid_vals)
            
            # Kiểm tra nếu có nhân viên không tồn tại
            if not_found_employees:
                error_message = "❌ Lưu thất bại! Không tìm thấy nhân viên trong hệ thống:\n\n"
                for idx, emp in enumerate(not_found_employees, 1):
                    error_message += f"{idx}. {emp}\n"
                error_message += "\n⚠️ Vui lòng kiểm tra lại MANS và tên nhân viên, hoặc tạo nhân viên trong hệ thống trước."
                return {"success": False, "message": error_message}
            
            # Đồng bộ tất cả grid records về monthly attendance lines
            self._sync_all_to_monthly_lines(month, year, department_id)
            
            return {"success": True, "message": "✅ Lưu thành công!"}
        
        except Exception as e:
            return {"success": False, "message": f"❌ Lỗi: {str(e)}"}
