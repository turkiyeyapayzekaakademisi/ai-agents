# Temel AI Agent Uygulaması

Bu projede **Ollama üzerinde lokal çalışan Qwen3:4B modeli** kullanılarak temel bir AI Agent uygulaması geliştirilmektedir.

Projenin amacı; bir Large Language Model'in yalnızca cevap üretmesi yerine, kullanıcı hedefini anlaması, uygun tool'ları seçmesi, tool sonuçlarını gözlemlemesi ve gerektiğinde yeni aksiyonlar almasıyla oluşan **agentic çalışma yapısını** göstermektir.

Proje kapsamında basit bir **Sipariş Yönetim Agent'ı** geliştirilmektedir.

---

# Proje Senaryosu

Sistemde bazı örnek siparişler bulunmaktadır.

Kullanıcı doğal dilde sipariş durumunu sorgulayabilir:

```text
ORD-1001 siparişimin durumunu kontrol et.
```

veya koşullu bir işlem isteyebilir:

```text
ORD-1001 siparişim henüz kargoya verilmediyse iptal et.
```

Agent'ın kullanabileceği iki tool bulunmaktadır:

```text
get_order_status
cancel_order
```

Agent hangi tool'un ne zaman kullanılacağına kullanıcı isteğine ve önceki tool sonuçlarına göre karar verir.

---

# Agentic Çalışma Mantığı

Bu uygulama yalnızca tek bir LLM çağrısından oluşmaz.

Temel çalışma akışı:

```text
Kullanıcı
   ↓
Qwen3:4B
   ↓
Karar
   ↓
Tool Call
   ↓
Python Tool
   ↓
Tool Result
   ↓
Qwen3:4B
   ↓
Yeni karar
   ↓
Gerekirse yeni Tool Call
   ↓
Final Structured Output
```

Örneğin kullanıcı:

```text
ORD-1001 siparişim henüz kargoya verilmediyse iptal et.
```

dediğinde agent şu şekilde ilerleyebilir:

```text
Kullanıcı isteği
       ↓
get_order_status("ORD-1001")
       ↓
hazirlaniyor
       ↓
Qwen3 sonucu değerlendirir
       ↓
cancel_order("ORD-1001")
       ↓
iptal_edildi
       ↓
Final cevap
```

Burada ikinci tool çağrısı Python kodunda sabit olarak tanımlanmamıştır.

Qwen3, ilk tool sonucunu gördükten sonra yeni bir karar verir.

Bu nedenle uygulama **agentic bir yapıdır**.

---

# Kullanılan Teknolojiler

- Python
- Ollama
- Qwen3:4B
- Ollama Python SDK
- Pydantic
- Function Calling / Tool Calling
- Agent Loop
- Structured Output

Bu projede herhangi bir bulut LLM API'si kullanılmamaktadır.

Model tamamen lokal olarak Ollama üzerinde çalışmaktadır.

---

# Proje Yapısı

```text
temel_ai_agent_uygulamasi/
│
├── main.py
├── models.py
├── tools.py
├── requirements.txt
├── README.md
│
└── data/
    └── orders.json
```

Dosyaların görevleri:

| Dosya | Görevi |
|---|---|
| `main.py` | Qwen3 modelini çalıştırır ve Agent Loop'u yönetir |
| `models.py` | Structured Output için Pydantic modelini tanımlar |
| `tools.py` | Agent'ın kullanabileceği Python tool'larını içerir |
| `data/orders.json` | Örnek sipariş verilerini tutar |
| `requirements.txt` | Gerekli Python kütüphanelerini içerir |
| `README.md` | Projenin çalışma mantığını ve kurulumunu açıklar |

---

# 1. Ollama Kurulumu

Öncelikle bilgisayarda Ollama kurulu ve çalışıyor olmalıdır.

Qwen3:4B modelini indir:

```bash
ollama pull qwen3:4b
```

Kurulu modelleri kontrol et:

```bash
ollama list
```

Listede:

```text
qwen3:4b
```

