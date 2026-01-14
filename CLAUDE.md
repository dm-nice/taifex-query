# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Taifex Query System** - A Taiwan futures trading prediction system that automates data collection from multiple sources and generates market analysis. The system fetches data from 25+ factors across early (F01-F17) and night (F21-F25) trading sessions, stores results as timestamped text files, and generates predictive dashboards.

## Common Development Commands

### Running the Main System

```bash
# Run all modules for today's data
python run.py

# Run for a specific date (YYYY-MM-DD format)
python run.py 2025-12-01

# Run only early session modules (F01-F17)
python run.py --session morning

# Run only night session modules (F21-F25)
python run.py --session night

# Run in dev/test mode
python run.py 2025-12-01 dev

# Show help
python run.py --help
```

### Testing

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_modules.py -v

# Run single test function
pytest tests/test_modules.py::test_function_name -v

# Run tests and show print statements
pytest tests/ -v -s

# Run with coverage report
pytest tests/ --cov=modules --cov-report=html
```

### Code Quality

```bash
# Format code with black
black .

# Sort imports with isort
isort .

# Run pre-commit hooks (if configured)
pre-commit run --all-files
```

### Data Management

- Fetched data is stored in `data/` directory with naming pattern: `YYYY-MM-DD_HHMM_f##_fetcher.txt`
- Each file contains the fetch result for a specific factor and timestamp
- View latest data files in `data/` to verify collection success

## Codebase Architecture

### Entry Points

**Primary:** `run.py` - Main orchestrator
- Auto-detects project root directory
- Dynamically discovers and loads all modules in `modules/` directory
- Manages ExecutionContext and ExecutionStats across sessions
- Handles safe console output to prevent I/O errors on Windows
- Creates timestamped data files in `data/` directory

**Secondary Entry Points:**
- `predict.py` - Loads factor data from `data/` directory and generates trading predictions
  - Parses factor files (e.g., `YYYY-MM-DD_HHMM_f##_fetcher.txt`)
  - Extracts numerical values, changes, and percentages from fetcher output
  - Generates predictive signals: 08:45 opening forecast and intraday trend analysis
  - Uses weighted scoring: night session price (90%), institutional positioning (5%), international markets (5%)
  - Returns prediction format: direction (📈/📉), amplitude, confidence level, supporting factors

- `predict_dashboard.py` - Generates market analysis report and updates README.md
  - Reads latest factor data from `data/` directory
  - Parses success/failure status from fetch results
  - Generates market signal indicator (🟢🟡🔴 for bullish/neutral/bearish)
  - Creates markdown tables for: international indicators, institutional positions, technical indicators, data quality
  - Auto-updates README.md with predictions and factor overview

- `main_tools.py` - CLI utility menu for running modules and tools
- `fetch_data.py` - Helper utility for manual data fetching

### Module Organization

All data fetching logic follows a **unified module contract**:

```python
def fetch(date: str) -> str:
    """
    Args: date string in YYYY-MM-DD format
    Returns: Status string

    Success: "YYYY.MM.DD F##: [factor name] [value] [source]"
    Failure: "F## 錯誤: [error message] [source] (timestamp)"
    """
```

**Early Session Modules** (`modules/f01_fetcher.py` through `f17_fetcher.py`):
- F01-F03: Foreign institutional positions (TAIFEX API)
- F04: Taiwan futures closing price (TAIFEX daily report)
- F05-F07: Additional technical factors
- F06, F11: Selenium-based browser automation for website scraping
- F12-F17: Technical indicators and market data

**Night Session Modules** (`modules/f21_fetcher.py` through `f25_fetcher.py`):
- F21-F24: International market indicators (NASDAQ, semiconductors, TSM ADR)
- F25: Taiwan futures after-hours price

### Data Fetcher Characteristics

**Type Safety:** Modules use TypedDict for structured data handling and type hints

**Error Handling:** Each module implements comprehensive try-catch with detailed error messages. Exceptions are always converted to status strings, never raised (fail-safe design)

**Logging:** Dual logging to both console and file with status tracking. Run.py manages centralized logging to prevent I/O conflicts on Windows

**Return Format:** Standardized strings with timestamps:
- Success: `"YYYY.MM.DD F##: [factor name] [value] [source]"`
- Failure: `"F## 錯誤: [error message] [source] (timestamp)"`

**Session Filtering:** Run.py filters module execution based on session type (morning F01-F17, night F21-F25)

**Browser Automation:** Modules F06 (VIX) and F11 (Weighted Index) use Selenium for dynamic website scraping. WebDriver is auto-managed by webdriver-manager

### Key Data Structures

**ExecutionContext** - Dataclass tracking:
- Current execution date
- Current session type (morning/night)
- Loaded modules cache
- Output directory path

**ExecutionStats** - Dataclass aggregating:
- Success/failed/error/invalid module counts
- Success percentage
- Execution start/end times

## Development Workflow

### Data Collection and Reporting Pipeline

1. **Data Collection Phase** (`run.py`):
   - Dynamically discovers and loads all modules from `modules/` directory
   - Executes fetch() function for each module with specified date
   - Saves output to timestamped text file: `data/YYYY-MM-DD_HHMM_f##_fetcher.txt`
   - Tracks execution stats (success/failed/error counts)

