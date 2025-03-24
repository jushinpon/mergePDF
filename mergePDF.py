import os
import sys
import subprocess
from pypdf import PdfReader, PdfWriter
import shutil
import glob

# 設定檔案大小限制（MB）
MAX_PDF_SIZE_MB = 100
MAX_BATCH_SIZE_MB = 95

# 判斷腳本目錄
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
else:
    script_dir = os.getcwd()

# 刪除舊的 merged_*.pdf 檔案
for file in glob.glob(os.path.join(script_dir, 'merged_*.pdf')):
    try:
        os.remove(file)
    except OSError as e:
        print(f"Error deleting {file}: {e}")

# 初始化 log 檔案
log_file_path = os.path.join(script_dir, 'merge_log.txt')
with open(log_file_path, 'a', encoding='utf-8') as log_file:
    log_file.write(f"\n--- New Run: {os.path.basename(sys.argv[0])} ---\n")

merged_counter = 1  # 用來命名 merged_01.pdf...

def compress_pdf(input_path, output_path):
    """
    使用 Ghostscript 壓縮 PDF（Windows 版本）
    """
    subprocess.run([
        'gswin64c',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/screen',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_path}',
        input_path
    ], check=True)

def safe_compress_pdf(input_path):
    """
    嘗試壓縮 PDF，如失敗則回傳原始檔案
    """
    compressed_path = input_path.replace('.pdf', '_compressed.pdf')
    try:
        compress_pdf(input_path, compressed_path)
        return compressed_path
    except Exception as e:
        print(f"⚠️ Failed to compress {input_path}: {e}")
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"Compression failed: {input_path} - {e}\n")
        return input_path

def merge_pdfs(pdf_list, output_path):
    """
    使用 PdfWriter 合併 PDF
    """
    writer = PdfWriter()
    added = False
    for pdf in pdf_list:
        try:
            reader = PdfReader(pdf)
            for page in reader.pages:
                writer.add_page(page)
            added = True
        except Exception as e:
            print(f"⚠️ Skipping {pdf}: {e}")
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f"Skip error in merge: {pdf} - {e}\n")
    if added:
        with open(output_path, 'wb') as f:
            writer.write(f)
        return True
    else:
        return False

# 設定搜尋根目錄
root_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

# 掃描資料夾
for root, dirs, files in os.walk(root_dir):
    pdf_files = [os.path.join(root, f) for f in files if f.endswith('.pdf') and not f.startswith('batch_')]
    if not pdf_files:
        continue

    # 刪除舊 batch 檔案
    for file in glob.glob(os.path.join(root, 'batch_*.pdf')):
        try:
            os.remove(file)
        except OSError as e:
            print(f"Error deleting {file}: {e}")

    batch_num = 1
    small_pdfs = []

    for pdf in pdf_files:
        size = os.path.getsize(pdf) / (1024 * 1024)
        if size > MAX_PDF_SIZE_MB:
            compressed_pdf = safe_compress_pdf(pdf)
            compressed_size = os.path.getsize(compressed_pdf) / (1024 * 1024)
            if compressed_size > MAX_PDF_SIZE_MB:
                print(f"⚠️ Still large: {compressed_pdf} is {compressed_size:.2f} MB.")
            output_path = os.path.join(root, f'batch_{batch_num:02d}.pdf')
            shutil.copy(compressed_pdf, output_path)
            batch_num += 1
        else:
            small_pdfs.append(pdf)

    current_batch = []
    current_sum = 0
    for pdf in small_pdfs:
        size = os.path.getsize(pdf) / (1024 * 1024)
        if current_sum + size < MAX_BATCH_SIZE_MB:
            current_batch.append(pdf)
            current_sum += size
        else:
            if current_batch:
                output_path = os.path.join(root, f'batch_{batch_num:02d}.pdf')
                if merge_pdfs(current_batch, output_path):
                    with open(log_file_path, 'a', encoding='utf-8') as log_file:
                        log_file.write(f"Merged PDF: {os.path.basename(output_path)}\n")
                        log_file.write("Contains:\n")
                        for p in current_batch:
                            log_file.write(f"  - {os.path.basename(p)}\n")
                        log_file.write("\n")
                    new_name = f"merged_{merged_counter:02d}.pdf"
                    shutil.copy(output_path, os.path.join(script_dir, new_name))
                    merged_counter += 1
                batch_num += 1
            current_batch = [pdf]
            current_sum = size

    if current_batch:
        output_path = os.path.join(root, f'batch_{batch_num:02d}.pdf')
        if merge_pdfs(current_batch, output_path):
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f"Merged PDF: {os.path.basename(output_path)}\n")
                log_file.write("Contains:\n")
                for p in current_batch:
                    log_file.write(f"  - {os.path.basename(p)}\n")
                log_file.write("\n")
            new_name = f"merged_{merged_counter:02d}.pdf"
            shutil.copy(output_path, os.path.join(script_dir, new_name))
            merged_counter += 1
