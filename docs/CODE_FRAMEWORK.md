# 代碼框架設計文檔

## 1. Entry Point Scripts

### 1.1 daytime_query.py (F01-F20, 21:00)

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TAIFEX 爬蟲系統 - 一般交易時段入口 (21:00 執行)
查詢 F01-F20 資料並輸出為 .md 檔案

執行時間: 每週一至週五 21:00
輸出路徑: output/taifex_YYYY.MM.DD_v{version}.md
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from config.settings import TIMEZONE, OUTPUT_DIR
from scrapers.daytime import query_daytime_data
from utils.helpers import save_to_markdown, get_next_version
from utils.date_utils import get_current_taiwan_date

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """主程式進入點"""
    logger.info("=" * 60)
    logger.info("🕘 一般交易時段資料查詢 (21:00 執行)")
    logger.info("=" * 60)

    try:
        # 取得當前台灣日期
        current_date = get_current_taiwan_date()
        logger.info(f"查詢日期: {current_date}")

        # 查詢 F01-F20 資料
        logger.info("開始查詢 F01-F20 資料...")
        data = query_daytime_data()

        if not data:
            logger.error("❌ 無法獲取任何資料，程式終止")
            return

        logger.info(f"✅ 成功取得 {len(data)} 條資料")

        # 決定檔案版號
        version = get_next_version(market_type='daytime', date=current_date)
        logger.info(f"檔案版本號: v{version}")

        # 保存為 .md 檔案
        output_path = save_to_markdown(
            data=data,
            date=current_date,
            version=version,
            market_type='daytime'
        )

        logger.info(f"✅ 資料已保存: {output_path}")
        logger.info("=" * 60)
        logger.info("🕘 一般交易時段查詢完成")
        logger.info("=" * 60)

    except Exception as e:
        logger.exception(f"❌ 程式執行出錯: {e}")
        raise


if __name__ == "__main__":
    main()
```

### 1.2 nighttime_query.py (F21-F25, 隔日 05:10)

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TAIFEX 爬蟲系統 - 盤後交易時段入口 (隔日 05:10 執行)
查詢 F21-F25 資料並輸出為 .md 檔案

執行時間: 每週二至週六 05:10 (隔日)
輸出路徑: output/taifex_YYYY.MM.DD_v{version}.md
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from config.settings import TIMEZONE, OUTPUT_DIR
from scrapers.nighttime import query_nighttime_data
from utils.helpers import save_to_markdown, get_next_version
from utils.date_utils import get_current_taiwan_date

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """主程式進入點"""
    logger.info("=" * 60)
    logger.info("🌙 盤後交易時段資料查詢 (05:10 執行)")
    logger.info("=" * 60)

    try:
        # 取得隔日台灣日期 (美股收盤後)
        current_date = get_current_taiwan_date()
        logger.info(f"查詢日期: {current_date}")

        # 查詢 F21-F25 資料
        logger.info("開始查詢 F21-F25 資料...")
        data = query_nighttime_data()

        if not data:
            logger.error("❌ 無法獲取任何資料，程式終止")
            return

        logger.info(f"✅ 成功取得 {len(data)} 條資料")

        # 決定檔案版號
        version = get_next_version(market_type='nighttime', date=current_date)
        logger.info(f"檔案版本號: v{version}")

        # 保存為 .md 檔案
        output_path = save_to_markdown(
            data=data,
            date=current_date,
            version=version,
            market_type='nighttime'
        )

        logger.info(f"✅ 資料已保存: {output_path}")
        logger.info("=" * 60)
        logger.info("🌙 盤後交易時段查詢完成")
        logger.info("=" * 60)

    except Exception as e:
        logger.exception(f"❌ 程式執行出錯: {e}")
        raise


if __name__ == "__main__":
    main()
```

---

## 2. 爬蟲模組