modelini görmelisin.

Modeli doğrudan test etmek için:

```bash
ollama run qwen3:4b
```

kullanılabilir.

---

# 2. Virtual Environment

Proje klasörüne gir:

```bash
cd temel_ai_agent_uygulamasi
```

Virtual environment oluştur:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
venv\Scripts\activate
```

Aktif olduğunda terminal başında genellikle:

```text
(venv)
```

görülür.

---

# 3. Gerekli Kütüphaneler

`requirements.txt`:

```text
ollama
pydantic
```

Kurulum:

```bash
pip install -r requirements.txt
```

---

# 4. Sipariş Verileri

Siparişler:

```text
data/orders.json
```

dosyasında tutulmaktadır.

Örnek:

```json
{
  "ORD-1001": {
    "urun": "Laptop Standı",
    "durum": "hazirlaniyor"
  },
  "ORD-1002": {
    "urun": "Monitör",
    "durum": "kargoya_verildi"
  },
  "ORD-1003": {
    "urun": "Mekanik Klavye",
    "durum": "hazirlaniyor"
  }
}
```

Projede kullanılan temel sipariş durumları:

```text
hazirlaniyor
kargoya_verildi
iptal_edildi
```

---

# 5. Function Tools

Agent'ın kullanabileceği iki Python fonksiyonu bulunmaktadır.

## get_order_status

Siparişin mevcut durumunu gerçek veri kaynağından getirir.

```text
get_order_status(order_id)
```

Örneğin:

```text
get_order_status("ORD-1001")
```

tool sonucu:

```json
{
  "order_id": "ORD-1001",
  "urun": "Laptop Standı",
  "status": "hazirlaniyor"
}
```

---

## cancel_order

Siparişi iptal etmeye çalışır.

```text
cancel_order(order_id)
```

Sipariş:

```text
hazirlaniyor
```

durumundaysa:

```text
iptal_edildi
```

durumuna geçirilir.

Sipariş:

```text
kargoya_verildi
```

durumundaysa iptal edilmez.

Bu kontrol Python tool'u içerisinde yapılır.

Bu nedenle LLM yanlışlıkla iptal tool'unu çağırsa bile kargoya verilmiş bir sipariş gerçekte iptal edilmez.

---

# 6. Tool Calling

Tool'lar modele:

```python
TOOLS = [
    get_order_status,
    cancel_order
]
```

şeklinde verilir.

Qwen3 kullanıcı isteğine göre hangi tool'un çağrılması gerektiğine karar verir.

Model bir tool çağırmak istediğinde:

```python
response.message.tool_calls
```

içerisinde tool çağrıları oluşur.

Örneğin:

```text
get_order_status
```

ve gerekli parametre:

```text
order_id = ORD-1001
```

model tarafından belirlenir.

---

# 7. Agent Loop

Agent Loop uygulamanın en önemli bölümüdür.

Temel yapı:

```python
for _ in range(MAX_STEPS):
```

ile yönetilir.

Her turda model çalıştırılır:

```python
response = chat(
    model=MODEL,
    messages=messages,
    tools=TOOLS,
    think=False
)
```

Model bir tool çağırmak isterse:

```python
response.message.tool_calls
```

kontrol edilir.

Tool çalıştırılır:

```text
Model
 ↓
Tool Call
 ↓
Python Function
```

ve tool sonucu tekrar modele gönderilir:

```text
Python Function
 ↓
Tool Result
 ↓
Qwen3
```

Qwen3 bu yeni bilgiyi gördükten sonra bir sonraki aksiyona karar verir.

Bu işlem görev tamamlanana kadar devam edebilir.

---

# 8. MAX_STEPS

Agent Loop:

```python
MAX_STEPS = 5
```

ile sınırlandırılmıştır.

Bu sınır, modelin gereksiz şekilde sürekli tool çağırarak:

```text
Model
 ↓
Tool
 ↓
Model
 ↓
Tool
 ↓
Model
 ↓
Tool
 ↓
