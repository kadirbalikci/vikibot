---
name: "vikipedi-genislet"
description: "Kadir 'madde genişlet', 'genişletme yap' veya /vikipedi-genislet dediğinde: tr.wikipedia taslaklarından aday bulup kaynaklı, kurallara uygun kısa ekleme hazırla ve düzenleme sayfasını aç."
---

# Türkçe Vikipedi madde genişletme

Kadir ile anlaşılan iş akışı. Ben (Claude) aday bulur, metni hazırlar, sayfayı açarım; **metni ekleyip kaydeden her zaman Kadir'dir.** Vikipedi'de asla kendim düzenleme kaydetmem.

## Argümanlar
- Konu/kategori verilirse (ör. `madde genişlet: giyim`) adayları oradan seç, verilmezse genel taslaklardan.
- Sayı verilirse (ör. `3 madde`) o kadar öneri hazırla; verilmezse 1.
- Uzunluk: aksi söylenmedikçe **kısa ekleme (1–3 cümle)**. Kadir "daha uzun" diyene kadar kısa kal.

## 1. Aday bulma
Tarayıcı panelini (Claude_Browser) tr.wikipedia.org'da aç ve sayfa içinde `fetch` ile API'yi kullan (bulut ortamı Vikipedi'ye erişemiyor):
- `Kategori:Tüm taslak maddeler` (ns 0) üyelerini `generator=categorymembers` ile çek, `prop=info|langlinks&lllang=en` (gerekirse `de`).
- İngilizce karşılığının uzunluğunu `en.wikipedia.org/w/api.php?origin=*` ile al.
- En/tr uzunluk oranı yüksek olanları öne al. Eleme: yaşayan kişiler (BLP riskli, ilk aşamada atla), tartışmalı/siyasi konular, zaten `{{Çeviri}}`/`{{Birleştir}}` vb. bakım şablonu olanlar, son 7 günde düzenlenmiş olanlar.

## 2. Metni hazırlama
- Kaynak madde İngilizce (veya başka dil) Vikipedi'deki karşılığıdır; **yalnızca kaynaklı cümleleri** al. Kaynaksız bilgiyi ekleme.
- Kaynakları gerçekten aç (tarayıcıda) ve cümlenin kaynakta geçtiğini doğrula. Erişilemeyen/ölü kaynak kullanma. Kontrol sonucunu Kadir'e yaz.
- Türkçe maddede zaten olan bilgiyi tekrar etme; önce mevcut metni oku.
- Tek bir kaynak uydurma, URL/tarih/yazar bilgisini asla tahmin etme.

## 3. Yazım ve biçem kuralları
- Doğal, sade, ansiklopedik Türkçe. Tarafsız ton, abartı ve süs yok.
- Kaçınılacak YZ kalıpları: "önemli bir yere sahiptir", "dikkat çekmektedir", "ayrıca belirtmek gerekir ki", "zengin bir geçmişe sahip", "çok yönlü", "günümüzde de ... devam etmektedir" türü dolgu; üçlü sıfat dizileri; sonuç/özet cümleleri.
- Noktalama: düz tırnak `"` ve düz kesme `'`; akıllı tırnak (“ ” ‘ ’), uzun tire (—) ve yarım tire (–) kullanma (aralıklarda `1920-1925`). Üç nokta `...` olarak.
- Tarih: `12 Mart 1998`; yüzyıl `19. yüzyıl`. Sayılarda binlik ayırıcı nokta, ondalık virgül.
- Özel adlara gelen ekler kesme ile: `Stetson'ın`.
- İç bağlantılar `[[...]]`, yalnızca Türkçe Vikipedi'de var olan maddelere (kontrol et) ve ilk geçtiği yerde.
- Kaynak biçimi: `<ref>{{Web kaynağı |url= |başlık= |erişimtarihi= |yayıncı= |tarih= |dil=en}}</ref>` veya `{{Kitap kaynağı |soyadı= |ad= |başlık= |yıl= |yayıncı= |sayfa= |isbn=}}`. Aynı kaynak tekrarı için `<ref name="...">`.

## 4. Kadir'e çıktı biçimi
Her öneri için:
1. **Madde:** bağlantısı, mevcut uzunluk, karşılık madde.
2. **Nereye:** hangi bölüm / hangi cümleden sonra.
3. **Eklenecek vikimetin:** tek kod bloğunda, kopyalanmaya hazır.
4. **Kaynak kontrolü:** her kaynak için "açıldı, şu ifade destekliyor" notu.
5. **Değişiklik özeti (hazır):** `İngilizce Vikipedi'den genişletme (YZ destekli, kaynaklar kontrol edildi)` — Vikipedi:Büyük dil modelleri YZ destekli düzenlemelerin özette belirtilmesini istiyor; bu satır her zaman verilir, çıkarılmasını önermem.

## 5. Sayfayı açma
Tarayıcı panelinde `https://tr.wikipedia.org/w/index.php?title=<Madde>&action=edit` (bölüm biliniyorsa `&section=N`) aç. Paneli gösterip göstermediğini `tabs_context` ile kontrol et; gizliyse Kadir'e Cmd+Shift+B ile açmasını söyle. Metni yapıştırma, kaydetme veya form gönderme — bunlar Kadir'in.

## Sınırlar
- Tam madde yazmam, sıfırdan madde açmam; yalnızca mevcut taslağa kaynaklı ekleme.
- YZ desteğini gizlemeye yönelik değişiklik yapmam; "insansı" yazım okunabilirlik ve biçem içindir.
- Kadir itiraz alırsa (geri alma, tartışma sayfası mesajı) öncelik onu çözmek.