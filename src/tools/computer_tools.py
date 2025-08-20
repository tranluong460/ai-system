"""
Tools để tương tác với máy tính
"""
import os
import subprocess
import shutil
import glob
import psutil
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path

class ComputerTools:
    """Class chứa các tools tương tác với máy tính"""
    
    def __init__(self):
        self.safe_mode = True  # Chế độ an toàn, hỏi trước khi thực hiện
    
    def execute_command(self, command: str, confirm: bool = True) -> Dict[str, Any]:
        """Thực hiện lệnh hệ thống"""
        if self.safe_mode and confirm:
            print(f"⚠️  Sắp thực hiện lệnh: {command}")
            choice = input("Xác nhận? (y/n): ").lower()
            if choice != 'y':
                return {"success": False, "message": "Đã hủy bởi người dùng"}
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Command timeout"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def list_files(self, path: str = ".", pattern: str = "*") -> List[Dict[str, Any]]:
        """Liệt kê files trong thư mục"""
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                return []
            
            files = []
            for item in path_obj.glob(pattern):
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir(),
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
            
            return sorted(files, key=lambda x: (not x["is_dir"], x["name"]))
        except Exception as e:
            return [{"error": str(e)}]
    
    def create_folder(self, path: str) -> Dict[str, Any]:
        """Tạo thư mục"""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return {"success": True, "message": f"Đã tạo thư mục: {path}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def copy_file(self, src: str, dst: str) -> Dict[str, Any]:
        """Copy file"""
        try:
            if self.safe_mode:
                print(f"🔄 Copy {src} -> {dst}")
                choice = input("Xác nhận? (y/n): ").lower()
                if choice != 'y':
                    return {"success": False, "message": "Đã hủy"}
            
            shutil.copy2(src, dst)
            return {"success": True, "message": f"Đã copy {src} -> {dst}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def move_file(self, src: str, dst: str) -> Dict[str, Any]:
        """Di chuyển file"""
        try:
            if self.safe_mode:
                print(f"📁 Move {src} -> {dst}")
                choice = input("Xác nhận? (y/n): ").lower()
                if choice != 'y':
                    return {"success": False, "message": "Đã hủy"}
            
            shutil.move(src, dst)
            return {"success": True, "message": f"Đã move {src} -> {dst}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def delete_file(self, path: str) -> Dict[str, Any]:
        """Xóa file/folder"""
        try:
            if self.safe_mode:
                print(f"🗑️  Delete: {path}")
                choice = input("Xác nhận? (y/n): ").lower()
                if choice != 'y':
                    return {"success": False, "message": "Đã hủy"}
            
            path_obj = Path(path)
            if path_obj.is_dir():
                shutil.rmtree(path)
            else:
                path_obj.unlink()
            
            return {"success": True, "message": f"Đã xóa: {path}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def read_file(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Đọc file"""
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True, 
                "content": content,
                "size": len(content),
                "lines": content.count('\n') + 1
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def write_file(self, path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Ghi file"""
        try:
            if self.safe_mode and Path(path).exists():
                print(f"📝 Ghi đè file: {path}")
                choice = input("Xác nhận? (y/n): ").lower()
                if choice != 'y':
                    return {"success": False, "message": "Đã hủy"}
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return {"success": True, "message": f"Đã ghi file: {path}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def search_files(self, query: str, path: str = ".", file_pattern: str = "*") -> List[Dict[str, Any]]:
        """Tìm kiếm files theo tên hoặc nội dung"""
        results = []
        
        try:
            # Tìm theo tên file
            for file_path in Path(path).rglob(file_pattern):
                if query.lower() in file_path.name.lower():
                    results.append({
                        "type": "filename",
                        "path": str(file_path),
                        "match": file_path.name
                    })
            
            # Tìm trong nội dung file text
            for file_path in Path(path).rglob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            results.append({
                                "type": "content",
                                "path": str(file_path),
                                "match": f"Found in content"
                            })
                except:
                    continue
            
            return results[:20]  # Giới hạn 20 kết quả
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_system_info(self) -> Dict[str, Any]:
        """Lấy thông tin hệ thống"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "processes": len(psutil.pids())
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Lấy danh sách processes đang chạy"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort theo CPU usage
            return sorted(processes, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_weather(self, city: str = "Ho Chi Minh City") -> Dict[str, Any]:
        """Lấy thông tin thời tiết (cần API key)"""
        try:
            # Sử dụng free weather API
            url = f"http://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                return {
                    "success": True,
                    "city": city,
                    "temperature": current['temp_C'],
                    "description": current['weatherDesc'][0]['value'],
                    "humidity": current['humidity'],
                    "wind_speed": current['windspeedKmph']
                }
            else:
                return {"success": False, "message": "Không thể lấy thông tin thời tiết"}
                
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """Mở ứng dụng"""
        try:
            if self.safe_mode:
                print(f"🚀 Mở ứng dụng: {app_name}")
                choice = input("Xác nhận? (y/n): ").lower()
                if choice != 'y':
                    return {"success": False, "message": "Đã hủy"}
            
            if os.name == 'nt':  # Windows
                os.startfile(app_name)
            else:  # Linux/Mac
                subprocess.Popen(['open', app_name])
            
            return {"success": True, "message": f"Đã mở: {app_name}"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def toggle_safe_mode(self):
        """Bật/tắt chế độ an toàn"""
        self.safe_mode = not self.safe_mode
        status = "BẬT" if self.safe_mode else "TẮT"
        return {"success": True, "message": f"Chế độ an toàn: {status}"}

class ToolExecutor:
    """Class thực hiện các tools dựa trên input của user"""
    
    def __init__(self):
        self.tools = ComputerTools()
        self.tool_mapping = {
            # File operations
            "list": self.tools.list_files,
            "create_folder": self.tools.create_folder,
            "copy": self.tools.copy_file,
            "move": self.tools.move_file,
            "delete": self.tools.delete_file,
            "read": self.tools.read_file,
            "write": self.tools.write_file,
            "search": self.tools.search_files,
            
            # System operations
            "system_info": self.tools.get_system_info,
            "processes": self.tools.get_running_processes,
            "command": self.tools.execute_command,
            "open": self.tools.open_application,
            
            # External APIs
            "weather": self.tools.get_weather,
            
            # Settings
            "safe_mode": self.tools.toggle_safe_mode
        }
    
    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Thực hiện tool"""
        if tool_name in self.tool_mapping:
            try:
                return self.tool_mapping[tool_name](**kwargs)
            except Exception as e:
                return {"success": False, "message": f"Lỗi thực hiện {tool_name}: {str(e)}"}
        else:
            return {"success": False, "message": f"Không tìm thấy tool: {tool_name}"}
    
    def get_available_tools(self) -> List[str]:
        """Lấy danh sách tools có sẵn"""
        return list(self.tool_mapping.keys())