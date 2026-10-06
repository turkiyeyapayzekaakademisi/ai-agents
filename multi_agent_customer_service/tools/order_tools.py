"""
Bu dosyada Order Agent tarafından kullanılan sipariş sorgulama tool'ları bulunur.

get_domestic_order_status:
    Yurt içi sipariş verisini okur.

get_international_order_status:
    Yurt dışı sipariş verisini okur.
"""

import json
from pathlib import Path

from langchain_core.tools import tool


BASE_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_PATH / "data"


def load_json(file_name: str) -> dict:
    with (DATA_PATH / file_name).open("r", encoding="utf-8") as file:
        return json.load(file)


@tool
def get_domestic_order_status(order_id: str) -> str:
    """Yurt içi bir siparişin mevcut kargo durumunu getirir."""

    print(f"\n[TOOL] get_domestic_order_status({order_id})")

    orders = load_json("domestic_orders.json")
    order = orders.get(order_id)

    if order is None:
        return json.dumps({
            "order_id": order_id,
            "sonuc": "Sipariş bulunamadı."
        }, ensure_ascii=False)

    return json.dumps({
        "order_id": order_id,
        **order
    }, ensure_ascii=False)


@tool
def get_international_order_status(order_id: str) -> str:
    """Yurt dışı bir siparişin mevcut kargo durumunu getirir."""

    print(f"\n[TOOL] get_international_order_status({order_id})")

    orders = load_json("international_orders.json")
    order = orders.get(order_id)

    if order is None:
        return json.dumps({
            "order_id": order_id,
            "sonuc": "Sipariş bulunamadı."
        }, ensure_ascii=False)

    return json.dumps({
        "order_id": order_id,
        **order
    }, ensure_ascii=False)