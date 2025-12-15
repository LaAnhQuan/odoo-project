# Module Bảng Chấm Công Grid View

## Tổng quan

Module này bổ sung **Grid View** (dạng bảng lưới) để hiển thị chấm công tháng, thay thế cho Calendar View không có sẵn trong Odoo Community Edition.

Grid view hiển thị:
- **Hàng**: Danh sách nhân viên (MANS, Họ tên)
- **Cột**: Các ngày trong tháng (1-31)
- **Ô**: Mã chấm công (W, P, KO, OFF...) và giờ công

## Tính năng chính

### 1. Grid View
- ✅ Hiển thị toàn bộ bảng công dạng ma trận
- ✅ Màu sắc phân biệt loại chấm công:
  - **Xanh lá**: Công (W)
  - **Xanh dương**: Phép (P, P/2)
  - **Đỏ**: Không lương (KO, KO/2)
  - **Xám**: Nghỉ (OFF)
- ✅ Highlight ngày cuối tuần
- ✅ Click vào ô để xem chi tiết chấm công ngày
- ✅ Tổng kết ngày công và giờ công

### 2. Import Excel tự động tạo Grid
- Import file Excel ma trận → Tự động tạo Grid View
- Đồng bộ dữ liệu từ `hr.daily.attendance` → `hr.monthly.attendance.grid`

### 3. Tương thích Community Edition
- Không cần Odoo Enterprise
- Không cần module calendar hay grid gốc
- Custom JavaScript widget hoàn toàn độc lập

## Cấu trúc Module

```
mo_hr_monthly_attendance/
├── models/
│   ├── hr_monthly_attendance_grid.py    # Model lưu dữ liệu grid
│   └── ...
├── wizard/
│   └── hr_monthly_attendance_import_wizard.py  # Import + sync grid
├── views/
│   └── hr_monthly_attendance_grid_views.xml    # XML views
├── static/
│   ├── src/
│   │   ├── js/
│   │   │   └── monthly_attendance_grid.js      # OWL Component
│   │   ├── xml/
│   │   │   └── monthly_attendance_grid.xml     # Template
│   │   └── css/
│   │       └── monthly_attendance_grid.css     # Styles
└── security/
    └── ir.model.access.csv
```

## Cài đặt

### 1. Cập nhật module

```bash
# Nâng cấp module
odoo-bin -u mo_hr_monthly_attendance -d your_database
```

### 2. Kiểm tra security

File `ir.model.access.csv` phải có dòng:
```csv
access_hr_monthly_attendance_grid,access_hr_monthly_attendance_grid,model_hr_monthly_attendance_grid,hr.group_hr_user,1,1,1,1
```

## Hướng dẫn sử dụng

### Cách 1: Import Excel → Tự động mở Grid

1. Vào **HR → Bảng chấm công tháng**
2. Tạo bảng công mới, chọn tháng/năm
3. Click **Import Excel (Ma trận)**
4. Upload file Excel
5. Click **Import**
6. ✅ Grid View sẽ tự động hiển thị sau khi import thành công

### Cách 2: Xem Grid từ bảng công hiện tại

1. Vào **HR → Bảng chấm công tháng**
2. Mở bảng công đã có sẵn
3. Click button **Xem dạng Grid** (màu xanh dương)
4. ✅ Grid View hiển thị dữ liệu từ chấm công ngày

### Cách 3: Menu Grid trực tiếp

**Chưa có menu mặc định, có thể thêm bằng cách:**

Thêm vào file `views/hr_monthly_attendance_grid_views.xml`:

```xml
<menuitem id="menu_hr_monthly_attendance_grid"
          name="Bảng chấm công Grid"
          parent="hr.menu_hr_root"
          action="action_hr_monthly_attendance_grid_menu"
          sequence="31"/>
```

## Các thao tác trong Grid View

### Click vào ô chấm công
- Mở form `hr.daily.attendance` của nhân viên trong ngày đó
- Có thể chỉnh sửa chi tiết check-in, check-out, giờ làm thêm

### Button "Làm mới"
- Reload dữ liệu từ database
- Cập nhật nếu có thay đổi từ chấm công ngày

