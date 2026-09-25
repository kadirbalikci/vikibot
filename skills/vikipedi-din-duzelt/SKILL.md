---
name: vikipedi-din-duzelt
description: Kadir 'din maddesi düzelt', 'dini madde düzelt' veya /vikipedi-din-duzelt dediğinde: tr.wikipedia'daki İslam konulu maddelerde yanlış/absürt bilgileri ve eksik genel kabul bilgilerini bulup sağlam kaynaklı düzeltme/ekleme hazırla ve düzenleme sayfasını aç.
---

# Türkçe Vikipedi dini madde düzeltme

Kadir ile anlaşılan iş akışı. Ben (Claude) aday bulur, sorunları tespit eder, kaynaklı metni hazırlar, sayfayı açarım; **metni ekleyip kaydeden her zaman Kadir'dir.** Vikipedi'de asla kendim düzenleme kaydetmem.

## Amaç ve ölçüt
Üç tür iş yapılır:
1. **Olgu hatası düzeltme:** İslami konularda açıkça yanlış veya absürt bilgi. Örnek: Miraç maddesinde Kâbe'nin Ürdün'de olduğunun yazılması. Diğer örnekler: yanlış sure/ayet numarası, hadisin yanlış kitaba/raviye atfı, bir mezhebin görüşünün ters aktarılması, yanlış hicri/miladi tarih, bir âlime ait olmayan söz.
2. **Marjinal görüşü olgu gibi sunma:** Akademide de kabul görmeyen bir iddia (ör. Kâbe'nin/ilk kıblenin Petra'da olduğu tezi) kesin bilgi gibi yazılmışsa, genel kabul bilgi olarak yazılır; marjinal görüş istenirse yalnızca atıfla ve marjinal olduğu belirtilerek kalır (Vikipedi: orantısız ağırlık).
3. **Eksik genel kabul bilgisini ekleme:** Üzerinde geniş ittifak olan temel bilgi maddede yoksa kaynaklı olarak eklenir.

**Dokunulmayacaklar:** Kaynaklı farklı görüşler (mezhepler arası farklar, akademik/tarihsel-eleştirel görüşler) silinmez veya değiştirilmez. Eksik kalan İslami görüş, silme yapmadan "İslami kaynaklara göre..." gibi atıfla eklenir. Vikipedi'de bir dinin bakış açısıyla yazmak (vaaz dili, "şüphesiz", "hak din" vb.) yok; bilgi her zaman ansiklopedik ve atıflı.

## Argümanlar
- Konu/madde verilirse (ör. `din maddesi düzelt: Miraç`) doğrudan o madde(ler) incelenir; verilmezse kategorilerden aday seçilir.
- Sayı verilirse o kadar madde incelenir; verilmezse 3 madde incelenip sorun bulunanlar raporlanır.

## 1. Aday bulma
Vikipedi API'sine `curl` ile erişilir (Python urllib bu makinede SSL hatası veriyor; Türkçe karakterli parametreler için `curl -G --data-urlencode` kullan, User-Agent ver):
- Kategoriler: `Kategori:İslam`, `Kategori:İslam tarihi`, `Kategori:Sahabeler`, `Kategori:Peygamberler`, `Kategori:Fıkıh`, `Kategori:İslami terimler`, `Kategori:Hadis`, `Kategori:Kur'an` ve alt kategorileri.
- Eleme: yaşayan kişiler, son 7 günde düzenlenmiş maddeler, tartışma sayfasında süren bir anlaşmazlık olan maddeler, koruma altındaki maddeler (`prop=info&inprop=protection`).
- Önce çok okunan ve kısa/orta uzunluktaki maddeler: hata etkisi yüksek, kontrolü mümkün.

## 2. Analiz
- Maddenin güncel vikimetnini oku (`prop=revisions&rvprop=content|timestamp&rvslots=main`).
- Her olgusal iddiayı (yer, tarih, kişi, ayet/hadis atfı, hüküm) tek tek kontrol listesine çıkar ve üç türden birine veya "sorun yok"a ayır.
- Şüpheli bir cümlenin **ne zaman ve kim tarafından eklendiğine** bak (sayfa geçmişi). Yakın zamanda anonim eklenmişse vandalizm olabilir: bu durumda Kadir'e "geri alma" seçeneğini de öner.
- Kaynaklı ama yanlış görünen bir bilgide önce kaynağı aç: kaynak gerçekten öyle mi diyor, yoksa yanlış mı aktarılmış?

