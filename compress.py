import os
import subprocess
import shutil
import stat

# ✅ Ghostscript 路徑（請確認此路徑正確）
GS_PATH = r"C:\Program Files\gs\gs10.05.0\bin\gswin64c.exe"

# ✅ 強制刪除唯讀檔案
def force_remove_readonly(func, path, _):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"❌ 無法刪除：{path} → {e}")

# ✅ 指定目錄
script_dir = os.path.dirname(os.path.abspath(__file__))
compressed_root = os.path.join(script_dir, "compressed")

# ✅ 清空 compressed 資料夾
if os.path.exists(compressed_root):
    shutil.rmtree(compressed_root, onerror=force_remove_readonly)
    print(f"🗑️ 已強制刪除舊 compressed 資料夾")
os.makedirs(compressed_root, exist_ok=True)
print(f"📁 建立新的 compressed 資料夾：{compressed_root}")

# ✅ 掃描所有非 compressed/ 中的 PDF
pdf_files = []
for root, _, files in os.walk(script_dir):
    for f in files:
        if f.lower().endswith(".pdf") and "_compressed" not in f:
            full_path = os.path.join(root, f)
            if os.path.commonpath([full_path, compressed_root]) != compressed_root:
                pdf_files.append(full_path)

if not pdf_files:
    print("⚠️ 沒有找到任何 .pdf 檔案。請確保 PDF 檔案位於主程式的子資料夾中。")
    exit()

# ✅ 開始壓縮 PDF
for input_path in pdf_files:
    relative_path = os.path.relpath(input_path, script_dir)
    relative_dir = os.path.dirname(relative_path)
    filename = os.path.basename(input_path)
    output_dir = os.path.join(compressed_root, relative_dir)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename.replace(".pdf", "_compressed.pdf"))

    print(f"🗜️ 壓縮中：{relative_path} ...")

    try:
        result = subprocess.run([
            GS_PATH,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/screen",
            "-dNOPAUSE",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ], capture_output=True, text=True, encoding='utf-8', errors='replace')  # 🔧 加入錯誤容忍

        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            original_size = os.path.getsize(input_path) / (1024 * 1024)
            compressed_size = os.path.getsize(output_path) / (1024 * 1024)
            ratio = compressed_size / original_size if original_size else 0
            print(f"✅ 壓縮成功：{relative_path}（{original_size:.2f}MB → {compressed_size:.2f}MB，壓縮率 {ratio:.2%}）")
        else:
            print(f"❌ 壓縮失敗：{relative_path}")
            print("📄 Ghostscript 錯誤訊息：")
            if result.stderr:
                print(result.stderr)
            if os.path.exists(output_path):
                os.remove(output_path)

    except Exception as e:
        print(f"❌ 執行 Ghostscript 發生例外：{relative_path}\n{e}")
        if os.path.exists(output_path):
            os.remove(output_path)
