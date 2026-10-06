# Multi-Agent Müşteri Hizmetleri Sistemi

Bu projede **LangGraph**, **Ollama**, **Qwen3:4B**, **FAISS** ve **Qwen3-Embedding-0.6B** kullanılarak Multi-Agent bir müşteri hizmetleri sistemi geliştirilmektedir.

Sistemde bir **Supervisor Agent** ve üç farklı uzman agent bulunmaktadır:

- Greeting Agent
- FAQ Agent
- Order Agent

Supervisor Agent, kullanıcının mesajını değerlendirerek hangi uzman agent'ın çalışacağına karar verir.

Uzman agent'lar ise gerektiğinde kendi tool'larını seçerek kullanır.

Projede ayrıca LangGraph üzerinden **conversation memory** kullanılmaktadır.

---

# Projenin Amacı

Bu proje ile aşağıdaki kavramların birlikte kullanılması amaçlanmaktadır:

- Multi-Agent Architecture
- Supervisor Agent
- Specialized Agents
- LangGraph State
- Node
- Edge
- Conditional Edge
- Agent Routing
- Tool Calling
- Agent Loop
- RAG
- Embedding
- FAISS Vector Database
- Conversation Memory
- Thread

---

# Genel Mimari

Sistemin temel çalışma yapısı:

```text
                         Kullanıcı
                             │
                             ▼
                           START
                             │
                             ▼
                    ┌─────────────────┐
                    │ Supervisor Agent│
                    │    Qwen3:4B     │
                    └────────┬────────┘
                             │
                      Conditional Edge
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       Greeting Agent     FAQ Agent      Order Agent
              │              │              │
              │              ▼              ▼
              │         Tool gerekli?   Tool gerekli?
              │          ┌────┴────┐     ┌────┴────┐
              │          │         │     │         │
              │         EVET      HAYIR EVET      HAYIR
              │          │         │     │         │
              │          ▼         │     ▼         │
              │      FAQ Tools     │ Order Tools   │
              │          │         │     │         │
              │          └──► FAQ Agent  └──► Order Agent
              │                ↺              ↺
              │
              ▼                ▼              ▼
             END              END            END
```

---

# Agent Yapısı

## Supervisor Agent

Supervisor Agent doğrudan müşteri sorusunu çözmez.

Görevi kullanıcı mesajını aşağıdaki üç agent'tan birine yönlendirmektir:

```text
greeting
faq
order
```

Örnek:

```text
Merhaba
→ Greeting Agent
```

```text
Fiyatlara KDV dahil mi?
→ FAQ Agent
```

```text
ORD-1001 yurt içi siparişim nerede?
→ Order Agent
```

---

## Greeting Agent

Selamlama, teşekkür ve vedalaşma mesajlarından sorumludur.

Tool kullanmaz.

Örnek:

```text
Merhaba
```

↓

```text
Merhaba, size nasıl yardımcı olabilirim?
```

---

## FAQ Agent

Şirket hakkında genel ve teknik sorulardan sorumludur.

İki RAG tool kullanabilir:

```text
search_general_faq()
search_technical_faq()
```

Agent kullanıcının sorusuna göre hangi bilgi kaynağını kullanacağına karar verir.

### Genel FAQ

Örnek konular:

```text
KDV
Kargo ücreti
İade
Ödeme
Yurt dışı gönderim
```

Veri kaynağı:

```text
general_faq.json
       ↓
Embedding
       ↓
FAISS
```

### Teknik FAQ

Örnek konular:

```text
Şifre
Giriş problemi
API
Mobil uygulama
İki faktörlü doğrulama
```

Veri kaynağı:

```text
technical_faq.json
       ↓
Embedding
       ↓
FAISS
```

---

## Order Agent

Sipariş ve kargo sorgularından sorumludur.

İki tool kullanabilir:

```text
get_domestic_order_status()
get_international_order_status()
```

Kullanıcı:

```text
ORD-1001 yurt içi siparişim nerede?
```

derse:

```text
get_domestic_order_status()
```

kullanılır.

Kullanıcı:

```text
ORD-2001 yurt dışı siparişim nerede?
```

derse:

```text
get_international_order_status()
```

kullanılır.

Siparişin yurt içi mi yurt dışı mı olduğu belirtilmemişse agent tahmin yapmaz.

Örneğin:

```text
ORD-1002 siparişim nerede?
```

Agent:

```text
Siparişiniz yurt içi mi yoksa yurt dışı mı?
```

diye sorar.

---

# LangGraph Node Yapısı

Projede altı temel node bulunmaktadır:

