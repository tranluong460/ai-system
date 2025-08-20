"""
Hot-reload mechanism để tự động restart khi code thay đổi
"""
import os
import sys
import time
import threading
import subprocess
from pathlib import Path
from typing import Set, Callable
import hashlib

class FileWatcher:
    """Theo dõi thay đổi file"""
    
    def __init__(self, watch_dirs: list, file_extensions: list = None):
        self.watch_dirs = [Path(d) for d in watch_dirs]
        self.file_extensions = file_extensions or ['.py']
        self.file_hashes = {}
        self.callbacks = []
        self.running = False
        self.thread = None
    
    def add_callback(self, callback: Callable):
        """Thêm callback khi file thay đổi"""
        self.callbacks.append(callback)
    
    def _get_file_hash(self, filepath: Path) -> str:
        """Tính hash của file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _scan_files(self) -> Set[Path]:
        """Scan tất cả files cần theo dõi"""
        files = set()
        for watch_dir in self.watch_dirs:
            if watch_dir.exists():
                for ext in self.file_extensions:
                    files.update(watch_dir.rglob(f"*{ext}"))
        return files
    
    def _check_changes(self):
        """Kiểm tra thay đổi files"""
        current_files = self._scan_files()
        changes_detected = False
        
        # Kiểm tra files mới hoặc đã thay đổi
        for filepath in current_files:
            current_hash = self._get_file_hash(filepath)
            if filepath not in self.file_hashes:
                # File mới
                self.file_hashes[filepath] = current_hash
                if self.file_hashes:  # Không trigger lần đầu
                    print(f"🆕 New file: {filepath}")
                    changes_detected = True
            elif self.file_hashes[filepath] != current_hash:
                # File thay đổi
                print(f"🔄 Changed: {filepath}")
                self.file_hashes[filepath] = current_hash
                changes_detected = True
        
        # Kiểm tra files đã xóa
        deleted_files = set(self.file_hashes.keys()) - current_files
        for filepath in deleted_files:
            print(f"🗑️  Deleted: {filepath}")
            del self.file_hashes[filepath]
            changes_detected = True
        
        if changes_detected:
            for callback in self.callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"❌ Callback error: {e}")
    
    def _watch_loop(self):
        """Vòng lặp theo dõi"""
        print("👀 File watcher started...")
        
        # Scan initial files
        self._check_changes()
        
        while self.running:
            try:
                time.sleep(1)  # Check every 1 second
                self._check_changes()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Watcher error: {e}")
                time.sleep(5)
    
    def start(self):
        """Bắt đầu theo dõi"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Dừng theo dõi"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

class HotReloader:
    """Hot-reload manager"""
    
    def __init__(self, main_script: str, watch_dirs: list = None):
        self.main_script = main_script
        self.watch_dirs = watch_dirs or ['src']
        self.process = None
        self.watcher = None
        self.restart_count = 0
        self.last_restart = 0
        
    def _restart_app(self):
        """Restart ứng dụng"""
        current_time = time.time()
        
        # Debounce: không restart quá nhanh (minimum 2 seconds)
        if current_time - self.last_restart < 2:
            return
        
        self.last_restart = current_time
        self.restart_count += 1
        
        print(f"\n🔄 Hot-reload #{self.restart_count} - Restarting application...")
        
        # Stop current process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                print(f"❌ Error stopping process: {e}")
        
        # Start new process with Unicode support
        try:
            # Prepare environment for Unicode
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Set console code page for Windows
            if sys.platform == 'win32':
                try:
                    subprocess.run('chcp 65001 > nul', shell=True, check=False)
                except:
                    pass
            
            self.process = subprocess.Popen(
                [sys.executable, self.main_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace',
                env=env
            )
            
            # Monitor output in separate thread
            threading.Thread(
                target=self._monitor_output, 
                daemon=True
            ).start()
            
            print(f"✅ Application restarted (PID: {self.process.pid})")
            
        except Exception as e:
            print(f"❌ Failed to restart: {e}")
    
    def _monitor_output(self):
        """Monitor subprocess output"""
        if not self.process:
            return
            
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    print(f"{line.rstrip()}")
        except Exception as e:
            print(f"❌ Output monitor error: {e}")
    
    def start(self):
        """Bắt đầu hot-reload"""
        print("🚀 Starting hot-reload development mode...")
        print(f"📁 Watching directories: {self.watch_dirs}")
        print("💡 Press Ctrl+C to stop")
        
        # Setup file watcher
        self.watcher = FileWatcher(
            watch_dirs=self.watch_dirs,
            file_extensions=['.py', '.yaml', '.yml', '.json']
        )
        self.watcher.add_callback(self._restart_app)
        
        # Start initial app
        self._restart_app()
        
        # Start file watcher
        self.watcher.start()
        
        try:
            # Keep main thread alive
            while True:
                if self.process and self.process.poll() is not None:
                    # Process died, restart it
                    print("⚠️  Process died, restarting...")
                    self._restart_app()
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping hot-reload...")
            self.stop()
    
    def stop(self):
        """Dừng hot-reload"""
        if self.watcher:
            self.watcher.stop()
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                pass
        
        print("✅ Hot-reload stopped")

def create_dev_runner():
    """Tạo development runner với hot-reload"""
    script_path = Path(__file__).parent.parent / "assistant" / "main.py"
    watch_dirs = [
        str(Path(__file__).parent.parent / "assistant"),
        str(Path(__file__).parent.parent / "tools"),
        str(Path(__file__).parent.parent / "learning"),
        str(Path(__file__).parent.parent / "utils"),
    ]
    
    return HotReloader(str(script_path), watch_dirs)

if __name__ == "__main__":
    reloader = create_dev_runner()
    reloader.start()