2. **Prediction Generation** (`predict.py`):
   - Loads latest factor data from `data/` directory
   - Parses numerical values and trends from fetcher output
   - Applies weighted scoring algorithm for market predictions
   - Generates 08:45 opening forecast and intraday trend analysis

3. **Dashboard Update** (`predict_dashboard.py`):
   - Reads all factor files and extracts latest values
   - Determines status (success/missing/error) for each factor
   - Generates market signal indicator and factor tables
   - Updates README.md with current predictions and factor overview

### Adding a New Data Fetcher

1. Create `modules/f##_fetcher.py` following the module contract
2. Implement `fetch(date: str) -> str` function with signature: `def fetch(date: str) -> str:`
3. Return standardized success format: `"YYYY.MM.DD F##: [factor name] [value] [source]"`
4. Return error format on failure: `"F## 錯誤: [detailed message] [source] (timestamp)"`
5. Use existing modules as templates (f01_fetcher.py recommended for API calls, f06_fetcher.py for Selenium)
6. Never raise exceptions - always catch and convert to error status strings
7. Add session metadata to decorator (if modules organization uses tags)

### Error Handling Convention

- All exceptions caught and converted to status strings
- Error format: `"F## 錯誤: [detailed message] [source] (timestamp)"`
- Return type always remains `str` - never raise exceptions from fetch()
- Log errors to both console and file via Python logging

### Data File Output

- Location: `data/` directory relative to project root
- Filename: `YYYY-MM-DD_HHMM_f##_fetcher.txt`
- Content: Single line with fetch() return value
- Timestamp auto-generated when run.py executes each module

## Project Dependencies

**Core Libraries:**
- `requests` (2.31.0+) - HTTP client for API calls
- `pandas` (2.1.0+) - Data manipulation and HTML parsing
- `lxml` (4.9.0+) - XML/HTML parsing for pandas.read_html()
- `pydantic` (2.5.0+) - Data validation and settings management
- `selenium` (4.36.0+) - Browser automation for dynamic content
- `webdriver-manager` (4.0.0+) - Automatic WebDriver management

**Development:**
- `pytest` (7.4.0+) - Testing framework
- `black` (23.9.0+) - Code formatting
- `isort` (5.12.0+) - Import sorting

**Python:** 3.9+

### Installing Dependencies

```bash
# Using Poetry (recommended)
poetry install

# Using pip
pip install -r requirements.txt
```

### Selenium WebDriver Setup

Selenium modules (F06, F11) use `webdriver-manager` for automatic driver management:
- No need for manual ChromeDriver download or version management
- First run automatically detects OS and downloads compatible WebDriver
- Cached in user's home directory: `~/.wdm/` (Windows) or `~/.wdm/` (Unix)
- If WebDriver fails to download, check: proxy settings, internet connectivity, or manually delete cache and retry

## OpenSpec Workflow

This project uses OpenSpec for spec-driven development. Always open `@/openspec/AGENTS.md` when requests involve:
- Planning or proposals (words: proposal, spec, change, plan)
- New capabilities, breaking changes, or architecture shifts
- Ambiguous requirements needing authoritative spec reference

**Quick OpenSpec Commands:**
```bash
openspec list                          # List active changes
openspec list --specs                  # List current specifications
openspec show [item]                   # Display change or spec details
openspec validate [item] --strict      # Validate changes
openspec archive <change-id> --yes     # Archive completed changes
```

## Important Notes

### Data Source Notes

- **TAIFEX API** - Direct API calls for futures positions and pricing
- **TAIFEX Daily Report** - Downloadable Excel/CSV files for historical data
- **Website Scraping** - F06 (VIX), F11 (Weighted Index) require Selenium
- **International Markets** - F21-F25 source NASDAQ futures and related indices

### Windows-Specific Considerations

- **UTF-8 Encoding:** All file I/O uses UTF-8 encoding explicitly to handle Traditional Chinese characters correctly
- **Console Safety:** Run.py wraps console output with safe handler to prevent I/O errors on Windows (common issue with asyncio and file descriptors)
- **Path Handling:** Use `Path` objects for cross-platform compatibility; PROJECT_ROOT is auto-detected from script location
- **Module Import:** Modules cached in memory (MODULE_CACHE dict) to avoid repeated disk reads during dynamic imports

### Session Scheduling

- **Morning Session** (F01-F17) - Executes during trading hours (9:00-13:45 TWN)
- **Night Session** (F21-F25) - Executes after-hours (15:00-05:00 TWN)
- GitHub Actions automate daily execution of both sessions

### Status Indicators

Output uses emoji indicators for quick status recognition:
- ✅ Success
- ⚠️ Warning/partial data
- ❌ Failure
- ⛔ Invalid/blocked

## File Structure

```
C:\AI\Taifex\
├── run.py                  # Main orchestrator
├── predict.py              # Prediction generator
├── predict_dashboard.py    # Dashboard generator
├── main_tools.py           # Utility menu
├── fetch_data.py           # Data fetching helper
├── requirements.txt        # Pip dependencies
├── pyproject.toml          # Poetry configuration
├── modules/                # Data fetcher modules (F01-F25)
├── dev/                    # Development & testing packages
├── tests/                  # Unit tests
├── data/                   # Output directory (timestamped files)
├── tools/                  # System utilities
├── utils/                  # Helper functions
├── openspec/               # OpenSpec specifications and changes
├── .github/workflows/      # GitHub Actions automation
└── .communication/         # Documentation coordination
```
