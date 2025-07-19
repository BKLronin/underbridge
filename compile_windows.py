#!/usr/bin/env python3
import os
import subprocess
import sys

def compile_for_windows():
    """Compile the application for Windows."""
    print("Compiling for Windows...")
    
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
        "--windows-icon-from-ico=logo.ico",
        "--windows-disable-console",
        "--static-libpython=no",
        "--output-dir=dist/windows",
        "underbridge.py"
    ]
    
    subprocess.run(cmd)
    print("Windows compilation complete. Output in dist/windows/")

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("dist/windows", exist_ok=True)
    
    compile_for_windows()