```text
1. supervisor
2. greeting_agent
3. faq_agent
4. faq_tools
5. order_agent
6. order_tools
```

Graph bağlantıları:

```text
START
  │
  ▼
supervisor
  │
  ├──────── greeting ───────► greeting_agent ─────► END
  │
  ├──────── faq ────────────► faq_agent
  │                              │
  │                         Tool Call?
  │                         │        │
  │                        EVET     HAYIR
  │                         │        │
  │                         ▼        ▼
  │                     faq_tools   END
  │                         │
  │                         └────► faq_agent
  │                                ↺
  │
  └──────── order ──────────► order_agent
                                 │
                            Tool Call?
                            │        │
                           EVET     HAYIR
                            │        │
                            ▼        ▼
                       order_tools  END
                            │
                            └────► order_agent
                                   ↺
```

FAQ ve Order tarafındaki dönüşler **Agent Loop** oluşturur.

Tool sonucu tekrar agent'a gönderilir ve model sonucu değerlendirerek nihai cevabı üretir.

---

# State

Multi-Agent sistemde ortak bir LangGraph State kullanılmaktadır.

```python
class CustomerServiceState(MessagesState):
    route: NotRequired[str]
    last_agent: NotRequired[str]
```

Temel alanlar:

```text
messages
route
last_agent
```

### messages

Kullanıcı ve agent mesajlarının geçmişini tutar.

### route

Supervisor'ın seçtiği agent'ı tutar.

Örneğin:

```text
faq
```

### last_agent

En son çalışan uzman agent'ı tutar.

Örneğin:

```text
order
```

Bu bilgi özellikle kısa follow-up mesajlarının doğru agent'a yönlendirilmesine yardımcı olur.

---

# Conversation Memory

Projede:

```text
InMemorySaver
+
thread_id
```

kullanılmaktadır.

Örneğin:

```python
config = {
    "configurable": {
        "thread_id": "customer-1"
    }
}
```

Aynı `thread_id` kullanıldığı sürece önceki konuşmalar korunur.

Örneğin:

```text
Kullanıcı:
ORD-1002 siparişim nerede?

Agent:
Siparişiniz yurt içi mi yoksa yurt dışı mı?

Kullanıcı:
Yurt içi.
```

İkinci mesajda kullanıcı tekrar:

```text
ORD-1002
```

yazmamıştır.

Agent sipariş numarasını conversation memory içerisinden kullanabilir.

---

# Proje Klasör Yapısı

```text
multi_agent_customer_service/
│
├── 01_create_vector_dbs.py
├── 02_multi_agent_customer_service.py
├── config.py
├── state.py
├── requirements.txt
│
├── agents/
│   ├── __init__.py
│   ├── supervisor_agent.py
│   ├── greeting_agent.py
│   ├── faq_agent.py
│   └── order_agent.py
│
├── tools/
│   ├── __init__.py
│   ├── faq_tools.py
│   └── order_tools.py
│
├── data/
│   ├── general_faq.json
│   ├── technical_faq.json
│   ├── domestic_orders.json
│   └── international_orders.json
│
└── vector_db/
    ├── general_faq/
    └── technical_faq/
```

---

# Dosyaların Görevleri

| Dosya | Görevi |
|---|---|
| `01_create_vector_dbs.py` | FAQ JSON dosyalarından FAISS veritabanlarını oluşturur |
| `02_multi_agent_customer_service.py` | LangGraph Multi-Agent sistemini çalıştırır |
| `config.py` | LLM ve embedding modellerini tanımlar |
| `state.py` | Ortak LangGraph State yapısını tanımlar |
| `supervisor_agent.py` | Agent routing işlemini gerçekleştirir |
| `greeting_agent.py` | Selamlama mesajlarını cevaplar |
| `faq_agent.py` | FAQ tool'larını seçer ve RAG cevabı üretir |
| `order_agent.py` | Sipariş tool'larını seçer |
| `faq_tools.py` | İki FAISS veritabanında retrieval yapar |
| `order_tools.py` | Yurt içi ve yurt dışı JSON siparişlerini sorgular |

---

# Kurulum

## 1. Proje Klasörüne Gir

```bash
cd multi_agent_customer_service
```

---

## 2. Virtual Environment Oluştur

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Requirements

`requirements.txt`:

```text
langgraph
langchain-core
langchain-ollama
langchain-community
faiss-cpu
```

Kur:

```bash
pip install -r requirements.txt
```

---

# Ollama Modelleri

LLM:

```bash
ollama pull qwen3:4b
```

Embedding modeli:

```bash
ollama pull qwen3-embedding:0.6b
```

