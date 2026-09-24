# Vikipedi botu ve Claude iş akışları (tr.wikipedia)

Bu depoda iki şey var:

1. **Bul-değiştir botu:** Pywikibot ile yazım hatalarını toplu düzeltir. Terminalden çalışır ve **varsayılan olarak deneme modundadır**; `-canli` vermediğin sürece hiçbir şey kaydetmez.
2. **Claude iş akışları:** Madde genişletme ve güncelleme. Claude aday bulur, kaynaklı metni hazırlar ve düzenleme sayfasını açar. **Metni yapıştırıp kaydeden her zaman sensin.**

Düzenlemeler `KadirBalikci` hesabıyla, her biri onaylanarak yapılır. Bot politikasına göre yardımlı (yarı otomatik) düzenlemeler için ayrı bir bot hesabı gerekmez, hatta kullanılmamalıdır.

---

## Claude'a verebileceğin talimatlar

| Talimat | Ne yapar |
|---|---|
| `madde genişlet` | Taslaklardan bir aday bulur ve 1-3 cümlelik kaynaklı bir ekleme hazırlar |
| `madde genişlet: giyim` | Adayı belirtilen konudan seçer |
| `3 madde genişlet` | Birden fazla öneri hazırlar |
| `madde güncelle` | `{{Güncelle}}` etiketli ya da eski tarihli bir bilgiyi güncel kaynakla düzeltir |
| `madde güncelle: Ankara` | Sadece belirtilen maddeye bakar |
| `madde güncelle: futbol` | Adayı belirtilen alandan seçer |
| `yazım tara` | TDK'ya göre kesin yanlış olan yaygın yazımları arar. Her birinin kaç maddede geçtiğini ve yanlış eşleşme riskini gösterir. |
| `yazım tara: 10` | Aynısını 10 adayla yapar |
| `yazım kuralı ekle: herkez → herkes` | Verdiğin kuralı TDK'dan ve örnek maddelerden doğrular, `duzeltmeler.tsv` dosyasına ekleyip commit'ler, çalıştırman gereken bot komutlarını verir |

`madde genişlet` komutunun becerisi `skills/vikipedi-genislet/SKILL.md` dosyasında. `yazım ...` komutlarının becerisi `skills/vikipedi-yazim/SKILL.md` dosyasında. `madde güncelle` komutunun çalışması için Claude'daki "vikipedi-guncelle" beceri önerisinin kaydedilmiş olması gerekir.

**Yazım düzeltmelerinde iş bölümü:** Claude kuralı bulur, doğrular ve dosyaya ekler. Botu sen kendi Terminal'inde çalıştırırsın. Önce deneme modunda farklara bakarsın, sonra canlı modda her düzenlemeyi `y`/`n` ile onaylarsın. Komutlar aşağıda.

**Her öneride Claude'dan gelenler:**

