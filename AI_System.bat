@echo off
title AI Assistant System Launcher
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

:menu
cls
echo ========================================
echo     🤖 AI ASSISTANT SYSTEM 
echo ========================================
echo.
echo Chọn chức năng:
echo.
echo [1] 🚀 Khởi động AI Assistant
echo [2] 🛠️ Thiết lập hệ thống (Setup)
echo [3] 🔧 Chế độ phát triển (Dev Mode)
echo [4] 🌐 Sửa lỗi Unicode
echo [5] 🧪 Kiểm tra hệ thống
echo [6] 📖 Xem hướng dẫn
echo [0] 👋 Thoát
echo.
echo ========================================
set /p choice="Nhập lựa chọn (0-6): "

if "%choice%"=="1" goto start_ai
if "%choice%"=="2" goto setup
if "%choice%"=="3" goto dev_mode
if "%choice%"=="4" goto fix_unicode
if "%choice%"=="5" goto system_check
if "%choice%"=="6" goto help
if "%choice%"=="0" goto exit
echo Lựa chọn không hợp lệ!
pause
goto menu

:start_ai
cls
echo ========================================
echo        🤖 KHỞI ĐỘNG AI ASSISTANT
echo ========================================
echo.
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Môi trường ảo chưa được tạo!
    echo 💡 Chạy tùy chọn [2] để thiết lập hệ thống
    pause
    goto menu
)
echo 📦 Kích hoạt môi trường ảo...
call venv\Scripts\activate.bat
echo 🚀 Khởi động AI Assistant...
python src\assistant\main.py
echo.
echo 👋 AI Assistant đã kết thúc
pause
goto menu

:setup
cls
echo ========================================
echo         🛠️ THIẾT LẬP HỆ THỐNG
echo ========================================
echo.
echo Đang thiết lập môi trường AI Assistant...
echo.

echo [1/6] 📦 Tạo môi trường ảo Python...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Lỗi tạo môi trường ảo
        echo 💡 Kiểm tra Python đã cài đặt chưa
        pause
        goto menu
    )
    echo ✅ Môi trường ảo đã được tạo
) else (
    echo ✅ Môi trường ảo đã tồn tại
)

echo.
echo [2/6] 📦 Kích hoạt môi trường ảo...
call venv\Scripts\activate.bat

echo.
echo [3/6] 🔄 Cập nhật pip...
python -m pip install --upgrade pip

echo.
echo [4/6] 📥 Cài đặt thư viện...
pip install -r requirements.txt

echo.
echo [5/6] 🛠️ Thiết lập Ollama...
python scripts\setup_ollama.py

echo.
echo [6/6] 🧪 Kiểm tra hệ thống...
python scripts\system_check.py

echo.
echo ========================================
echo ✅ THIẾT LẬP HOÀN TẤT!
echo ========================================
pause
goto menu

:dev_mode
cls
echo ========================================
echo        🔧 CHẾ ĐỘ PHÁT TRIỂN
echo ========================================
echo.
echo 🔄 Khởi động Hot-Reload...
echo 💡 Code sẽ tự động reload khi thay đổi
echo 🛑 Nhấn Ctrl+C để dừng
echo.
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
python scripts\dev.py
echo.
echo 👋 Dev mode đã kết thúc
pause
goto menu

:fix_unicode
cls
echo ========================================
echo         🌐 SỬA LỖI UNICODE
echo ========================================
echo.
echo 🔧 Cấu hình Unicode cho Windows...
python scripts\fix_terminal_unicode.py
echo.
echo ✅ Hoàn tất cấu hình Unicode
pause
goto menu

:system_check
cls
echo ========================================
echo         🧪 KIỂM TRA HỆ THỐNG
echo ========================================
echo.
if exist "scripts\system_check.py" (
    python scripts\system_check.py
) else (
    echo ❌ File kiểm tra hệ thống không tìm thấy
)
echo.
pause
goto menu

:help
cls
echo ========================================
echo          📖 HƯỚNG DẪN SỬ DỤNG
echo ========================================
echo.
echo 🎯 CÁC TÍNH NĂNG CHÍNH:
echo.
echo 🚀 [1] Khởi động AI Assistant:
echo     - Chạy trợ lý AI với giao diện chat
echo     - Hỗ trợ nhiều model AI (qwen2.5:7b khuyến nghị)
echo     - Có memory và học từ tương tác
echo.
echo 🛠️ [2] Thiết lập hệ thống:
echo     - Cài đặt môi trường Python ảo
echo     - Tải các thư viện cần thiết
echo     - Thiết lập Ollama và AI models
echo.
echo 🔧 [3] Chế độ phát triển:
echo     - Hot-reload cho developers
echo     - Tự động restart khi code thay đổi
echo.
echo 🌐 [4] Sửa lỗi Unicode:
echo     - Khắc phục lỗi hiển thị emoji
echo     - Tối ưu cho Windows terminal
echo.
echo 📋 CÁC FILE QUAN TRỌNG:
echo     - QUICK_START.md: Hướng dẫn nhanh
echo     - README.md: Tài liệu chi tiết
echo     - requirements.txt: Danh sách thư viện
echo.
pause
goto menu

:exit
cls
echo ========================================
echo        👋 CẢM ƠN BẠN ĐÃ SỬ DỤNG
echo          AI ASSISTANT SYSTEM
echo ========================================
echo.
echo 💡 Để sử dụng lại, chạy: AI_System.bat
echo 📖 Xem tài liệu: QUICK_START.md
echo.
pause
exit