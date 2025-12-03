
# Witness Archive: Emotion & Theme Dashboard (Real Data)

This Streamlit dashboard visualizes **real news and testimony data** about ICE-related events in Chicago.

## How to run locally

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```

The app will open in your browser (default: http://localhost:8501).

## Files

- `app.py` – main Streamlit app.
- `ICE_Chicago_REAL_dataset.csv` – cleaned dataset with:
  - Title
  - URL
  - Source
  - Publication Date
  - Summary
  - Emotion Label
  - Thematic Label
- `requirements.txt` – Python dependencies.
