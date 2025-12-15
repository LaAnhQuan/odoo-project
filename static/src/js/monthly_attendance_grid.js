/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Monthly Attendance Grid Widget
 * Hiển thị bảng chấm công dạng lưới với nhân viên theo hàng, ngày theo cột
 */
export class MonthlyAttendanceGrid extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.state = useState({
            month: null,
            year: null,
            department_id: null,
            records: [],
            days: [],
            loading: true,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        const context = this.props.context || {};
        const month = context.default_month || new Date().getMonth() + 1;
        const year = context.default_year || new Date().getFullYear();
        const department_id = context.default_department_id || false;

        this.state.month = month;
        this.state.year = year;
        this.state.department_id = department_id;

        // Tính số ngày trong tháng
        const daysInMonth = new Date(year, month, 0).getDate();
        this.state.days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

        // Load grid records
        const domain = [
            ["month", "=", String(month)],
            ["year", "=", year],
        ];

        if (department_id) {
            domain.push(["department_id", "=", department_id]);
        }

        this.state.records = await this.orm.searchRead(
            "hr.monthly.attendance.grid",
            domain,
            [
                "id",
                "employee_id",
                "employee_name",
                "mans",
                "department_id",
                ...this.state.days.map(d => `day_${String(d).padStart(2, "0")}`),
                "worked_days",
                "paid_leave_days",
                "unpaid_leave_days",
                "overtime_hours",
                "total_paid_days",
            ],
            { order: "employee_name" }
        );

        this.state.loading = false;

        // Tính toán width động cho cột MANS sau khi render
        setTimeout(() => this.adjustMansColumnWidth(), 100);
    }

    adjustMansColumnWidth() {
        // Tìm tất cả các cell trong cột MANS
        const mansCells = document.querySelectorAll('.o_attendance_grid_table .sticky-col:nth-child(2)');
        if (mansCells.length === 0) return;

        // Tìm width lớn nhất
        let maxWidth = 80; // Min width
        mansCells.forEach(cell => {
            const textWidth = cell.scrollWidth;
            if (textWidth > maxWidth) {
                maxWidth = Math.min(textWidth + 20, 150); // +20 cho padding, max 150
            }
        });

        // Set CSS variable cho dynamic width
        document.documentElement.style.setProperty('--mans-width', `${maxWidth}px`);

        // Cập nhật left position của cột Họ tên
        const nameCells = document.querySelectorAll('.o_attendance_grid_table .sticky-col:nth-child(3)');
        nameCells.forEach(cell => {
            cell.style.left = `${50 + maxWidth}px`;
        });
    }

    async onRefresh() {
        this.state.loading = true;
        await this.loadData();
    }

    async onCellClick(record, day) {
        // Mở chi tiết chấm công ngày của nhân viên
        const date = `${this.state.year}-${String(this.state.month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

        const action = {
            type: "ir.actions.act_window",
            name: `Chấm công ${record.employee_name} - ${day}/${this.state.month}/${this.state.year}`,
            res_model: "hr.daily.attendance",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [
                ["employee_id", "=", record.employee_id[0]],
                ["date", "=", date],
            ],
            context: {
                default_employee_id: record.employee_id[0],
                default_date: date,
            },
        };

        this.action.doAction(action);
    }

    getCellValue(record, day) {
        const field = `day_${String(day).padStart(2, "0")}`;
        return record[field] || "";
    }

    shouldShowCellValue(record, day) {
        // Kiểm tra xem có phải chủ nhật không
        const date = new Date(this.state.year, this.state.month - 1, day);
        const isSunday = date.getDay() === 0;

        // Nếu là chủ nhật và giá trị là X hoặc W hoặc rỗng thì không hiển thị
        if (isSunday) {
            const value = this.getCellValue(record, day);
            const normalizedValue = (value || "").trim().toUpperCase();

            // Chỉ ẩn nếu là X, W hoặc rỗng (nghỉ bình thường)
            if (!normalizedValue || normalizedValue === "X" || normalizedValue === "W") {
                return false;
            }
        }

        return true;
    }

    getCellClass(record, day) {
        const value = this.getCellValue(record, day);

        if (!value) return "cell-empty";

        // Phân loại theo code
        if (value.includes("P")) return "cell-leave";
        if (value.includes("KO")) return "cell-unpaid";
        if (value.includes("OFF")) return "cell-off";

        return "cell-work";
    }

    getWeekday(day) {
        const date = new Date(this.state.year, this.state.month - 1, day);
        const weekdays = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"];
        return weekdays[date.getDay()];
    }

    isWeekend(day) {
        const date = new Date(this.state.year, this.state.month - 1, day);
        return date.getDay() === 0 || date.getDay() === 6;
    }

    isSaturday(day) {
        const date = new Date(this.state.year, this.state.month - 1, day);
        return date.getDay() === 6;
    }
}

MonthlyAttendanceGrid.template = "mo_hr_monthly_attendance.MonthlyAttendanceGrid";

// Register widget
registry.category("actions").add("monthly_attendance_grid", MonthlyAttendanceGrid);
