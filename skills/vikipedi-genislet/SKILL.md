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

## İş kaydı ve çeşitlilik (her çalışmada, aday aramadan önce)
Aynı maddeler etrafında dönmemek için iş kaydı tutulur: `/Users/kadir.balikci/PycharmProjects/vikibot/claude_kaydi.tsv` (TAB ayrılmış: tarih, beceri, madde, sonuç, not).
- **Önce kaydı oku.** Kayıtta herhangi bir beceriyle geçen bir maddeyi yeniden aday yapma; başka bir beceri için bile. İstisna: Kadir maddeyi adıyla verirse ya da "devam et" derse.
- **Çeşitlilik:** Taslak kategorisini hep aynı noktadan okuma; `gcmstart` için rastgele bir tarih seç ya da farklı konu taslak kategorilerinden (ör. `Kategori:Film taslakları`) birini rastgele al. Aynı konu alanından arka arkaya öneri yapma.
- **Sonra kaydı yaz.** Raporu verdikten sonra incelenen her madde için bir satır ekle: `tarih<TAB>genislet<TAB>madde<TAB>sonuç<TAB>kısa not`. Sonuç: `öneri`, `sorun yok`, `uygulandı` (Kadir kaydettiyse) veya `kaynak yok`. Son 7 gün kuralı vb. ile elenen maddeler yazılmaz.
- Kadir önceki bir öneriyi kaydettiyse (sayfa geçmişinde KadirBalikci düzenlemesi), ilgili satırın sonucunu `uygulandı` yap.

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

### Doğal üslup (her metinde uygula)
Amaç, metnin deneyimli bir Vikipedi editörünün elinden çıkmış gibi akıcı ve doğal okunmasıdır. YZ desteği değişiklik özetinde her zaman belirtilir; bu kurallar okunabilirlik içindir, tespit araçlarını atlatmak için değildir (kasıtlı yazım hatası, yapay çeşitlilik gibi hileler yapılmaz).
- **Kip:** Tarihî anlatımda yalın geçmiş zaman (`inşa edildi`, `satın aldı`). `-mıştır/-mektedir` yığınından kaçın; bir paragrafta en fazla bir iki kez.
- **Cümle ritmi:** Kısa ve orta cümleleri karıştır. Her cümle aynı kalıpla (özne + ... + fiil) başlamasın; ara sıra zarf, tarih veya yer tümleciyle başla ("1544'te kale...").
- **Bağlaç tekrarı yok:** Cümleleri "Ayrıca", "Bunun yanı sıra", "Öte yandan", "Bununla birlikte" ile başlatma; bağlantıyı cümlenin kendisi kursun.
- **Çeviri kokusu:** İngilizce söz dizimini taşıma. Edilgen yığını (`... tarafından ... edilmektedir`), gereksiz `olarak`, `sahip olmak` kalıbı (`altıgen bir plana sahiptir` yerine `planı altıgendir`), `bir` fazlalığı, `-ki` ile uzayan cümleler. Kaynak İngilizceyse önce anlamı kavra, sonra Türkçe düşünerek yeniden yaz; kelime kelime çevirme.
- **Somutluk:** Soyut övgü ve genelleme yerine kaynaktaki somut ayrıntı (tarih, sayı, ad, yer). Kaynakta olmayan yorum, bağlam cümlesi veya kapanış cümlesi ekleme.
- **Dolgu listesi (kullanma):** "önemli bir yere sahiptir", "dikkat çekmektedir", "büyük önem taşır", "zengin bir geçmişe sahip", "çok yönlü", "kilit rol oynadı", "ayrıca belirtmek gerekir ki", "günümüzde de ... devam etmektedir", "sonuç olarak", üçlü sıfat/isim dizileri, her maddeyi ikiye ayıran simetrik cümleler.
- **Maddeye uyum:** Eklenen metin mevcut maddenin kipine, terim tercihine (ör. "Muhammed", "Kâbe"), yazım biçimine ve paragraf uzunluğuna uysun; ayrı bir elden çıkmış gibi durmasın.
- **Son okuma:** Metni teslim etmeden önce bir kez baştan oku: yukarıdaki listedeki kalıpları tara, aynı kelimeyle başlayan ardışık cümleleri düzelt, sesli okununca takılan yeri sadeleştir.

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