### 2.1 scrapers/daytime.py (F01-F20)

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一般交易時段爬蟲 (F01-F20)
查詢台灣期貨交易所、台股及其他資料來源

包含:
- F01-F03: 台指期貨外資持倉
- F04: 台指期貨收盤
- F05-F07: 台指選擇權相關
- F11-F17: 股票市場相關
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, validator

from config.field_mapping import FIELD_MAPPING
from config.settings import MAX_RETRIES, TIMEOUT
from utils.date_utils import is_trading_day, get_previous_trading_day

logger = logging.getLogger(__name__)


class DaytimeData(BaseModel):
    """一般交易時段資料模型"""
    f_code: str  # F01-F20
    name: str
    field: str
    value: str
    unit: Optional[str] = ""
    date: str  # YYYY.MM.DD

    class Config:
        frozen = True


def query_daytime_data(
    date: Optional[str] = None,
    auto_fallback: bool = True
) -> List[DaytimeData]:
    """
    查詢一般交易時段資料 (F01-F20)

    Args:
        date: 查詢日期 (YYYY.MM.DD format), 預設為當日
        auto_fallback: 當日無資料是否自動查前一交易日

    Returns:
        DaytimeData 列表
    """
    logger.info(f"開始查詢一般交易時段資料 (date={date})")

    results: List[DaytimeData] = []

    # F01-F03: 台指期貨外資持倉
    logger.info("查詢 F01-F03 (台指期貨外資)...")
    f01_f03 = _query_taifex_foreign_holdings(date, auto_fallback)
    results.extend(f01_f03)

    # F04: 台指期貨收盤
    logger.info("查詢 F04 (台指期貨收盤)...")
    f04 = _query_taifex_settlement(date, auto_fallback)
    if f04:
        results.append(f04)

    # F05-F07: 台指選擇權相關
    logger.info("查詢 F05-F07 (台指選擇權)...")
    f05_f07 = _query_taifex_options(date, auto_fallback)
    results.extend(f05_f07)

    # F08-F10: 保留項目
    for f_code in ['F08', 'F09', 'F10']:
        results.append(DaytimeData(
            f_code=f_code,
            name="[保留項目]",
            field="",
            value="[ 保留項目 ]",
            date=date or _get_current_date()
        ))

    # F11-F17: 股票市場相關
    logger.info("查詢 F11-F17 (股票市場)...")
    f11_f17 = _query_stock_market_data(date, auto_fallback)
    results.extend(f11_f17)

    # F18-F20: 保留項目
    for f_code in ['F18', 'F19', 'F20']:
        results.append(DaytimeData(
            f_code=f_code,
            name="[保留項目]",
            field="",
            value="[ 保留項目 ]",
            date=date or _get_current_date()
        ))

    logger.info(f"✅ 成功查詢 {len(results)} 條資料")
    return results


def _query_taifex_foreign_holdings(
    date: Optional[str],
    auto_fallback: bool
) -> List[DaytimeData]:
    """查詢 F01-F03: 台指期貨外資持倉"""
    # 實作爬蟲邏輯
    pass


def _query_taifex_settlement(
    date: Optional[str],
    auto_fallback: bool
) -> Optional[DaytimeData]:
    """查詢 F04: 台指期貨收盤"""
    # 實作爬蟲邏輯
    pass


def _query_taifex_options(
    date: Optional[str],
    auto_fallback: bool
) -> List[DaytimeData]:
    """查詢 F05-F07: 台指選擇權相關"""
    # 實作爬蟲邏輯
    pass


def _query_stock_market_data(
    date: Optional[str],
    auto_fallback: bool
) -> List[DaytimeData]:
    """查詢 F11-F17: 股票市場相關 (台股、台積電、外資)"""
    # 實作爬蟲邏輯
    pass


def _get_current_date() -> str:
    """取得當前日期 (YYYY.MM.DD)"""
    from utils.date_utils import get_current_taiwan_date
    return get_current_taiwan_date()
