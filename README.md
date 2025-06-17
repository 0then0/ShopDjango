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
- [REST API](#rest-api)
  - [Authentication](#authentication)
  - [Categories](#categories)
  - [Products](#products)
  - [Cart](#cart)
  - [Orders](#orders)

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

## REST API

The project exposes a full RESTful JSON API via Django REST Framework. All API routes are mounted under `/api/`.

### Authentication

- **Obtain JWT tokens**  
  `POST /api/token/`  
  Request body:

  ```json
  { "username": "admin", "password": "secret123" }
  ```

  Response:

  ```json
  {
  	"refresh": "<refresh_token>",
  	"access": "<access_token>"
  }
  ```

- **Refresh access token**
  `POST /api/token/refresh/`
  Request body:

  ```json
  { "refresh": "<refresh_token>" }
  ```

  Response:

  ```json
  { "access": "<new_access_token>" }
  ```

- **Session‑based login/logout** (for browsable API)

  - `GET  /api/auth/login/`
  - `POST /api/auth/logout/`

### Categories

| Method | Endpoint                | Description                      | Permissions                           |
| ------ | ----------------------- | -------------------------------- | ------------------------------------- |
| GET    | `/api/categories/`      | List all categories              | Public (anonymous)                    |
| POST   | `/api/categories/`      | Create a new category            | **Managers** only (`add_category`)    |
| GET    | `/api/categories/{id}/` | Retrieve a single category by ID | Public                                |
| PATCH  | `/api/categories/{id}/` | Partially update a category      | **Managers** only (`change_category`) |
| PUT    | `/api/categories/{id}/` | Replace a category               | **Managers** only                     |
| DELETE | `/api/categories/{id}/` | Delete a category                | **Managers** only (`delete_category`) |

### Products

| Method | Endpoint              | Description                          | Permissions                          |
| ------ | --------------------- | ------------------------------------ | ------------------------------------ |
| GET    | `/api/products/`      | List all products (supports filters) | Public                               |
| POST   | `/api/products/`      | Create a new product                 | **Managers** only (`add_product`)    |
| GET    | `/api/products/{id}/` | Retrieve a single product by ID      | Public                               |
| PATCH  | `/api/products/{id}/` | Partially update a product           | **Managers** only (`change_product`) |
| PUT    | `/api/products/{id}/` | Replace a product                    | **Managers** only                    |
| DELETE | `/api/products/{id}/` | Delete a product                     | **Managers** only (`delete_product`) |

Supports query parameters on the list endpoint:

- `?category={id}`
- `?price__gte={min}`
- `?price__lte={max}`
- `?stock__gt=0`
- Search: `?search={query}`

### Cart

| Method | Endpoint          | Description                                                | Permissions        |
| ------ | ----------------- | ---------------------------------------------------------- | ------------------ |
| GET    | `/api/cart/`      | List current user’s cart items                             | Authenticated only |
| POST   | `/api/cart/`      | Add a product (body: `{ "product_id": 5, "quantity": 2 }`) | Authenticated only |
| PATCH  | `/api/cart/{id}/` | Update quantity of a cart item                             | Authenticated only |
| DELETE | `/api/cart/{id}/` | Remove an item from the cart                               | Authenticated only |

### Orders

| Method | Endpoint            | Description                                     | Permissions                                  |
| ------ | ------------------- | ----------------------------------------------- | -------------------------------------------- |
| GET    | `/api/orders/`      | List orders belonging to the authenticated user | Authenticated                                |
| POST   | `/api/orders/`      | Create a new order (body: shipping data)        | Authenticated                                |
| GET    | `/api/orders/{id}/` | Retrieve order details (including items)        | Owner only                                   |
| PATCH  | `/api/orders/{id}/` | Update order status (`{"status":"COMPLETED"}`)  | **Staff** only (and only for `status` field) |
| DELETE | `/api/orders/{id}/` | Deletion is **not allowed**                     | –                                            |

#### Notes

- All write operations (POST, PATCH, DELETE) require authentication via **Bearer JWT** (or session).
- Permissions are enforced based on Django’s **groups** and **model‑level permissions**:

  - **Managers** group: full CRUD on `Category` and `Product`.
  - **Staff** group: only allowed to change `Order.status`.
  - **Authenticated users**: can manage their own cart and place orders.

- Browsable API and OPTIONS responses list allowed methods automatically (with `SimpleMetadata`).

```bash
# Example: list products
curl -H "Authorization: Bearer <access_token>" http://127.0.0.1:8000/api/products/

# Example: create product as Manager
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer <manager_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"New","price":10,"stock":5,"category_id":1}'
```
