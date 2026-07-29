# Python Basics (AI/ML uchun) — Middle D

## 1. Nima? (Ta'rif)

**Python** — sodda sintaksisi, katta ekotizimi (ayniqsa AI/ML
sohasida) tufayli keng tarqalgan yuqori darajadagi dasturlash tili.

## 2. Nima uchun kerak?

AI/ML kutubxonalarining aksariyati (TensorFlow, PyTorch, scikit-learn,
Pandas) — Python'da yozilgan/eng yaxshi qo'llab-quvvatlanadi. C#
backend developer sifatida — ML modellarni tushunish, prototiplash,
yoki data science jamoasi bilan muloqot qilish uchun Python asoslari
zarur.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 C# dan farqi

```
C#:                              Python:
Statik tiplash (compile-time)    Dinamik tiplash (runtime)
{ } bilan blok belgilash          INDENTATSIYA (bo'shliq) bilan blok
Kompilyatsiya qilinadi            INTERPRETATSIYA qilinadi
Thread — to'liq parallel          GIL (Global Interpreter Lock) —
                                   BIR VAQTDA faqat 1 THREAD Python
                                   bytecode'ni bajaradi (CPU-bound
                                   parallellik uchun multiprocessing kerak)
```

```python
# Indentatsiya — MAJBURIY, {} O'RNIGA
def greet(name):
    if name:
        print(f"Salom, {name}!")
    else:
        print("Salom, notanish!")
```

### 3.2 Asosiy sintaksis

```python
# O'zgaruvchilar — TUR e'lon qilinmaydi
age = 25
name = "Orzibek"
is_active = True

# Shartlar
if age >= 18:
    print("Kattalar")
elif age >= 13:
    print("O'smir")
else:
    print("Bola")

# Loop
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

count = 0
while count < 5:
    count += 1
```

### 3.3 Funksiyalar — def, args, kwargs, default

```python
def calculate_bonus(salary, years, rate=0.1):  # rate — DEFAULT qiymat
    return salary * rate * years

def sum_all(*args):           # *args — ISTALGAN sonli POSITIONAL argument
    return sum(args)

def print_info(**kwargs):     # **kwargs — ISTALGAN sonli NAMED argument
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Orzibek", age=25)
```

### 3.4 List, Dict, Tuple, Set

```python
employees = ["Orzibek", "Dilnoza", "Ali"]        # List — o'zgaruvchan, tartiblangan
employee = {"name": "Orzibek", "age": 25}        # Dict — key-value (C#'dagi Dictionary)
coordinates = (41.29, 69.24)                      # Tuple — O'ZGARMAS (immutable)
unique_ids = {1, 2, 3}                            # Set — TAKRORLANMAYDIGAN elementlar

employees.append("Malika")
employee["salary"] = 5000000
```

### 3.5 List comprehension

```python
squares = [x**2 for x in range(10)]                    # [0, 1, 4, 9, 16, ...]
even_squares = [x**2 for x in range(10) if x % 2 == 0]  # Faqat JUFT sonlar

# C#'dagi LINQ ga o'xshash:
# var squares = Enumerable.Range(0, 10).Select(x => x * x);
```

### 3.6 String formatting — f-string

```python
name = "Orzibek"
age = 25
print(f"{name} {age} yoshda")  # C#'dagi $"{name} {age} yoshda" ga TENG
```

### 3.7 File I/O

```python
with open("data.txt", "r") as f:   # "with" — C#'dagi "using" ga TENG (avtomatik yopadi)
    content = f.read()

with open("output.txt", "w") as f:
    f.write("Salom dunyo")
```

### 3.8 Exception handling

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Xato: {e}")
finally:
    print("Har doim bajariladi")