```

### 2.2 scrapers/nighttime.py (F21-F25)

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盤後交易時段爬蟲 (F21-F25)
查詢美股及期貨盤後資料

包含:
- F21: NASDAQ指數
- F22: 費城半導體指數
- F23: EM-ND期指數
- F24: 台積電ADR
- F25: 台指期盤後
"""

import logging
from typing import List, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, validator

from config.field_mapping import FIELD_MAPPING
from config.settings import MAX_RETRIES, TIMEOUT
from utils.date_utils import is_trading_day, get_previous_trading_day

logger = logging.getLogger(__name__)


class NighttimeData(BaseModel):
    """盤後交易時段資料模型"""
    f_code: str  # F21-F25
    name: str
    field: str
    value: str  # 格式: +301.26 或 -45.89
    date: str  # YYYY.MM.DD (隔日)

    @validator('value')
    def validate_value(cls, v):
        """驗證值格式 (必須包含符號)"""
        if not v.startswith(('+', '-')):
            raise ValueError(f"盤後資料必須包含符號: {v}")
        return v

    class Config:
        frozen = True


def query_nighttime_data(
    date: Optional[str] = None,
    auto_fallback: bool = True
) -> List[NighttimeData]:
    """
    查詢盤後交易時段資料 (F21-F25)

    Args:
        date: 查詢日期 (YYYY.MM.DD format), 預設為當日
        auto_fallback: 當日無資料是否自動查前一交易日

    Returns:
        NighttimeData 列表
    """
    logger.info(f"開始查詢盤後交易時段資料 (date={date})")

    results: List[NighttimeData] = []

    # 從 Wantgoo 查詢所有 F21-F25 資料
    logger.info("查詢 F21-F25 (美股及期盤後)...")
    f21_f25 = _query_wantgoo_global_data(date, auto_fallback)
    results.extend(f21_f25)

    logger.info(f"✅ 成功查詢 {len(results)} 條資料")
    return results


def _query_wantgoo_global_data(
    date: Optional[str],
    auto_fallback: bool
) -> List[NighttimeData]:
    """
    從 Wantgoo 查詢全球股指資料 (F21-F25)

    預期爬蟲結果:
    - F21: NASDAQ (+/- value)
    - F22: 費城半導體 (+/- value)
    - F23: EM-ND期指數 (+/- value)
    - F24: 台積電ADR (+/- value)
    - F25: 台指期盤後 (+/- value)
    """
    url = "https://www.wantgoo.com/global"

    try:
        logger.info(f"爬蟲 URL: {url}")

        # 發送請求
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()

        # 解析 HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # 實作爬蟲邏輯並返回結果
        # ...

    except Exception as e:
        logger.error(f"查詢失敗: {e}")
        if auto_fallback:
            logger.info("嘗試查詢前一交易日...")
            # 遞迴呼叫前一交易日
            pass
        else:
            raise
```

---

## 3. 工具函式

### 3.1 utils/helpers.py

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通用工具函式

包含:
- save_to_markdown(): 保存資料到 .md 檔案
- get_next_version(): 取得下一個版本號
- format_value(): 格式化數值
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from config.settings import OUTPUT_DIR, FILENAME_FORMAT, TIMEZONE

logger = logging.getLogger(__name__)


