# Analytics Microservice V2 - Test Suite

## Test Files

### 1. `test_all_charts.py`
**Purpose**: Comprehensive test of all 24 chart types supported by the service.

**What it tests**:
- All chart type generation capabilities
- Synthetic data generation
- Chart rendering with matplotlib
- WebSocket communication
- Response handling and error recovery

**Usage**:
```bash
python3 test_all_charts.py
```

**Output**:
- Generates `analytics_test_report.html` with all successful charts
- Shows success/failure statistics
- Displays actual PNG charts in HTML report

---

### 2. `test_metadata_validation.py`
**Purpose**: Validates that all metadata and table-ready data is properly included in responses.

**What it tests**:
- Chart title inclusion
- X and Y axis labels
- Axis type classification
- Table data formatting
- Table column headers
- Data statistics
- All metadata field completeness

**Usage**:
```bash
python3 test_metadata_validation.py
```

**Output**:
- Generates `enhanced_metadata_report.html` with validation results
- Shows metadata completeness for each chart type
- Displays table data preview
- Reports any missing or malformed fields

---

## Test Reports

### `analytics_test_report.html`
Visual report showing all successfully generated charts with:
- Actual PNG images
- Generation statistics
- Chart type coverage
- Feedback capability for each chart

### `enhanced_metadata_report.html`
Validation report showing:
- Metadata completeness checks
- Table data formatting validation
- Field-by-field verification
- Pass/fail status for each requirement

---

## Running Tests

### Prerequisites
1. Ensure the WebSocket service is running:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Ensure GOOGLE_API_KEY is set in `.env` file

### Run All Tests
```bash
# Test all chart generation
python3 test_all_charts.py

# Test metadata and table data
python3 test_metadata_validation.py
```

### Expected Results
- All 24 chart types should generate (some may fail due to WebSocket message size limits)
- All metadata fields should be populated
- Table data should be properly formatted
- Reports should open automatically in browser

---

## Test Coverage

| Test Area | Coverage | Test File |
|-----------|----------|-----------|
| Chart Generation | 24 chart types | test_all_charts.py |
| Metadata Fields | 10+ fields | test_metadata_validation.py |
| Table Data | All formats | test_metadata_validation.py |
| Error Handling | Basic | Both files |
| WebSocket Protocol | Full cycle | Both files |

---

*These tests ensure the Analytics Microservice V2 meets all requirements for chart generation, metadata completeness, and data formatting.*