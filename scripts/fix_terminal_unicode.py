"""
Fix Terminal Unicode/Emoji Support on Windows
"""
import os
import sys
import subprocess
import locale

def enable_unicode_terminal():
    """Enable Unicode and emoji support in Windows terminal"""
    print("🔧 Configuring Windows terminal for Unicode/emoji support...")
    
    # 1. Set environment variables
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # 2. Set console code page to UTF-8
    if sys.platform == 'win32':
        try:
            # Enable UTF-8 code page
            subprocess.run('chcp 65001', shell=True, check=True)
            print("✅ Console code page set to UTF-8 (65001)")
        except subprocess.CalledProcessError:
            print("⚠️ Could not set console code page")
    
    # 3. Configure Python locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        print("✅ Locale set to UTF-8")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            print("✅ Locale set to C.UTF-8")
        except locale.Error:
            print("⚠️ Could not set UTF-8 locale")
    
    # 4. Set Windows console to use Unicode
    if sys.platform == 'win32':
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get console handles
            STD_OUTPUT_HANDLE = -11
            STD_ERROR_HANDLE = -12
            
            kernel32 = ctypes.windll.kernel32
            
            # Set console output code page to UTF-8
            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)
            
            print("✅ Windows console configured for UTF-8")
        except Exception as e:
            print(f"⚠️ Could not configure Windows console: {e}")
    
    # 5. Test emoji display
    print("\n🧪 Testing emoji display:")
    test_emojis = ["🤖", "🧠", "✅", "❌", "🔧", "📊", "💡", "🚀"]
    for emoji in test_emojis:
        try:
            print(f"  {emoji} - OK")
        except UnicodeEncodeError:
            print(f"  [?] - Failed to display emoji")
    
    print("\n📝 Additional recommendations:")
    print("1. Use Windows Terminal (not Command Prompt)")
    print("2. Install a font that supports emojis (e.g., Segoe UI Emoji)")
    print("3. Set terminal font to 'Cascadia Code' or similar")
    
    return True

def create_terminal_config():
    """Create Windows Terminal configuration for better Unicode support"""
    terminal_config = {
        "profiles": {
            "defaults": {
                "fontFace": "Cascadia Code",
                "fontSize": 12,
                "colorScheme": "Campbell Powershell"
            }
        },
        "schemes": [
            {
                "name": "Unicode Friendly",
                "background": "#0C0C0C",
                "foreground": "#CCCCCC",
                "black": "#0C0C0C",
                "blue": "#0037DA",
                "brightBlack": "#767676",
                "brightBlue": "#3B78FF",
                "brightCyan": "#61D6D6",
                "brightGreen": "#16C60C",
                "brightPurple": "#B4009E",
                "brightRed": "#E74856",
                "brightWhite": "#F2F2F2",
                "brightYellow": "#F9F1A5",
                "cyan": "#3A96DD",
                "green": "#13A10E",
                "purple": "#881798",
                "red": "#C50F1F",
                "white": "#CCCCCC",
                "yellow": "#C19C00"
            }
        ]
    }
    
    # Try to find Windows Terminal settings file
    terminal_settings_path = os.path.expanduser("~/AppData/Local/Packages/Microsoft.WindowsTerminal_8wekyb3d8bbwe/LocalState/settings.json")
    
    if os.path.exists(os.path.dirname(terminal_settings_path)):
        print(f"💡 Windows Terminal settings location: {terminal_settings_path}")
        print("   You can manually update your terminal settings for better Unicode support")
    else:
        print("💡 Windows Terminal not found. Consider installing it from Microsoft Store")
    
    return terminal_config

def main():
    """Main function to enable Unicode terminal support"""
    print("🌟 Windows Terminal Unicode/Emoji Enabler")
    print("=" * 50)
    
    try:
        # Enable Unicode support
        enable_unicode_terminal()
        
        # Create terminal config suggestion
        create_terminal_config()
        
        print("\n🎉 Unicode configuration completed!")
        print("💡 Restart your terminal/IDE for changes to take effect")
        
        # Test if configuration worked
        print("\n🧪 Final test - if you see emojis below, it worked!")
        print("🤖 AI Assistant ready! 🚀")
        
    except Exception as e:
        print(f"❌ Error configuring Unicode support: {e}")
        print("💡 Try running as administrator or use Windows Terminal")

if __name__ == "__main__":
    main()