# State ve Memory Kullanan AI Agent

Bu projede **LangGraph**, **Ollama** ve **Qwen3** modelleri kullanılarak state ve farklı memory türlerini kullanan bir AI Agent geliştirilmektedir.

Projenin amacı yalnızca çalışan bir chatbot oluşturmak değildir. Amaç, bir AI Agent içerisinde aşağıdaki kavramların birbirinden nasıl ayrıldığını ve kod tarafında nasıl uygulandığını göstermektir:

- State
- Conversation Memory
- Long-Term Memory
- Semantic Memory
- Session / Thread
- Embedding
- Vector Database
- Semantic Retrieval

Her kavram önce ayrı bir Python dosyasında gösterilir. Son aşamada bütün yapılar tek bir AI Agent içerisinde birleştirilir.

---

# Kullanılan Teknolojiler

Projede aşağıdaki teknolojiler kullanılmaktadır:

| Teknoloji | Kullanım Amacı |
|---|---|
| Python | Uygulama geliştirme |
| LangGraph | Stateful agent ve graph yapısı |
| LangChain | Model ve vector store entegrasyonları |
| Ollama | Modelleri lokal çalıştırma |
| Qwen3:4B | Agent'ın cevap üreten LLM modeli |
| Qwen3-Embedding-0.6B | Semantic Memory için embedding modeli |
| Chroma | Semantic Memory için vector database |
| JSON | Basit Long-Term Memory |
| InMemorySaver | Conversation Memory |

---

# Temel Mimari

Projenin final halinde genel akış aşağıdaki gibidir:

```text
Kullanıcı
   ↓
Conversation / Thread
   ↓
LangGraph State
   ↓
Memory Katmanı
   ├── Conversation Memory
   ├── Long-Term Memory
   └── Semantic Memory
   ↓
Qwen3:4B
   ↓
Cevap
   ↓
State Güncelleme
```

Buradaki önemli nokta, bütün memory yapılarının aynı şey olmamasıdır.

---

# State ve Memory Arasındaki Fark

## State

State, agent'ın **o anda üzerinde çalıştığı sürece ait mevcut durumu** temsil eder.

Örneğin:

```text
current_task
step_count
messages
retrieved_memories
response
```

gibi bilgiler state içerisinde tutulabilir.

State'in amacı agent'ın çalışma sürecinin hangi noktada olduğunu taşımaktır.

Örneğin:

```text
Kullanıcı girdisi
     ↓
Node 1
     ↓
State güncellenir
     ↓
Node 2
     ↓
Aynı State kullanılmaya devam eder
```

State tek başına uzun süreli hafıza anlamına gelmez.

---

# Conversation Memory

Conversation Memory, mevcut konuşmada daha önce gerçekleşen mesajların hatırlanmasını sağlar.

Örneğin:

```text
Kullanıcı: En sevdiğim programlama dili Python.

Kullanıcı: En sevdiğim programlama dili neydi?

Agent: Python.
```

Burada agent ikinci sorunun cevabını ilk mesajın conversation history içerisinde bulunması sayesinde verebilir.

Bu projede Conversation Memory için:

```text
MessagesState
+
InMemorySaver
+
thread_id
```

kullanılmaktadır.

---

# Long-Term Memory

Long-Term Memory, bilginin yalnızca mevcut konuşma sırasında değil, **program kapatılıp yeniden açıldıktan sonra da saklanmasını** sağlar.

Örneğin:

```text
Kullanıcı: hatırla: En sevdiğim programlama dili Python.
```

bilgisi:

```text
data/long_term_memory.json
```

dosyasına kaydedilir.

Program kapatılıp tekrar açıldığında:

```text
Kullanıcı: En sevdiğim programlama dili ne?
```

sorusuna agent:

```text
Python.
```

cevabını verebilir.

Bu eğitimde Long-Term Memory mantığını görünür kılmak için basit bir JSON dosyası kullanılmaktadır.

Gerçek üretim sistemlerinde aynı yaklaşım:

```text
SQL
NoSQL
Key-Value Store
LangGraph Store
Redis
PostgreSQL
```

