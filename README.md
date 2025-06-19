# Lite Forecast App

This project provides a simple Streamlit application for forecasting ARR based on KPI metrics and monthly NBM targets.

## Usage

1. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app/app.py
   ```
3. Open the provided URL in your browser.

You may also build and run with Docker:

```bash
docker build -t forecast-app app/
docker run -p 8501:8501 forecast-app
```

Sample CSV files are provided in the `app/` directory.

