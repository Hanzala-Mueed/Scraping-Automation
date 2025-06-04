## Project Structure (Suggested)

```text
filecr_scraper/
├── main.py                  # Entry point for FastAPI
├── scraper/
│   ├── __init__.py
│   ├── phase1_scraper.py    # Phase 1: Category and URL scraping logic
│   ├── phase2_scraper.py    # Phase 2: Metadata and download link scraping logic
│   ├── phase3_downloader.py # Phase 3: File download automation logic
├── db/
│   ├── database.py          # DB session setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
├── routers/
│   ├── __init__.py
│   ├── categories.py        # Routes related to categories
│   ├── software.py          # Routes related to software data
├── utils/
│   ├── helpers.py           # Utility functions
├── data/
│   ├── logs/                # Scraping logs
│   ├── scraped_data.json    # Local storage before DB
│   └── scraping_progress/   # Tracks current scraping progress
└── requirements.txt         # Dependencies
└── docs/
    └── project_doc.md        # The documentation
```