### Màu sắc ô
- **Trắng/Trống**: Chưa có dữ liệu
- **Xanh lá**: Công (W)
- **Xanh dương**: Phép (P, P/2)
- **Đỏ**: Không lương (KO, KO/2)
- **Xám**: Nghỉ (OFF)
- **Vàng nhạt**: Cuối tuần (background)

## Đồng bộ dữ liệu

### Luồng dữ liệu

```
Excel Import → hr.daily.attendance → hr.monthly.attendance.grid
                                  ↓
                       hr.monthly.attendance (tổng hợp)
```

### Model `hr.monthly.attendance.grid`

**Fields:**
- `employee_id`: Nhân viên
- `month`, `year`: Tháng, năm
- `day_01` đến `day_31`: Dữ liệu 31 ngày
- `total_workdays`: Tổng ngày công
- `total_work_hours`: Tổng giờ công

**Methods:**
- `action_sync_from_daily()`: Đồng bộ từ chấm công ngày
- `sync_all_from_monthly_sheet(sheet_id)`: Đồng bộ toàn bộ sheet

## Tuỳ chỉnh

### Thay đổi màu sắc

Chỉnh file `static/src/css/monthly_attendance_grid.css`:

```css
.cell-work {
    background-color: #d1e7dd;  /* Màu xanh lá cho công */
}

.cell-leave {
    background-color: #cfe2ff;  /* Màu xanh dương cho phép */
}
```

### Thay đổi format hiển thị

Chỉnh method `_sync_to_grid_view()` trong `wizard/hr_monthly_attendance_import_wizard.py`:

```python
# Format hiện tại: "W (8h)"
display_value = f"{code} ({daily.work_hours:.0f}h)"

# Có thể đổi thành: "8h / 184h"
display_value = f"{daily.work_hours:.0f}h / 184h"
```

### Thêm filter phòng ban

Grid view đã hỗ trợ filter theo phòng ban qua context:

```python
{
    'default_department_id': department.id,
}
```

## Troubleshooting

### Grid không hiển thị dữ liệu

**Nguyên nhân**: Chưa đồng bộ từ daily attendance

**Giải pháp**:
1. Vào bảng công → Click "Xem dạng Grid"
2. Hoặc import lại file Excel

### Lỗi "model hr.monthly.attendance.grid not found"

**Nguyên nhân**: Module chưa được nâng cấp

**Giải pháp**:
```bash
odoo-bin -u mo_hr_monthly_attendance -d your_database
```

### Grid view bị trống sau import

**Nguyên nhân**: Import thất bại hoặc không có nhân viên

**Giải pháp**:
1. Kiểm tra log import có báo lỗi không
2. Đảm bảo nhân viên có MANS đúng
3. Kiểm tra file Excel đúng format

### Màu sắc không hiển thị

**Nguyên nhân**: CSS chưa load

**Giải pháp**:
1. Clear browser cache (Ctrl+Shift+R)
2. Kiểm tra `__manifest__.py` có khai báo assets đúng
3. Restart Odoo server với `--dev=all`

## API cho Developer

### Tạo grid programmatically

```python
Grid = self.env['hr.monthly.attendance.grid']

# Tạo mới
grid = Grid.create({
    'employee_id': employee.id,
    'month': '12',
    'year': 2025,
})

# Đồng bộ từ daily
grid.action_sync_from_daily()
```

### Lấy dữ liệu grid

```python
grids = self.env['hr.monthly.attendance.grid'].search([
    ('month', '=', '12'),
    ('year', '=', 2025),
    ('department_id', '=', dept.id),
])

for grid in grids:
    print(f"{grid.employee_name}: {grid.total_workdays} ngày")
```

### Mở grid view từ code

```python
return {
    'type': 'ir.actions.client',
    'tag': 'monthly_attendance_grid',
    'context': {
        'default_month': 12,
        'default_year': 2025,
    },
}
```

## Tương thích

- ✅ Odoo 15.0+
- ✅ Odoo 16.0+
- ✅ Odoo 17.0+
- ✅ Community Edition
- ✅ Enterprise Edition

## License

LGPL-3

## Tác giả

Phát triển cho dự án mo_hr_monthly_attendance

## Changelog

### Version 1.0
- ✅ Grid view component với OWL
- ✅ Import Excel tự động tạo grid
- ✅ Màu sắc phân loại chấm công
- ✅ Click để xem chi tiết
- ✅ Responsive design
- ✅ Tổng kết tự động
