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
            hasChanges: false, // Đánh dấu có thay đổi chưa lưu
            showEmployeeModal: false, // Hiển thị modal edit nhân viên
            editingRecord: null, // Record đang được edit trong modal
            showContextMenu: false, // Hiển thị context menu
            contextMenuPosition: { top: 0, left: 0 },
            contextMenuRecord: null, // Record cho context menu
            changedRecords: new Set(), // Set của record IDs đã thay đổi
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

    async onSaveChanges() {
        if (!this.state.hasChanges) return;

        this.state.loading = true;

        try {
            // Chuẩn bị dữ liệu để lưu
            const recordsToSave = this.state.records.filter(rec =>
                this.state.changedRecords.has(rec.id) || rec.id < 0
            );

            // Gọi API để lưu tất cả thay đổi
            const result = await this.orm.call(
                "hr.monthly.attendance.grid",
                "save_grid_changes",
                [recordsToSave, this.state.month, this.state.year, this.state.department_id],
                {}
            );

            if (result.success) {
                // Reset trạng thái thay đổi
                this.state.hasChanges = false;
                this.state.changedRecords.clear();

                // Reload dữ liệu
                await this.loadData();

                // Hiển thị thông báo thành công
                this.env.services.notification.add(
                    "Lưu thành công!",
                    { type: "success" }
                );
            }
        } catch (error) {
            console.error("Error saving changes:", error);
            this.env.services.notification.add(
                "Lỗi khi lưu dữ liệu: " + (error.message || "Unknown error"),
                { type: "danger" }
            );
        }

        this.state.loading = false;
    }

    onAddNewRow() {
        // Tạo record mới với ID âm (tạm thời)
        const newId = -(Date.now());
        const newRecord = {
            id: newId,
            employee_id: false,
            employee_name: "",
            mans: "",
            department_id: this.state.department_id ? [this.state.department_id, ""] : false,
            monthly_sheet_id: false,
            worked_days: 0,
            paid_leave_days: 0,
            unpaid_leave_days: 0,
            maternity_days: 0,
            holiday_days: 0,
            bereavement_days: 0,
            wedding_days: 0,
            overtime_hours: 0,
            total_paid_days: 0,
        };

        // Thêm các field day
        this.state.days.forEach(day => {
            const field = `day_${String(day).padStart(2, "0")}`;
            newRecord[field] = "";
        });

        this.state.records.push(newRecord);

        // Mở modal để nhập thông tin
        this.state.editingRecord = newRecord;
        this.state.showEmployeeModal = true;
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

        // Tìm record và cập nhật giá trị local
        const record = this.state.records.find(r => r.id === recordId);
        if (record) {
            const field = `day_${String(day).padStart(2, "0")}`;
            record[field] = code;

            // Đánh dấu record đã thay đổi
            this.state.changedRecords.add(recordId);
            this.state.hasChanges = true;

            // Tính lại totals cho record này
            this.recalculateTotals(record);
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
        // Đóng context menu
        if (this.state.showContextMenu) {
            this.state.showContextMenu = false;
            this.state.contextMenuRecord = null;
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

    onModalInputChange(event, field) {
        if (!this.state.editingRecord) return;

        const value = event.target.value;
        if (field === 'mans') {
            this.state.editingRecord.mans = value;
        } else if (field === 'employee_name') {
            this.state.editingRecord.employee_name = value;
        }
    }

    onCloseEmployeeModal() {
        // Nếu là record mới và chưa có tên, xóa khỏi danh sách
        if (this.state.editingRecord &&
            this.state.editingRecord.id < 0 &&
            !this.state.editingRecord.employee_name) {
            const index = this.state.records.findIndex(r => r.id === this.state.editingRecord.id);
            if (index >= 0) {
                this.state.records.splice(index, 1);
            }
        }

        this.state.showEmployeeModal = false;
        this.state.editingRecord = null;
    }

    onSaveEmployeeModal() {
        if (!this.state.editingRecord) return;

        // Kiểm tra đã nhập tên chưa
        if (!this.state.editingRecord.employee_name || !this.state.editingRecord.employee_name.trim()) {
            alert('Vui lòng nhập tên nhân viên!');
            return;
        }

        // Đánh dấu thay đổi
        this.state.changedRecords.add(this.state.editingRecord.id);
        this.state.hasChanges = true;

        // Đóng modal
        this.state.showEmployeeModal = false;
        this.state.editingRecord = null;
    }

    onRowRightClick(event, record) {
        event.preventDefault();
        event.stopPropagation();

        this.state.contextMenuRecord = record;
        this.state.showContextMenu = true;
        this.state.contextMenuPosition = {
            top: event.pageY,
            left: event.pageX,
        };
    }

    onEditEmployee(event, record) {
        event.stopPropagation();
        this.state.editingRecord = record;
        this.state.showEmployeeModal = true;
    }

    onEditEmployeeFromMenu() {
        if (!this.state.contextMenuRecord) return;

        this.state.editingRecord = this.state.contextMenuRecord;
        this.state.showEmployeeModal = true;
        this.state.showContextMenu = false;
        this.state.contextMenuRecord = null;
    }

    onDeleteEmployee() {
        if (!this.state.contextMenuRecord) return;

        if (!confirm(`Xóa nhân viên "${this.state.contextMenuRecord.employee_name}"?`)) {
            this.state.showContextMenu = false;
            return;
        }

        const index = this.state.records.findIndex(r => r.id === this.state.contextMenuRecord.id);
        if (index >= 0) {
            this.state.records.splice(index, 1);

            // Nếu là record đã tồn tại, đánh dấu cần xóa
            if (this.state.contextMenuRecord.id > 0) {
                // TODO: Thêm vào danh sách cần xóa
                this.state.hasChanges = true;
            }
        }

        this.state.showContextMenu = false;
        this.state.contextMenuRecord = null;
    }

    recalculateTotals(record) {
        // Tính lại totals cho record dựa trên các ngày đã nhập
        const codeToValue = {
            "P": 1.0, "P2": 0.5, "P/2": 0.5,
            "KO": 1.0, "KO2": 0.5, "KO/2": 0.5,
            "TS": 1.0, "TS2": 0.5, "TS/2": 0.5,
            "L": 1.0, "L2": 0.5, "L/2": 0.5,
            "H": 1.0, "H2": 0.5, "H/2": 0.5,
            "HY": 1.0, "HY2": 0.5, "HY/2": 0.5,
            "OFF": 0.0,
        };

        let worked = 0, leave = 0, unpaid = 0, maternity = 0;
        let holiday = 0, bereavement = 0, wedding = 0;

        this.state.days.forEach(day => {
            const field = `day_${String(day).padStart(2, "0")}`;
            const value = record[field] || "";
            const code = value.split(/[\s(]/)[0].trim().toUpperCase();

            if (!code || code === "OFF") return;

            const date = new Date(this.state.year, this.state.month - 1, day);
            const isSat = date.getDay() === 5;
            const isSun = date.getDay() === 6;

            if (code === "W" || code === "X") {
                if (isSun) worked += 0;
                else if (isSat) worked += 0.5;
                else worked += 1.0;
            } else if (code.startsWith("P")) {
                leave += codeToValue[code] || 1.0;
            } else if (code.startsWith("KO")) {
                unpaid += codeToValue[code] || 1.0;
            } else if (code.startsWith("TS")) {
                maternity += codeToValue[code] || 1.0;
            } else if (code.startsWith("L")) {
                holiday += codeToValue[code] || 1.0;
            } else if (code.startsWith("H") && !code.startsWith("HY")) {
                bereavement += codeToValue[code] || 1.0;
            } else if (code.startsWith("HY")) {
                wedding += codeToValue[code] || 1.0;
            }
        });

        record.worked_days = worked;
        record.paid_leave_days = leave;
        record.unpaid_leave_days = unpaid;
        record.maternity_days = maternity;
        record.holiday_days = holiday;
        record.bereavement_days = bereavement;
        record.wedding_days = wedding;
        record.total_paid_days = worked + leave + maternity + holiday + bereavement + wedding;
    }
}

MonthlyAttendanceGrid.template = "mo_hr_monthly_attendance.MonthlyAttendanceGrid";

// Register widget
registry.category("actions").add("monthly_attendance_grid", MonthlyAttendanceGrid);