Kontrol:

```bash
ollama list
```

Listede şu modeller bulunmalıdır:

```text
qwen3:4b
qwen3-embedding:0.6b
```

---

# FAISS Vector Database

FAQ Agent doğrudan JSON içerisinde arama yapmaz.

Öncelikle JSON içerisindeki bilgiler embedding'e dönüştürülerek FAISS içerisine kaydedilir.

Akış:

```text
general_faq.json
       ↓
Qwen3-Embedding-0.6B
       ↓
Embedding
       ↓
FAISS
       ↓
vector_db/general_faq/
```

Aynı işlem teknik sorular için de yapılır:

```text
technical_faq.json
       ↓
Qwen3-Embedding-0.6B
       ↓
Embedding
       ↓
FAISS
       ↓
vector_db/technical_faq/
```

---

# Dosyaları Çalıştırma Sırası

## 1. Modelleri İndir

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

---

## 2. Python Paketlerini Kur

```bash
pip install -r requirements.txt
```

---

## 3. FAISS Veritabanlarını Oluştur

Bu işlem ilk çalıştırmada yapılmalıdır:

```bash
python 01_create_vector_dbs.py
```

Beklenen:

```text
[OK] general_faq oluşturuldu.
[OK] technical_faq oluşturuldu.
```

Sonrasında:

```text
vector_db/
├── general_faq/
│   ├── index.faiss
│   └── index.pkl
│
└── technical_faq/
    ├── index.faiss
    └── index.pkl
```

oluşmalıdır.

FAQ JSON dosyaları değişirse bu script tekrar çalıştırılmalıdır.

---

## 4. Multi-Agent Sistemini Çalıştır

```bash
python 02_multi_agent_customer_service.py
```

Terminal:

```text
Multi-Agent Müşteri Hizmetleri
Çıkmak için 'exit' yazın.

Kullanıcı:
```

şeklinde giriş bekler.

---

# Test Sırası

Testleri aşağıdaki sırayla yapmak önerilir.

---

# Test 1 — Greeting Agent

Sor:

```text
Merhaba
```

Beklenen terminal akışı:

```text
[SUPERVISOR] → greeting
[AGENT] Greeting Agent
```

Beklenen cevap yaklaşık olarak:

```text
Merhaba, size nasıl yardımcı olabilirim?
```

Bu test:

```text
Supervisor Routing
+
Greeting Agent
```

yapısını gösterir.

---

# Test 2 — General FAQ RAG

Sor:

```text
Fiyatlara KDV dahil mi?
```

Beklenen terminal:

```text
[SUPERVISOR] → faq
[AGENT] FAQ Agent

[TOOL] search_general_faq(...)
```

Beklenen cevap:

```text
Evet, web sitesinde gösterilen tüm ürün fiyatlarına KDV dahildir.
```

Buradaki akış:

```text
Supervisor
   ↓
FAQ Agent
   ↓
General FAQ Tool
   ↓
General FAISS DB
   ↓
FAQ Agent
   ↓
Cevap
```

---

# Test 3 — Farklı Bir General FAQ

Sor:

```text
Kargo ücretsiz mi?
```

Beklenen:

```text
1500 TL ve üzeri siparişlerde kargo ücretsizdir.
Daha düşük siparişlerde 79 TL kargo ücreti uygulanır.
```

Yine:

```text
search_general_faq()
```

kullanılmalıdır.

---

# Test 4 — Technical FAQ RAG

Sor:

```text
Şifremi nasıl sıfırlarım?
```

Beklenen terminal:

```text
[SUPERVISOR] → faq
[AGENT] FAQ Agent

[TOOL] search_technical_faq(...)
```

Beklenen cevap yaklaşık olarak:

```text
Giriş ekranındaki Şifremi Unuttum bağlantısını kullanarak
kayıtlı e-posta adresinize şifre sıfırlama bağlantısı gönderebilirsiniz.
```

Burada aynı FAQ Agent farklı bir tool seçmiştir.

```text
FAQ Agent
   ↓
Technical FAQ Tool
   ↓
Technical FAISS
```

---

# Test 5 — Technical FAQ / API

Sor:

```text
API erişimi sağlıyor musunuz?
```

Beklenen:

```text
Kurumsal müşteriler için REST API erişimi sunulmaktadır.
```

Kullanılması gereken tool:

```text
search_technical_faq()
```

---

# Test 6 — Yurt İçi Sipariş

Sor:

```text
ORD-1001 yurt içi siparişim nerede?
```

Beklenen terminal:

