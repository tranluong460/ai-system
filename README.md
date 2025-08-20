# 🤖 AI Assistant System - Hệ thống Trợ lý AI Thông minh

Một hệ thống AI Assistant mạnh mẽ với khả năng học tập, ghi nhớ và tương tác thông minh.

---

## 📋 Tài Liệu Liên Quan

- 📖 **[README.md](./README.md)** - Tài liệu chính (file này)
- ⚡ **[QUICK_START.md](./QUICK_START.md)** - Hướng dẫn khởi động nhanh
- 🗂️ **[STRUCTURE.md](./STRUCTURE.md)** - Cấu trúc thư mục chi tiết

## 🚀 Khởi động nhanh

> 📖 **Xem hướng dẫn chi tiết:** [QUICK_START.md](./QUICK_START.md)

### **Bước 1: Khởi động hệ thống**
```bash
# Windows - Launcher đa chức năng
AI_System.bat

# Linux/Mac - Launcher đa chức năng
./AI_System.sh
```

### **Bước 2: Chọn chức năng**
- `[1]` 🚀 Khởi động AI Assistant
- `[2]` 🛠️ Thiết lập hệ thống 
- `[3]` 🔧 Chế độ phát triển
- `[4]` 🌐 Sửa lỗi Unicode
- `[5]` 🧪 Kiểm tra hệ thống
- `[6]` 📖 Xem hướng dẫn

## 📁 Cấu Trúc Dự Án

> 🗂️ **Xem cấu trúc chi tiết:** [STRUCTURE.md](./STRUCTURE.md)

```
ai-system/
├── 🎛️ AI_System.bat             # LAUNCHER WINDOWS (ALL-IN-ONE)
├── 🐧 AI_System.sh              # LAUNCHER LINUX/MAC (ALL-IN-ONE)
│
├── 📖 README.md                 # Tài liệu chính
├── ⚡ QUICK_START.md            # Hướng dẫn nhanh
├── 📋 STRUCTURE.md             # Cấu trúc chi tiết
│
├── 📦 requirements.txt          # Thư viện Python
│
├── 📁 src/                     # MÃ NGUỒN CHÍNH
├── 📁 scripts/                 # SCRIPTS HỆ THỐNG
├── 📁 data/                    # DỮ LIỆU & CACHE
├── 📁 config/                  # CẤU HÌNH
├── 📁 logs/                    # LOGS HỆ THỐNG
├── 📁 tests/                   # TESTS
├── 📁 notebooks/               # JUPYTER NOTEBOOKS
├── 📁 experiments/             # THÍ NGHIỆM
└── 📁 venv/                    # MÔI TRƯỜNG ẢO
```

## 🛠️ Cài Đặt và Sử Dụng

> ⚡ **Chi tiết đầy đủ:** [QUICK_START.md](./QUICK_START.md)

### **Chỉ cần 1 bước - Launcher tự động:**

```bash
# Windows:
AI_System.bat

# Linux/Mac:
./AI_System.sh
```

Launcher sẽ hiển thị menu tương tác với đầy đủ các tùy chọn thiết lập và sử dụng.

## 🎯 Sử Dụng

> 📋 **Hướng dẫn chi tiết:** [QUICK_START.md](./QUICK_START.md)

```bash
# Launcher tích hợp đầy đủ:
AI_System.bat/.sh

# Chạy trực tiếp:
python src/assistant/main.py
```

### 🎯 Tính Năng Chính:
- **🤖 AI Assistant thông minh** với khả năng học tập và ghi nhớ
- **📁 Quản lý file hệ thống** - tạo, copy, di chuyển files
- **💻 Thực hiện lệnh hệ thống** - chạy commands, kiểm tra thông tin
- **🧠 Bộ nhớ tăng cường** - Vector DB, Knowledge graphs
- **🔒 Bảo mật local-first** - mã hóa dữ liệu cục bộ
- **🎨 Xử lý hình ảnh** - OCR, Computer Vision
- **📊 Phân tích cảm xúc** - theo dõi mood, empathetic responses

### ⚡ Commands Đặc Biệt:
- `/help` - Hướng dẫn chi tiết
- `/name <tên>` - Đặt tên của bạn  
- `/feedback <1-5> <comment>` - Đánh giá AI
- `/stats` - Xem thống kê sử dụng
- `/tools` - Danh sách công cụ
- `/clear` - Xóa màn hình
- `/exit` - Thoát chương trình

## ⚙️ Cấu Hình

Hệ thống sử dụng các file cấu hình trong thư mục `config/` để tùy chỉnh hoạt động của AI Assistant.

## 🔧 Đặc Điểm Kỹ Thuật

- **🏗️ Kiến trúc modular** - Code được tổ chức theo module, dễ bảo trì
- **📝 Logging chi tiết** - Theo dõi hoạt động với logs chi tiết  
- **🧪 Testing framework** - Kiểm thử tự động với pytest
- **🔒 Bảo mật** - Mã hóa local, không gửi dữ liệu ra ngoài
- **🚀 Hot-reload** - Tự động restart khi code thay đổi
- **📊 Experiment tracking** - Theo dõi và so sánh thí nghiệm

## 📚 Công Nghệ Sử Dụng

- **🤖 Ollama** - Local LLM server
- **🧠 ChromaDB** - Vector database cho memory
- **🕸️ NetworkX** - Knowledge graphs
- **👁️ OpenCV, Tesseract** - Computer vision và OCR
- **📊 TextBlob, VADER** - Sentiment analysis
- **🔢 NumPy, Pandas** - Xử lý dữ liệu
- **🎨 Rich, Colorama** - Terminal UI đẹp