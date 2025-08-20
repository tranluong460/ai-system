"""
Hệ thống kiểm tra tự động cho AI Assistant
"""
import sys
import os
import importlib.util

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

def check_imports():
    """Kiểm tra các import quan trọng"""
    checks = [
        ('assistant.core', 'AIAssistant'),
        ('memory.enhanced_memory', 'EnhancedMemorySystem'),
        ('tools.computer_tools', 'ToolExecutor'),
        ('learning.adaptive_system', 'LearningSystem'),
        ('emotion.emotion_system', 'EmotionSystem'),
        ('vision.enhanced_vision', 'EnhancedVision'),
        ('security.security_manager', 'SecurityManager'),
        ('ml.personalization_engine', 'PersonalizationSystem'),
    ]
    
    results = []
    for module_name, class_name in checks:
        try:
            module = importlib.import_module(module_name)
            getattr(module, class_name)
            results.append(f"[OK] {module_name}.{class_name}")
        except Exception as e:
            results.append(f"[FAIL] {module_name}.{class_name}: {e}")
    
    return results

def check_dependencies():
    """Kiểm tra các thư viện bắt buộc"""
    required_packages = [
        'requests', 'chromadb', 'sentence_transformers', 
        'numpy', 'scikit-learn', 'opencv-python', 'transformers'
    ]
    
    results = []
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            else:
                importlib.import_module(package.replace('-', '_'))
            results.append(f"[OK] {package}")
        except ImportError:
            results.append(f"[MISSING] {package}")
    
    return results

def check_directories():
    """Kiểm tra cấu trúc thư mục"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    required_dirs = [
        'src', 'data', 'logs', 'config', 'tests'
    ]
    
    results = []
    for dir_name in required_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path):
            results.append(f"[OK] {dir_name}/")
        else:
            results.append(f"[MISSING] {dir_name}/")
            # Tạo thư mục nếu thiếu
            os.makedirs(dir_path, exist_ok=True)
            results.append(f"[CREATED] {dir_name}/")
    
    return results

def main():
    """Chạy tất cả kiểm tra"""
    print("=" * 50)
    print("AI ASSISTANT SYSTEM CHECK")
    print("=" * 50)
    
    print("\n1. KIEM TRA IMPORTS:")
    for result in check_imports():
        print(f"  {result}")
    
    print("\n2. KIEM TRA DEPENDENCIES:")
    for result in check_dependencies():
        print(f"  {result}")
    
    print("\n3. KIEM TRA DIRECTORIES:")
    for result in check_directories():
        print(f"  {result}")
    
    print("\n" + "=" * 50)
    print("SYSTEM CHECK COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    main()