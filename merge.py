import os
import shutil
import stat
import glob
from pypdf import PdfReader, PdfWriter

MAX_BATCH_SIZE_MB = 100

script_dir = os.path.dirname(os.path.abspath(__file__))
compressed_root = os.path.join(script_dir, "compressed")
merged_dir = os.path.join(script_dir, "merged")

# ✅ 強制刪除唯讀檔案
def force_remove_readonly(func, path, _):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"❌ 無法刪除：{path} → {e}")

# ✅ 重建 merged 資料夾
if os.path.exists(merged_dir):
    shutil.rmtree(merged_dir, onerror=force_remove_readonly)
    print("🗑️ 已清除舊 merged 資料夾")
os.makedirs(merged_dir, exist_ok=True)
print("📁 已建立新的 merged 資料夾")

# ✅ 合併 PDF 用
def merge_pdfs(pdf_list, output_path):
    writer = PdfWriter()
    added = False
    for pdf in pdf_list:
        try:
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)
            added = True
        except Exception as e:
            print(f"⚠️ 無法讀取：{pdf} → {e}")
    if added:
        with open(output_path, 'wb') as f:
            writer.write(f)
        return True
    return False

# ✅ 記錄所有 batch 檔案路徑
all_batch_paths = []

# ✅ 掃描每個 compressed 子資料夾
for root, dirs, files in os.walk(compressed_root):
    # 先刪除舊的 batch_*.pdf
    for batch_file in glob.glob(os.path.join(root, "batch_*.pdf")):
        try:
            os.remove(batch_file)
            print(f"🗑️ 刪除舊檔案：{batch_file}")
        except Exception as e:
            print(f"⚠️ 無法刪除 {batch_file}: {e}")

    # 取得待合併 PDF 檔
    pdf_files = [os.path.join(root, f) for f in files if f.lower().endswith(".pdf") and not f.startswith("batch_")]
    if not pdf_files:
        continue

    batch_num = 1
    current_batch = []
    current_sum = 0

    for pdf in pdf_files:
        size = os.path.getsize(pdf) / (1024 * 1024)
        if current_sum + size < MAX_BATCH_SIZE_MB:
            current_batch.append(pdf)
            current_sum += size
        else:
            if current_batch:
                batch_name = f"batch_{batch_num:02d}.pdf"
                batch_path = os.path.join(root, batch_name)
                if merge_pdfs(current_batch, batch_path):
                    all_batch_paths.append(batch_path)
                    print(f"✅ 建立 {batch_path}")
                batch_num += 1
            current_batch = [pdf]
            current_sum = size

    # 最後一批
    if current_batch:
        batch_name = f"batch_{batch_num:02d}.pdf"
        batch_path = os.path.join(root, batch_name)
        if merge_pdfs(current_batch, batch_path):
            all_batch_paths.append(batch_path)
            print(f"✅ 建立 {batch_path}")

# ✅ 複製所有 batch_*.pdf 到 merged/ 並重新命名為 merged_01.pdf ...
merged_counter = 1
merged_paths = []

for batch_path in sorted(all_batch_paths):
    merged_name = f"merged_{merged_counter:02d}.pdf"
    merged_path = os.path.join(merged_dir, merged_name)
    shutil.copy(batch_path, merged_path)
    merged_paths.append(merged_path)
    print(f"📄 複製為 {merged_name}")
    merged_counter += 1

# ✅ 合併為 all.pdf
all_path = os.path.join(merged_dir, "all.pdf")
if merge_pdfs(merged_paths, all_path):
    print(f"📦 所有 merged 檔案已合併為 all.pdf")
else:
    print("⚠️ 沒有成功合併成 all.pdf")
