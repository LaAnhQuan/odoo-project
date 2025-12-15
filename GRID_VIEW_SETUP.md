# Hướng dẫn cài đặt nhanh Grid View

## Bước 1: Cài đặt module

```bash
# Nâng cấp module trong Odoo
odoo-bin -u mo_hr_monthly_attendance -d your_database

# Hoặc restart với --dev mode
odoo-bin --dev=all -u mo_hr_monthly_attendance -d your_database
```

## Bước 2: Kiểm tra cài đặt

### 2.1 Kiểm tra file đã tạo

Đảm bảo các file sau đã được tạo:

```
✅ models/hr_monthly_attendance_grid.py
✅ views/hr_monthly_attendance_grid_views.xml
✅ static/src/js/monthly_attendance_grid.js
✅ static/src/xml/monthly_attendance_grid.xml
✅ static/src/css/monthly_attendance_grid.css
```

### 2.2 Kiểm tra __manifest__.py

Đảm bảo có:

```python
"data": [
    ...
    "views/hr_monthly_attendance_grid_views.xml",
],
"assets": {
    "web.assets_backend": [
        "mo_hr_monthly_attendance/static/src/js/monthly_attendance_grid.js",
        "mo_hr_monthly_attendance/static/src/xml/monthly_attendance_grid.xml",
        "mo_hr_monthly_attendance/static/src/css/monthly_attendance_grid.css",
    ],
},
```

### 2.3 Kiểm tra security/ir.model.access.csv

Phải có dòng:
```csv
access_hr_monthly_attendance_grid,access_hr_monthly_attendance_grid,model_hr_monthly_attendance_grid,hr.group_hr_user,1,1,1,1
```

### 2.4 Kiểm tra models/__init__.py

Phải có:
```python
from . import hr_monthly_attendance_grid
```

## Bước 3: Thử nghiệm

### Test 1: Import Excel

1. Vào **HR → Bảng chấm công tháng**
2. Tạo bảng mới: Tháng 12/2025
3. Click **Import Excel (Ma trận)**
4. Upload file Excel của bạn
5. Click **Import**
6. ✅ **Kết quả mong đợi**: Grid view hiển thị tự động

### Test 2: Xem Grid từ bảng có sẵn

1. Vào bảng công đã có dữ liệu
2. Click button **Xem dạng Grid**
3. ✅ **Kết quả mong đợi**: Grid view hiển thị với dữ liệu

### Test 3: Click vào ô

1. Trong Grid view, click vào một ô có dữ liệu
2. ✅ **Kết quả mong đợi**: Mở form chấm công ngày

## Xử lý lỗi thường gặp

### Lỗi: "Cannot read properties of undefined"

**Nguyên nhân**: JavaScript chưa load

**Giải pháp**:
```bash
# Restart với dev mode
odoo-bin --dev=all
```

Sau đó Ctrl+Shift+R để clear cache browser.

### Lỗi: "Model hr.monthly.attendance.grid not found"

**Nguyên nhân**: Module chưa update

**Giải pháp**:
```bash
odoo-bin -u mo_hr_monthly_attendance -d your_database
```

### Lỗi: Grid view trống

**Nguyên nhân**: Chưa có dữ liệu hoặc chưa đồng bộ

**Giải pháp**:
1. Import file Excel lại
2. Hoặc vào form bảng công → Click "Xem dạng Grid"

### Lỗi: "Access Denied"

**Nguyên nhân**: Thiếu quyền

**Giải pháp**:
1. Kiểm tra user có group `hr.group_hr_user`
2. Kiểm tra `ir.model.access.csv` có đầy đủ

### Lỗi: CSS không hiển thị

**Nguyên nhân**: Assets chưa build

**Giải pháp**:
```bash
# Clear assets
rm -rf ~/.local/share/Odoo/sessions/*

# Restart Odoo
odoo-bin --dev=all
```

Hoặc trong browser: Ctrl+Shift+R (hard refresh)

## Debug mode

### Bật debug mode

Trong Odoo:
1. Settings → Activate Developer Mode
2. Hoặc thêm `?debug=1` vào URL

### Xem console log

Mở Chrome DevTools (F12):
- Console tab: Xem lỗi JavaScript
- Network tab: Kiểm tra file JS/CSS có load không

### Kiểm tra model trong database

```sql
-- Kiểm tra grid records
SELECT * FROM hr_monthly_attendance_grid LIMIT 10;

-- Kiểm tra daily attendance
SELECT * FROM hr_daily_attendance 
WHERE date >= '2025-12-01' AND date <= '2025-12-31'
LIMIT 10;
```

## Kiểm tra hoàn tất

✅ Module upgrade thành công  
✅ Không có lỗi trong log  
✅ Button "Xem dạng Grid" hiển thị trong form  
✅ Import Excel tự động mở Grid  
✅ Grid hiển thị đầy đủ nhân viên và ngày  
✅ Click vào ô mở được form chi tiết  
✅ Màu sắc hiển thị đúng  
✅ Tổng ngày công/giờ công tính đúng  

## Câu hỏi thường gặp

**Q: Grid view có thể xuất Excel không?**  
A: Hiện tại chưa có. Nhưng có thể dùng button "Export Excel" trong form bảng công.

**Q: Grid view có thể chỉnh sửa trực tiếp không?**  
A: Hiện tại chỉ xem. Muốn sửa click vào ô để mở form chi tiết.

**Q: Có thể filter theo phòng ban không?**  
A: Có. Khi mở grid từ bảng công có chọn phòng ban, grid sẽ tự động filter.

**Q: Grid view có in được không?**  
A: Có. CSS đã có print styles. Ctrl+P để in.

**Q: Làm sao thêm menu Grid vào sidebar?**  
A: Uncomment đoạn code menu trong file `hr_monthly_attendance_grid_views.xml`.

## Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Odoo log: `odoo-bin -d your_db --log-level=debug`
2. Browser console (F12)
3. File GRID_VIEW_README.md để biết thêm chi tiết