...
```

şeklinde sonsuz veya gereksiz bir döngü oluşturmasını engeller.

Bu yapı agent sistemlerindeki **Execution Limit** kavramının basit bir örneğidir.

---

# 9. Structured Output

Agent görevi tamamladıktan sonra kullanıcıya serbest metin yerine belirli bir veri yapısında cevap üretir.

`models.py` içerisinde:

```python
class OrderResult(BaseModel):
    order_id: str
    status: Literal[
        "hazirlaniyor",
        "kargoya_verildi",
        "iptal_edildi",
        "bulunamadi"
    ]
    message: str
```

tanımlanmıştır.

Bu Pydantic modeli JSON Schema'ya dönüştürülerek Qwen3'e gönderilir:

```python
format=OrderResult.model_json_schema()
```

Böylece Qwen3 final cevabını tanımlanan yapıya göre üretir.

Örnek:

```json
{
  "order_id": "ORD-1001",
  "status": "hazirlaniyor",
  "message": "Siparişiniz hazırlanıyor."
}
```

Structured Output'un önemli özelliği:

```text
Cevabın yapısını belirler.
```

Ancak:

```text
Verinin doğruluğunu tek başına garanti etmez.
```

Bu nedenle sipariş gibi gerçek bilgiler Python tool'larından alınmaktadır.

---

# 10. Projeyi Çalıştırma

Terminalde:

```bash
python main.py
```

komutunu çalıştır.

Uygulama:

```text
Kullanıcı:
```

şeklinde giriş bekler.

---

# 11. Test 1 — Sipariş Durumu

Kullanıcı:

```text
ORD-1001 siparişimin durumunu kontrol et.
```

Agent'ın çağırmasını beklediğimiz tool:

```text
[TOOL] get_order_status(ORD-1001)
```

Beklenen sonuç:

```json
{
  "order_id": "ORD-1001",
  "status": "hazirlaniyor",
  "message": "Siparişiniz hazırlanıyor."
}
```

Bu senaryoda:

```text
cancel_order
```

tool'una ihtiyaç yoktur.

---

# 12. Test 2 — Sipariş İptali

Testten önce `ORD-1001`:

```text
hazirlaniyor
```

durumunda olmalıdır.

Kullanıcı:

```text
ORD-1001 siparişim henüz kargoya verilmediyse iptal et.
```

Beklenen Agent Loop:

```text
[TOOL] get_order_status(ORD-1001)

          ↓

status = hazirlaniyor

          ↓

Qwen3 tekrar karar verir

          ↓

[TOOL] cancel_order(ORD-1001)
```

Beklenen final çıktı:

```json
{
  "order_id": "ORD-1001",
  "status": "iptal_edildi",
  "message": "Sipariş başarıyla iptal edildi."
}
```

Ayrıca `orders.json` içerisindeki veri gerçekten:

```json
"durum": "iptal_edildi"
```

olarak değişir.

---

# 13. Test 3 — Kargoya Verilmiş Sipariş

`ORD-1002`:

```text
kargoya_verildi
```

durumundadır.

Kullanıcı:

```text
ORD-1002 siparişimi iptal et.
```

Agent önce:

```text
get_order_status("ORD-1002")
```

ile sipariş durumunu öğrenmelidir.

Sonuç:

```text
kargoya_verildi
```

olduğu için sipariş iptal edilmemelidir.

Beklenen final çıktı:

```json
{
  "order_id": "ORD-1002",
  "status": "kargoya_verildi",
  "message": "Sipariş kargoya verildiği için iptal edilemez."
}
```

Qwen3 yanlışlıkla `cancel_order` tool'unu çağırsa bile tool içerisindeki Python kontrolü siparişin değiştirilmesini engeller.

---

# 14. Tool Çağrılarını İzleme

Eğitim sırasında agent'ın gerçekten tool kullanıp kullanmadığını görmek için tool fonksiyonlarının içerisinde:

```python
print(f"\n[TOOL] get_order_status({order_id})")
```

ve:

```python
print(f"\n[TOOL] cancel_order({order_id})")
```

satırları bulunmaktadır.

Örneğin:

```text
Kullanıcı: ORD-1001 siparişimin durumunu kontrol et.