gibi farklı kalıcı veri katmanlarıyla uygulanabilir.

---

# Semantic Memory

Semantic Memory de uzun süreli bir hafıza türüdür.

Fakat burada bilgi birebir anahtar veya kelime eşleşmesiyle değil, **anlam benzerliği ile bulunur**.

Örneğin hafızada şu bilgi olsun:

```text
Lokal çalışan açık kaynaklı yapay zeka modellerini tercih ediyorum.
```

Kullanıcı daha sonra:

```text
Yeni bir LLM seçerken benim için nasıl bir model mantıklı?
```

diye sorabilir.

Soru içerisinde:

```text
lokal
açık kaynak
```

kelimeleri birebir geçmese bile semantic search ilgili memory kaydını bulabilir.

Temel akış:

```text
Memory
   ↓
Embedding Model
   ↓
Sayısal Vektör
   ↓
Vector Database
   ↓
Similarity Search
   ↓
İlgili Memory
```

Bu projede:

```text
Qwen3-Embedding-0.6B
```

embedding modeli olarak,

```text
Chroma
```

ise vector database olarak kullanılmaktadır.

---

# Memory Türlerinin Karşılaştırılması

| Yapı | Ne Tutar? | Ne Kadar Yaşar? | Nasıl Bulunur? |
|---|---|---|---|
| State | Mevcut çalışma durumu | Graph çalışması | State alanları |
| Conversation Memory | Önceki mesajlar | Aynı conversation/thread | Message history |
| Long-Term Memory | Kalıcı bilgiler | Program kapansa da kalır | JSON / DB |
| Semantic Memory | Anlamsal bilgiler | Program kapansa da kalır | Vector similarity |

---

# Proje Yapısı

```text
state_memory_ai_agent/
│
├── 01_stateful_agent.py
├── 02_conversation_memory.py
├── 03_long_term_memory.py
├── 04_semantic_memory.py
├── 05_state_memory_agent.py
│
├── requirements.txt
├── README.md
│
└── data/
    ├── long_term_memory.json
    └── semantic_memory/
```

Dosyaların görevleri:

| Dosya | Amaç |
|---|---|
| `01_stateful_agent.py` | LangGraph State yapısını göstermek |
| `02_conversation_memory.py` | Conversation Memory göstermek |
| `03_long_term_memory.py` | Kalıcı Long-Term Memory göstermek |
| `04_semantic_memory.py` | Embedding + Vector DB ile Semantic Memory göstermek |
| `05_state_memory_agent.py` | Tüm memory yapılarını tek agent içerisinde birleştirmek |
| `data/long_term_memory.json` | Kalıcı Long-Term Memory |
| `data/semantic_memory/` | Chroma Vector Database |

---

# Kurulum

## 1. Virtual Environment

Proje klasörüne gir:

```bash
cd state_memory_ai_agent
```

Virtual environment oluştur:

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

---

# 2. Gerekli Python Kütüphaneleri

`requirements.txt`:

```text
langgraph
langchain-core
langchain-ollama
langchain-chroma
chromadb
```

Kurulum:

```bash
pip install -r requirements.txt
```

---

# 3. Ollama Modelleri

Agent'ın cevap üretmesi için:

```bash
ollama pull qwen3:4b
```

Semantic Memory için embedding modeli:

```bash
ollama pull qwen3-embedding:0.6b
```

Kurulu modelleri kontrol etmek için:

```bash
ollama list
```

Aşağıdaki modeller görünmelidir:

```text
qwen3:4b
qwen3-embedding:0.6b
```

---

# 4. Long-Term Memory Dosyası

`data/long_term_memory.json` oluştur:

```json
{
  "memories": []
}
```

İlk çalıştırmada herhangi bir kalıcı bilgi bulunmadığı için liste boştur.

---

# 01 — Stateful Agent

Dosya:

```text
01_stateful_agent.py
```

## Amaç

Bu bölümde henüz herhangi bir memory kullanılmaz.

Amaç yalnızca LangGraph içerisindeki:

```text
State
Node
Edge
START
END
```