def save_to_markdown(
    data: List[Dict[str, Any]],
    date: str,
    version: int,
    market_type: str = 'daytime'
) -> str:
    """
    保存資料到 Markdown 檔案

    Args:
        data: 資料列表 (字典或 Pydantic Model)
        date: 日期 (YYYY.MM.DD format)
        version: 版本號 (1, 2, 3...)
        market_type: 市場類型 ('daytime' 或 'nighttime')

    Returns:
        輸出檔案路徑

    格式範例:
        2026.01.15 F01 台指期貨-外資 [ 未平倉 多空淨額: -181389口 ]
        2026.01.15 F02 台指期貨-外資 [ 未平倉 多方: 185467口 ]
    """
    # 確保輸出目錄存在
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    # 組合檔案名稱
    filename = FILENAME_FORMAT.format(date=date, version=version)
    filepath = output_path / filename

    logger.info(f"準備保存到檔案: {filepath}")

    try:
        # 開啟檔案 (追加模式)
        with open(filepath, 'a', encoding='utf-8') as f:
            for item in data:
                # 轉換 Pydantic Model 為字典
                if hasattr(item, 'dict'):
                    item_dict = item.dict()
                else:
                    item_dict = item

                # 組合輸出行
                line = _format_data_line(item_dict)
                f.write(line + '\n')

        logger.info(f"✅ 資料已保存: {filepath}")
        return str(filepath)

    except Exception as e:
        logger.error(f"❌ 保存檔案失敗: {e}")
        raise


def get_next_version(
    market_type: str = 'daytime',
    date: Optional[str] = None
) -> int:
    """
    取得下一個版本號

    查詢 output/ 目錄，找出當日最高版本號，返回 +1

    Args:
        market_type: 市場類型 ('daytime' 或 'nighttime')
        date: 日期 (YYYY.MM.DD format)，預設為當日

    Returns:
        下一個版本號 (1, 2, 3...)

    範例:
        taifex_2026.01.15_v1.md  -> 返回 2
        taifex_2026.01.15_v2.md  -> 返回 3
        (無檔案) -> 返回 1
    """
    if date is None:
        from utils.date_utils import get_current_taiwan_date
        date = get_current_taiwan_date()

    output_path = Path(OUTPUT_DIR)

    if not output_path.exists():
        return 1

    # 查詢所有符合日期的檔案
    pattern = f"taifex_{date}_v*.md"
    matching_files = list(output_path.glob(pattern))

    if not matching_files:
        logger.info(f"未找到日期 {date} 的檔案，版本從 v1 開始")
        return 1

    # 提取版本號並排序
    versions = []
    for file in matching_files:
        # 格式: taifex_YYYY.MM.DD_v{version}.md
        try:
            version_str = file.stem.split('_v')[-1]
            version_num = int(version_str)
            versions.append(version_num)
        except (ValueError, IndexError):
            logger.warning(f"無法解析版本號: {file}")
            continue

    if not versions:
        return 1

    next_version = max(versions) + 1
    logger.info(f"下一個版本號: v{next_version}")
    return next_version


def _format_data_line(item: Dict[str, Any]) -> str:
    """
    格式化單行資料

    格式:
        2026.01.15 F01 台指期貨-外資 [ 未平倉 多空淨額: -181389口 ]
    """
    date = item.get('date', '')
    f_code = item.get('f_code', '')
    name = item.get('name', '')
    field = item.get('field', '')
    value = item.get('value', '')
    unit = item.get('unit', '')

    # 處理保留項目和查詢失敗
    if value.startswith('['):
        # 已經格式化的特殊值
        return f"{date} {f_code} {name} {value}"

    # 一般格式
    if unit:
        formatted_value = f"{value}{unit}"
    else:
        formatted_value = value

    return f"{date} {f_code} {name} [ {field}: {formatted_value} ]"


def format_value(
    value: Any,
    unit: Optional[str] = None,
    decimal_places: int = 2
) -> str:
    """
    格式化數值

    Args:
        value: 原始值
        unit: 單位
        decimal_places: 小數位數

    Returns:
        格式化後的字符串
    """
    if isinstance(value, (int, float)):
        # 添加千位分隔符
        if decimal_places > 0:
            formatted = f"{float(value):,.{decimal_places}f}"
        else:
            formatted = f"{int(value):,}"
    else:
        formatted = str(value)

    if unit:
        return f"{formatted}{unit}"
    else:
        return formatted
```

### 3.2 utils/date_utils.py

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日期工具函式

包含:
- get_current_taiwan_date(): 取得當前台灣日期
- is_trading_day(): 判斷是否交易日
- get_previous_trading_day(): 取得前一交易日
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import pytz

from config.settings import TIMEZONE

logger = logging.getLogger(__name__)

# 台灣股市休市日期 (2026)
# 需要動態取得或使用外部 API
HOLIDAYS_2026 = {
    '2026-01-01',  # 元旦
    '2026-01-28', '2026-01-29', '2026-01-30',  # 農曆年
    # ... 更多日期
}


def get_current_taiwan_date(format: str = '%Y.%m.%d') -> str:
    """
    取得當前台灣日期

    Args:
        format: 日期格式 (預設: YYYY.MM.DD)

    Returns:
        台灣日期字符串
    """
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    return now.strftime(format)


def is_trading_day(date: Optional[str] = None) -> bool:
    """
    判斷是否台灣股市交易日

    Args:
        date: 日期 (YYYY.MM.DD 或 YYYY-MM-DD format)

    Returns:
        True 如果是交易日，False 如果是假日
    """
    if date is None:
        date = get_current_taiwan_date()

    # 轉換格式
    date_obj = datetime.strptime(date, '%Y.%m.%d')

    # 檢查是否週末
    if date_obj.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False

    # 檢查是否假日
    date_str = date_obj.strftime('%Y-%m-%d')
    if date_str in HOLIDAYS_2026:
        return False

    return True


def get_previous_trading_day(date: Optional[str] = None) -> str:
    """
    取得前一個交易日

    Args:
        date: 起始日期 (YYYY.MM.DD format)

    Returns:
        前一個交易日
    """
    if date is None:
        date = get_current_taiwan_date()

    date_obj = datetime.strptime(date, '%Y.%m.%d')

    # 向前查詢直到找到交易日
    current = date_obj - timedelta(days=1)
    while not is_trading_day(current.strftime('%Y.%m.%d')):
        current -= timedelta(days=1)

    return current.strftime('%Y.%m.%d')
```

### 3.3 utils/validators.py

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
資料驗證工具

包含:
- validate_date(): 驗證日期格式
- validate_numeric(): 驗證數值
- validate_signed_number(): 驗證帶符號的數值
"""

import logging
import re
from typing import Optional, Union

logger = logging.getLogger(__name__)


def validate_date(date_str: str, format: str = '%Y.%m.%d') -> bool:
    """驗證日期格式"""
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        logger.warning(f"無效的日期格式: {date_str}")
        return False


def validate_numeric(value: str) -> bool:
    """驗證數值 (支援千位分隔符)"""
    pattern = r'^-?\d{1,3}(,\d{3})*(\.\d+)?$|^\d+(\.\d+)?$'
    return bool(re.match(pattern, str(value)))


def validate_signed_number(value: str) -> bool:
    """驗證帶符號的數值 (F21-F25 格式)"""
    pattern = r'^[+\-]\d+(\.\d+)?$'
    return bool(re.match(pattern, str(value)))
```

---

## 4. 配置文件

### 4.1 config/settings.py

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全域設定檔
"""

import os
from pathlib import Path

# 項目根目錄
PROJECT_ROOT = Path(__file__).parent.parent

# 輸出目錄
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 檔案名稱格式
FILENAME_FORMAT = "taifex_{date}_v{version}.md"

# 時區
TIMEZONE = "Asia/Taipei"

# 重試次數
MAX_RETRIES = 3

# 超時設定 (秒)
TIMEOUT = 10

# HTTP Headers (避免被阻止)
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 日誌設定
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

