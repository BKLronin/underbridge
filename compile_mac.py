#!/usr/bin/env python3
import os
import subprocess
import sys

def compile_for_mac():
    """Compile the application for macOS."""
    print("Compiling for macOS...")
    
    # Ensure we have the necessary dependencies
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
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
    # Create output directory if it doesn't exist
    os.makedirs("dist/macos", exist_ok=True)
    
    compile_for_mac()