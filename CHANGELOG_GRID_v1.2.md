# Cập nhật Grid View - Version 1.2

## Ngày: 2025-12-13

### 📋 Các thay đổi chính:

## 1. ✅ Sửa lỗi CSS - Các cột bị đè lên nhau

### Vấn đề:
- Các cột sticky (STT, MANS, Họ tên) bị đè lên các cột ngày
- Text hiển thị mờ mờ, khó đọc

### Giải pháp:

#### CSS Updates:
```css
/* Sticky chung - Sửa lỗi đè lên nhau */
.sticky-col {
    position: -webkit-sticky;
    position: sticky;
    background: #fff !important;
    z-index: 10 !important;
    border-right: 2px solid #adb5bd !important;
}

/* Width cố định cho từng cột */
- STT: 50px (left: 0)
- MANS: 100px (left: 50px)
- Họ tên: 200px (left: 150px)
```

### Kết quả:
- ✅ Các cột sticky không còn bị đè
- ✅ Border rõ ràng giữa các cột
- ✅ Width cố định, không bị tràn

---

## 2. ✅ Chủ nhật không hiển thị X

### Logic mới:
**Chủ nhật**: Không hiển thị gì (ô trống) nếu là X, W hoặc rỗng

### Code:
```javascript
shouldShowCellValue(record, day) {
    const date = new Date(this.state.year, this.state.month - 1, day);
    const isSunday = date.getDay() === 0;
    
    if (isSunday) {
        const value = this.getCellValue(record, day);
        const normalizedValue = (value || "").trim().toUpperCase();
        
        // Chỉ ẩn nếu là X, W hoặc rỗng
        if (!normalizedValue || normalizedValue === "X" || normalizedValue === "W") {
            return false;
        }
    }
    
    return true;
}
```

### Kết quả:
- ✅ Chủ nhật nghỉ bình thường: Không hiển thị gì
- ✅ Chủ nhật có mã đặc biệt (P, KO): Vẫn hiển thị

---

## 3. ✅ Thêm các cột tính toán chi tiết

### Các trường mới:

| Tên trường | Mô tả | Cách tính |
|------------|-------|-----------|
| **total_workdays** | Tổng công | W=1.0, Thứ 7=0.5, P=1.0 |
| **paid_leave_days** | Phép | P=1.0, P/2=0.5 |
| **unpaid_leave_days** | Không lương | KO=1.0, KO/2=0.5 |
| **maternity_days** | Thai sản | 0.0 (dự phòng) |
| **sick_days** | Ốm | 0.0 (dự phòng) |
| **holiday_days** | Lễ | 0.0 (dự phòng) |
| **tet_days** | Tết | 0.0 (dự phòng) |
| **company_anniversary_days** | Thành lập | 0.0 (dự phòng) |
| **salary_percentage** | % nhận lương | (Công / Ngày LV) × 100 |

### Logic tính toán:

#### File: `models/hr_monthly_attendance_grid.py`

```python
def _compute_totals(self):
    """Tính tổng các loại ngày công chi tiết"""
    
    for rec in self:
        total_days = 0.0
        paid_leave = 0.0
        unpaid_leave = 0.0
        
        # Tính số ngày làm việc trong tháng (trừ CN)
        working_days = 0
        for d in range(1, last_day + 1):
            dt = date(rec.year, month_int, d)
            if dt.weekday() == 6:  # Chủ nhật - bỏ qua
                continue
            elif dt.weekday() == 5:  # Thứ 7
                working_days += 0.5
            else:
                working_days += 1.0
        
        # Duyệt từng ngày
        for day_num in range(1, 32):
            value = getattr(rec, f"day_{day_num:02d}", None)
            if not value:
                continue
            
            code = value.split()[0].strip().upper()
            
            # Bỏ qua chủ nhật nghỉ bình thường
            if is_sunday and code in ["W", "X", ""]:
                continue
            
            # Phân loại
            if code in ["P", "P2", "P/2"]:
                day_value = code_to_value.get(code, 1.0)
                paid_leave += day_value
                total_days += day_value
                
            elif code in ["KO", "KO2", "KO/2"]:
                day_value = code_to_value.get(code, 1.0)
                unpaid_leave += day_value
                
            elif code in ["W", "X"]:
                if is_saturday:
                    day_value = 0.5
                else:
                    day_value = 1.0
                total_days += day_value
        
        # % lương
        salary_pct = (total_days / working_days) * 100.0 if working_days > 0 else 0.0
        rec.salary_percentage = min(salary_pct, 100.0)
```

---

## 4. ✅ Hiển thị các cột mới trong Grid

### Template XML Updates:

```xml
<!-- Header -->
<th>Công</th>
<th>Phép</th>
<th>Không lương</th>
<th>Thai sản</th>
<th>Ốm</th>
<th>Lễ</th>
<th>Tết</th>
<th>Thành lập</th>
<th>% nhận lương</th>

<!-- Body -->
<td class="o_grid_cell_total o_grid_cell_work">
    <strong><t t-esc="record.total_workdays.toFixed(1)"/></strong>
</td>
<td class="o_grid_cell_total o_grid_cell_leave">
    <strong><t t-esc="record.paid_leave_days.toFixed(1)"/></strong>
</td>
...
<td class="o_grid_cell_total o_grid_cell_percentage">
    <strong><t t-esc="record.salary_percentage.toFixed(2)"/>%</strong>
</td>
```

