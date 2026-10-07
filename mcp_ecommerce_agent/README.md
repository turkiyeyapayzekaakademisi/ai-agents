# MCP E-Commerce AI Agent

## Final Proje Mimarisi

Bu projede **iki farklı MCP Server** aynı AI Agent tarafından kullanılmaktadır:

- **Filesystem MCP Server:** Hazır MCP Server. Ürün kataloğu dosyasını okur.
- **Database MCP Server:** FastMCP ile geliştirdiğimiz özel MCP Server. SQLite veritabanına erişir.

AI Agent tarafında **Ollama üzerinde çalışan Qwen3:4B** kullanılmaktadır.

```text
                         Kullanıcı
                             │
                             ▼
                        Qwen3:4B
                             │
                 Hangi bilgiye ihtiyacım var?
                             │
             ┌───────────────┴────────────────┐
             │                                │
             ▼                                ▼
      Filesystem MCP                    Database MCP
      Hazır MCP Server                  Custom FastMCP
             │                                │
             │                                │
     ┌───────┼────────┐             ┌─────────┼──────────┐
     ▼       ▼        ▼             ▼         ▼          ▼
    list   search    read          order      stock    shipping
     │       │        │             │          │          │
     └───────┴────────┘             └──────────┴──────────┘
             │                                │
             ▼                                ▼
        urunler.txt                       SQLite
                                      ecommerce.db
             │                                │
             └──────────────┬─────────────────┘
                            ▼
                         Qwen3:4B
                            │
                            ▼
                     Kullanıcı Cevabı
```

Bu yapı sayesinde agent yalnızca hangi **tool'u** kullanacağını değil, hangi **MCP Server üzerindeki tool'un** gerekli olduğunu da seçmektedir.

---

# Projenin Amacı

Bu projede MCP'nin iki temel kullanımını göstermek amaçlanmaktadır:

```text
1. Hazır bir MCP Server kullanmak
2. Kendi MCP Server'ımızı geliştirmek
```

Hazır Filesystem MCP Server:

```text
ürün teknik bilgileri
        ↓
company_files/urunler.txt
```

Custom Database MCP Server:

```text
stok
fiyat
sipariş
kargo ücreti
        ↓
SQLite
```

Böylece aynı ürün hakkında farklı bilgi türleri farklı kaynaklardan alınabilir.

Örneğin:

```text
"MacBook Air M3'ün özellikleri nelerdir?"
                    ↓
             Filesystem MCP
                    ↓
              urunler.txt
```

ancak:

```text
"MacBook Air M3 stokta kaç tane var?"
                    ↓
              Database MCP
                    ↓
                  SQLite
```

---

# Kullanılan Teknolojiler

| Teknoloji | Kullanım |
|---|---|
| Python | Uygulama geliştirme |
| Qwen3:4B | LLM |
| Ollama | Lokal model çalıştırma |
| MCP | Agent ile dış sistemler arasındaki standart iletişim |
| Filesystem MCP Server | Dosya sistemi tool'ları |
| FastMCP | Custom MCP Server geliştirme |
| SQLite | Operasyonel veri kaynağı |
| LangChain | Agent ve MCP entegrasyonu |
| LangGraph | Agent altyapısı |

---

# Proje Klasör Yapısı

```text
mcp_ecommerce_agent/
│
├── requirements.txt
│
├── company_files/
│   └── urunler.txt
│
├── database_mcp/
│   ├── create_database.py
│   ├── database.py
│   ├── server.py
│   └── ecommerce.db
│
└── agent/
    └── main.py
```

Dosyaların görevleri:

| Dosya | Görevi |
|---|---|
| `company_files/urunler.txt` | Ürünlerin teknik özelliklerini tutar |
| `create_database.py` | SQLite database ve örnek verileri oluşturur |
| `database.py` | SQLite sorgularını gerçekleştirir |
| `server.py` | Database fonksiyonlarını MCP tool olarak sunar |
| `agent/main.py` | İki MCP Server'a bağlanan Qwen agent'ını çalıştırır |
| `requirements.txt` | Gerekli Python paketlerini içerir |

---

# 1. Virtual Environment

Proje klasörüne gir:

```powershell
cd mcp_ecommerce_agent
```

Virtual environment oluştur:

```powershell
python -m venv venv
```

Aktifleştir:

```powershell
.\venv\Scripts\Activate.ps1
```

---

# 2. Ollama Modeli

Qwen3:4B modelini indir:

```powershell
ollama pull qwen3:4b
```

Kontrol:

```powershell
ollama list
```

Listede:

```text
qwen3:4b
```

bulunmalıdır.