## 3. Kaynak araştırması
Kaynaklar internetten gerçekten açılır ve ifadenin kaynakta geçtiği doğrulanır. Açılamayan kaynak kullanılmaz; URL, sayfa, yazar, tarih asla tahmin edilmez veya uydurulmaz.
Tercih sırası:
- **TDV İslâm Ansiklopedisi** (islamansiklopedisi.org.tr): madde yazarı ve cilt/sayfa bilgisiyle.
- **Akademik kaynaklar:** Encyclopaedia of Islam (Brill), Encyclopaedia Britannica, hakemli makaleler (DergiPark, JSTOR açık erişim).
- **Birincil metinler:** Kur'an ayetleri için Diyanet Kur'an Yolu meali (kuran.diyanet.gov.tr) ile sure:ayet numarası; hadisler için sunnah.com veya Hadislerle İslam (Diyanet) ile kitap ve numara. Birincil metin tek başına yorum için kullanılmaz, yalnızca "şu ayette şöyle geçer" türü olgu için.
- Kaçınılacaklar: fetva/vaaz siteleri, kişisel bloglar, forumlar, mezhep veya cemaat propaganda siteleri, YZ üretimi içerik siteleri.
- Tartışmalı olmayan temel bilgi için bile en az bir bağımsız, güvenilir kaynak; "geniş ittifak" iddiası için bunu açıkça söyleyen bir kaynak (ör. TDV'de "İslam âlimlerinin çoğunluğuna göre...").

## 4. Yazım ve biçem kuralları
- Doğal, sade, ansiklopedik Türkçe. Tarafsız ton; dua/tazim ifadeleri (s.a.v., r.a., "Hazreti") metne eklenmez, maddede zaten varsa ellenmez.
- YZ dolgu kalıplarından kaçın: "önemli bir yere sahiptir", "dikkat çekmektedir", "büyük önem taşır", üçlü sıfat dizileri, sonuç/özet cümleleri.
- Noktalama: düz tırnak `"` ve düz kesme `'`; akıllı tırnak ve uzun/yarım tire yok (aralıklarda `1920-1925`). Üç nokta `...`.
- Tarih: `12 Mart 1998`; hicri tarih verilirse miladi karşılığıyla (`H. 11 / M. 632`).
- Özel adlara gelen ekler kesme ile: `Kâbe'nin`, `Mekke'de`.
- İç bağlantılar `[[...]]` yalnızca var olan Türkçe maddelere (API ile kontrol et) ve ilk geçtiği yerde.
- Kaynak biçimi: `<ref>{{Web kaynağı |url= |başlık= |erişimtarihi= |yayıncı= |tarih= |yazar= |dil=tr}}</ref>`; TDV için yazar, cilt, sayfa varsa `{{Ansiklopedi kaynağı}}` veya `{{Kitap kaynağı}}`. Aynı kaynak tekrarı için `<ref name="...">`.

## 5. Kadir'e çıktı biçimi
Her madde için:
1. **Madde:** bağlantısı, son düzenleme tarihi.
2. **Sorunlu kısım:** maddedeki mevcut cümle aynen alıntılanır, hangi bölümde olduğu.
3. **Tür:** olgu hatası / marjinal görüş olgu gibi / eksik genel kabul bilgisi. Vandalizm şüphesi varsa ekleyen düzenleme ve tarihi.
4. **Önerilen vikimetin:** tek kod bloğunda, kopyalanmaya hazır; neyin yerine geçeceği açıkça belirtilir.
5. **Kaynak kontrolü:** her kaynak için "açıldı, şu ifade destekliyor" notu (kaynaktaki ilgili ifade kısa alıntıyla).
6. **Değişiklik özeti (hazır):** düzeltme için `Kaynaklı düzeltme: <kısa açıklama> (YZ destekli, kaynaklar kontrol edildi)`; ekleme için `Kaynaklı ekleme: <kısa açıklama> (YZ destekli, kaynaklar kontrol edildi)`. YZ ibaresi her zaman verilir, çıkarılmasını önermem.
7. **Tartışma sayfası notu (gerekirse):** silme veya büyük değişiklik içeren düzeltmelerde tartışma sayfasına yazılabilecek kısa gerekçe metni.

Sorun bulunmayan maddeler için tek satır: "incelendi, sorun bulunmadı".

## 6. Sayfayı açma
Düzenleme sayfasını açar: `https://tr.wikipedia.org/w/index.php?title=<Madde>&action=edit` (bölüm biliniyorsa `&section=N`). Tarayıcı paneli (Claude_Browser) varsa orada, yoksa `open "<url>"` ile varsayılan tarayıcıda. Metni yapıştırma, kaydetme veya form gönderme Kadir'indir.

## Sınırlar
- Kaynaklı farklı görüşleri silmem veya zayıflatmam; yalnızca eksik görüşü atıflı eklerim.
- Maddeyi baştan yazmam; hedefli düzeltme ve kısa ekleme (1-3 cümle) yaparım, Kadir "daha uzun" demedikçe.
- Emin olmadığım bir iddiayı "yanlış" diye işaretlemem; "doğrulanamadı" olarak raporlarım.
- YZ desteğini gizlemeye yönelik değişiklik yapmam.
- Kadir itiraz alırsa (geri alma, tartışma mesajı) öncelik onu çözmek.
