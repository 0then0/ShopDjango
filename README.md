# Django Shop

A simple e-commerce project built with Django 5.2, PostgreSQL, and Bootstrap.  
Supports product catalog, shopping cart (guest & authenticated), checkout, order history, user profiles, admin enhancements, AJAX updates, filters, search, and more.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Database Setup & Migrations](#database-setup--migrations)
- [Usage](#usage)
  - [Running the Development Server](#running-the-development-server)
  - [Admin Site](#admin-site)

## Features

- **Product Catalog**

  - List, detail pages
  - Pagination
  - Full-text search (name & description)
  - Filtering by category, price range, in-stock only

- **Shopping Cart**

  - Guest cart stored in session
  - Authenticated cart persisted in database
  - AJAX add, update quantity, remove item, clear cart
  - Dynamic cart badge in navbar

- **Checkout & Orders**

  - Checkout form pre-filled from user profile
  - Order model with items, status (`PENDING`, `PROCESSING`, `COMPLETED`, `CANCELLED`)
  - Order history & detail pages with pagination

- **User Accounts & Profiles**

  - Registration & login
  - Email-unique validation
  - Extended profile (avatar, phone, address, city, postal code, birth date)
  - Editable first name, last name
  - Profile page shows avatar preview

- **Admin Enhancements**

  - Inline order items, status‐based edit restrictions
  - Auto-fill `price_at_order` from product price
  - Image preview in product list
  - Custom groups & permissions (`Managers`, `Staff`)
  - Staff can only change order status
  - Managers have full CRUD on catalog

- **Configuration & Security**
  - Environment variables via `.env` (django-environ)
  - SECRET_KEY, DEBUG, DB credentials read from env

## Tech Stack

- Python 3.13
- Django 5.2
- PostgreSQL
- Bootstrap 5

## Getting Started

### Prerequisites

- Python 3.13
- PostgreSQL
- `pip` or `pipenv` / `poetry`

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/0then0/ShopDjango
   cd ShopDjango
   ```

2. **Create and activate a virtualenv**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

Create and edit `.env`:

```dotenv
SECRET_KEY=your_django_secret_key
DEBUG=True

DB_ENGINE=django.db.backends.postgresql
DB_NAME=shop_db
DB_USER=shop_user
DB_PASSWORD=strong_password
DB_HOST=localhost
DB_PORT=5432
```

### Database Setup & Migrations

1. **Create PostgreSQL database & user**

   ```sql
   CREATE DATABASE shop_db;
   CREATE USER shop_user WITH PASSWORD 'strong_password';
   GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_user;
   ```

2. **Run migrations**

   ```bash
   python manage.py migrate
   ```

3. **Collect static files**

   ```bash
   python manage.py collectstatic
   ```

4. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

## Usage

### Running the Development Server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

### Admin Site

- URL: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- Use superuser credentials.
- **Managers** group: full CRUD on Products & Categories.
- **Staff** group: can only change Order status.
