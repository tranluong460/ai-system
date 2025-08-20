"""
Script để cài đặt và cấu hình Ollama local LLM
"""
import subprocess
import sys
import os
import requests
import time

def run_command(command):
    """Chạy command và trả về kết quả"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore'  # Ignore encoding errors
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def download_ollama():
    """Download và cài đặt Ollama"""
    print("🔄 Downloading Ollama...")
    
    if os.name == 'nt':  # Windows
        ollama_url = "https://ollama.com/download/windows"
        print(f"📥 Vui lòng tải Ollama từ: {ollama_url}")
        print("💡 Sau khi cài đặt xong, chạy lại script này")
        return False
    else:  # Linux/Mac
        success, output, error = run_command("curl -fsSL https://ollama.com/install.sh | sh")
        if success:
            print("✅ Ollama đã được cài đặt thành công!")
            return True
        else:
            print(f"❌ Lỗi khi cài đặt Ollama: {error}")
            return False

def check_ollama_installed():
    """Kiểm tra xem Ollama đã được cài đặt chưa"""
    success, output, error = run_command("ollama --version")
    return success

def start_ollama_service():
    """Khởi động Ollama service"""
    print("🔄 Khởi động Ollama service...")
    
    if os.name == 'nt':  # Windows
        success, output, error = run_command("ollama serve")
    else:  # Linux/Mac
        success, output, error = run_command("ollama serve &")
    
    # Đợi service khởi động
    time.sleep(5)
    return check_ollama_running()

def check_ollama_running():
    """Kiểm tra xem Ollama service có đang chạy không"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def pull_model(model_name="llama3.2"):
    """Tải model từ Ollama"""
    print(f"📦 Đang tải model {model_name}...")
    print("⚠️  Quá trình này có thể mất vài phút...")
    
    try:
        # Use Popen for better control over long-running process
        process = subprocess.Popen(
            f"ollama pull {model_name}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        # Show progress
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Filter out non-essential progress messages
                if any(keyword in output.lower() for keyword in ['pulling', 'verifying', 'writing', 'success']):
                    print(f"📥 {output.strip()}")
        
        return_code = process.poll()
        
        if return_code == 0:
            print(f"✅ Model {model_name} đã được tải thành công!")
            return True
        else:
            print(f"❌ Lỗi khi tải model (return code: {return_code})")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi tải model: {e}")
        return False

def list_available_models():
    """Liệt kê các model có sẵn"""
    print("📋 Các model được khuyến nghị:")
    models = {
        "llama3.2": "Model tổng quát tốt, nhẹ (2GB)",
        "llama3.2:3b": "Model nhỏ, phù hợp máy yếu (2GB)", 
        "qwen2.5:7b": "Model mạnh cho coding (4.7GB)",
        "codellama:7b": "Chuyên về coding (3.8GB)",
        "mistral:7b": "Cân bằng tốt (4.1GB)"
    }
    
    for model, description in models.items():
        print(f"  • {model}: {description}")
    
    return models

def test_model(model_name="llama3.2"):
    """Test model với câu hỏi đơn giản"""
    print(f"🧪 Testing model {model_name}...")
    
    test_prompt = "Hello! Please introduce yourself briefly."
    
    try:
        # Use Popen with proper encoding handling
        process = subprocess.Popen(
            f'ollama run {model_name} "{test_prompt}"',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        stdout, stderr = process.communicate(timeout=30)
        
        if process.returncode == 0:
            print("✅ Model hoạt động tốt!")
            print("📤 Phản hồi từ AI:")
            print(stdout)
            return True
        else:
            print(f"❌ Lỗi khi test model: {stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ Test timeout - model có thể đang load")
        return False
    except Exception as e:
        print(f"❌ Lỗi khi test model: {e}")
        return False

def main():
    print("🤖 Local AI Assistant Setup")
    print("=" * 40)
    
    # 1. Kiểm tra Ollama đã cài đặt
    if not check_ollama_installed():
        print("❌ Ollama chưa được cài đặt")
        download_ollama()
        return
    
    print("✅ Ollama đã được cài đặt")
    
    # 2. Kiểm tra service có chạy không
    if not check_ollama_running():
        print("🔄 Ollama service chưa chạy, đang khởi động...")
        if not start_ollama_service():
            print("❌ Không thể khởi động Ollama service")
            print("💡 Thử chạy: ollama serve")
            return
    
    print("✅ Ollama service đang chạy")
    
    # 3. Hiển thị các model có sẵn
    models = list_available_models()
    
    # 4. Cho phép user chọn model
    print("\n🎯 Chọn model để tải:")
    model_choice = input("Nhập tên model (mặc định: llama3.2): ").strip()
    if not model_choice:
        model_choice = "llama3.2"
    
    # 5. Tải model
    if pull_model(model_choice):
        # 6. Test model
        test_model(model_choice)
        
        print("\n🎉 Setup hoàn tất!")
        print(f"💬 Để chat với AI, sử dụng: ollama run {model_choice}")
        print("🔧 Tiếp theo, chạy main AI assistant: python src/assistant/main.py")
    else:
        print("❌ Setup thất bại")

if __name__ == "__main__":
    main()