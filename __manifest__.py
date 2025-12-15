{
    "name": "Monthly Attendance Sheet",
    "version": "1.0",
    "summary": "Bảng chấm công tháng phục vụ tính lương",
    "description": """
        Bảng chấm công tháng cho nhân viên
        - Import / Export Excel dạng ma trận (giống file thực tế)
        - Chuẩn hoá dữ liệu ngày công theo mã (W, P, P2, KO, KO2…)
        - Tổng hợp từ chấm công ngày
        - Chuẩn bị dữ liệu cho tính lương
    """,
    "author": "Your Name",
    "depends": [
        "hr",
        "hr_attendance",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",

        "views/hr_employee_views.xml",
        "views/hr_daily_attendance_views.xml",
        "views/hr_monthly_attendance_import_wizard_views.xml",
        "views/hr_monthly_attendance_views.xml",
        "views/hr_monthly_attendance_grid_views.xml",

    ],
    "assets": {
        "web.assets_backend": [
            "mo_hr_monthly_attendance/static/src/js/monthly_attendance_grid.js",
            "mo_hr_monthly_attendance/static/src/xml/monthly_attendance_grid.xml",
            "mo_hr_monthly_attendance/static/src/css/monthly_attendance_grid.css",
        ],
    },
    "installable": True,
    "application": False,
}
