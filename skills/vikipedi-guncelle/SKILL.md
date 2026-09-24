---
name: "vikipedi-guncelle"
description: "Kadir 'madde güncelle', 'güncelleme yap' veya /vikipedi-guncelle dediğinde: tr.wikipedia'da eskimiş bilgi bulup güncel kaynakla düzeltme öner ve düzenleme sayfasını aç."
---

# Türkçe Vikipedi madde güncelleme

Genişletmeden farkı: yeni bilgi eklemek değil, maddede **eskimiş/yanlış hale gelmiş bir bilgiyi** güncel, güvenilir bir kaynakla düzeltmek. Ben (Claude) aday bulur, değişikliği hazırlar, sayfayı açarım; **metni değiştirip kaydeden her zaman Kadir'dir.** Vikipedi'de asla kendim kaydetmem.

## Argümanlar
- Madde adı verilirse (ör. `madde güncelle: Ankara`) yalnızca o maddeyi incele.
- Konu verilirse (ör. `madde güncelle: futbol`) adayları o alandan seç.
- Sayı verilirse o kadar öneri; verilmezse 1. Başlangıçta her öneri **tek bir bilgi** (bir sayı, bir isim, bir cümle) olsun.

## 1. Aday bulma
Tarayıcı panelini (Claude_Browser) tr.wikipedia.org'da aç, sayfa içinde `fetch` ile API'yi kullan (bulut ortamı Vikipedi'ye erişemiyor). Kaynaklar, öncelik sırasıyla:
1. `{{Güncelle}}` etiketli maddeler: `Kategori:Güncellenmesi gereken tüm maddeler` / `Kategori:Güncellenmesi gereken maddeler`. Tartışma sayfasında ve sayfa geçmişinde neyin güncellenmesi istendiğine bak.
2. Zamana bağlı ifadeler içeren maddeler: `insource:` aramasıyla `"itibarıyla"` + eski yıl, `"hâlen"`, `"hâlâ"`, `"günümüzde"`, `"şu anda"`, `{{Ne zaman}}`.
3. Bilgi kutusundaki değerleri Vikiveri ile karşılaştır (nüfus, görevdeki kişi, kulüp, stadyum kapasitesi vb.); farklıysa ve Vikiveri değerinin kaynağı varsa aday.
Eleme: yaşayan kişilerin hassas bilgileri (sağlık, hukuki durum, ölüm haberi), tartışmalı/siyasi konular, son 7 günde düzenlenmiş veya değişiklik savaşı olan maddeler, koruma altındaki sayfalar.

## 2. Değişikliği hazırlama
- **Güncel ve güvenilir bir kaynak bul ve tarayıcıda aç:** resmî kurum (TÜİK, bakanlıklar, belediye, federasyon, şirketin kendi sitesi/faaliyet raporu), güvenilir haber ajansı/gazete. Blog, forum, sosyal medya, Vikipedi'nin kendisi kaynak değildir.
- PDF raporlar tarayıcıda metin olarak okunamazsa sayfa içinde pdf.js (cdnjs) ile metni çıkar.
- Kaynakta yeni değerin açıkça geçtiğini doğrula; tarihini not et. Kaynak bulunamazsa öneri yapma, Kadir'e "kaynak bulamadım" de.
- Siteyi arka arkaya çok sorgulama (WAF engeli); bir iki okuma yeterli. Engellenirsem Kadir'e linki kendisinin açıp kontrol etmesini söyle.
- Eski bilgi silinmez, **geçmiş bilgi olarak değerliyse dönüştürülür** (ör. "2015'te nüfusu X iken 2024'te Y'ye ulaştı"). Aksi halde yalnızca değer ve kaynak değiştirilir.
- Tarih belirt: "2024 itibarıyla", "Mart 2026'da" gibi. "Hâlâ", "günümüzde", "mevcut" gibi zamanla eskiyen ifadeleri kullanma.
- Eski kaynağı yalnızca yeni bilgi onu geçersiz kılıyorsa kaldır; geçmiş bilgiyi destekliyorsa bırak.
- `{{Güncelle}}` etiketi, maddedeki istenen güncelleme tamamen yapıldıysa kaldırılabilir; kısmi güncellemede kalsın.
- URL/tarih/yazar asla tahmin edilmez, kaynak uydurulmaz. İç bağlantı vermeden önce Türkçe Vikipedi'de maddenin var olduğunu kontrol et.

## 3. Yazım ve biçem kuralları
- Doğal, sade, tarafsız ansiklopedik Türkçe; YZ dolgu kalıpları yok ("önemli bir yere sahiptir", "dikkat çekmektedir" vb.).
- Düz tırnak `"` ve kesme `'`; akıllı tırnak, uzun tire (—) ve yarım tire (–) yok (aralıklar `2020-2024`).
- Tarih `12 Mart 2026`; binlik ayırıcı nokta, ondalık virgül; yüzde `%81,59'u`.
- Kaynak: `<ref>{{Web kaynağı |url= |başlık= |yayıncı= |tarih= |erişimtarihi= |dil=}}</ref>` (Türkçe kaynakta `dil` gerekmez).
- Maddede Kaynakça bölümü yoksa `== Kaynakça ==` + `{{Kaynakça}}` eklemeyi öner.

## 4. Kadir'e çıktı biçimi
Her öneri için:
1. **Madde:** bağlantısı ve neden aday olduğu (etiket / eski tarihli ifade / Vikiveri farkı).
2. **Eskimiş bilgi:** maddedeki mevcut metin, olduğu gibi, Cmd+F ile bulunacak anahtar ifadeyle.
3. **Yerine yazılacak vikimetin:** tek kod bloğunda, kopyalanmaya hazır.
4. **Kaynak kontrolü:** kaynak açıldı, yayın tarihi, yeni değeri destekleyen ifade.
5. **Değişiklik özeti (hazır):** `Bilgi güncellendi: <ne> (YZ destekli, kaynak kontrol edildi)`. Vikipedi:Büyük dil modelleri gereği YZ desteği özette belirtilir; bu satır her zaman verilir.
6. Maddede fark ettiğim başka eskimiş bilgiler varsa tek satırla not et (bir sonraki öneri için).

## 5. Sayfayı açma
Tarayıcı panelinde `https://tr.wikipedia.org/w/index.php?title=<Madde>&action=edit` (bölüm biliniyorsa `&section=N`) aç ve sekmeyi öne getir; `tabs_context` ile panelin görünür olduğunu kontrol et, gizliyse Kadir'e Cmd+Shift+B ile açmasını söyle. `mw.config.get('wgUserName')` ile oturumun `KadirBalikci` olarak açık olduğunu kontrol et; kapalıysa uyar (IP ile düzenleme yapılmasın). Metni yapıştırma, kaydetme, form gönderme Kadir'indir.

## Sınırlar
- Tek seferde tek bilgi; toplu güncelleme bot işidir ve ayrı onay ister.
- Kaynaksız güncelleme önermem; emin olmadığım bilgide "doğrulayamadım" derim.
- YZ desteğini gizlemeye yönelik değişiklik yapmam.
- Kadir itiraz alırsa (geri alma, tartışma mesajı) öncelik onu çözmek.