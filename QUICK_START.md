# 🚀 Quick Start Guide - AI Assistant

## ⚡ Khởi động trong 2 bước

### 1️⃣ **Khởi động hệ thống**
```bash
# Windows: Nhấp đúp vào file này
AI_System.bat

# Linux/Mac: Chạy terminal và gõ
./AI_System.sh
```

### 2️⃣ **Chọn chức năng trong menu**
- `[1]` 🚀 Khởi động AI Assistant  
- `[2]` 🛠️ Thiết lập hệ thống (lần đầu)
- `[3]` 🔧 Chế độ phát triển
- `[4]` 🌐 Sửa lỗi Unicode
- `[5]` 🧪 Kiểm tra hệ thống
- `[6]` 📖 Xem hướng dẫn

---

## 🛠️ Các tính năng nâng cao

### **Chế độ phát triển** (Hot reload)
```bash
# Chọn option [3] trong menu AI_System.bat/sh
# Hoặc chạy trực tiếp:
python scripts/dev.py
```
- 🔄 Tự động reload khi code thay đổi
- 🔧 Dành cho developers

### **Cấu hình Unicode** (Nếu emoji không hiển thị)
```bash  
# Chọn option [4] trong menu AI_System.bat/sh
# Hoặc chạy trực tiếp:
python scripts/fix_terminal_unicode.py
```
- 🌐 Sửa lỗi hiển thị emoji
- 💻 Tối ưu cho Windows terminal

---

## 🎯 Các lệnh AI Assistant

| Lệnh | Mô tả |
|------|--------|
| `/help` | Xem hướng dẫn |
| `/stats` | Thống kê sử dụng |
| `/name <tên>` | Đặt tên của bạn |
| `/feedback <1-5> <comment>` | Đánh giá AI |
| `/tools` | Xem tools khả dụng |
| `/exit` | Thoát |

---

## 🆘 Khắc phục sự cố

### **Lỗi Python không tìm thấy**
```bash
# Cài đặt Python từ python.org
# Chọn "Add to PATH" khi cài đặt
```

### **Lỗi Ollama không kết nối**
```bash
# Mở cmd riêng và chạy:
ollama serve
```

### **Lỗi Unicode/Emoji**
```bash
# Chạy:
AI_System.bat   # Windows - chọn option [4]
./AI_System.sh  # Linux/Mac - chọn option [4]

# Hoặc trực tiếp:
python scripts/fix_terminal_unicode.py
```

---

## 📞 Hỗ trợ

- 📖 Xem `README.md` để biết chi tiết
- 🔧 Kiểm tra thư mục `logs/` nếu có lỗi
- 💡 Tất cả các file `.bat` đều có thể nhấp đúp để chạy