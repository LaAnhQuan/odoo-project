# Fix Grid View - Sticky Columns

## Vấn đề đã sửa:

### 1. ✅ Lòi ra ở mép phải khi scroll
**Nguyên nhân**: Sticky columns có shadow và border làm lòi ra ngoài vùng hiển thị

**Giải pháp**: 
```css
.sticky-col {
    clip-path: inset(0 -10px 0 0);
    /* Cắt phần thừa ở bên phải, giữ shadow bên trái */
}
```

### 2. ✅ Cột MANS co dãn động theo text
**Thay đổi**:
- Từ: `width: 100px` (cố định)
- Thành: `width: auto` với `min-width: 80px` và `max-width: 150px`

**JavaScript động**:
```javascript
adjustMansColumnWidth() {
    // Tính width lớn nhất của tất cả MANS
    let maxWidth = 80;
    mansCells.forEach(cell => {
        maxWidth = Math.min(cell.scrollWidth + 20, 150);
    });
    
    // Set CSS variable
    document.documentElement.style.setProperty('--mans-width', `${maxWidth}px`);
    
    // Cập nhật left position của cột Họ tên
    nameCells.forEach(cell => {
        cell.style.left = `${50 + maxWidth}px`;
    });
}
```

### 3. ✅ Cột Họ tên cũng co dãn
```css
.sticky-col:nth-child(3) {
    left: calc(50px + var(--mans-width, 130px)) !important;
    width: auto;
    min-width: 180px;
    max-width: 250px;
}
```

## Cách hoạt động:

1. **Load data** → JavaScript tính toán width thực tế của MANS
2. **Set CSS variable** `--mans-width` 
3. **Cột Họ tên tự động adjust** position dựa trên MANS width
4. **Clip-path** cắt phần lòi ra ở mép phải

## Files đã sửa:

1. ✅ `static/src/css/monthly_attendance_grid.css`
   - Thêm `clip-path` cho sticky columns
   - Width auto cho MANS và Họ tên
   - Dynamic left position

2. ✅ `static/src/js/monthly_attendance_grid.js`
   - Method `adjustMansColumnWidth()`
   - Gọi sau khi load data xong

## Test:

```
✅ Scroll ngang → Không còn lòi ra mép phải
✅ MANS ngắn (VD: "ABC") → Cột nhỏ ~80px
✅ MANS dài (VD: "BTGDDUONG...") → Cột rộng ~130px
✅ Cột Họ tên tự động dịch chuyển theo MANS
```

## Refresh:

```bash
# Clear cache browser
Ctrl + Shift + R
```
