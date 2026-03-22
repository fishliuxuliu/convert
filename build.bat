@echo off
chcp 65001 >nul
echo ========================================
echo   DocMarkdownConverter 一键打包工具
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    echo   下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装依赖
echo [1/3] 安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败，请尝试手动运行:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)
echo   OK

:: 安装 Pandoc 检查
where pandoc >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到 Pandoc，PDF 和 .doc 转换功能将受限
    echo   推荐安装: https://pandoc.org/installing.html
    echo.
)

:: PyInstaller 打包
echo [2/3] 打包中（首次运行约需 1-3 分钟）...
pyinstaller build.spec --clean --noconfirm
if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)
echo   OK

:: 完成
echo [3/3] 完成！
echo.
echo ========================================
echo   打包成功!
echo ========================================
echo.
echo exe 目录: dist\DocMarkdownConverter\
echo.
echo 找到 DocMarkdownConverter.exe 双击运行即可
echo.
echo [提示] 首次使用请安装 Pandoc:
echo   https://pandoc.org/installing.html
echo.
pause