kavramlarını görmek ve state'in node'lar arasında nasıl taşındığını anlamaktır.

State örneği:

```python
class AgentState(TypedDict):
    user_input: str
    current_task: str
    step_count: int
    response: str
```

Graph:

```text
START
  ↓
prepare_task
  ↓
agent
  ↓
END
```

İlk node:

```text
user_input
```

bilgisini:

```text
current_task
```

alanına taşır.

İkinci node Qwen3 modelini çalıştırır.

Her node state'in belirli alanlarını günceller.

---

## Çalıştırma

```bash
python 01_stateful_agent.py
```

### Test Sorusu

```text
Kullanıcı: Python nedir?
```

### Beklenen Davranış

Terminalde:

```text
[NODE] prepare_task
[NODE] run_agent
```

görülmelidir.

Agent yaklaşık olarak:

```text
Python, genel amaçlı ve yüksek seviyeli bir programlama dilidir.
```

şeklinde cevap vermelidir.

Final State içerisinde:

```text
user_input = Python nedir?
current_task = Python nedir?
step_count = 2
response = ...
```

bulunmalıdır.

Buradaki önemli sonuç:

> State, graph çalışırken node'lar arasında taşınmıştır.

---

# 02 — Conversation Memory

Dosya:

```text
02_conversation_memory.py
```

## Amaç

Bu bölümde agent'ın aynı konuşma içerisindeki önceki mesajları hatırlaması sağlanır.

Kullanılan temel yapılar:

```text
MessagesState
InMemorySaver
thread_id
```

Conversation Memory'nin çalışma mantığı:

```text
Thread
  ↓
Mesaj 1
  ↓
Checkpoint
  ↓
Mesaj 2
  ↓
Önceki mesajlar yüklenir
  ↓
Qwen3
```

Aynı `thread_id`, aynı conversation'ı temsil eder.

Örneğin:

```python
config = {
    "configurable": {
        "thread_id": "conversation-1"
    }
}
```

---

## Çalıştırma

```bash
python 02_conversation_memory.py
```

### Test 1

Önce:

```text
Kullanıcı: En sevdiğim programlama dili Python.
```

Beklenen cevap yaklaşık olarak:

```text
Anladım, en sevdiğin programlama dili Python.
```

Sonra programı kapatmadan:

```text
Kullanıcı: En sevdiğim programlama dili neydi?
```

Beklenen cevap:

```text
Python.
```

### Ne Oldu?

İkinci soruda:

```text
Python
```

kelimesi bulunmuyor.

Agent bu bilgiyi mevcut conversation history içerisinden aldı.

---

## Önemli Test

Programı:

```text
exit
```

ile kapat.

Tekrar:

```bash
python 02_conversation_memory.py
```

çalıştır.

Sonra:

```text
Kullanıcı: En sevdiğim programlama dili neydi?
```

sor.

Bu kez agent'ın bu bilgiyi bilmemesi normaldir.

Çünkü:

```text
InMemorySaver
```

RAM üzerinde çalışmaktadır.

Program kapandığında mevcut memory silinir.

Bu örnek Conversation Memory ile Long-Term Memory arasındaki farkı göstermek için önemlidir.

---

# 03 — Long-Term Memory

Dosya:

```text
03_long_term_memory.py
```

## Amaç

Bu bölümde bilgilerin program kapatılsa bile kalıcı olarak saklanması gösterilir.

Kullanıcı bir bilgiyi:

```text
hatırla:
```

komutuyla kaydeder.

Örneğin:

```text
hatırla: En sevdiğim programlama dili Python.
```

Memory şu dosyaya yazılır:

```text
data/long_term_memory.json
```

Örnek dosya:

```json
{
  "memories": [
    "En sevdiğim programlama dili Python."
  ]
}
```

---

## Teknik Akış

```text
Kullanıcı
   ↓
memory_node
   ↓
JSON Memory okunur
   ↓
Yeni bilgi varsa kaydedilir
   ↓
Long-Term Memory
   ↓
agent_node
   ↓
Qwen3
```

Burada LangGraph State:

```text
user_input
memories
memory_saved
response
```