- Madde bağlantısı ve neden aday olduğu
- Eklenecek ya da değiştirilecek vikimetin, kopyalanmaya hazır
- Kaynak kontrolü: kaynağın açıldığı ve metni desteklediği
- Hazır değişiklik özeti, "YZ destekli" notuyla. [Vikipedi:Büyük dil modelleri](https://tr.wikipedia.org/wiki/Vikipedi:B%C3%BCy%C3%BCk_dil_modelleri) bu notu istiyor, özetten çıkarma.
- Düzenleme sayfasının tarayıcı panelinde açılması

**Senin adımların:**

1. Metni yapıştır.
2. "Önizlemeyi göster" ile kontrol et.
3. Özeti gir ve kaydet.

Tarayıcı paneli görünmüyorsa Claude masaüstü uygulamasında Cmd+Shift+B ile açabilirsin.

**Diğer talimatlar:**

- Bot çıktısını, bir farkı veya hata mesajını Claude'a yapıştırıp "şuna bak" diyebilirsin.
- `duzeltmeler.tsv'ye kural ekle: X → Y` ile yeni düzeltme kuralı ekletebilirsin.

---

## Terminal komutları

Tüm komutlar proje klasöründe çalıştırılır:

```bash
cd ~/PycharmProjects/vikibot
```

> **zsh uyarısı:** Mac'teki zsh, `#` ile başlayan açıklamaları komutun parçası sanıp `bad pattern: #` hatası veriyor. Bu dosyadaki komutları kopyalarken açıklamaları alma, sadece komut satırını kopyala.

### Kurulum ve test

```bash
pip3 install pywikibot pytest
python3 -m pytest -q test_kurallar.py
```

Testlerin hepsi geçmeli.

### Deneme modu (hiçbir şey kaydetmez)

Tüm kurallar için arama yapıp farkları gösterir:

```bash
python3 bul_degistir.py
```

Tek bir sayfada dener:

```bash
python3 bul_degistir.py -page:"Ankara"
```

Bir kategorideki en fazla 50 sayfayı tarar:

```bash
python3 bul_degistir.py -cat:"Türk yazarlar" -limit:50
```

Her kural için arama sonucunu en fazla 5 sayfayla sınırlar:

```bash
python3 bul_degistir.py -limit:5
```

Deneme modundaki "Page ... saved" mesajı yanıltıcı. Hemen üstündeki "SIMULATION: edit action blocked" satırı hiçbir şeyin kaydedilmediğini gösterir.

### Canlı mod (kaydeder, her düzenlemede onay sorar)

```bash
python3 bul_degistir.py -canli -enfazla:3
```

Her sayfada fark gösterilir ve senden onay beklenir:

- `y` kaydeder
- `n` atlar
- `q` çıkar
- `a` kalan hepsini onaylar. Kendi hesabınla bunu kullanma.

### Sadece yeni eklenen kuralları denemek

Claude yeni kuralları `yeni_kurallar.tsv` dosyasına da yazdıysa, sadece onları çalıştırmak için önce deneme modunda farklara bak:

```bash
python3 bul_degistir.py -kurallar:yeni_kurallar.tsv -limit:5
```

Farklar doğruysa canlı modda çalıştır:

```bash
python3 bul_degistir.py -kurallar:yeni_kurallar.tsv -canli -enfazla:5
```

Canlı modda küçük partilerle ilerle (`-enfazla:5` ile `-enfazla:20` arası). Yüksek hızlı toplu düzenleme, onaylı olsa bile bot gibi değerlendirilebilir.

### Seçenekler

| Seçenek | Anlamı |
|---|---|
| `-canli` | Değişiklikleri gerçekten kaydet |
| `-enfazla:N` | En fazla N düzenleme yap, sonra dur |
| `-limit:N` | En fazla N sayfa tara |
| `-page:"Başlık"` | Tek sayfa |
| `-cat:"Kategori adı"` | Kategorideki sayfalar |
| `-kurallar:dosya.tsv` | Başka bir kurallar dosyası kullan |
| `-sablonlar` | Şablon içlerinde de değiştir (dikkatli kullan) |
| `-baglantilar` | Bağlantı içlerinde de değiştir; bağlantı hedefini de değiştirir (dikkatli kullan) |
| `-otomatik` | Onay sormadan kaydet. Sadece bot yetkisi olan hesapta çalışır, bu hesapta kullanılmaz. |

Diğer Pywikibot sayfa seçenekleri (`-search:`, `-file:`, `-ns:` vb.) de çalışır.

Her çalışma `duzenleme_kaydi.tsv` dosyasına yazılır. Bu dosya git'e gönderilmez.

### Acil durdurma

`Kullanıcı:KadirBalikci/Durdur` sayfasına `DUR` yazarsan çalışan bot en geç 10 sayfa içinde durur. Terminalde `Ctrl+C` de aynı işi görür.

### Git

```bash
git add -A && git commit -m "açıklama" && git push
```

`user-password.py` (şifre), `*.lwp` (oturum çerezi), `logs/`, `apicache/` ve `duzenleme_kaydi.tsv` `.gitignore` ile dışarıda tutulur.

---

## Kurallar dosyası (`duzeltmeler.tsv`)

Her satır bir kural. Sütunlar TAB ile ayrılır:

```
bul	değiştir	tip	not
```

| Tip | Davranış |
|---|---|
| `kelime` (varsayılan) | Tam kelime. `Herkez` → `Herkes` gibi büyük harfle başlayanı da düzeltir (Türkçe i/İ, ı/I doğru işlenir). |
| `kok` | Sonuna ek gelebilir: `herkezin` → `herkesin`. Başka bir kelimenin içinde tetiklenmez: `hiçbirşey` için `birşey` kuralı çalışmaz. |
| `metin` | Düz metin, kelime sınırı yok |
| `regex` | Python düzenli ifadesi, `\1` gibi gruplar kullanılabilir |

Bağlama göre değişen hatalar (ör. -de/-da ayrımı) bul-değiştirle güvenli şekilde düzeltilemez, bunları listeye ekleme.

### Bot neye dokunmaz

- Metin bölgeleri: kaynaklar (`<ref>`), şablonlar, bağlantılar (`[[...]]`), dosya ve kategori adları, URL'ler, alıntılar («», ""), yorumlar, `<nowiki>`, `<blockquote>`, `<poem>`, `<math>` vb.
- Sayfalar: yönlendirmeler, madde dışı ad alanları, korumalı sayfalar ve `{{nobots}}` içeren sayfalar.

---

## Dosyalar

| Dosya | Görevi |
|---|---|
| `bul_degistir.py` | Bot |
| `kurallar.py` | Kuralları yükler ve vikimetne güvenli şekilde uygular |
| `duzeltmeler.tsv` | Düzeltme listesi |
| `test_kurallar.py` | Çevrimdışı testler |
| `user-config.py` | Pywikibot ayarları: hesap adı, kaydetmeler arası 10 sn bekleme |
| `user-password.py.ornek` | Bot şifresi şablonu. Gerçek dosya `user-password.py`, git'e girmez. |
| `skills/vikipedi-genislet/SKILL.md` | Claude'un madde genişletme becerisi |

Bot şifresini yenilemek için `Özel:BotŞifreleri` sayfasından yeni şifre oluştur ve `user-password.py` dosyasına yaz:

```
('KadirBalikci', BotPassword('VikiTrBot', 'YENİ_ŞİFRE'))
```

Bot bayrağı gerektiren tam otomatik işler için `Vikipedi:Botlar/Başvurular` sayfasından ayrı bir bot hesabıyla başvuru yapılır.
