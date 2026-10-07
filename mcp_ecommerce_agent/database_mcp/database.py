"""
Bu dosya SQLite veritabanına erişmek için kullanılan yardımcı fonksiyonları içerir.

Fonksiyonlar:
    get_order()
    get_stock()
    get_shipping()
"""

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "ecommerce.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_order(order_id: str) -> dict | None:
    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            order_id,
            product_name,
            status,
            cargo_company,
            tracking_number
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None


def get_stock(product_name: str) -> dict | None:
    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            name,
            stock,
            price
        FROM products
        WHERE LOWER(name) = LOWER(?)
        """,
        (product_name,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None


def get_shipping(country: str) -> dict | None:
    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            country,
            price,
            currency
        FROM shipping_prices
        WHERE LOWER(country) = LOWER(?)
        """,
        (country,)
    ).fetchone()

    connection.close()

    return dict(row) if row else None