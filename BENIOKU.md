# Vikipedi bul-değiştir botu (tr.wikipedia)

Pywikibot tabanlı, yazım hatalarını toplu düzelten bot. **Varsayılan olarak deneme modunda çalışır** — `-canli` vermediğiniz sürece hiçbir şey kaydetmez.

## Dosyalar

| Dosya | Görevi |
|---|---|
| `bul_degistir.py` | Botun kendisi |
| `kurallar.py` | Kuralları yükler ve vikimetne güvenli şekilde uygular |
| `duzeltmeler.tsv` | Düzeltme listesi (`bul⇥değiştir⇥tip⇥not`) |
| `user-config.py` | Pywikibot ayarları (bot adı, hız sınırı) |
| `user-password.py.ornek` | Bot şifresi şablonu |
| `test_kurallar.py` | Çevrimdışı testler |

## Kurulum

```bash
pip install pywikibot pytest
cd vikibot
python -m pytest -q test_kurallar.py   # 12 test geçmeli
```

## Hesap ve izinler (sırayla)

1. Ayrı bir **bot hesabı** açın (ör. `KadirBot`), kullanıcı sayfasına sahibinin siz olduğunu ve ne yaptığını yazın.
2. Bot hesabıyla girip `Özel:BotŞifreleri` sayfasından bir bot şifresi oluşturun (“Yüksek hacimli düzenleme” ve “Mevcut sayfaları düzenle” izinleri yeterli).
3. `user-config.py` içinde `BOT_HESAP_ADI` yerine hesap adını yazın; `user-password.py.ornek` dosyasını `user-password.py` adıyla kopyalayıp doldurun.
4. **Vikipedi:Botlar/Başvurular** sayfasından bot bayrağı başvurusu yapın. Onay gelene kadar yalnızca deneme modunda veya `-canli` ile (her düzenlemeyi tek tek onaylayarak) az sayıda deneme düzenlemesi yapın.
5. Acil durdurma: `Kullanıcı:KadirBot/Durdur` sayfasına `DUR` yazılırsa bot 10 sayfa içinde durur. Başvuruda bunu belirtmek iyi olur.

## Kullanım

```bash
python bul_degistir.py                            # tüm kurallar için arama + farkları göster
python bul_degistir.py -page:"Ankara"             # tek sayfada dene
python bul_degistir.py -cat:"Türk yazarlar" -limit:50
python bul_degistir.py -limit:10 -canli           # kaydeder, her düzenlemede sorar
python bul_degistir.py -canli -otomatik -enfazla:100   # yalnızca bot bayrağı alındıktan sonra
```

Her çalışma `duzenleme_kaydi.tsv` dosyasına yazılır.

## Kural tipleri

- `kelime` (varsayılan): Tam kelime; `Herkez` → `Herkes` gibi baş harfi büyük olanı da düzeltir (Türkçe i/İ, ı/I doğru işlenir).
- `kok`: Sonuna ek gelebilir: `herkezin` → `herkesin`. Başka bir kelimenin içinde tetiklenmez (`hiçbirşey` ≠ `birşey`).
- `metin`: Düz metin, kelime sınırı yok.
- `regex`: Python düzenli ifadesi, `\1` gibi gruplar kullanılabilir.

## Bot neye dokunmaz

Kaynaklar (`<ref>`), şablonlar, bağlantılar (`[[...]]`), dosya/kategori adları, URL'ler, alıntılar («», ""), yorumlar, `<nowiki>`, `<blockquote>`, `<poem>`, `<math>` vb. Ayrıca yönlendirmeler, madde dışı ad alanları, korumalı sayfalar ve `{{nobots}}` içeren sayfalar atlanır.

Şablon içlerinde de düzeltme için `-sablonlar`, bağlantı etiketlerinde de düzeltme için `-baglantilar` verin (dikkatli kullanın: bağlantı hedefi de değişir).
