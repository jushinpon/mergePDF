This script creates PDF files which merged PDF files under subfolders, and fianlly
move all merged PDF files in the parent folder


一、安裝 Ghostscript (download from https://ghostscript.com/releases/gsdnld.html)
雙擊 gs10050w64.exe 安裝檔

建議安裝路徑為：

C:\Program Files\gs\gs10.05.0\
安裝完後，你會看到類似這個目錄結構：

C:\Program Files\gs\gs10.05.0\bin\gswin64c.exe
✅ 二、設定系統環境變數（讓 Python 找得到 gs）
在 Windows 上搜尋「環境變數」或「Edit the system environment variables」
→ 點「環境變數（Environment Variables）」按鈕

在「系統變數（System variables）」區塊中找到 Path
→ 點【編輯（Edit）】→【新增】以下路徑：

C:\Program Files\gs\gs10.05.0\bin
點「確定」，關閉所有設定視窗。

🔁 重新啟動終端機（例如 cmd、PowerShell、Anaconda Prompt）

✅ 三、驗證 Ghostscript 是否安裝成功
打開命令提示字元（cmd）或 PowerShell，輸入：


gswin64c -v

GPL Ghostscript 10.05.0 (2024-xx-xx)
Copyright (C) 2024 Artifex Software, Inc. All rights reserved.