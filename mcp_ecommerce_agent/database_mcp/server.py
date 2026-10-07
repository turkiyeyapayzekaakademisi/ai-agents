"""
Bu dosya SQLite veritabanındaki bilgileri MCP tool'ları olarak sunar.

MCP Tools:
    get_order_status
    get_product_stock
    get_shipping_price

Server:
    FastMCP kullanır.
    HTTP üzerinden 8000 portunda çalışır.
"""

import json

from fastmcp import FastMCP

from database import (
    get_order,
    get_shipping,
    get_stock
)


mcp = FastMCP("E-Commerce Database MCP Server")


@mcp.tool
def get_order_status(order_id: str) -> str:
    """Sipariş numarasına göre sipariş ve kargo durumunu getirir."""

    print(f"[MCP TOOL] get_order_status({order_id})")

    order = get_order(order_id)

    if order is None:
        return json.dumps(
            {
                "order_id": order_id,
                "error": "Sipariş bulunamadı."
            },
            ensure_ascii=False
        )

    return json.dumps(order, ensure_ascii=False)


@mcp.tool
def get_product_stock(product_name: str) -> str:
    """Ürün adına göre güncel stok miktarını ve fiyatını getirir."""

    print(f"[MCP TOOL] get_product_stock({product_name})")

    product = get_stock(product_name)

    if product is None:
        return json.dumps(
            {
                "product_name": product_name,
                "error": "Ürün bulunamadı."
            },
            ensure_ascii=False
        )

    return json.dumps(product, ensure_ascii=False)


@mcp.tool
def get_shipping_price(country: str) -> str:
    """Belirtilen ülkeye gönderim ücretini getirir."""

    print(f"[MCP TOOL] get_shipping_price({country})")

    shipping = get_shipping(country)

    if shipping is None:
        return json.dumps(
            {
                "country": country,
                "error": "Bu ülke için gönderim bilgisi bulunamadı."
            },
            ensure_ascii=False
        )

    return json.dumps(shipping, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )