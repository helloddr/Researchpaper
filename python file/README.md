# PySpark Data Processing Sample

This workspace contains a simple PySpark data processing example.

## Setup

1. Create a Python virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Run

```powershell
python main.py
```

## What it does

- Reads a sample CSV file (`data/sample.csv`)
- Applies basic transformations (filter, group, aggregate, sort)
- Writes output to `output/` as Parquet
