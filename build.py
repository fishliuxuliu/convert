#!/usr/bin/env python3
"""
构建脚本 - 生成独立 exe
用法: python build.py
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"


def step1_install_deps():
    print("=" * 50)
    print("步骤1: 安装依赖...")
    print("=" * 50)
    subprocess.run(
        [sys.executable, "-m", "pip", "install",
         "-r", str(ROOT / "requirements.txt"), "--quiet"]
    )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"]
    )
    print("✅ 依赖安装完成\n")


def step2_build():
    print("=" * 50)
    print("步骤2: PyInstaller 打包...")
    print("=" * 50)

    # 清理旧构建
    if DIST.exists():
        shutil.rmtree(DIST)

    spec_file = ROOT / "build.spec"

    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", str(spec_file)],
        capture_output=False,
    )

    if result.returncode != 0:
        print("❌ 打包失败，请检查上方错误信息")
        sys.exit(1)

    # 找 exe
    dist_dir = DIST / "DocMarkdownConverter"
    exe_files = list(dist_dir.glob("*.exe"))

    if exe_files:
        exe_path = exe_files[0]
        size_mb = exe_path.stat().st_size / 1024 / 1024
        print(f"\n{'='*50}")
        print(f"🎉 构建成功!")
        print(f"{'='*50}")
        print(f"exe 路径: {exe_path}")
        print(f"文件大小: {size_mb:.1f} MB")
        print(f"\n📌 使用说明:")
        print(f"  1. 将 exe 复制到任意 Windows 电脑")
        print(f"  2. 确保已安装 Pandoc: https://pandoc.org/installing.html")
        print(f"  3. 双击运行即可")
    else:
        print("❌ 未找到 exe 文件")


if __name__ == "__main__":
    step1_install_deps()
    step2_build()
