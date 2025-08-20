# 📁 Cấu trúc thư mục AI Assistant System

## 🗂️ Thư mục gốc (Root Directory)

```
📁 ai-system/
├── 🎛️ AI_System.bat             # LAUNCHER WINDOWS (ALL-IN-ONE)
├── 🐧 AI_System.sh              # LAUNCHER LINUX/MAC (ALL-IN-ONE)
│
├── 📖 README.md                 # Tài liệu chính
├── ⚡ QUICK_START.md            # Hướng dẫn nhanh
├── 📋 STRUCTURE.md             # File này
│
├── 📦 requirements.txt          # Thư viện Python
│
├── 📁 src/                     # MÃ NGUỒN CHÍNH
├── 📁 scripts/                 # SCRIPTS HỆ THỐNG
│   ├── setup_ollama.py         # Thiết lập Ollama
│   ├── fix_terminal_unicode.py # Cấu hình Unicode
│   ├── dev.py                  # Hot-reload development
│   └── system_check.py         # Kiểm tra hệ thống
├── 📁 data/                    # DỮ LIỆU & CACHE
├── 📁 config/                  # CẤU HÌNH
├── 📁 logs/                    # LOGS HỆ THỐNG
├── 📁 tests/                   # TESTS
├── 📁 notebooks/               # JUPYTER NOTEBOOKS
├── 📁 experiments/             # THÍ NGHIỆM
└── 📁 venv/                    # MÔI TRƯỜNG ẢO
```

## 🎯 Cách sử dụng siêu đơn giản

### **2 FILE LAUNCHER CHÍNH:**
- `AI_System.bat` - Windows launcher 
- `AI_System.sh` - Linux/Mac launcher

### **MENU TƯƠNG TÁC:**
- `[1]` 🚀 Khởi động AI Assistant
- `[2]` 🛠️ Thiết lập hệ thống
- `[3]` 🔧 Chế độ phát triển  
- `[4]` 🌐 Sửa lỗi Unicode
- `[5]` 🧪 Kiểm tra hệ thống
- `[6]` 📖 Xem hướng dẫn

### **Tự động tạo:**
- `venv/` - Môi trường Python ảo
- `data/` - Cache và dữ liệu AI
- `logs/` - Log files

## ✨ Ưu điểm của cấu trúc mới

1. **🎯 Đơn giản hóa:** Chỉ cần nhấp đúp vào file `.bat`
2. **📱 User-friendly:** Tên file rõ ràng, dễ hiểu
3. **🔧 Tách biệt:** User vs Developer files
4. **📖 Tài liệu:** Hướng dẫn đầy đủ
5. **🧹 Sạch sẽ:** Loại bỏ file cũ không dùng