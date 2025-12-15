# Cập nhật Grid View - Version 1.1

## Ngày: 2025-12-13

### Các thay đổi chính:

## 1. ✅ CSS - Sửa lỗi overflow text

### Vấn đề:
- Các cột MANS, tên nhân viên và ô ngày bị hiển thị mờ mờ khi text tràn
- Khó đọc dữ liệu

### Giải pháp:
Thêm vào **tất cả các ô table**:
```css
overflow: hidden;          /* Ẩn hoàn toàn text tràn */
text-overflow: ellipsis;   /* Hiển thị ... nếu tràn */
white-space: nowrap;       /* Không xuống dòng */
```

### Files đã sửa:
- `static/src/css/monthly_attendance_grid.css`
  - `.sticky-col` - Cột STT, MANS, Họ tên
  - `.o_grid_cell` - Các ô ngày
  - `.o_grid_cell_content` - Nội dung ô
  - `.o_grid_cell_number` - Cột STT
  - `.o_grid_cell_mans` - Cột MANS
  - `.o_grid_cell_name` - Cột Họ tên

### Kết quả:
- ✅ Text tràn bị ẩn hoàn toàn, không còn mờ mờ
- ✅ Hiển thị "..." khi text dài
- ✅ Dễ đọc hơn

---

## 2. ✅ Logic tính công - Thứ 7 tính nửa ngày

### Quy tắc mới:
**Thứ 7 với mã "W" (Công thường) → Chỉ tính 0.5 ngày công**

Các trường hợp:
- ✅ **Thứ 7 đi làm bình thường (W)**: 0.5 ngày công
- ✅ **Thứ 7 nghỉ phép (P)**: 1.0 ngày công (theo code P)
- ✅ **Thứ 7 không lương (KO)**: 0.0 ngày công (theo code KO)
- ✅ **Các ngày khác (T2-T6, CN)**: Giữ nguyên logic cũ

### Code cập nhật:

#### File: `models/hr_monthly_attendance_grid.py`

Trong method `_compute_totals()`:

```python
# Kiểm tra ngày có phải thứ 7 không
try:
    current_date = date(rec.year, month_int, day_num)
    is_saturday = current_date.weekday() == 5  # 5 = Saturday
except:
    is_saturday = False

# Tính ngày công từ code
if code == "W" and is_saturday:
    # Thứ 7 làm việc bình thường: chỉ tính 0.5 ngày công
    day_value = 0.5
else:
    # Các trường hợp khác: theo code
    day_value = code_to_value.get(code, 0.0)
```

### Files đã sửa:
- `models/hr_monthly_attendance_grid.py`
  - Method `_compute_totals()` - Thêm logic kiểm tra thứ 7
  - Added dependency: `month`, `year` vào `@api.depends`

### Visual indicator:

Thêm badge "0.5" vào header cột thứ 7:

#### File: `static/src/js/monthly_attendance_grid.js`
```javascript
isSaturday(day) {
    const date = new Date(this.state.year, this.state.month - 1, day);
    return date.getDay() === 6;
}
```

#### File: `static/src/xml/monthly_attendance_grid.xml`
```xml
<t t-if="isSaturday(day)">
    <span class="badge badge-warning">0.5</span>
</t>
```

#### File: `static/src/css/monthly_attendance_grid.css`
```css
.o_grid_cell_day.saturday {
    background: #ffeaa7;
    color: #d63031;
    font-weight: 700;
}
```

### Kết quả:
- ✅ Thứ 7 có nền vàng đậm hơn
- ✅ Hiển thị badge "0.5" ở header
- ✅ Tự động tính 0.5 công cho thứ 7 (code W)
- ✅ Các code khác vẫn theo logic cũ

---

## Ví dụ minh họa:

### Trước khi cập nhật:
```
Nhân viên A:
- Thứ 2-6: W (5 ngày) = 5.0 công
- Thứ 7: W (1 ngày) = 1.0 công
- Chủ nhật: OFF = 0.0 công
→ Tổng: 6.0 công ❌ (Sai!)
```

### Sau khi cập nhật:
```
Nhân viên A:
- Thứ 2-6: W (5 ngày) = 5.0 công
- Thứ 7: W (1 ngày) = 0.5 công ✅
- Chủ nhật: OFF = 0.0 công
→ Tổng: 5.5 công ✅ (Đúng!)
```

### Trường hợp đặc biệt:
```
Nhân viên B:
- Thứ 2-5: W (4 ngày) = 4.0 công
- Thứ 6: P (phép) = 1.0 công
- Thứ 7: P (phép) = 1.0 công ✅ (Vẫn 1.0 vì là phép, không phải W)
→ Tổng: 6.0 công
```

---

## Cách test:

### Test 1: CSS overflow
1. Import file Excel với tên nhân viên dài
2. Kiểm tra không có text mờ mờ
3. ✅ Text bị cắt và hiển thị "..."

### Test 2: Thứ 7 tính công
1. Tạo chấm công tháng 12/2025
2. Ngày 6, 13, 20, 27 (thứ 7) đánh mã "W"
3. Kiểm tra tổng công:
   - 4 thứ 7 × 0.5 = 2.0 công
   - 23 ngày khác (trừ CN) × 1.0 = 23.0 công
   - ✅ Tổng = 25.0 công

### Test 3: Visual
1. Mở Grid View
2. Các cột thứ 7 (6, 13, 20, 27) có:
   - ✅ Nền vàng đậm
   - ✅ Badge "0.5"
   - ✅ Chữ đỏ

---

## Breaking Changes:

### ⚠️ Tổng ngày công sẽ thay đổi!

Nếu đã có dữ liệu cũ:
- Tổng công của các tháng đã tính sẽ **tự động tính lại**
- Các bản ghi có thứ 7 mã "W" sẽ giảm 0.5 công/thứ 7

**Khuyến nghị**: Backup database trước khi upgrade!

---

## Migration Script (nếu cần)

Nếu muốn recalculate tất cả grid records:

```python
# Trong Odoo shell hoặc tạo migration script
grids = env['hr.monthly.attendance.grid'].search([])
grids._compute_totals()
```

---

## Files đã thay đổi:

1. ✅ `static/src/css/monthly_attendance_grid.css`
2. ✅ `static/src/js/monthly_attendance_grid.js`
3. ✅ `static/src/xml/monthly_attendance_grid.xml`
4. ✅ `models/hr_monthly_attendance_grid.py`

---

## Cài đặt:

```bash
# Nâng cấp module
odoo-bin -u mo_hr_monthly_attendance -d your_database

# Restart Odoo
# Clear browser cache (Ctrl+Shift+R)
```

---

## Changelog:

### v1.1 - 2025-12-13
- ✅ Fixed: Text overflow trong tất cả các ô
- ✅ Feature: Thứ 7 tính 0.5 ngày công
- ✅ UI: Badge "0.5" cho header thứ 7
- ✅ UI: Màu vàng đậm cho cột thứ 7

### v1.0 - 2025-12-12
- Initial release Grid View