alanlarını taşır.

---

## Çalıştırma

```bash
python 03_long_term_memory.py
```

### Test 1 — Memory Kaydetme

```text
Kullanıcı: hatırla: En sevdiğim programlama dili Python.
```

Beklenen cevap:

```text
Bu bilgiyi hatırlamak üzere kaydettim.
```

Kelime kelime aynı olmak zorunda değildir.

Kontrol:

```text
data/long_term_memory.json
```

dosyasını aç.

Şuna benzer veri görülmelidir:

```json
{
  "memories": [
    "En sevdiğim programlama dili Python."
  ]
}
```

---

## Test 2 — Programı Kapat

```text
exit
```

yaz.

Programı yeniden çalıştır:

```bash
python 03_long_term_memory.py
```

Sor:

```text
Kullanıcı: En sevdiğim programlama dili ne?
```

Beklenen cevap:

```text
Python.
```

Burada önemli nokta:

> Önceki conversation artık mevcut değildir.

Ama bilgi JSON dosyasında bulunduğu için agent yine cevap verebilir.

Bu nedenle bu yapı:

```text
Long-Term Memory
```

olarak değerlendirilir.

---

# 04 — Semantic Memory

Dosya:

```text
04_semantic_memory.py
```

## Amaç

Bu bölümde Long-Term Memory içerisindeki bilgilerin yalnızca birebir kelime eşleşmesiyle değil, **anlam benzerliği** ile bulunması gösterilir.

Bu işlem için:

```text
Qwen3-Embedding-0.6B
+
Chroma
```

kullanılır.

---

# Embedding Nedir?

Embedding modeli metni sayısal bir vektöre dönüştürür.

Örneğin:

```text
"Lokal modelleri tercih ediyorum."
```

şeklindeki bir cümle:

```text
[0.021, -0.184, 0.445, ...]
```

gibi yüksek boyutlu bir vektörle temsil edilir.

Anlam açısından birbirine yakın cümlelerin vektörleri de birbirine yakın olur.

Bu sayede:

```text
lokal model
```

ile:

```text
kendi bilgisayarımda çalışan model
```

ifadeleri birebir aynı kelimeleri kullanmasa bile semantik olarak eşleştirilebilir.

---

# Vector Database Neden Kullanılıyor?

Embedding vektörlerinin saklanması ve benzer vektörlerin hızlı biçimde bulunması gerekir.

Bu projede:

```text
Chroma
```

kullanılır.

Semantic Memory kayıtları:

```text
data/semantic_memory/
```

klasöründe saklanır.

Bu bilgiler program kapatıldığında kaybolmaz.

---

# Semantic Memory Akışı

```text
Memory
   ↓
Qwen3-Embedding-0.6B
   ↓
Embedding Vector
   ↓
Chroma
```

Kullanıcı soru sorduğunda:

```text
Kullanıcı Sorusu
   ↓
Embedding
   ↓
Similarity Search
   ↓
En Benzer Memory'ler
   ↓
Qwen3 Context
   ↓
Cevap
```

---

## Çalıştırma

```bash
python 04_semantic_memory.py
```

### Test 1 — Semantic Memory Kaydetme

```text
Kullanıcı: hatırla: Lokal çalışan açık kaynaklı yapay zeka modellerini tercih ediyorum.
```

Beklenen cevap yaklaşık olarak:

```text
Bu tercihini hatırlamak üzere kaydettim.
```

Memory aynı zamanda Chroma içerisine embedding olarak kaydedilir.

---

## Test 2 — Semantik Arama

Programı kapatıp tekrar çalıştırabilirsin.

Sor:

```text
Kullanıcı: Yeni bir LLM seçerken benim için nasıl bir tercih mantıklı?
```

Terminalde:

```text
Bulunan Semantic Memory:
- Lokal çalışan açık kaynaklı yapay zeka modellerini tercih ediyorum.
```

görülmelidir.

Agent'ın cevabında da buna benzer bir bilgi bulunmalıdır:

```text
Daha önceki tercihine göre lokal çalıştırılabilen ve açık kaynaklı bir model senin için daha uygun olabilir.
```

Buradaki önemli nokta:

Kullanıcının yeni sorusunda:

```text
lokal çalışan açık kaynaklı
```

ifadesi birebir kullanılmamıştır.

Memory:

```text
anlam benzerliği
```

sayesinde bulunmuştur.

---

# Long-Term Memory ve Semantic Memory Arasındaki Fark

Bu projede iki yapı özellikle ayrı gösterilmektedir.

## Long-Term Memory

```text
En sevdiğim programlama dili Python.
```

JSON içerisinde kalıcı olarak tutulur.

Agent isterse tüm memory kayıtlarını okuyabilir.

---

## Semantic Memory

```text
Lokal çalışan açık kaynaklı modelleri tercih ediyorum.
```

embedding olarak vector database içerisinde temsil edilir.

Kullanıcı:

```text
Model seçiminde benim için ne önemliydi?
```

dediğinde ilgili memory semantic similarity ile bulunur.

Özet:

```text
Long-Term Memory
→ Bilginin kalıcı olması

Semantic Memory
→ Kalıcı bilginin anlam üzerinden geri çağrılması
```

Semantic Memory aslında Long-Term Memory'nin özel kullanım biçimlerinden biri olarak düşünülebilir.

---

# 05 — State + Memory AI Agent

Dosya:

```text
05_state_memory_agent.py
```

Bu dosya bölümün final uygulamasıdır.

Amaç önceki örneklerde öğrendiğimiz bütün yapıları tek agent içerisinde birleştirmektir.

Kullanılan bileşenler:

```text
LangGraph State
Conversation Memory
Long-Term Memory
Semantic Memory
Qwen3:4B
Qwen3-Embedding-0.6B
Chroma
```

---

# Final Agent Mimarisi

```text
                   Kullanıcı
                       ↓
                  thread_id
                       ↓
               Conversation State
                       ↓
                   Memory Node
                 ↙             ↘
        Long-Term Memory    Semantic Search
                 ↘             ↙
                   Agent State
                       ↓
                    Qwen3
                       ↓
                     Cevap
                       ↓
                Conversation Checkpoint
```

---

# Final State

Final uygulamada LangGraph State içerisinde:

```text
messages
long_term_memories
semantic_memories
memory_saved
```

bilgileri taşınır.

`messages`:

```text
Conversation Memory
```

için kullanılır.

`long_term_memories`:

```text
JSON Long-Term Memory
```

içerir.

`semantic_memories`:

```text
Vector Database'den getirilen ilgili memory'leri
```

tutar.

---

# Final Uygulamayı Çalıştırma

```bash
python 05_state_memory_agent.py
```

---

# Final Test 1 — Conversation Memory

İlk mesaj:

```text
Kullanıcı: Bu oturumda LangGraph öğreniyorum.
```

Beklenen cevap:

```text
Anladım, bu oturumda LangGraph öğreniyorsun.
```

Ardından:

```text
Kullanıcı: Bu oturumda ne öğreniyorum?
```

Beklenen cevap:

```text
LangGraph öğreniyorsun.
```

Bu bilgi mevcut conversation history üzerinden gelmektedir.

---

# Final Test 2 — Long-Term Memory

Şunu yaz:

```text
Kullanıcı: hatırla: En sevdiğim programlama dili Python.
```

Beklenen cevap:

```text
En sevdiğin programlama dilinin Python olduğunu kaydettim.
```

Sonra programı kapat:

```text
exit
```

Programı tekrar aç:

```bash
python 05_state_memory_agent.py
```

Sor:

```text
Kullanıcı: En sevdiğim programlama dili ne?
```

Beklenen cevap:

```text
En sevdiğin programlama dili Python.
```

Conversation history silinmiş olsa bile Long-Term Memory JSON üzerinde kalmıştır.

---

# Final Test 3 — Semantic Memory

Şunu kaydet:

```text
Kullanıcı: hatırla: Lokal çalışan açık kaynaklı yapay zeka modellerini tercih ediyorum.
```

Programı istersen kapatıp tekrar aç.

Daha sonra:

```text
Kullanıcı: Yeni bir LLM projesi yapacağım. Benim için nasıl bir model seçimi mantıklı?
```

Terminalde semantic retrieval sonucu:

```text
Semantic Memory:
- Lokal çalışan açık kaynaklı yapay zeka modellerini tercih ediyorum.
```

görülmelidir.

Beklenen agent cevabı:

```text
Daha önceki tercihine göre lokal çalıştırılabilen ve açık kaynaklı bir LLM seçmek senin için daha uygun görünüyor.
```

Burada agent birebir kelime araması yapmamıştır.

İlgili bilgi embedding similarity sayesinde bulunmuştur.

---

# Final Test 4 — Conversation ve Long-Term Memory Farkı

Aynı program çalışırken:

```text
Kullanıcı: Bugün transformer mimarisini çalışıyorum.
```

Sonra:

```text
Kullanıcı: Bugün ne çalışıyorum?
```

Beklenen:

```text
Transformer mimarisini çalışıyorsun.
```

Şimdi programı kapatıp tekrar aç.

Sor:

```text
Kullanıcı: Bugün ne çalışıyorum?
```

Bu bilginin artık hatırlanmaması normaldir.

Çünkü bu bilgi:

```text
hatırla:
```

komutuyla Long-Term Memory'ye kaydedilmemiştir.

Bu test:

```text
Conversation Memory
```

ile:

```text
Long-Term Memory
```

arasındaki farkı gösterir.

---

# Final Test 5 — Yeni Thread

Conversation Memory `thread_id` ile ilişkilidir.

Kodda:

```python
thread_id = "conversation-1"
```

bulunmaktadır.

Bunu:

```python
thread_id = "conversation-2"
```

olarak değiştirirsen yeni bir conversation oluşturmuş olursun.

Yeni thread önceki conversation mesajlarını görmez.

Fakat:

```text
Long-Term Memory
Semantic Memory
```

kalıcı veri katmanlarında bulunduğu için kullanılmaya devam edebilir.

Bu ayrım önemlidir:

```text
Conversation Memory
→ Thread Scoped

Long-Term Memory
→ Thread'ler Arası Kalıcı

Semantic Memory
→ Thread'ler Arası Kalıcı + Anlamsal Retrieval
```

---

# Memory Yazma Stratejisi

Bu eğitimde memory yazma işlemini açık hale getirmek için:

```text
hatırla:
```

komutu kullanılmaktadır.

Örneğin:

```text
hatırla: Python kullanmayı seviyorum.
```

Bu yaklaşım eğitim için özellikle tercih edilmiştir.

Çünkü öğrenci:

```text
hangi bilginin memory'ye yazıldığını
```

net şekilde görebilir.

Gerçek agent sistemlerinde memory yazma kararı:

```text
LLM
Memory Manager
Extraction Model
Rule-Based Filter
```

gibi yapılar tarafından otomatik olarak da verilebilir.

---

# Memory Management Neden Önemli?

Gerçek sistemlerde her konuşmanın tamamını Long-Term Memory'ye yazmak doğru değildir.

Örneğin:

```text
Merhaba
Teşekkürler
Saat kaç?
```

gibi geçici bilgiler genellikle kalıcı memory için anlamlı değildir.

Daha değerli bilgiler:

```text
Kullanıcı tercihleri
Uzun süreli hedefler
Önemli kararlar
Tekrarlayan çalışma biçimleri
```

olabilir.

Bu nedenle production seviyesinde memory sistemlerinde:

```text
Selection
Filtering
Summarization
Update
Delete
Deduplication
```

gibi ek işlemler uygulanabilir.

Bu eğitimde konu karmaşıklaşmaması için memory yazımı açık `hatırla:` komutuyla yapılmaktadır.

---

# Semantic Memory ve RAG Aynı Şey Mi?

Hayır.

Teknik olarak benzer bileşenler kullanılabilir:

```text
Embedding
Vector Database
Similarity Search
```

ancak kullanım amaçları farklıdır.

RAG:

```text
Harici bilgi kaynaklarından bilgi getirir.
```