```text
[SUPERVISOR] → order
[AGENT] Order Agent

[TOOL] get_domestic_order_status(ORD-1001)
```

Beklenen cevap:

```text
ORD-1001 numaralı siparişiniz kargoya verilmiştir.

Kargo firması: Yurtiçi Kargo
Takip numarası: YK123456
Hedef: Ankara
```

Cevap metni birebir aynı olmak zorunda değildir.

Veriler tool sonucuyla uyumlu olmalıdır.

---

# Test 7 — Yurt Dışı Sipariş

Sor:

```text
ORD-2001 yurt dışı siparişim nerede?
```

Beklenen terminal:

```text
[SUPERVISOR] → order
[AGENT] Order Agent

[TOOL] get_international_order_status(ORD-2001)
```

Beklenen bilgi:

```text
Durum: transit
Kargo firması: DHL
Takip numarası: DHL987654
Hedef: Germany
```

Bu test Order Agent'ın ikinci tool'u seçebildiğini gösterir.

---

# Test 8 — Eksik Bilgi

Şimdi memory kullanımını göstermek için:

```text
ORD-1002 siparişim nerede?
```

sor.

Yurt içi veya yurt dışı bilgisi verilmediği için Order Agent'ın tool çağırmaması gerekir.

Beklenen cevap:

```text
Siparişiniz yurt içi mi yoksa yurt dışı mı?
```

---

# Test 9 — Conversation Memory

Bir önceki testi yaptıktan hemen sonra:

```text
Yurt içi.
```

yaz.

Agent conversation history içerisinde:

```text
ORD-1002
```

sipariş numarasını görebilmelidir.

Beklenen terminal:

```text
[SUPERVISOR] → order
[AGENT] Order Agent

[TOOL] get_domestic_order_status(ORD-1002)
```

Beklenen cevap:

```text
ORD-1002 numaralı siparişiniz hazırlanıyor.
```

Bu test:

```text
Conversation Memory
+
Follow-up Question
+
Tool Calling
```

yapısını gösterir.

---

# Testlerin Özeti

| Test | Soru | Beklenen Agent / Tool |
|---|---|---|
| 1 | `Merhaba` | Greeting Agent |
| 2 | `Fiyatlara KDV dahil mi?` | FAQ → General RAG |
| 3 | `Kargo ücretsiz mi?` | FAQ → General RAG |
| 4 | `Şifremi nasıl sıfırlarım?` | FAQ → Technical RAG |
| 5 | `API erişimi var mı?` | FAQ → Technical RAG |
| 6 | `ORD-1001 yurt içi siparişim nerede?` | Order → Domestic Tool |
| 7 | `ORD-2001 yurt dışı siparişim nerede?` | Order → International Tool |
| 8 | `ORD-1002 siparişim nerede?` | Order → Bilgi ister |
| 9 | `Yurt içi.` | Order → Domestic Tool + Memory |

---

# Projedeki Karar Seviyeleri

Projede iki farklı seviyede karar verilmektedir.

## 1. Agent Seçimi

Supervisor:

```text
Greeting
FAQ
Order
```

arasından seçim yapar.

## 2. Tool Seçimi

FAQ Agent:

```text
General FAQ Tool
Technical FAQ Tool
```

arasından seçim yapar.

Order Agent:

```text
Domestic Order Tool
International Order Tool
```

arasından seçim yapar.

Bu nedenle sistem yalnızca Multi-Agent değildir.

Aynı zamanda uzman agent'ların kendi içerisinde **tool selection** yaptığı agentic bir yapıdır.

---

# Final Mimari Özeti

```text
1 Supervisor Agent

3 Specialist Agent
├── Greeting Agent
├── FAQ Agent
└── Order Agent

4 Tool
├── search_general_faq()
├── search_technical_faq()
├── get_domestic_order_status()
└── get_international_order_status()

2 FAISS Vector Database
├── General FAQ
└── Technical FAQ

2 JSON Sipariş Database
├── Domestic Orders
└── International Orders

1 Shared LangGraph State

1 Conversation Memory

1 Qwen3:4B LLM

1 Qwen3-Embedding-0.6B Embedding Model
```

Projenin genel akışı:

```text
Kullanıcı
   ↓
Supervisor
   ↓
Specialist Agent
   ↓
Gerekirse Tool
   ↓
Gerçek Veri / Retrieval
   ↓
Specialist Agent
   ↓
Cevap
```

Böylece **LangGraph tabanlı routing, Multi-Agent mimarisi, RAG, tool calling, FAISS ve conversation memory** tek bir müşteri hizmetleri projesi içerisinde birlikte uygulanmış olur.