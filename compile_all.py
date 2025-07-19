#!/usr/bin/env python3
import os
import platform
import subprocess
import sys

def compile_for_windows():
    """Compile the application for Windows."""
    print("Compiling for Windows...")
    
    # Compile with Nuitka
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--follow-imports",
        "--include-package=mido",
        "--include-package=pyaudio",
        "--include-package=nicegui",
        "--include-data-files=logo.ico=logo.ico",
        "--windows-icon-from-ico=logo.ico",
        "--windows-disable-console",
        "--static-libpython=no",
        "--output-dir=dist/windows",
        "underbridge.py"
    ]
    
    subprocess.run(cmd)
    print("Windows compilation complete. Output in dist/windows/")

def compile_for_mac():
    """Compile the application for macOS."""
    print("Compiling for macOS...")
    
    # Compile with Nuitka
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--follow-imports",
        "--include-package=mido",
        "--include-package=pyaudio",
        "--include-package=nicegui",
        "--include-data-files=logo.ico=logo.ico",
        "--macos-create-app-bundle",
        "--macos-app-icon=logo.ico",  # Note: For macOS, you should ideally use a .icns file
        "--static-libpython=no",
        "--output-dir=dist/macos",
        "underbridge.py"
    ]
    
    subprocess.run(cmd)
    print("macOS compilation complete. Output in dist/macos/")

if __name__ == "__main__":
    # Create output directories if they don't exist
    os.makedirs("dist/windows", exist_ok=True)
    os.makedirs("dist/macos", exist_ok=True)
    
    # Ensure we have the necessary dependencies
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Detect platform and compile accordingly
    current_platform = platform.system()
    
    if len(sys.argv) > 1:
        # If platform is specified as an argument
        if sys.argv[1].lower() == "windows":
            compile_for_windows()
        elif sys.argv[1].lower() == "mac" or sys.argv[1].lower() == "macos":
            compile_for_mac()
        elif sys.argv[1].lower() == "all":
            compile_for_windows()
            compile_for_mac()
        else:
            print(f"Unknown platform: {sys.argv[1]}")
            print("Usage: python compile_all.py [windows|mac|all]")
    else:
        # Auto-detect platform
        if current_platform == "Windows":
            compile_for_windows()
        elif current_platform == "Darwin":  # macOS
            compile_for_mac()
        else:
            print(f"Unsupported platform for automatic compilation: {current_platform}")
            print("Please specify platform: python compile_all.py [windows|mac|all]")