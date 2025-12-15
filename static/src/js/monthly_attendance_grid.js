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
            monthly_sheet_id: null,
            records: [],
            days: [],
            loading: true,
            editingCell: null, // {recordId, day}
            showDropdown: false,
            dropdownPosition: { top: 0, left: 0 },
        });

        this.attendanceCodes = [
            { code: "X", label: "Công", color: "#28a745" },
            { code: "W", label: "Công", color: "#28a745" },
            { code: "P", label: "Phép", color: "#ffc107" },
            { code: "P/2", label: "Phép 1/2", color: "#ffc107" },
            { code: "KO", label: "Không lương", color: "#dc3545" },
            { code: "KO/2", label: "Không lương 1/2", color: "#dc3545" },
            { code: "TS", label: "Thai sản", color: "#e83e8c" },
            { code: "TS/2", label: "Thai sản 1/2", color: "#e83e8c" },
            { code: "L", label: "Lễ", color: "#17a2b8" },
            { code: "L/2", label: "Lễ 1/2", color: "#17a2b8" },
            { code: "H", label: "Hiếu", color: "#6c757d" },
            { code: "H/2", label: "Hiếu 1/2", color: "#6c757d" },
            { code: "HY", label: "Hỷ", color: "#fd7e14" },
            { code: "HY/2", label: "Hỷ 1/2", color: "#fd7e14" },
            { code: "OFF", label: "Nghỉ", color: "#6c757d" },
            { code: "", label: "Xóa", color: "#ffffff" },
        ];

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
                "monthly_sheet_id",
                ...this.state.days.map(d => `day_${String(d).padStart(2, "0")}`),
                "worked_days",
                "paid_leave_days",
                "unpaid_leave_days",
                "maternity_days",
                "holiday_days",
                "bereavement_days",
                "wedding_days",
                "overtime_hours",
                "total_paid_days",
            ],
            { order: "employee_name" }
        );

        // Lấy monthly_sheet_id từ record đầu tiên (tất cả record trong cùng tháng có cùng sheet)
        if (this.state.records.length > 0 && this.state.records[0].monthly_sheet_id) {
            this.state.monthly_sheet_id = this.state.records[0].monthly_sheet_id[0];
        }

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

    async onCellClick(event, record, day) {
        // Hiển thị dropdown để chỉnh sửa
        event.stopPropagation();

        const cellRect = event.currentTarget.getBoundingClientRect();
        const dropdownHeight = 400; // Chiều cao ước tính của dropdown
        const viewportHeight = window.innerHeight;
        const spaceBelow = viewportHeight - cellRect.bottom;
        const spaceAbove = cellRect.top;

        // Quyết định hiển thị dropdown ở trên hay dưới
        let top, openUpward = false;

        if (spaceBelow < dropdownHeight && spaceAbove > spaceBelow) {
            // Không đủ chỗ bên dưới và trên có nhiều chỗ hơn -> hiển thị lên trên
            top = cellRect.top + window.scrollY - dropdownHeight;
            openUpward = true;
        } else {
            // Hiển thị xuống dưới (mặc định)
            top = cellRect.bottom + window.scrollY;
            openUpward = false;
        }

        this.state.editingCell = { recordId: record.id, day: day };
        this.state.showDropdown = true;
        this.state.dropdownPosition = {
            top: top,
            left: cellRect.left + window.scrollX,
            openUpward: openUpward,
        };
    }

    async onCodeSelect(code) {
        if (!this.state.editingCell) return;

        const { recordId, day } = this.state.editingCell;

        try {
            // Gọi API để update cell value
            const result = await this.orm.call(
                "hr.monthly.attendance.grid",
                "update_cell_value",
                [recordId, day, code],
                {}
            );

            if (result.success) {
                // Cập nhật lại dữ liệu local
                await this.loadData();
            }
        } catch (error) {
            console.error("Error updating cell:", error);
        }

        // Đóng dropdown
        this.state.showDropdown = false;
        this.state.editingCell = null;
    }

    onClickOutside() {
        // Đóng dropdown khi click bên ngoài
        if (this.state.showDropdown) {
            this.state.showDropdown = false;
            this.state.editingCell = null;
        }
    }

    async onBackToMonthlySheet() {
        // Quay lại bảng chấm công tháng chính
        if (this.state.monthly_sheet_id) {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "hr.monthly.attendance",
                res_id: this.state.monthly_sheet_id,
                views: [[false, "form"]],
                target: "current",
            });
        } else {
            // Tìm monthly sheet
            const sheets = await this.orm.searchRead(
                "hr.monthly.attendance",
                [
                    ["month", "=", String(this.state.month)],
                    ["year", "=", this.state.year],
                ],
                ["id"],
                { limit: 1 }
            );

            if (sheets.length > 0) {
                this.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: "hr.monthly.attendance",
                    res_id: sheets[0].id,
                    views: [[false, "form"]],
                    target: "current",
                });
            }
        }
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