---

# 3. Node.js Kontrolü

Hazır Filesystem MCP Server `npx` üzerinden çalıştırılmaktadır.

Kontrol:

```powershell
node --version
npx --version
```

Her iki komutun da bir sürüm numarası döndürmesi gerekir.

---

# 4. Python Paketleri

`requirements.txt`:

```text
langchain[mcp]>=1.4.0
langchain-ollama
langgraph
fastmcp>=4.0.1,<5.0.0
```

Kurulum:

```powershell
pip install -r requirements.txt
```

---

# 5. Filesystem MCP Verisi

Dosya:

```text
company_files/urunler.txt
```

Bu dosya ürünlerin teknik özelliklerini içerir.

Örnek:

```text
ÜRÜN KATALOĞU

1. MacBook Air M3

Ekran:
13.6 inç Liquid Retina

İşlemci:
Apple M3

Bellek:
16 GB RAM

Depolama:
512 GB SSD

Garanti:
2 yıl


2. Dell UltraSharp U2723QE

Ekran:
27 inç

Çözünürlük:
3840 x 2160 4K

Panel:
IPS Black

USB-C güç:
90W

Garanti:
3 yıl


3. Logitech MX Master 3S

Ürün tipi:
Kablosuz mouse

Bağlantı:
Bluetooth
Logi Bolt

Şarj:
USB-C

Uyumluluk:
Windows
macOS

Garanti:
2 yıl
```

Bu dosyaya agent doğrudan Python ile erişmez.

Akış:

```text
Qwen
 ↓
MCP Client
 ↓
Filesystem MCP Server
 ↓
urunler.txt
```

---

# 6. SQLite Database Oluşturma

Database içerisinde üç tablo bulunmaktadır:

```text
products
orders
shipping_prices
```

Örnek veriler:

### products

```text
MacBook Air M3             → 14 adet
Dell UltraSharp U2723QE    → 7 adet
Logitech MX Master 3S      → 32 adet
```

### orders

```text
ORD-1001 → kargoya_verildi
ORD-1002 → hazirlaniyor
ORD-1003 → teslim_edildi
```

### shipping_prices

```text
Germany        → 25 EUR
Netherlands    → 27 EUR
United Kingdom → 30 GBP
USA            → 35 USD
```

Database'i oluştur:

```powershell
python database_mcp/create_database.py
```

Beklenen:

```text
[OK] SQLite database oluşturuldu: ...\ecommerce.db
```

Bu işlem sonunda:

```text
database_mcp/ecommerce.db
```

oluşur.

---

# 7. Custom Database MCP Server

`database_mcp/server.py` içerisinde üç MCP Tool bulunmaktadır:

```text
get_order_status(order_id)
get_product_stock(product_name)
get_shipping_price(country)
```

Bunların arkasında doğrudan SQLite sorguları çalışmaktadır.

Örneğin:

```text
get_product_stock("MacBook Air M3")
        ↓
SQLite
        ↓
SELECT ...
FROM products
        ↓
14 adet
```

Burada RAG kullanılmamaktadır.

Bu doğrudan veritabanı sorgusudur.

---

# 8. Database MCP Server'ı Çalıştırma

Bir terminal aç:

```powershell
cd mcp_ecommerce_agent
.\venv\Scripts\Activate.ps1
python database_mcp/server.py
```

Server çalıştığında MCP endpoint:

```text
http://127.0.0.1:8000/mcp
```

olur.

Bu terminal açık kalmalıdır.

Tarayıcıdan `/mcp` adresine doğrudan girildiğinde:

```json
{
  "jsonrpc": "2.0",
  "id": null,
  "error": {
    "code": -32600,
    "message": "Bad Request: Missing session ID"
  }
}
```

gibi bir cevap görülmesi normaldir.

Çünkü bu adres normal web sayfası değildir.

MCP Client önce gerekli MCP oturumunu oluşturur ve protokol mesajlarını gönderir.

---

# 9. Hazır Filesystem MCP Server

Filesystem MCP Server'ı ayrıca elle başlatmamıza gerek yoktur.

Agent çalıştırıldığında:

```text
npx
 ↓
@modelcontextprotocol/server-filesystem
```

otomatik olarak başlatılır.

Server yalnızca:

```text
company_files/
```

klasörüne erişebilir.

Agent tarafında özellikle read-only ağırlıklı tool'lar kullanılmaktadır:

```text
list_allowed_directories
list_directory
search_files
read_text_file
```

---

# 10. Agent'ın Görebildiği Tool'lar

Agent iki MCP Server'a bağlandığında tool'lar tek tool havuzunda görünür.

