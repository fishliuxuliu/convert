---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502206f75d9332fdf8745c9185edbf89072343434de2ea3920c8af61f7caa671f090c022100aa1d31c396befc413dafe6b431546bbfe88e83e1e5e0eb4ed0b8b90ac1fbd368
    ReservedCode2: 3044022015cc2934699b8d3fe10457ea5d480fd2c09e3ab14c9f70e2796035a41cd4e51d022055d24fc5181f625d770ddb661ac64adc209766968c4e934adef5f82ae64cb0da
---

# DocMarkdownConverter - 批量文件转换工具

## 项目概述
- **功能**: 批量将 doc/docx/pdf/markdown 文件互相转换
- **技术栈**: Python 3 + PyQt6 + pandoc
- **输出**: 单文件 exe，可独立运行

## 功能列表
1. ✅ 选中单个或多个文件（支持 doc/docx/pdf/md/txt）
2. ✅ 选择目标转换格式（md / docx / pdf / txt）
3. ✅ 一键批量转换
4. ✅ 自动保存到原文件目录
5. ✅ 重名自动编号（file_1.md, file_2.md...）
6. ✅ 显示转换进度条
7. ✅ 转换完成后弹出提示

## 界面配色
- 主色: #4A90D9 (蓝色)
- 背景: #F5F7FA (浅灰白)
- 按钮: #4A90D9 圆角
- 文字: #333333

## 依赖
- PyQt6
- python-docx
- pdfplumber
- pandoc (系统安装，代码调用)
- PyInstaller

## 文件结构
- main.py - 入口
- converter.py - 转换逻辑
- ui.py - 界面
- build.spec - 打包配置
