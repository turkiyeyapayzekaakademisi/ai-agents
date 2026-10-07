"""
Bu uygulama Qwen3:4B tabanlı bir AI Agent oluşturur.

Agent iki farklı MCP Server kullanır:

1. Filesystem MCP Server
    Hazır MCP Server'dır.
    urunler.txt dosyasına erişir.

2. Database MCP Server
    FastMCP ile bizim oluşturduğumuz server'dır.
    SQLite içerisindeki sipariş, stok ve kargo bilgilerine erişir.

Agent kullanıcının isteğine göre hangi MCP Server'daki
hangi tool'u kullanacağına kendisi karar verir.
"""

import asyncio
import os
from pathlib import Path

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_ollama import ChatOllama


BASE_PATH = Path(__file__).resolve().parent.parent
FILES_PATH = BASE_PATH / "company_files"


SYSTEM_PROMPT = """
Sen bir e-ticaret müşteri hizmetleri AI agentısın.

İki farklı MCP Server tarafından sağlanan tool'lara erişebilirsin.

FILESYSTEM MCP:
Ürünlerin teknik özellikleri ve ürün kataloğu company_files/urunler.txt
dosyasında bulunmaktadır.

Ürün özellikleri, bağlantıları, garanti süresi veya teknik detaylar
sorulursa Filesystem MCP tool'larını kullan.

Dosyanın tam yolunu bilmiyorsan önce filesystem_list_allowed_directories
tool'unu kullan. Ardından urunler.txt dosyasını filesystem_read_text_file
ile oku.

DATABASE MCP:
Güncel operasyonel bilgiler SQLite database içerisinde bulunmaktadır.

Sipariş durumu için:
database_get_order_status

Güncel stok ve fiyat için:
database_get_product_stock

Yurt dışı gönderim ücreti için:
database_get_shipping_price

Kurallar:
- Şirket veya ürün bilgisi uydurma.
- Gerekli bilgi bir MCP tool ile alınabiliyorsa mutlaka tool kullan.
- Ürün teknik özellikleri için filesystem kullan.
- Stok, fiyat, sipariş ve gönderim ücreti için database kullan.
- Tool sonucundaki bilgileri değiştirme.
- Türkçe ve kısa cevap ver.
"""


def filesystem_server_config() -> dict:
    """İşletim sistemine göre Filesystem MCP Server config oluşturur."""

    if os.name == "nt":
        return {
            "command": "cmd",
            "args": [
                "/c",
                "npx",
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(FILES_PATH)
            ]
        }

    return {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            str(FILES_PATH)
        ]
    }


async def main() -> None:
    mcp_config = {
        "mcpServers": {
            "filesystem": filesystem_server_config(),
            "database": {
                "url": "http://127.0.0.1:8000/mcp"
            }
        }
    }

    async with MCPAdapter(mcp_config) as adapter:
        all_tools = await adapter.list_tools()

        allowed_tools = {
            "filesystem_list_allowed_directories",
            "filesystem_list_directory",
            "filesystem_search_files",
            "filesystem_read_text_file",
            "database_get_order_status",
            "database_get_product_stock",
            "database_get_shipping_price"
        }

        tools = [
            tool
            for tool in all_tools
            if tool.name in allowed_tools
        ]

        print("\nMCP üzerinden bulunan tool'lar:")

        for tool in tools:
            print(f"- {tool.name}")

        llm = ChatOllama(
            model="qwen3:4b",
            temperature=0
        )

        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=SYSTEM_PROMPT
        )

        messages = []

        print("\nMCP E-Commerce Agent")
        print("Çıkmak için 'exit' yazın.\n")

        while True:
            user_input = input("Kullanıcı: ")

            if user_input.lower() == "exit":
                break

            messages.append(
                {
                    "role": "user",
                    "content": user_input
                }
            )

            previous_message_count = len(messages)

            result = await agent.ainvoke(
                {
                    "messages": messages
                }
            )

            messages = result["messages"]

            print("\nAgent:", messages[-1].content)
            print()


if __name__ == "__main__":
    asyncio.run(main())