[TOOL] get_order_status(ORD-1001)

Agent Sonucu:
...
```

görülüyorsa model gerçekten tool kullanmıştır.

Eğer `[TOOL]` satırı görünmüyorsa model tool çağırmadan doğrudan cevap üretmiş demektir.

---

# 15. Neden Bu Yapı Agentic?

Normal bir LLM uygulamasında:

```text
Kullanıcı
   ↓
LLM
   ↓
Cevap
```

akışı bulunur.

Bu uygulamada ise:

```text
Kullanıcı
   ↓
LLM
   ↓
Karar
   ↓
Tool
   ↓
Observation
   ↓
Yeni karar
   ↓
Tool
   ↓
Observation
   ↓
Final cevap
```

akışı bulunmaktadır.

Model yalnızca metin üretmez.

Model:

- Kullanıcı hedefini değerlendirir.
- Kullanacağı tool'u seçer.
- Tool parametrelerini oluşturur.
- Tool sonucunu gözlemler.
- Bir sonraki adıma karar verir.
- Gerekirse yeni bir tool kullanır.
- Görev tamamlandığında durur.

Bu nedenle uygulama bir **AI Agent** örneğidir.

---

# 16. Tool Güvenliği

Önemli bir prensip:

> LLM karar verebilir ancak kritik iş kuralları yalnızca LLM'e bırakılmamalıdır.

Örneğin `cancel_order` içerisinde:

```python
if order["durum"] == "kargoya_verildi":
```

kontrolü bulunmaktadır.

Böylece model yanlışlıkla:

```text
cancel_order
```

çağırsa bile kargoya verilmiş bir sipariş iptal edilmez.

Bu yaklaşım:

```text
LLM → karar
Python Tool → gerçek işlem ve iş kuralı
```

ayrımını sağlar.

---

# 17. Eğitimde Kullanılan Kavramlar

| Kavram | Projedeki Karşılığı |
|---|---|
| AI Agent | Qwen3 tabanlı Sipariş Yönetim Agent'ı |
| LLM | Qwen3:4B |
| Model Runtime | Ollama |
| Instructions | `SYSTEM_PROMPT` |
| Tool | Python fonksiyonları |
| Tool Description | Fonksiyon docstring'leri |
| Tool Parameters | Python fonksiyon parametreleri |
| Tool Selection | Qwen3 |
| Tool Call | `response.message.tool_calls` |
| Tool Result | Python fonksiyon çıktısı |
| Multiple Tools | `get_order_status`, `cancel_order` |
| Agent Loop | `for` döngüsü |
| Observation | Tool sonucunun tekrar modele verilmesi |
| Execution Limit | `MAX_STEPS` |
| Structured Output | `OrderResult` |
| Validation | Pydantic |
| Business Rule | `cancel_order` içindeki Python kontrolleri |

---

# Sonuç

Bu projede kullanıcı agent'a yalnızca hedefini doğal dil ile verir:

```text
ORD-1001 siparişim henüz kargoya verilmediyse iptal et.
```

Agent ise:

```text
Sipariş durumunu öğren
        ↓
Tool kullan
        ↓
Tool sonucunu gözlemle
        ↓
Yeni karar ver
        ↓
Gerekirse başka bir tool kullan
        ↓
Görevi tamamla
        ↓
Structured Output üret
```

akışını gerçekleştirir.

Bu projede agent'ın karar mekanizması Qwen3:4B tarafından yürütülür.

Python kodu ise:

- Tool'ları sağlar.
- Gerçek sipariş verilerini yönetir.
- Agent Loop'u çalıştırır.
- Kritik iş kurallarını uygular.
- Structured Output sonucunu doğrular.

Böylece **LLM + Tools + Agent Loop + Structured Output** bileşenlerini içeren temel bir agentic AI uygulaması oluşturulmuş olur.