"""
Development runner với hot-reload
"""
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from utils.hot_reload import HotReloader

def main():
    """Main development runner"""
    print("🔥 AI Assistant - Development Mode with Hot-Reload")
    print("=" * 60)
    
    # Script to run
    main_script = str(Path(__file__).parent / "src" / "assistant" / "main.py")
    
    # Directories to watch
    watch_dirs = [
        str(Path(__file__).parent / "src" / "assistant"),
        str(Path(__file__).parent / "src" / "tools"), 
        str(Path(__file__).parent / "src" / "learning"),
        str(Path(__file__).parent / "src" / "utils"),
        str(Path(__file__).parent / "config"),
    ]
    
    # Create and start hot-reloader
    reloader = HotReloader(main_script, watch_dirs)
    reloader.start()

if __name__ == "__main__":
    main()