```

### 3.9 `pip` — paket o'rnatish

```bash
pip install numpy pandas scikit-learn
pip freeze > requirements.txt   # O'rnatilgan paketlar RO'YXATI (C#'dagi .csproj ga o'xshash)
pip install -r requirements.txt # Ro'yxatdan O'RNATISH
```

### 3.10 Virtual Environment — `venv`

```bash
python -m venv myenv          # Yangi izolyatsiyalangan muhit yaratish
source myenv/bin/activate     # Linux/Mac — YOQISH
myenv\Scripts\activate        # Windows — YOQISH
```

`venv` — har loyiha uchun **alohida** paket versiyalarini saqlash
imkonini beradi (C#'dagi har loyihaning o'z `.csproj`/NuGet
paketlariga ega bo'lishiga o'xshaydi).

### 3.11 Jupyter Notebook / Google Colab

```
Jupyter Notebook — kod, matn, GRAFIK natijalarni BIR HUJJATDA
                    aralashtirib yozish imkonini beruvchi INTERAKTIV
                    muhit — ma'lumotlarni TEZKOR tahlil qilish uchun
                    IDEAL.

Google Colab — Jupyter Notebook'ning BULUTDAGI (bepul GPU bilan)
                versiyasi — o'rnatishsiz, brauzerda ishlaydi.
```

### 3.12 NumPy — asosiy operatsiyalar

```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
print(arr * 2)          # [2, 4, 6, 8, 10] — VEKTORIZATSIYA (har element AVTOMATIK)
print(arr.mean())        # O'rtacha
matrix = np.array([[1, 2], [3, 4]])
```

NumPy — Python'ning **standart** list'idan ANCHA tezroq (C
darajasida optimallashtirilgan) — katta massivlar/matritsalar
ustida ML hisob-kitoblar uchun ASOS.

### 3.13 Pandas — DataFrame, CSV o'qish

```python
import pandas as pd

df = pd.read_csv("employees.csv")
print(df.head())              # Birinchi 5 qatorni ko'rsatish
print(df["salary"].mean())    # "salary" ustunining o'rtachasi
filtered = df[df["age"] > 25] # SQL WHERE ga o'xshash filtrlash
```

Pandas'ning `DataFrame` — Excel jadvaliga o'xshash, lekin
dasturiy boshqariladigan ma'lumot strukturasi — ERP hisobotlarini
tahlil qilish uchun ham ishlatilishi mumkin.

### 3.14 AI/ML bilan bog'liqlik — nima uchun Python

```
✅ TensorFlow, PyTorch, scikit-learn — ASOSAN Python API'ga ega
✅ Katta community, KO'P tayyor namuna/hujjat
✅ Prototiplash TEZ (dinamik tiplash, qisqa sintaksis)
❌ Ishlab chiqarish (production) tizimida — ko'pincha C#/Java/Go
   bilan "wrap" qilinadi (performance-kritik qismlar uchun)
```

## 4. Kod — oddiy ML misoli (scikit-learn)

```python
from sklearn.linear_model import LinearRegression
import numpy as np

X = np.array([[1], [2], [3], [4]])  # Ish staji (yil)
y = np.array([3000000, 4000000, 5000000, 6000000])  # Maosh

model = LinearRegression()
model.fit(X, y)
prediction = model.predict([[5]])  # 5 yillik stajga ega xodim maoshini BASHORAT qilish
print(prediction)
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| ML model prototiplash | Python + scikit-learn/PyTorch |
| Ma'lumotlarni tahlil qilish (CSV, statistika) | Python + Pandas |
| Tezkor skript, avtomatlashtirish | Python |
| Production Web API (asosiy stack) | C# / ASP.NET Core (Python EMAS) |

## 6. Muhim nuqtalar

- Python — indentatsiyaga **JUDA** sezgir — noto'g'ri bo'shliq
  `IndentationError` beradi.
- GIL (Global Interpreter Lock) — CPU-intensive parallel ishlash
  uchun cheklov qo'yadi — I/O-bound (masalan tarmoq) ishlar uchun
  muammo emas.
- `venv` — har loyiha uchun paket versiyalarini **izolyatsiya**
  qilish uchun har doim ishlatilishi tavsiya etiladi.

## 7. Imtihon savollari

1. Python va C# orasidagi eng muhim sintaktik farq (blok belgilash)
   nima?
2. `*args` va `**kwargs` orasidagi farq nima?
3. List comprehension nima va u C#'dagi LINQ'ga qanday o'xshaydi?
4. `venv` nima uchun kerak?
5. NumPy nima uchun oddiy Python list'idan tezroq?
6. Nima uchun AI/ML sohasida Python C#'dan ko'proq ustunlik qiladi?