Örneğin:

```text
filesystem_list_allowed_directories
filesystem_list_directory
filesystem_search_files
filesystem_read_text_file

database_get_order_status
database_get_product_stock
database_get_shipping_price
```

Tool isimlerindeki:

```text
filesystem_
```

ve:

```text
database_
```

bölümleri hangi MCP Server'dan geldiklerini gösterir.

---

# 11. Agent Tool Seçimini Nasıl Yapıyor?

Qwen3:4B tool açıklamalarını görür.

Örneğin kullanıcı:

```text
MacBook Air M3'ün özellikleri neler?
```

dediğinde agent teknik bilgilerin dosyada bulunduğunu bilir ve:

```text
filesystem_read_text_file
```

kullanabilir.

Ancak:

```text
MacBook Air M3 stokta kaç tane var?
```

dediğinde:

```text
database_get_product_stock
```

seçer.

Tool seçimi Python tarafında:

```python
if "stok" in soru:
```

şeklinde hard-code edilmemiştir.

Kararı LLM verir.

---

# 12. Agent'ı Çalıştırma

Database MCP Server açıkken ikinci bir terminal aç:

```powershell
cd mcp_ecommerce_agent
.\venv\Scripts\Activate.ps1
python agent/main.py
```

Başlangıçta MCP üzerinden bulunan tool'lar listelenmelidir.

Yaklaşık:

```text
MCP üzerinden bulunan tool'lar:

- filesystem_list_allowed_directories
- filesystem_list_directory
- filesystem_search_files
- filesystem_read_text_file
- database_get_order_status
- database_get_product_stock
- database_get_shipping_price
```

---

# Çalıştırma Sırası

İlk kurulumda:

```text
1. Ollama modelini indir
        ↓
2. Python paketlerini kur
        ↓
3. SQLite database oluştur
        ↓
4. Database MCP Server'ı başlat
        ↓
5. AI Agent'ı başlat
```

Komutlar:

```powershell
ollama pull qwen3:4b
```

```powershell
pip install -r requirements.txt
```

```powershell
python database_mcp/create_database.py
```

Terminal 1:

```powershell
python database_mcp/server.py
```

Terminal 2:

```powershell
python agent/main.py
```

Sonraki çalıştırmalarda `create_database.py` tekrar çalıştırılmak zorunda değildir.

Normal kullanım:

```text
1. Database MCP Server
2. Agent
```

---

# Test 1 — Ürün Listesi

Sor:

```text
Ürün kataloğunda hangi ürünler var?
```

Beklenen veri kaynağı:

```text
Filesystem MCP
```

Beklenen cevap:

```text
Ürün kataloğunda:

- MacBook Air M3
- Dell UltraSharp U2723QE
- Logitech MX Master 3S

bulunmaktadır.
```

---

# Test 2 — Teknik Özellik

Sor:

```text
MacBook Air M3'ün özellikleri neler?
```

Beklenen akış:

```text
Qwen3
 ↓
Filesystem MCP
 ↓
read_text_file
 ↓
urunler.txt
 ↓
Qwen3
```

Beklenen cevap yaklaşık:

```text
MacBook Air M3:

- Apple M3 işlemci
- 13.6 inç Liquid Retina ekran
- 16 GB RAM
- 512 GB SSD
- 2 yıl garanti
```

---

# Test 3 — Stok

Sor:

```text
MacBook Air M3 stokta kaç tane var?
```

Bu kez Filesystem MCP kullanılmamalıdır.

Beklenen:

```text
Database MCP
 ↓
get_product_stock()
 ↓
SQLite
```

Database Server terminalinde:

```text
[MCP TOOL] get_product_stock(MacBook Air M3)
```

görülmelidir.

Beklenen cevap:

```text
MacBook Air M3 stokta 14 adet bulunmaktadır.
```

---

# Test 4 — Fiyat ve Stok

Sor:

```text
Dell UltraSharp U2723QE'nin güncel fiyatı ve stoğu nedir?
```

Beklenen tool:

```text
database_get_product_stock
```

Beklenen bilgi:

```text
Stok: 7
Fiyat: 28999
```

---

# Test 5 — Aynı Ürün, İki Farklı MCP Server

Önce sor:

```text
MacBook Air M3'ün teknik özellikleri nedir?
```

Beklenen:

```text
Filesystem MCP
```

Sonra sor:

```text
MacBook Air M3'ün güncel fiyatı ve stoğu nedir?
```

Beklenen:

```text
Database MCP
```

Bu test projenin ana fikrini göstermektedir:

