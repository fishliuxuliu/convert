---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502201ae66465eab71f3a4c44b6d56edf1964fa3b277ba580becfd3d1826b9b07ef92022100980cbeaff4453ced0cb9096b3f5b66c988c740c728d136c60f6f13b2bd6d6b3e
    ReservedCode2: 30450220206fa9d3ffaf797e0faafb6dcadb2ae537a61fe2cc0027ba8a91e99fd9bd22b5022100c7a3795d1ab14fb88dcf99a53fbb15dea63f157d82448160ce6cecc44c976726
---

# DocMarkdown 批量转换工具

> 支持 docx / doc / pdf / md / txt 互转的 Windows 桌面程序

---

## 一键构建（在 Windows 上运行）

### 方法 A：自动构建（推荐）
```
双击运行 build.bat
```
构建完成后 exe 在 `dist\DocMarkdownConverter\DocMarkdownConverter.exe`

### 方法 B：手动构建
```cmd
# 1. 安装依赖
pip install -r requirements.txt

# 2. 打包
pyinstaller build.spec --clean --noconfirm

# 3. 找到 exe
# dist\DocMarkdownConverter\DocMarkdownConverter.exe
```

---

## 使用说明

1. **安装 Pandoc**（必须，否则 doc/pdf 功能受限）
   下载地址：https://pandoc.org/installing.html
   安装后确保 `pandoc --version` 能运行

2. **运行程序**
   双击 `DocMarkdownConverter.exe`

3. **添加文件**
   - 点击「添加文件」选择单个或多个文件
   - 点击「添加文件夹」批量导入整个文件夹
   - 也可以直接拖拽文件/文件夹到窗口

4. **选择格式**
   下拉选择目标格式（md / docx / pdf / txt）

5. **开始转换**
   点击「开始转换」，完成后会弹出提示
   文件自动保存在源文件所在目录，重名自动编号

---

## 格式支持

| 输入格式 | 输出支持 |
|---------|---------|
| docx    | md txt pdf docx |
| doc     | md txt pdf docx（需 Pandoc）|
| pdf     | md txt |
| md      | docx pdf txt |
| txt     | docx pdf md |

---

## 技术栈

- GUI：PyQt6
- Word 读取：python-docx
- PDF 读取：pdfplumber
- 格式转换：Pandoc
- 打包：PyInstaller
