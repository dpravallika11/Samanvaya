Samanvãya is a Python/Flask-based data harmonization and semantic transformation platform. It helps you map and align data from different sources into consistent schema formats using AI-assisted transformation and rule-based harmonization.

## Key Features

- Upload source datasets (CSV) and define target schema/categorical mappings.
- Automatic semantic mapping between source and target columns.
- AI-driven prompt transformation with Gemini API support.
- Review and edit generated transformations before applying.
- Export harmonized datasets for downstream use.
- Includes explainability and reliability modules for quality checks.

## Project Structure

- `app.py` - Main Flask application and route handlers.
- `dataset_loader.py` - CSV upload and parsing logic.
- `schema_harmonizer.py` - Schema alignment and mapping operations.
- `semantic_engine.py` - Semantic mapping and nearest matching.
- `transformer.py` - Data transformation engine.
- `llm_transformer.py` - LLM prompt generation and transformation logic.
- `reliability.py` / `reliability_engine.py` - Data reliability checks and metadata.
- `explainability_engine.py` - Explainability utilities and transformation explanations.
- `database.py` - Simple local data storage and session persistence.
- `templates/` - Flask HTML templates for web interface.
- `static/` - CSS and JS assets.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create `.env` with your Gemini API key (see `README_API.md`).
3. Run the app:
   ```bash
   python app.py
   ```
4. Open `http://localhost:5000` in your browser.

## Usage

1. Upload your CSV dataset.
2. Choose target schema and select columns that need harmonization.
3. Review generated mappings and transformations.
4. Apply transformations and download harmonized CSV.

## Notes

- The project is intended for PoC and internal ETL workflows.
- Keep API keys secret by storing them in `.env`.

## License

This project is provided as-is for demonstration and learning.
