"""
Bu dosya MCP Database Server tarafından kullanılacak SQLite veritabanını oluşturur.

Tablolar:
    products
    orders
    shipping_prices

Dosya çalıştırıldığında ecommerce.db oluşturulur ve örnek veriler eklenir.
"""

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "ecommerce.db"


def main() -> None:
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS shipping_prices;

    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        stock INTEGER NOT NULL,
        price REAL NOT NULL
    );

    CREATE TABLE orders (
        order_id TEXT PRIMARY KEY,
        product_name TEXT NOT NULL,
        status TEXT NOT NULL,
        cargo_company TEXT,
        tracking_number TEXT
    );

    CREATE TABLE shipping_prices (
        country TEXT PRIMARY KEY,
        price REAL NOT NULL,
        currency TEXT NOT NULL
    );
    """)

    cursor.executemany(
        "INSERT INTO products (name, stock, price) VALUES (?, ?, ?)",
        [
            ("MacBook Air M3", 14, 54999),
            ("Dell UltraSharp U2723QE", 7, 28999),
            ("Logitech MX Master 3S", 32, 4999)
        ]
    )

    cursor.executemany(
        """
        INSERT INTO orders (
            order_id,
            product_name,
            status,
            cargo_company,
            tracking_number
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                "ORD-1001",
                "MacBook Air M3",
                "kargoya_verildi",
                "Yurtiçi Kargo",
                "YK123456"
            ),
            (
                "ORD-1002",
                "Dell UltraSharp U2723QE",
                "hazirlaniyor",
                None,
                None
            ),
            (
                "ORD-1003",
                "Logitech MX Master 3S",
                "teslim_edildi",
                "Aras Kargo",
                "AR987654"
            )
        ]
    )

    cursor.executemany(
        """
        INSERT INTO shipping_prices (
            country,
            price,
            currency
        )
        VALUES (?, ?, ?)
        """,
        [
            ("Germany", 25, "EUR"),
            ("Netherlands", 27, "EUR"),
            ("United Kingdom", 30, "GBP"),
            ("USA", 35, "USD")
        ]
    )

    connection.commit()
    connection.close()

    print(f"[OK] SQLite database oluşturuldu: {DB_PATH}")


if __name__ == "__main__":
    main()