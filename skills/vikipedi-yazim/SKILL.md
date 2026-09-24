---
name: "vikipedi-yazim"
description: "Kadir 'yazım kuralı ekle', 'yazım tara' veya /vikipedi-yazim dediğinde: tr.wikipedia için yeni bul-değiştir kuralları bul/test et, duzeltmeler.tsv'ye ekle ve çalıştırılacak bot komutunu ver."
---

# Türkçe Vikipedi yazım düzeltme kuralları

Bot: `~/PycharmProjects/vikibot` (Mac, bağlı klasör). Kurallar `duzeltmeler.tsv` dosyasında (`bul<TAB>değiştir<TAB>tip<TAB>not`; tipler: kelime, kok, metin, regex). Botu **Kadir kendi Terminal'inde çalıştırır**; benim ortamım Vikipedi'ye bağlanamaz, ben Vikipedi'ye yalnızca tarayıcı paneli (Claude_Browser) üzerinden okuma yaparım.

## Komutlar
- `yazım kuralı ekle: X → Y` (birden fazla olabilir): verilen kuralı doğrula, ekle.
- `yazım tara` / `yazım tara: 5`: yeni kural adayları bul (varsayılan 5), Kadir onayladıklarını ekle.

## 1. Aday bulma (`yazım tara`)
- Aday kaynakları: TDK'nın sık yapılan yanlışları (bitişik/ayrı yazılan kelimeler: "herkez", "yanlız", "birşey", "herbir", "hiçbir zaman" vs. "hiç bir", "birkaç" vs. "bir kaç", "yalnış", "orjinal", "entellektuel", "süpriz" vs. "sürpriz" gibi), duzeltmeler.tsv'de henüz olmayanlar.
- Doğru biçimi TDK Güncel Türkçe Sözlük / Yazım Kılavuzu'ndan (sozluk.gov.tr) tarayıcıda kontrol et; emin olamadığını önerme.
- **Bağlama göre değişen hataları asla kural yapma**: -de/-da, -ki, mi soru eki, "değil mi", büyük/küçük harf, özel ad olabilecek kelimeler, eski yazımın alıntıda korunması gereken durumlar.

## 2. Her aday için doğrulama
Tarayıcı panelinde tr.wikipedia.org açıkken sayfa içi `fetch` ile:
1. `list=search&srsearch=insource:"X"&srnamespace=0&srinfo=totalhits` ile madde sayısını bul.
2. 5-10 örnek maddenin vikimetninde geçtiği yerleri (çevresindeki ~60 karakterle) göster.
3. Yanlış pozitif ara: özel ad, eser adı, alıntı, başka kelimenin parçası, başka dil. Varsa kural tipini daralt (`kok` yerine `kelime`) ya da kuralı önerme.
4. Tip seç: ekli halleri de yanlışsa ve güvenliyse `kok`, değilse `kelime`.

## 3. Kadir'e çıktı
Tablo: `yanlış → doğru | tip | madde sayısı | yanlış pozitif riski | kaynak (TDK)`. Altında 2-3 örnek bağlam. Kadir hangilerini onayladığını söyleyene kadar dosyaya ekleme (`yazım kuralı ekle` komutunda Kadir kuralı zaten vermiştir; doğrulamada sorun yoksa ekle, sorun varsa önce sor).

## 4. Ekleme
- `device_bash` ile `~/mnt/PycharmProjects/vikibot/duzeltmeler.tsv` sonuna TAB ile ayrılmış satır ekle (`printf` ile, gerçek TAB karakteri). Aynı kural varsa ekleme.
- `kurallar.py`'nin yükleyebildiğini kontrol et: `python3 -c "from kurallar import kurallari_yukle as k; print(len(k('duzeltmeler.tsv')))"` (pywikibot yoksa `PYWIKIBOT_NO_USER_CONFIG=1` ve gerekirse sadece TSV'yi sütun sayısı için kontrol et).
- Git commit: `git -c safe.directory=* commit -am "Yazım kuralı: X → Y"`. Push'u Kadir yapar.

## 5. Çalıştırma komutlarını ver
Yeni kuralları sadece onlar için denemek üzere geçici bir kural dosyası oluşturabilirsin (`yeni_kurallar.tsv`) ve Kadir'e şu sırayla ver (açıklamasız, zsh `#` hatası yüzünden):
```
cd ~/PycharmProjects/vikibot
python3 bul_degistir.py -kurallar:yeni_kurallar.tsv -limit:5
python3 bul_degistir.py -kurallar:yeni_kurallar.tsv -canli -enfazla:5
```
Önce deneme modu, farkları Kadir kontrol eder; sonra canlı mod (her düzenlemede y/n onayı). `-otomatik` önermem (hesabın bot yetkisi yok). Kadir çıktıyı yapıştırırsa yanlış pozitifleri incele ve gerekirse kuralı daralt.

## Sınırlar
- Tartışmalı veya bağlama bağlı düzeltme yok; yalnızca TDK'ya göre kesin yanlış olanlar.
- Yüksek hacimli düzenleme bot gibi sayılabilir: canlı modda tek seferde küçük partiler (`-enfazla:5`-`20`) öner.