# Bakery-POS

Playwright-driven browser automation for Odoo Point of Sale (POS) sessions. Automates concurrent POS workflows including login, product search, customer assignment, payment processing, and session closing.

## Features

- **Concurrent Sessions**: Run multiple POS sessions in parallel using Python threading (default: 4 instances)
- **Automated Login**: Authenticates to Odoo using credentials from environment variables
- **POS Session Management**: Opens register, creates sales orders, and closes sessions automatically
- **Customer & Product Sync**: Fetches partners and products from Odoo via XML-RPC API
- **Randomized Sales**: Generates random sale orders with varying product lines and payment methods (Nequi, Cash, Card, Rappi)

## Prerequisites

- Python 3.10+
- Odoo instance running locally (default: `http://localhost:8069`)
- Chromium-based browser (installed by Playwright)

## Setup

### 1. Clone and create virtual environment

```bash
git clone <repository-url>
cd Bakery-POS
python3 -m venv playwright
source playwright/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
sudo playwright install-deps chromium
```

### 3. Configure credentials

Create or edit `credentials.env`:

```env
password_api = "your_api_key"
password = "your_user_password"
db = "your_database"
url = "http://localhost:8069/"
username = "admin"
```

## Usage

### Fetch partners and products from Odoo API

```bash
python get_partners.py   # Saves partners to data/partners.csv
python get_products.py   # Saves products to data/products.csv
```

### Run POS automation

```bash
python odoo_login.py
```

This launches 4 concurrent browser instances, each handling a different POS register.

### Customize session count

Edit `odoo_login.py` and change the argument in `run_concurrent_sessions()`:

```python
run_concurrent_sessions(2)  # Run only 2 instances
```

### Change session duration

Modify the `minutes` variable in the `_perform_session_tasks` method (default: 1 minute):

```python
minutes = 180  # 3 hours
```

## Project Structure

```
Bakery-POS/
├── odoo_login.py        # Main automation script
├── get_partners.py      # Fetch partners via Odoo XML-RPC API
├── get_products.py      # Fetch products via Odoo XML-RPC API
├── credentials.env      # Environment variables (not committed)
├── requirements.txt     # Python dependencies
├── data/
│   ├── partners.csv     # Generated partner data
│   └── products.csv     # Generated product data
└── playwright/          # Virtual environment
```

## Workflow

Each POS session follows this flow:

1. Login to Odoo
2. Navigate to Point of Sale module
3. Open the assigned POS register
4. Loop (for configured duration):
   - Search and add random products to the order
   - Assign a random customer
   - Process payment (random method)
   - Validate the order
   - Start a new order
5. Close register with cash count reconciliation
6. Return to Odoo backend

## Notes

- Runs in headful mode (`headless=False`) for visibility
- Each browser instance uses an isolated context to prevent conflicts
- Credentials file is git-ignored; share `credentials.env.example` for team setup
- `dotenv` package is `python-dotenv` on PyPI
