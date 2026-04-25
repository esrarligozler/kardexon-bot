# Discord Kart Analiz Botu

Bu proje, Python ve `discord.py` kullanılarak geliştirilmiş bir Discord botudur. Bot; kart numarası formatı, Luhn algoritması, kart tipi tespiti ve basit kalite kontrolleri gibi konuları eğitim/test amacıyla göstermeyi hedefler.

> ⚠️ Bu proje yalnızca eğitim ve yazılım geliştirme pratiği içindir. Gerçek kart bilgileriyle kullanılmamalıdır. Yasa dışı veya kötüye kullanım amaçlı kullanımdan geliştirici sorumlu değildir.

## Özellikler

* Discord komut sistemi
* Visa, Mastercard, American Express, Discover ve JCB format desteği
* Luhn algoritması kontrolü
* Kart tipi tanıma
* Skor bazlı filtreleme
* Tekrarlayan blok kontrolü
* Ardışık sayı kontrolü
* Embed mesaj çıktısı
* Sadece bot sahibine özel komut kullanımı

## Gereksinimler

* Python 3.10+
* discord.py

Kurulum:

```bash
pip install discord.py
```

## Ayarlar

Kod içinde aşağıdaki alanları doldurun:

```python
BOT_TOKEN = "bot tokeni"
OWNER_ID = admin_id
```

* `BOT_TOKEN`: Discord Developer Portal üzerinden aldığınız bot tokeni
* `OWNER_ID`: Komutu kullanabilecek Discord kullanıcı ID’niz

## Kullanım

Botu çalıştırmak için:

```bash
python bot.py
```

Discord üzerinde yardım menüsü:

```text
!komutlar
```

Örnek komutlar:

```text
!kart visa 5
!kart mc 10 --min-score 85
!kart amex 3 --no-sequence --no-repeat
!kart visa 5 --bin 4539
```

## Komutlar

### `!komutlar`

Bot komutlarını ve kullanım örneklerini gösterir.

### `!kart <tip> [adet] [opsiyonlar]`

Belirtilen kart tipi için test/simülasyon verisi üretir.

Geçerli tipler:

```text
visa
mc
mastercard
amex
americanexpress
discover
jcb
```

Opsiyonlar:

| Parametre       | Açıklama                              |
| --------------- | ------------------------------------- |
| `--bin BIN`     | Başlangıç numarası belirtir           |
| `--min-score X` | Minimum kalite skoru belirler         |
| `--no-sequence` | Ardışık sayı içerenleri filtreler     |
| `--no-repeat`   | Tekrarlayan blok içerenleri filtreler |

## Proje Yapısı

Kodda temel olarak şu bölümler bulunur:

* `AdvancedCC` sınıfı
* Luhn doğrulama fonksiyonları
* Kart tipi tanımlama
* CVV ve son kullanma tarihi simülasyonu
* Discord bot komutları
* Embed çıktı sistemi
* Yetki kontrolü

## Güvenlik Notları

* Bot tokeninizi kimseyle paylaşmayın
* Gerçek kişilere ait kart verileriyle test yapmayın (yaparsanız sorumluluk kullanıcıya aittir)
* Bu botu herkese açık sunucularda kontrolsüz çalıştırmayın . Hesabınıza işlem uygulana bilir

## İletişim için
  discord.gg/keless
  esrarigozler 
  

## Lisans

Bu proje eğitim amaçlıdır. Kullanım sorumluluğu tamamen kullanıcıya aittir.
