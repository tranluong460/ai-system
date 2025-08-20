#!/bin/bash

# AI Assistant System Launcher for Linux/Mac
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

show_menu() {
    clear
    echo "========================================"
    echo "     🤖 AI ASSISTANT SYSTEM"
    echo "========================================"
    echo
    echo "Chọn chức năng:"
    echo
    echo "[1] 🚀 Khởi động AI Assistant"
    echo "[2] 🛠️ Thiết lập hệ thống (Setup)"
    echo "[3] 🔧 Chế độ phát triển (Dev Mode)"
    echo "[4] 🌐 Sửa lỗi Unicode"
    echo "[5] 🧪 Kiểm tra hệ thống"
    echo "[6] 📖 Xem hướng dẫn"
    echo "[0] 👋 Thoát"
    echo
    echo "========================================"
    read -p "Nhập lựa chọn (0-6): " choice
}

start_ai() {
    clear
    echo "========================================"
    echo "        🤖 KHỞI ĐỘNG AI ASSISTANT"
    echo "========================================"
    echo
    
    if [ ! -d "venv" ]; then
        echo "❌ Môi trường ảo chưa được tạo!"
        echo "💡 Chạy tùy chọn [2] để thiết lập hệ thống"
        read -p "Nhấn Enter để tiếp tục..."
        return
    fi
    
    echo "📦 Kích hoạt môi trường ảo..."
    source venv/bin/activate
    echo "🚀 Khởi động AI Assistant..."
    python src/assistant/main.py
    echo
    echo "👋 AI Assistant đã kết thúc"
    read -p "Nhấn Enter để tiếp tục..."
}

setup_system() {
    clear
    echo "========================================"
    echo "         🛠️ THIẾT LẬP HỆ THỐNG"
    echo "========================================"
    echo
    echo "Đang thiết lập môi trường AI Assistant..."
    echo

    echo "[1/6] 📦 Tạo môi trường ảo Python..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo "❌ Lỗi tạo môi trường ảo"
            echo "💡 Kiểm tra Python3 đã cài đặt chưa"
            read -p "Nhấn Enter để tiếp tục..."
            return
        fi
        echo "✅ Môi trường ảo đã được tạo"
    else
        echo "✅ Môi trường ảo đã tồn tại"
    fi

    echo
    echo "[2/6] 📦 Kích hoạt môi trường ảo..."
    source venv/bin/activate

    echo
    echo "[3/6] 🔄 Cập nhật pip..."
    python -m pip install --upgrade pip

    echo
    echo "[4/6] 📥 Cài đặt thư viện..."
    pip install -r requirements.txt

    echo
    echo "[5/6] 🛠️ Thiết lập Ollama..."
    python scripts/setup_ollama.py

    echo
    echo "[6/6] 🧪 Kiểm tra hệ thống..."
    if [ -f "scripts/system_check.py" ]; then
        python scripts/system_check.py
    else
        echo "❌ File kiểm tra hệ thống không tìm thấy"
    fi

    echo
    echo "========================================"
    echo "✅ THIẾT LẬP HOÀN TẤT!"
    echo "========================================"
    read -p "Nhấn Enter để tiếp tục..."
}

dev_mode() {
    clear
    echo "========================================"
    echo "        🔧 CHẾ ĐỘ PHÁT TRIỂN"
    echo "========================================"
    echo
    echo "🔄 Khởi động Hot-Reload..."
    echo "💡 Code sẽ tự động reload khi thay đổi"
    echo "🛑 Nhấn Ctrl+C để dừng"
    echo
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python scripts/dev.py
    echo
    echo "👋 Dev mode đã kết thúc"
    read -p "Nhấn Enter để tiếp tục..."
}

fix_unicode() {
    clear
    echo "========================================"
    echo "         🌐 SỬA LỖI UNICODE"
    echo "========================================"
    echo
    echo "🔧 Cấu hình Unicode cho terminal..."
    python scripts/fix_terminal_unicode.py
    echo
    echo "✅ Hoàn tất cấu hình Unicode"
    read -p "Nhấn Enter để tiếp tục..."
}

system_check() {
    clear
    echo "========================================"
    echo "         🧪 KIỂM TRA HỆ THỐNG"
    echo "========================================"
    echo
    
    if [ -f "scripts/system_check.py" ]; then
        python scripts/system_check.py
    else
        echo "❌ File kiểm tra hệ thống không tìm thấy"
    fi
    echo
    read -p "Nhấn Enter để tiếp tục..."
}

show_help() {
    clear
    echo "========================================"
    echo "          📖 HƯỚNG DẪN SỬ DỤNG"
    echo "========================================"
    echo
    echo "🎯 CÁC TÍNH NĂNG CHÍNH:"
    echo
    echo "🚀 [1] Khởi động AI Assistant:"
    echo "     - Chạy trợ lý AI với giao diện chat"
    echo "     - Hỗ trợ nhiều model AI (qwen2.5:7b khuyến nghị)"
    echo "     - Có memory và học từ tương tác"
    echo
    echo "🛠️ [2] Thiết lập hệ thống:"
    echo "     - Cài đặt môi trường Python ảo"
    echo "     - Tải các thư viện cần thiết"
    echo "     - Thiết lập Ollama và AI models"
    echo
    echo "🔧 [3] Chế độ phát triển:"
    echo "     - Hot-reload cho developers"
    echo "     - Tự động restart khi code thay đổi"
    echo
    echo "🌐 [4] Sửa lỗi Unicode:"
    echo "     - Khắc phục lỗi hiển thị emoji"
    echo "     - Tối ưu cho terminal"
    echo
    echo "📋 CÁC FILE QUAN TRỌNG:"
    echo "     - QUICK_START.md: Hướng dẫn nhanh"
    echo "     - README.md: Tài liệu chi tiết"
    echo "     - requirements.txt: Danh sách thư viện"
    echo
    read -p "Nhấn Enter để tiếp tục..."
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1) start_ai ;;
        2) setup_system ;;
        3) dev_mode ;;
        4) fix_unicode ;;
        5) system_check ;;
        6) show_help ;;
        0) 
            clear
            echo "========================================"
            echo "        👋 CẢM ƠN BẠN ĐÃ SỬ DỤNG"
            echo "          AI ASSISTANT SYSTEM"
            echo "========================================"
            echo
            echo "💡 Để sử dụng lại, chạy: ./AI_System.sh"
            echo "📖 Xem tài liệu: QUICK_START.md"
            echo
            exit 0
            ;;
        *)
            echo "Lựa chọn không hợp lệ!"
            sleep 2
            ;;
    esac
done