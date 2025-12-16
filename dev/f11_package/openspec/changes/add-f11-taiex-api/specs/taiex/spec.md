# Capability Specification: TAIEX (加權股價收盤指數)

## Overview

The F11 TAIEX module provides real-time Taiwan Weighted Stock Index data extraction from TWSE (Taiwan Stock Exchange) official website. It follows the OpenSpec 4-phase development framework and integrates with the unified data fetching system.

---

## ADDED Requirements

### Requirement: Fetch TAIEX Index Function

The system SHALL provide a `fetch_taiex_index()` function that retrieves the latest Taiwan Weighted Stock Index value from TWSE.

#### Scenario: Success - Index Value Retrieved

- **WHEN** the function is called during trading hours
- **AND** the TWSE website is accessible
- **AND** the HTML structure contains valid index data
- **THEN** the function returns a formatted string:

  ```
  YYYY.MM.DD  F11: 加權股價收盤指數 : [VALUE] [TWSE]
  ```

- **AND** the date format is `YYYY.MM.DD`
- **AND** the value is a float with 2 decimal places (e.g., 18254.50)
- **AND** the log records the success with `[F11]` prefix at INFO level

#### Scenario: Failure - No Trading Data

- **WHEN** the function is called on a non-trading day (weekend, holiday)
- **AND** the TWSE website returns a page with no trading data
- **THEN** the function returns an error string:

  ```
  F11 錯誤: 該日無交易資料（可能是假日或休市日） [TWSE]
  ```

- **AND** the log records the situation with `[F11]` prefix at INFO level
- **AND** the function does NOT raise an exception (graceful handling)

#### Scenario: Error - Network Connection Failure

- **WHEN** the function attempts to fetch the webpage
- **AND** the HTTP request fails (network unreachable, timeout, HTTP 4xx/5xx)
- **THEN** the function returns an error string:

  ```
  F11 錯誤: 網路連線失敗 [TWSE]
  ```

- **AND** the log records the exception with `[F11]` prefix at ERROR level
- **AND** the function does NOT raise an exception (returns error string instead)

#### Scenario: Error - HTML Structure Changed

- **WHEN** the function attempts to parse the HTML
- **AND** the expected table structure is not found
- **AND** the required index column is missing
- **THEN** the function returns an error string:

  ```
  F11 錯誤: 無法解析頁面結構 [TWSE]
  ```

- **AND** the log records the parsing error with `[F11]` prefix at ERROR level
- **AND** the function does NOT raise an exception (graceful degradation)

---

### Requirement: HTTP Request and HTML Parsing

The system SHALL implement HTTP request handling and HTML parsing logic.

#### Scenario: HTTP Request with Timeout

- **WHEN** the function sends an HTTP GET request to TWSE
- **THEN** the request includes a timeout parameter (default 10 seconds)
- **AND** if the request exceeds the timeout, it fails gracefully
- **AND** the error is logged with appropriate context

#### Scenario: HTML Parsing Strategy

- **WHEN** the HTML response is received
- **THEN** the system uses BeautifulSoup to parse the HTML
- **AND** it searches for the data table by tag and attributes
- **AND** it handles potential HTML structure variations (5+ column name variants)
- **AND** it prioritizes searching for "目前指數" as the primary column

#### Scenario: Data Extraction

- **WHEN** the HTML table is found and parsed
- **THEN** the system extracts the most recent (last row) closing index value
- **AND** it validates the value is a valid float
- **AND** it handles missing or malformed data gracefully

---

### Requirement: Output Formatting

The system SHALL format the TAIEX data in a unified, parseable format.

#### Scenario: Standard Success Output

- **WHEN** the index value is successfully retrieved
- **THEN** the output format SHALL be:

  ```
  YYYY.MM.DD  F11: 加權股價收盤指數 : [VALUE] [TWSE]
  ```

- **AND** the date component uses `YYYY.MM.DD` format (e.g., `2025.12.17`)
- **AND** the value is formatted to 2 decimal places (e.g., `18254.50`)
- **AND** the module name "F11" is consistently identified
- **AND** the source "[TWSE]" is always appended at the end

#### Scenario: Standard Error Output

- **WHEN** an error occurs
- **THEN** the output format SHALL be:

  ```
  F11 錯誤: [ERROR_MESSAGE] [TWSE]
  ```

