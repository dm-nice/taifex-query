"""
快速試驗版 - 資料整合程式
用途: 將 data 目錄下的所有 txt 檔案內容整合到 Total_data.txt
試驗版特點: 快速、簡單、驗證可行性
"""

import io
import sys
from pathlib import Path

# 設定 UTF-8 輸出
if sys.platform == 'win32' and not getattr(sys, "frozen", False):
    if not hasattr(sys.stdout, '_wrapped_for_utf8') and hasattr(sys.stdout, 'buffer'):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stdout._wrapped_for_utf8 = True
        except (AttributeError, ValueError):
            pass


def merge_data_files():
    """
    整合 data 目錄下的所有 .txt 檔案

    功能:
    1. 讀取 data 目錄下所有 .txt 檔案
    2. 按檔名排序（確保順序一致）
    3. 整合到 Total_data.txt
    """
    try:
        # 定義路徑 (使用相對路徑，從專案根目錄計算)
        project_root = Path(__file__).parent.parent.parent  # dev/data_merger_test -> dev -> Taifex
        data_dir = project_root / "data"
        output_file = project_root / "dev" / "data_merger_test" / "Total_data.txt"

        # 檢查 data 目錄是否存在
        if not data_dir.exists():
            print(f"❌ 錯誤: 找不到目錄 {data_dir}")
            return

        # 取得所有 .txt 檔案並排序
        txt_files = sorted(data_dir.glob("*.txt"))

        if not txt_files:
            print(f"❌ 錯誤: {data_dir} 目錄下沒有 .txt 檔案")
            return

        print(f"📂 找到 {len(txt_files)} 個檔案")

        # 準備輸出內容
        output_lines = []

        # 添加標題區塊
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_lines.append("# 台灣期貨 20 因子預測系統 - 整合資料")
        output_lines.append(f"# 整合時間: {timestamp}")
        output_lines.append(f"# 資料來源: {data_dir}")
        output_lines.append(f"# 檔案數量: {len(txt_files)}")
        output_lines.append("#" + "=" * 70)
        output_lines.append("")  # 空行
        output_lines.append("")  # 第二個空行

        # 讀取並整合每個檔案
        for txt_file in txt_files:
            print(f"  📄 處理: {txt_file.name}")

            try:
                # 讀取檔案內容
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                # 添加資料內容
                output_lines.append(content)

            except Exception as e:
                print(f"  ⚠️  警告: 讀取 {txt_file.name} 失敗: {e}")
                output_lines.append(f"錯誤: 無法讀取檔案 {txt_file.name} - {e}")

        # 寫入輸出檔案
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

        print(f"\n✅ 成功! 整合完成")
        print(f"📊 輸出檔案: {output_file}")
        print(f"📏 總行數: {len(output_lines)}")
        print(f"📦 檔案大小: {output_file.stat().st_size} bytes")

        # 顯示前幾行預覽
        print(f"\n📋 預覽 (前 10 行):")
        print("-" * 70)
        for line in output_lines[:10]:
            print(line)
        print("-" * 70)

        return True

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 70)
    print("  台灣期貨 20 因子預測系統 - 資料整合工具 (試驗版)")
    print("=" * 70)
    print()

    # 執行整合
    result = merge_data_files()

    if result:
        print("\n🎉 試驗版測試成功!")
    else:
        print("\n❌ 試驗版測試失敗，請檢查錯誤訊息")
