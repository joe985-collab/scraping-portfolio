# Design Document: Web Scraper Suite

**Projects:** Amazon Basic Scraper, Naukri Basic Scraper
**Tech Stack:** Python 3.12, Playwright (sync), Flask, CSV
**Non-Goals:** Login handling, CAPTCHA bypass, distributed crawling

---

## 1. Shared Architecture (Both Projects)

### 1.1 High-Level Flow

```
Flask UI
  ↓ (user input)
Scraper Runner
  ↓
Playwright Scraper
  ↓
CSV Output
  ↓
Flask Table Renderer
```

---

### 1.2 Shared Constraints

* Playwright **sync API only**
* No Selenium
* No hard sleeps (`time.sleep`)
* Pagination supported
* Scraper must **not crash on missing fields**
* CSV output must be **deduplicated**
* Flask must **not block UI indefinitely**
* One scraper run = one CSV file

---

### 1.3 Shared Utilities (Recommended)

Create a shared utils module:

```
utils/
 ├── csv_utils.py
 ├── dedupe.py
 ├── time_utils.py
 └── scraper_utils.py
```

#### CSV Utilities

* Write CSV with headers
* Append rows safely
* Load CSV for rendering

#### Deduplication Rule (Both)

* Deduplicate on **primary link URL**
* Keep first occurrence

---

## 2. Project 1: Amazon Basic Scraper

---

### 2.1 Goal

Allow a user to:

* Enter a product keyword in a **Flask UI**
* Trigger an **Amazon search scraper**
* View results in a **table**
* Download the generated **CSV**

---

### 2.2 Input

**From Flask form**

```json
{
  "query": "wireless mouse"
}
```

---

### 2.3 Scraper Responsibilities

#### Search

* Navigate to Amazon search with query
* Encode query properly
* Handle pagination

#### Extract per product:

| Field       | Source                   |
| ----------- | ------------------------ |
| title       | product title            |
| price       | visible price (nullable) |
| rating      | star rating (nullable)   |
| reviews     | review count (nullable)  |
| product_url | canonical product link   |

---

### 2.4 Pagination Strategy (Amazon)

#### Rule

* Click **Next** pagination link
* Stop when:

  * Next button not found
  * OR page count limit reached (configurable)

#### Selector Pattern

* Role-based or container-scoped selectors
* Must avoid strict-mode violations

---

### 2.5 CSV Output

**Filename**

```
amazon_<query>_<timestamp>.csv
```

**Deduplication**

* Based on `product_url`
* Remove duplicates **after scraping completes**

---

### 2.6 Flask App (Amazon)

#### Routes

```text
GET  /amazon
POST /amazon/search
GET  /amazon/results/<filename>
```

#### Behavior

* POST triggers scraper in project directory
* Scraper writes CSV
* Flask reads CSV
* Render results as HTML table

---

### 2.7 Error Handling

* Empty results → show message
* Scraper exception → return error status
* CSV missing → handled gracefully

---

## 3. Project 2: Naukri Basic Scraper

---

### 3.1 Goal

Enhance existing scraper to:

* Accept **dynamic search input**
* Support pagination
* Output **CSV instead of JSON**
* Remove duplicate job entries
* Integrate with Flask UI

---

### 3.2 Input

**From Flask form**

```json
{
  "keyword": "data engineer",
  "location": "bangalore" (optional)
}
```

---

### 3.3 Required Changes to Existing Scraper

#### Current Behavior

* Hardcoded keyword: `"python"`
* Output: JSON
* Pagination partially implemented

#### Updated Behavior

* Keyword passed as function argument
* Pagination mandatory
* CSV output
* Deduplication enabled

---

### 3.4 Job Data Model

| Field      | Description                 |
| ---------- | --------------------------- |
| title      | Job title                   |
| company    | Company name                |
| experience | Experience range (nullable) |
| location   | Job location                |
| salary     | Salary (nullable)           |
| job_url    | Job detail page             |
| posted     | Posted date (nullable)      |

---

### 3.5 Pagination Strategy (Naukri)

#### Rule

* Click **Next** link by role/name
* Wait for job cards to reload
* Stop when:

  * Next is hidden/disabled
  * OR no new jobs detected

---

### 3.6 Deduplication Strategy

#### Primary Key

```
job_url
```

#### Implementation

* Store seen URLs in a set
* OR dedupe CSV post-scrape

---

### 3.7 CSV Output

**Filename**

```
naukri_<keyword>_<timestamp>.csv
```

---

### 3.8 Flask App (Naukri)

#### Routes

```text
GET  /naukri
POST /naukri/search
GET  /naukri/results/<filename>
```

#### Behavior

* User submits keyword
* Scraper executes
* CSV generated
* Table rendered

---

## 4. Flask UI Requirements (Both)

### 4.1 Pages

* Search input form
* Loading indicator (optional)
* Results table
* CSV download link

---

### 4.2 Table Requirements

* Auto-generated from CSV headers
* Pagination optional (frontend)
* Empty values shown as `—`

---

## 5. Non-Functional Requirements

### Performance

* JS-side extraction preferred
* Avoid Python loops over locators

### Stability

* No strict-mode violations
* No assumptions about optional fields

### Maintainability

* One container = one record
* No global selectors inside loops

---

## 6. Explicit Non-Goals (Important for Agents)

❌ CAPTCHA solving
❌ Login / cookies
❌ Headless detection evasion
❌ Distributed crawling
❌ Database persistence

---

## 7. Acceptance Criteria

### Amazon

* Search term from UI works
* Pagination works
* CSV generated
* No duplicate product URLs
* Table renders correctly

### Naukri

* Keyword configurable
* Pagination works
* CSV output
* No duplicate job URLs
* Flask UI works end-to-end

---

## 8. Suggested Agent Execution Plan

1. Refactor scrapers to accept parameters
2. Add pagination guards
3. Convert JSON → CSV (Naukri)
4. Add deduplication utility
5. Build Flask routes
6. Wire scraper execution
7. Render CSV tables
8. Final cleanup

---

## 9. Safety Checklist (Before Agent Runs)

```bash
git status
git commit -am "checkpoint before agent changes"
```

---