### CSS cho các cột:

```css
.o_grid_cell_work {
    background-color: #d1e7dd !important;  /* Xanh lá */
    color: #0f5132;
}

.o_grid_cell_leave {
    background-color: #cfe2ff !important;  /* Xanh dương */
    color: #084298;
}

.o_grid_cell_unpaid {
    background-color: #f8d7da !important;  /* Đỏ */
    color: #842029;
}

.o_grid_cell_percentage {
    background-color: #fff3cd !important;  /* Vàng */
    color: #664d03;
    font-weight: 700;
}
```

---

## 📊 Ví dụ tính toán:

### Tháng 12/2025:
```
Tổng ngày trong tháng: 31 ngày
Chủ nhật (1, 8, 15, 22, 29): 5 ngày → Không tính
Thứ 7 (6, 13, 20, 27): 4 ngày → 4 × 0.5 = 2.0 công
Các ngày khác: 22 ngày → 22 × 1.0 = 22.0 công
→ Tổng ngày làm việc chuẩn: 24.0 công
```

### Nhân viên A (ví dụ):
```
- T2-T6: W (22 ngày) = 22.0 công
- Thứ 7: W (4 ngày) = 2.0 công
- Chủ nhật: (ẩn) = 0.0 công
- Phép: P (1 ngày) = 1.0 công
- Không lương: KO/2 (1 ngày) = 0.5 công

→ Công: 23.0
→ Phép: 1.0
→ Không lương: 0.5
→ % lương: (23.0 / 24.0) × 100 = 95.83%
```

---

## 🚀 Cài đặt:

```bash
# Nâng cấp module
odoo-bin -u mo_hr_monthly_attendance -d your_database

# Restart Odoo server
# Clear browser cache (Ctrl+Shift+R)
```

---

## 📝 Files đã thay đổi:

### Backend:
1. ✅ `models/hr_monthly_attendance_grid.py`
   - Thêm 8 trường mới
   - Cập nhật `_compute_totals()` với logic chi tiết

### Frontend:
2. ✅ `static/src/js/monthly_attendance_grid.js`
   - Thêm `shouldShowCellValue()` - Ẩn X chủ nhật
   - Load các trường mới

3. ✅ `static/src/xml/monthly_attendance_grid.xml`
   - Thêm 9 cột header mới
   - Hiển thị các giá trị tính toán

4. ✅ `static/src/css/monthly_attendance_grid.css`
   - Sửa sticky columns (width cố định, z-index)
   - Style cho các cột tổng kết

### Views:
5. ✅ `views/hr_monthly_attendance_grid_views.xml`
   - Cập nhật form view
   - Cập nhật list view

---

## ⚠️ Breaking Changes:

### 1. Dữ liệu cũ sẽ tính lại
- Tất cả grid records sẽ recalculate
- % lương có thể thay đổi

### 2. Chủ nhật không còn hiển thị X
- UI sẽ khác so với trước

### 3. Cột "Tổng công" → "Công"
- Tên cột đã đổi

---

## 🧪 Test Cases:

### Test 1: CSS không đè
```
✅ Scroll ngang → Cột STT, MANS, Tên cố định
✅ Border rõ ràng giữa sticky và các cột ngày
✅ Text không bị mờ
```

### Test 2: Chủ nhật ẩn X
```
✅ Chủ nhật nghỉ bình thường: Ô trống
✅ Chủ nhật có P: Hiển thị "P"
✅ Chủ nhật có KO: Hiển thị "KO"
```

### Test 3: Tính toán chính xác
```
Input:
- 22 ngày W (T2-T6)
- 4 thứ 7 W
- 1 ngày P
- 1 ngày KO/2

Expected:
- Công: 24.0 (22 + 2 + 0)
- Phép: 1.0
- Không lương: 0.5
- % lương: 100%
```

### Test 4: Các cột hiển thị đúng
```
✅ 9 cột tổng kết hiển thị
✅ Màu sắc đúng (xanh/xanh dương/đỏ/vàng)
✅ Giá trị 1 chữ số thập phân
✅ % nhận lương 2 chữ số thập phân
```

---

## 📚 Tài liệu tham khảo:

- [GRID_VIEW_README.md](GRID_VIEW_README.md) - Hướng dẫn tổng quan
- [GRID_VIEW_SETUP.md](GRID_VIEW_SETUP.md) - Hướng dẫn cài đặt
- [CHANGELOG_GRID_v1.1.md](CHANGELOG_GRID_v1.1.md) - Version trước

---

## Changelog:

### v1.2 - 2025-12-13
- ✅ Fixed: CSS sticky columns bị đè
- ✅ Feature: Ẩn X cho chủ nhật
- ✅ Feature: Thêm 8 cột tính toán chi tiết
- ✅ Feature: Tính % nhận lương
- ✅ UI: Màu sắc cho các cột tổng kết
- ✅ Logic: Chủ nhật không tính công

### v1.1 - 2025-12-13
- ✅ Fixed: Text overflow
- ✅ Feature: Thứ 7 tính 0.5 công

### v1.0 - 2025-12-12
- Initial release Grid View