- **OR** with timestamp for critical errors:

  ```
  F11 錯誤: [ERROR_MESSAGE] [TWSE] (YYYY-MM-DD HH:MM:SS)
  ```

- **AND** the "[TWSE]" source identifier is always present
- **AND** the error message is clear and actionable

---

### Requirement: Logging and Tracing

The system SHALL provide comprehensive logging for debugging and monitoring.

#### Scenario: Info-Level Logging

- **WHEN** normal operations occur (successful fetch, no trading data)
- **THEN** log messages at INFO level
- **AND** all messages include the `[F11]` prefix
- **AND** log format includes timestamp and operation details
- **Example**: `[F11] 開始抓取加權股價收盤指數...`

#### Scenario: Debug-Level Logging

- **WHEN** detailed flow information is needed
- **THEN** log messages at DEBUG level
- **AND** debug logs include intermediate steps (HTML size, parsing progress, etc.)
- **AND** debug logs help troubleshoot page structure issues
- **Example**: `[F11] HTML 頁面大小: 125KB`

#### Scenario: Error-Level Logging

- **WHEN** exceptions or failures occur
- **THEN** log messages at ERROR level
- **AND** error logs include the exception type and details
- **AND** error logs include the full stack trace for debugging
- **Example**: `[F11] 網路連線失敗: ConnectionError: Max retries exceeded`

---

### Requirement: Exception Handling Strategy

The system SHALL handle all expected exceptions without raising unhandled errors.

#### Scenario: RequestException Handling

- **WHEN** a `requests.exceptions.RequestException` occurs (network, timeout, HTTP error)
- **THEN** the function catches it and returns an error string
- **AND** the error is NOT re-raised
- **AND** the log records the exception type and details at ERROR level

#### Scenario: AttributeError Handling

- **WHEN** HTML parsing fails (expected element not found)
- **THEN** the function catches `AttributeError` and returns parsing error string
- **AND** the error is NOT re-raised

#### Scenario: ValueError Handling

- **WHEN** value conversion to float fails (malformed number)
- **THEN** the function catches `ValueError` and returns data format error string
- **AND** the error is NOT re-raised

#### Scenario: Generic Exception Handling

- **WHEN** an unexpected exception occurs
- **THEN** the function catches it with a generic `Exception` handler
- **AND** it returns a generic error message
- **AND** the error is logged with full context for investigation

---

### Requirement: Performance and Reliability

The system SHALL meet performance and reliability targets.

#### Scenario: Execution Time Target

- **WHEN** the function executes successfully
- **THEN** execution time SHALL be < 5 seconds
- **AND** typical execution time is around 1-2 seconds for HTML parsing and extraction

#### Scenario: Success Rate Target

- **WHEN** called during trading hours on a trading day
- **THEN** success rate SHALL be > 95%
- **AND** only excluding cases where TWSE is unavailable or network is unstable

#### Scenario: Memory Efficiency

- **WHEN** the function processes HTML content
- **THEN** memory usage SHALL remain < 50MB
- **AND** temporary objects are properly cleaned up
- **AND** no memory leaks occur during repeated calls

---

### Requirement: Integration with Unified System

The system SHALL integrate seamlessly with the existing fetcher framework.

#### Scenario: Module Import

- **WHEN** the F11 module is imported into the main system
- **THEN** it follows the same import pattern as other fetchers (F06, etc.)
- **AND** it is compatible with the `run.py` orchestration system
- **AND** it returns data in the expected format for result collection

#### Scenario: Consistency with Other Modules

- **WHEN** F11 output is collected alongside other modules (F06, F02, etc.)
- **THEN** the output format is consistent with the overall system convention
- **AND** the log format (with module prefix) matches other modules
- **AND** error handling follows the same patterns

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| requests | >= 2.28.0 | HTTP requests |
| beautifulsoup4 | >= 4.11.0 | HTML parsing |
| python | >= 3.9.0 | Core language |
| pytest | >= 7.0.0 | Unit testing |

---

## Success Criteria

- [ ] All ADDED requirements are implemented
- [ ] All scenarios have corresponding test cases
- [ ] Unit test coverage >= 90%
- [ ] All 15+ tests pass successfully
- [ ] Integration test with run.py succeeds
- [ ] Production deployment verified with real data

---

## Notes

- This spec defines the F11 capability as part of the add-f11-taiex-api change proposal
- Implementation follows the design.md technical decisions
- Testing is guided by test scenarios in this spec
- See tasks.md for the 18-task implementation checklist