### 4.2 config/field_mapping.py

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
F01-F25 完整欄位對應表
定義每個 F 值的：URL、資料名稱、抓取欄位
"""

FIELD_MAPPING = {
    # F01-F03: 台指期貨外資持倉
    'F01': {
        'url': 'https://www.taifex.com.tw/cht/3/totalTableDate',
        'name': '台指期貨-外資',
        'field': '未平倉 多空淨額',
        'unit': '口',
        'category': 'daytime'
    },
    'F02': {
        'url': 'https://www.taifex.com.tw/cht/3/totalTableDate',
        'name': '台指期貨-外資',
        'field': '未平倉 多方',
        'unit': '口',
        'category': 'daytime'
    },
    'F03': {
        'url': 'https://www.taifex.com.tw/cht/3/totalTableDate',
        'name': '台指期貨-外資',
        'field': '未平倉 空方',
        'unit': '口',
        'category': 'daytime'
    },

    # F04: 台指期貨收盤
    'F04': {
        'url': 'https://www.taifex.com.tw/cht/3/futDailyMarketReport',
        'name': '台指期貨-當日收盤',
        'field': '最後成交價',
        'unit': '',
        'category': 'daytime'
    },

    # F05: 台指選擇權成交
    'F05': {
        'url': 'https://www.taifex.com.tw/cht/3/optDailyMarketReport',
        'name': '台指選擇權-當日',
        'field': '選擇權總成交量',
        'unit': '',
        'category': 'daytime'
    },

    # ... 以此類推 F06-F07, F11-F17, F21-F25

    # 保留項目
    'F08': {'category': 'daytime', 'status': 'reserved'},
    'F09': {'category': 'daytime', 'status': 'reserved'},
    'F10': {'category': 'daytime', 'status': 'reserved'},
    'F18': {'category': 'daytime', 'status': 'reserved'},
    'F19': {'category': 'daytime', 'status': 'reserved'},
    'F20': {'category': 'daytime', 'status': 'reserved'},
}
```

---

## 5. 類型定義與數據模型

### 5.1 數據模型層次

```python
# Entry Point
├── daytime_query.py / nighttime_query.py
│   └── scrapers.daytime / scrapers.nighttime
│       └── 返回 List[DaytimeData] / List[NighttimeData]
│           └── utils.helpers.save_to_markdown()
│               └── 輸出檔案
```

### 5.2 Pydantic 模型

```python
from pydantic import BaseModel, validator
from typing import Optional

class DaytimeData(BaseModel):
    """一般交易時段資料"""
    f_code: str       # F01-F20
    name: str         # 資料名稱
    field: str        # 欄位名稱
    value: str        # 資料值
    unit: Optional[str]  # 單位
    date: str         # YYYY.MM.DD

    class Config:
        frozen = True  # 不可變


class NighttimeData(BaseModel):
    """盤後交易時段資料"""
    f_code: str       # F21-F25
    name: str         # 資料名稱
    field: str        # 欄位名稱
    value: str        # 資料值 (+/- 格式)
    date: str         # YYYY.MM.DD

    @validator('value')
    def validate_value(cls, v):
        if not v.startswith(('+', '-')) and not v.startswith('['):
            raise ValueError(f"值必須以 +/- 開始: {v}")
        return v

    class Config:
        frozen = True
```

---

## 6. 開發流程

### Phase 1: 基礎爬蟲實現
1. 實現 `_query_taifex_foreign_holdings()` (F01-F03)
2. 實現 `_query_taifex_settlement()` (F04)
3. 實現 `_query_taifex_options()` (F05-F07)
4. 實現 `_query_wantgoo_global_data()` (F21-F25)

### Phase 2: 股票資料爬蟲
1. 實現 `_query_stock_market_data()` (F11-F17)
2. 集成 TWSE API 或爬蟲

### Phase 3: 錯誤處理
1. 實現自動降級邏輯
2. 實現 "查詢失敗" 標記

### Phase 4: 本地測試
1. 測試單個爬蟲函式
2. 測試完整流程
3. 驗證輸出格式

### Phase 5: GitHub Actions 部署
1. 建立 `.github/workflows/` 目錄
2. 上傳 daytime-schedule.yml
3. 上傳 nighttime-schedule.yml
4. 驗證排程執行