Örneğin:

```text
PDF
Web
Şirket dokümanları
Knowledge Base
```

Semantic Memory ise:

```text
Agent'ın geçmişte öğrendiği veya sakladığı bilgileri getirir.
```

Örneğin:

```text
Kullanıcı lokal modelleri tercih ediyor.
```

Her ikisi de vector search kullanabilir fakat veri kaynağı ve kullanım amacı farklıdır.

---

# Memory Temizleme

Eğitim sırasında testleri baştan yapmak istersen memory verilerini sıfırlayabilirsin.

## Long-Term Memory

`data/long_term_memory.json` dosyasını:

```json
{
  "memories": []
}
```

haline getir.

## Semantic Memory

Şu klasörü sil:

```text
data/semantic_memory/
```

Program tekrar çalıştırıldığında Chroma gerekli dosyaları yeniden oluşturur.

## Conversation Memory

`InMemorySaver` kullandığımız için programı kapatıp tekrar açmak yeterlidir.

---

# Sık Karşılaşılabilecek Problemler

## Ollama Çalışmıyor

Kontrol:

```bash
ollama list
```

Model yoksa:

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

---

## Semantic Memory Sonucu Bulunmuyor

Öncelikle memory kaydet:

```text
hatırla: Lokal modelleri tercih ediyorum.
```

Daha sonra anlamsal olarak ilgili bir soru sor:

```text
Model seçerken nasıl bir tercihim vardı?
```

---

## Yanlış veya Alakasız Semantic Memory Geliyor

Semantic search:

```python
similarity_search(..., k=3)
```

ile en yakın üç sonucu getirir.

Her getirilen sonucun mutlaka doğru veya gerekli olduğu anlamına gelmez.

Gerçek sistemlerde:

```text
Similarity Threshold
Metadata Filtering
Reranking
Memory Scoring
```

gibi teknikler eklenebilir.

---

## Aynı Memory Birden Fazla Kez Kaydediliyor

JSON Long-Term Memory içerisinde basit duplicate kontrolü yapılmaktadır.

Semantic Memory tarafında ise eğitim örneği sade tutulduğu için aynı bilgi tekrar Chroma'ya yazılabilir.

Production seviyesinde:

```text
Deduplication
Memory ID
Similarity Check
Update Existing Memory
```

gibi mekanizmalar eklenebilir.

---

# Bu Projede Öğrenilen Kavramlar

| Kavram | Projedeki Karşılığı |
|---|---|
| State | `AgentState` |
| Node | `memory_node`, `agent_node` |
| Edge | Node'lar arasındaki LangGraph bağlantıları |
| Graph | `StateGraph` |
| Conversation History | `MessagesState` |
| Conversation Memory | `InMemorySaver` |
| Session | `thread_id` |
| Long-Term Memory | `long_term_memory.json` |
| Semantic Memory | Chroma Vector Store |
| Embedding | `Qwen3-Embedding-0.6B` |
| Semantic Search | `similarity_search()` |
| LLM | `Qwen3:4B` |
| Local Model Runtime | Ollama |
| Memory Retrieval | Semantic Memory Node |
| Memory Injection | Retrieved memory'nin system prompt'a eklenmesi |

---

# Final Özet

Bu eğitimde memory yapısını tek bir kavram olarak ele almadık.

Adım adım:

```text
State
 ↓
Conversation Memory
 ↓
Long-Term Memory
 ↓
Semantic Memory
 ↓
State + Memory Agent
```

şeklinde ilerledik.

State:

```text
Agent'ın mevcut çalışma durumunu
```

temsil eder.

Conversation Memory:

```text
Mevcut konuşmadaki mesajları
```

hatırlar.

Long-Term Memory:

```text
Bilginin oturumlar arasında kalmasını
```

sağlar.

Semantic Memory:

```text
Kalıcı bilgilerin anlam üzerinden bulunmasını
```

sağlar.

Final uygulamada ise bu yapılar birlikte kullanılarak:

```text
stateful
conversation-aware
long-term-memory-aware
semantic-memory-aware
```

bir AI Agent oluşturulmuştur.