```text
                  MacBook Air M3
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
      Teknik özellik         Güncel veri
             │                   │
      Filesystem MCP         Database MCP
             │                   │
       urunler.txt              SQLite
```

---

# Test 6 — Sipariş Durumu

Sor:

```text
ORD-1001 siparişim nerede?
```

Beklenen tool:

```text
database_get_order_status
```

Database MCP Server terminalinde:

```text
[MCP TOOL] get_order_status(ORD-1001)
```

görülmelidir.

Beklenen cevap yaklaşık:

```text
ORD-1001 numaralı siparişiniz kargoya verilmiştir.

Kargo firması: Yurtiçi Kargo
Takip numarası: YK123456
```

---

# Test 7 — Hazırlanan Sipariş

Sor:

```text
ORD-1002 siparişim ne durumda?
```

Beklenen cevap:

```text
ORD-1002 numaralı siparişiniz hazırlanıyor.
```

Veritabanında kargo firması ve takip numarası bulunmadığı için agent bunları uydurmamalıdır.

---

# Test 8 — Yurt Dışı Gönderim Ücreti

Sor:

```text
Almanya'ya gönderim ücreti ne kadar?
```

Beklenen tool:

```text
database_get_shipping_price
```

Beklenen MCP çağrısı:

```text
get_shipping_price(country="Germany")
```

Beklenen cevap:

```text
Almanya için gönderim ücreti 25 EUR'dur.
```

---

# Filesystem MCP ve Database MCP Arasındaki Fark

## Filesystem MCP

```text
Statik / dokümansal bilgi
```

Örnek:

```text
Ürünün ekranı kaç inç?
Garanti süresi ne?
Hangi bağlantılar var?
```

Kaynak:

```text
urunler.txt
```

---

## Database MCP

```text
Güncel / operasyonel bilgi
```

Örnek:

```text
Stokta kaç adet var?
Güncel fiyat ne?
Sipariş nerede?
Kargo ücreti ne?
```

Kaynak:

```text
SQLite
```

---

# Normal Tool Calling ile MCP Arasındaki Fark

Normal tool calling:

```text
Agent
 ↓
Python Function
```

Tool çoğunlukla doğrudan agent projesinin içerisindedir.

MCP:

```text
Agent
 ↓
MCP Client
 ↓
MCP Server
 ↓
Tool
 ↓
Gerçek sistem
```

Bu projede:

```text
Qwen Agent
    │
    ├── Filesystem MCP Server
    │       ↓
    │   urunler.txt
    │
    └── Database MCP Server
            ↓
          SQLite
```

şeklinde iki ayrı MCP Server kullanılmaktadır.

---

# Neden İki MCP Server?

Bu tasarım eğitim açısından iki farklı MCP kullanımını göstermektedir.

### 1. Hazır MCP Server

```text
Filesystem MCP
```

Hazır bir entegrasyonu doğrudan kullanıyoruz.

### 2. Custom MCP Server

```text
Database MCP
```

FastMCP kullanarak kendi MCP Server'ımızı geliştiriyoruz.

Bu sayede hem:

```text
MCP Server tüketme
```

hem de:

```text
MCP Server geliştirme
```

aynı projede gösterilmektedir.

---

# MCP'nin Projedeki Rolleri

```text
Qwen3:4B
→ hangi tool'un gerekli olduğuna karar verir

MCP Client
→ MCP Server'lara bağlanır

Filesystem MCP Server
→ dosya sistemi tool'larını sunar

Database MCP Server
→ bizim business tool'larımızı sunar

SQLite
→ gerçek operasyonel veriyi tutar

urunler.txt
→ ürün teknik bilgilerini tutar
```

---

# Final Özet

Bu projede:

```text
1 AI Agent
+
2 MCP Server
+
7 seçilmiş MCP Tool
+
1 SQLite Database
+
1 Local File
```

kullanılmaktadır.

En önemli mimari:

```text
                    Qwen3:4B
                        │
                Tool Selection
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
     Filesystem MCP           Database MCP
       hazır server            custom server
            │                       │
      urunler.txt                 SQLite
```

Kullanıcı yalnızca doğal dilde isteğini belirtir.

Agent:

1. İhtiyacı değerlendirir.
2. Uygun MCP tool'unu seçer.
3. Gerekli MCP Server'a çağrı yapar.
4. Gerçek veriyi alır.
5. Tool sonucunu değerlendirir.
6. Kullanıcıya nihai cevabı üretir.

Böylece MCP'nin temel amacı olan **AI uygulamalarının harici tool ve veri kaynaklarına standart bir protokol üzerinden bağlanması** gerçek bir proje üzerinde gösterilmiş olur.