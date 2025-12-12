# HƯỚNG DẪN TEST MODULE CHẤM CÔNG THÁNG

## 📋 CHUẨN BỊ

### 1. Cài đặt thư viện Python
```powershell
pip install openpyxl
```

### 2. Kiểm tra cấu trúc file
- ✅ `wizard/__init__.py` (đã sửa từ init.py)
- ✅ `static/src/xlsx/monthly_template.xlsx` (đã có)
- ✅ `security/ir.model.access.csv` (đã thêm access rights)

### 3. Restart Odoo Server
Sau khi sửa code, restart Odoo server để load lại module.

---

## 🔧 BƯỚC 1: CÀI ĐẶT/NÂNG CẤP MODULE

1. Vào Odoo → Apps
2. Tìm module "Monthly Attendance Sheet"
3. Click **Upgrade** (hoặc Install nếu chưa cài)
4. Đợi quá trình upgrade hoàn tất

**Lỗi thường gặp:**
- ❌ "Model not found": Kiểm tra file `wizard/__init__.py` tồn tại
- ❌ "action_export_csv is not valid": Đã sửa thành `action_export_xlsx_matrix`
- ❌ Access denied: Kiểm tra file `ir.model.access.csv`

---

## 👥 BƯỚC 2: TẠO DỮ LIỆU NHÂN VIÊN

### Tạo nhân viên test
1. Vào **HR → Employees → Create**
2. Tạo ít nhất 3 nhân viên với thông tin:
   - **Tên**: Nguyễn Văn A
   - **MANS**: NV001 (quan trọng để import/export)
   - **Department**: Phòng kế toán
   
3. Tương tự tạo thêm:
   - Tên: Trần Thị B, MANS: NV002
   - Tên: Lê Văn C, MANS: NV003

**Lưu ý:** Trường MANS rất quan trọng để map dữ liệu khi import Excel!

---

## 📅 BƯỚC 3: TẠO BẢNG CHẤM CÔNG THÁNG

1. Vào menu **HR → Monthly Attendance Sheet**
2. Click **Create**
3. Điền thông tin:
   - **Tháng**: 12
   - **Năm**: 2025
   - **Công ty**: (chọn công ty hiện tại)
   - **Phòng ban**: (có thể để trống)
4. Click **Save**

---

## 📥 BƯỚC 4: TEST IMPORT EXCEL

### A. Chuẩn bị file Excel

1. Tạo file Excel với cấu trúc:
   ```
   Row 8 (Header):
   | A (STT) | B (MANS) | C (Họ tên) | D (01) | E (02) | F (03) | ... | AH (31) |
   
   Row 9 (Data):
   | 1 | NV001 | Nguyễn Văn A |   |   | P | ... | KO |
   | 2 | NV002 | Trần Thị B   | P |   |   | ... |    |
   | 3 | NV003 | Lê Văn C     |   | X |   | ... | P/2|
   ```

2. **Quy tắc nhập dữ liệu:**
   - Để trống = Công (W)
   - `P` = Nghỉ phép cả ngày
   - `P/2` hoặc `P2` = Nghỉ phép nửa ngày
   - `KO` = Nghỉ không lương
   - `KO/2` hoặc `KO2` = Nghỉ không lương nửa ngày
   - `OFF` = Nghỉ
   - `X` hoặc `C` = Công

### B. Thực hiện import

1. Mở bảng chấm công tháng vừa tạo
2. Click nút **"Import Excel (Ma trận)"**
3. Upload file Excel
4. Click **Import**

**Kết quả mong đợi:**
- Hiển thị thông báo: "Import thành công. Tạo mới: XX | Cập nhật: YY"
- Không có lỗi "Không tìm thấy nhân viên"

**Lỗi thường gặp:**
- ❌ "Không tìm thấy nhân viên": MANS trong Excel không khớp với MANS trong hệ thống
- ❌ "Thiếu thư viện openpyxl": Chạy `pip install openpyxl`
- ❌ "UnicodeEncodeError": Lỗi encoding, đã fix trong code

---

## 📊 BƯỚC 5: TÍNH BẢNG CÔNG

1. Sau khi import xong, click nút **"Tính từ chấm công ngày"**
2. Hệ thống sẽ:
   - Đọc tất cả dữ liệu chấm công ngày trong tháng
   - Tổng hợp theo nhân viên
   - Tính toán:
     - **Ngày công thực tế**: Tổng giá trị W, P, P2 theo quy đổi
     - **Ngày phép**: Tổng P (1.0) + P2 (0.5)
     - **Ngày không lương**: Tổng KO, KO2, OFF
     - **Giờ làm thêm**: Từ hr.daily.attendance
3. Click tab **Chi tiết chấm công** để xem kết quả

**Kết quả mong đợi:**
- State chuyển sang **"Đã tính từ chấm công"**
- Tab "Chi tiết chấm công" hiển thị danh sách nhân viên với số liệu tổng hợp

---

## 📤 BƯỚC 6: TEST EXPORT EXCEL

