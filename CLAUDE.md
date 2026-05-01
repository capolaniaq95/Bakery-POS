# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based browser automation project using Playwright to automate login and navigation to Odoo ERP instances, generate 4 POS sessions and complete the sales for 3 hours.

## Commands

- **Run the get_partners.py**: `python get_partners.py` - Execute the API code, to save all partners
- **Run the get_products.py**: `python get_products.py` - Execute the API code, to save all products
- **Run the automation**: `python odoo_login.py` - Executes concurrent Odoo login sessions.
    - **Modifying Session Timeout**: To change the session timeout duration (currently set to 1 minute/60 seconds), modify the `SESSION_TIMEOUT` constant within `odoo_login.py` (e.g., change `60` to `300` for 5 minutes). This controls how long each session remains open after initial setup.
- **Install Playwright**: `playwright install` (already installed in `./playwright/` venv)
- **Install pandas**: `pip install pandas`
- **Run tests**: `pytest` (if test files are added)

## Code Architecture

- **`odoo_login.py`**: Main automation script
  - `PosSession` class: Manages each browser instance
  - `login_odoo()`: Launches Chromium browser, logs into Odoo at `http://localhost:8069/web/login`, navigates to Point of Sale
  - `run_concurrent_sessions(num_instances)`: Uses Python threading to run multiple browser instances concurrently.
    - **Modification Point**: The session timeout is controlled by the `SESSION_TIMEOUT` variable. **To change the time, edit this constant directly in `odoo_login.py`**.
  - Each instance opens a different POS: "Panaderia Caja 1", "Panaderia Caja 2", "Panaderia Caja 3", "Panaderia Caja 4"

- **Navigation Flow**:
  1. Go to Odoo login page
  2. Fill credentials from credentials.env
  3. Navigate to POS module via URL: `http://localhost:8069/web#menu_id=83&action=99`
  4. Wait for kanban grid to load
  5. Find the POS card with name "Panaderia Caja {instance_id}"
  6. Click the "Open Session" button on the POS card

- **Virtual environment**: Located in `./playwright/` directory with Playwright and dependencies pre-installed

## Notes

- The script uses `headless=False` to display the browser window
- Targets Odoo instance running on `localhost:8069`
- Uses `threading` module for concurrent session handling
- Each browser instance runs in its own context to avoid conflicts
- The script keeps browsers open for 20 seconds for verification, then closes them