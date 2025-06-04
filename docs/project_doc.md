# Project Documentation: FileCR Software Scraper

## Project Overview

This project is a web scraping and automation tool designed to extract software data from the website [FileCR.com](https://filecr.com). The scraper is built using Python and incorporates technologies such as **Selenium**, **BeautifulSoup (bs4)**, **FastAPI**, **SQLAlchemy**, and **PostgreSQL**. The objective is to systematically collect software metadata, download links, and organize the software files in a local directory or external drive using automated drag-and-drop functionality.

---

## Technologies Used

- **Programming Language**: Python
- **Framework**: FastAPI
- **Libraries**:
  - Selenium
  - BeautifulSoup (bs4)
  - pyautogui
  - time, os, json, etc.
- **Database**:
  - PostgreSQL
  - SQLAlchemy (ORM)

---

## Phase 1: Post URL and Category Scraping

### Objective:

Extract product titles, post URLs, and associated categories from FileCR by navigating its category hierarchy.

### Workflow:

1. **Starting Point**:

   * Navigate to FileCR home page: `https://filecr.com`
   * Click on **"Windows"** from the header (acts as primary category)

2. **Navigation**:

   * Select Sub-Category (e.g., Antivirus & Security)
   * Extract the following from the first page:

     * Title
     * Post URL
     * Primary Category
     * Sub-Category

   * Navigate through all pages using the **Next** button.

3. **Tracking Information**:

   * Resume scraping from last saved point
   * Total products per page (usually 12)
   * Total pages per sub-category
   * Total products per sub-category
   * Total products per primary category

### Tools & Methods:

* Selenium to simulate clicks and pagination
* BeautifulSoup to extract HTML data
* Progress tracking with printed logs and structured flow control

### Database relation

* The data scraped in this phase is stored in the categories table.**
* The software table references these entries by their id, forming a relational link between both tables.

---

## Phase 2: Metadata & Direct Download Button link Extraction

### Objective:

Deep scrape software metadata and prepare direct download button links.

### Planned Workflow:

1. **Navigation**:

   * From home, click **Categories** in the header
   * On the new page, use sidebar to select subcategories
   * Click each software link to open its details page

2. **Scrape Details**:

   * Software Title
   * Post URL
   * Software Size (Value + Unit)
   * Version
   * Release Date (from right sidebar)
   * Direct Download Button Url
   * Status (Pending, Processing, Downloaded)

3. **DB Table**

   * Create a table with columns for each metadata field
   * Download_page column for direct download button link
   * Status column for tracking download status (for phase 3)
   * As the data is stored in the software table and linked to categories via category id.


## Phase 3 – File Download Automation Strategy

### Goal:
 Automate the process of downloading software from direct download links and update the download status in the database.

### Logic Breakdown:

1. **Scraper Initialization:**

* Connect to the database.
* Fetch software entries from the software table using the download_link field.
* Also the links can be fetch in batch of 100 links at a time.

2. **Download Process:**

* Update the status field to processing.
* Open the download_link using a headless Chromium browser or Selenium WebDriver.
* Parse the download page using BeautifulSoup to find the final Download button.
* Click the button to start the software download (target location: Desktop).

3. **Post-Processing:**

* Monitor for successful download.
* Update the status field in the database to success.

This phase ensures the software is downloaded programmatically and tracks its download progress in real-time for automation and further action


4. **Drag & Drop Script (for Storage Automation)**:

   * Right side of desktop shows downloaded software
   * Left side: Opened external/local drive
   * Use drag-and-drop script to move files

### Drag and Drop Automation

To automate the transfer of downloaded software from the Desktop to a designated drive or folder, the project uses the `pyautogui` library. This approach simulates a natural human drag-and-drop action and is fully compatible with **Windows, macOS, and Linux**.

The automation follows these steps:

1. **File Selection**: The script initiates by clicking to select the downloaded software file on the desktop.
2. **Mouse Press (Drag Initiation)**: It then simulates pressing and holding the left mouse button to start the drag action.
3. **Smooth Movement**: The file is moved gradually to the destination using a controlled delay, ensuring compatibility with various system speeds and screen resolutions.
4. **Mouse Release (Drop Completion)**: Finally, the mouse button is released to drop the file into the target location.

> This method is designed to be OS-independent, providing a stable and consistent drag-and-drop mechanism across different desktop environments.
---

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
    └── project_doc.md        # This documentation
```

---

## Database Schema (Example)

### Table: `software`

```sql
id SERIAL PRIMARY KEY,
title TEXT,
post_url TEXT,
software_size TEXT,
version TEXT,
release_date DATE,
download_link TEXT,
status TEXT,
```

### Table: `categories`

```sql
id SERIAL PRIMARY KEY,
title TEXT,
post_url TEXT,
primary_category TEXT,
sub_category TEXT
child_category
```

## Future Enhancements

* Duplicate avoidance and merging new metadata
* Admin dashboard to monitor scraping status
* Multi-threaded scraping for faster performance
* Logging and alerting system

---

## Conclusion

This project is a scalable web scraping tool that can help automate the collection and organization of software metadata and files from FileCR. The structured approach and modular design allow for easy extensions in future phases.
