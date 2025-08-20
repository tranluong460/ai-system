"""
Development runner với hot-reload
"""
import sys
import os
from pathlib import Path

# Add src to path - go up one level from scripts to project root, then into src
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from utils.hot_reload import HotReloader

def main():
    """Main development runner"""
    print("AI Assistant - Development Mode with Hot-Reload")
    print("=" * 60)
    
    # Script to run
    main_script = str(project_root / "src" / "assistant" / "main.py")
    
    # Directories to watch
    watch_dirs = [
        str(project_root / "src" / "assistant"),
        str(project_root / "src" / "tools"), 
        str(project_root / "src" / "learning"),
        str(project_root / "src" / "utils"),
        str(project_root / "config"),
    ]
    
    # Create and start hot-reloader
    reloader = HotReloader(main_script, watch_dirs)
    reloader.start()

if __name__ == "__main__":
    main()