1. Trong bảng chấm công tháng, click nút **"Export Excel"**
2. File Excel sẽ được tải về tự động

**Kiểm tra file export:**
- ✅ Tên file: `Bang_cham_cong_12_2025.xlsx`
- ✅ Format giống template (giữ nguyên merge cells, màu sắc, logo)
- ✅ Dữ liệu được điền vào đúng vị trí:
  - Cột B: MANS
  - Cột C: Họ tên
  - Cột D-AH: Các ngày trong tháng
- ✅ Mã chấm công hiển thị đúng:
  - Trống = Công
  - P/2, Ko/2 được format đúng

**Lỗi thường gặp:**
- ❌ "Không tìm thấy template": Kiểm tra file `static/src/xlsx/monthly_template.xlsx`
- ❌ "Thiếu thư viện openpyxl": Chạy `pip install openpyxl`
- ❌ File không tải về: Kiểm tra permissions và đường dẫn

---

## ✅ BƯỚC 7: TEST WORKFLOW HOÀN CHỈNH

### Test flow đầy đủ:

1. **Draft** → Import Excel → Tính từ chấm công
2. **Computed** → Click "Xác nhận"
3. **Confirmed** → Click "Đã chuyển lương"
4. **Done** → Click "Chuyển về nháp" (nếu cần sửa)

### Test case nâng cao:

#### Test 1: Import rồi tính lại
1. Import file Excel lần 1
2. Tính từ chấm công
3. Import file Excel lần 2 (sửa dữ liệu)
4. Tính lại từ chấm công
→ Dữ liệu phải được cập nhật, không bị trùng

#### Test 2: Export rồi re-import
1. Export Excel
2. Sửa dữ liệu trong file export
3. Import lại file vừa sửa
4. Tính lại
→ Dữ liệu phải khớp với file sửa

#### Test 3: Test với nhân viên không có MANS
1. Tạo nhân viên không điền MANS
2. Trong Excel chỉ điền Họ tên
3. Import
→ Phải tìm được nhân viên theo tên (nếu không trùng)

---

## 🐛 XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi 1: UnicodeEncodeError
**Nguyên nhân:** Windows console encoding
**Giải pháp:** Đã fix trong code, restart Odoo server

### Lỗi 2: Model not found
**Nguyên nhân:** File `wizard/__init__.py` sai tên
**Giải pháp:** Đã đổi tên từ `init.py` → `__init__.py`

### Lỗi 3: action_export_csv not found
**Nguyên nhân:** Tên method không khớp
**Giải pháp:** Đã sửa thành `action_export_xlsx_matrix`

### Lỗi 4: Access Denied
**Nguyên nhân:** Thiếu quyền trong security/ir.model.access.csv
**Giải pháp:** Đã thêm access rights cho tất cả models

### Lỗi 5: Import không tìm thấy nhân viên
**Nguyên nhân:** MANS trong Excel không khớp với hệ thống
**Giải pháp:** 
- Kiểm tra MANS trong HR → Employees
- Đảm bảo MANS trong Excel khớp chính xác (case-sensitive)
- Hoặc chỉ điền Họ tên (nếu không trùng)

---

## 📝 CHECKLIST CUỐI CÙNG

### Trước khi test:
- [ ] Đã cài openpyxl: `pip install openpyxl`
- [ ] Đã restart Odoo server
- [ ] Đã upgrade module thành công
- [ ] File `wizard/__init__.py` tồn tại
- [ ] File `static/src/xlsx/monthly_template.xlsx` tồn tại

### Test import:
- [ ] Tạo được file Excel đúng format
- [ ] MANS nhân viên khớp với hệ thống
- [ ] Import thành công không lỗi
- [ ] Dữ liệu được tạo trong hr.daily.attendance

### Test tính công:
- [ ] Click "Tính từ chấm công ngày" thành công
- [ ] State chuyển sang "Đã tính từ chấm công"
- [ ] Số liệu tổng hợp hiển thị đúng
- [ ] Tab "Chi tiết chấm công" có dữ liệu

### Test export:
- [ ] Click "Export Excel" tải file về
- [ ] File giữ nguyên format template
- [ ] Dữ liệu hiển thị đúng vị trí
- [ ] Mã chấm công format đúng (P/2, Ko/2...)

---

## 🎯 KẾT LUẬN

Module đã được sửa và sẵn sàng để test. Các lỗi chính đã được khắc phục:

1. ✅ Sửa tên file `wizard/__init__.py`
2. ✅ Sửa method export từ `action_export_csv` → `action_export_xlsx_matrix`
3. ✅ Thêm access rights đầy đủ
4. ✅ Sửa lỗi load workbook trong import wizard
5. ✅ Template Excel đã tồn tại

**Bước tiếp theo:** 
1. Restart Odoo server
2. Upgrade module
3. Làm theo hướng dẫn test từ Bước 1-7

**Nếu gặp lỗi mới, cung cấp:**
- Full error traceback
- Bước đang thực hiện
- Screenshot (nếu có)
