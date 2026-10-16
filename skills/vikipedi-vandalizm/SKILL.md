---
name: vikipedi-vandalizm
description: Kadir 'vandalizm tara', 'vandalizm avı' veya /vikipedi-vandalizm dediğinde: tr.wikipedia'da gözden kaçmış, uzun süredir duran (kalıcı) vandalizmi bulur; farkı inceleyip sınıflandırır, geri alma bağlantısı, uyarı ve gerekiyorsa engelleme talebi metnini hazırlar ve sayfayı açar.
---

# Türkçe Vikipedi kalıcı vandalizm avı

Kadir ile anlaşılan iş akışı. Ben (Claude) adayları bulur, farkları inceler, geri alma bağlantısını ve uyarı metnini hazırlarım; **geri almayı, uyarıyı ve bildirimi kaydeden her zaman Kadir'dir.** Vikipedi'de asla kendim düzenleme kaydetmem.

**Amaç:** Vandalizmle mücadeleye düzenli ve temkinli katkı; ileride devriyelik başvurusu ([[Vikipedi:Devriyelik başvurusu]]) için temiz bir kayıt. Hizmetliler başvuruda niceliğe değil isabete bakar: yanlış geri alma, eksik uyarı veya içerik anlaşmazlığını vandalizm saymak başvuruyu zayıflatır. Bu yüzden **şüpheli her vakada temkinli taraf seçilir** ve son kararı Kadir farkı kendisi okuyarak verir.

**Kapsam (şimdilik):** Yalnızca *kalıcı* vandalizm: en az 24 saattir duran, kimsenin geri almadığı düzenlemeler. Anlık son değişiklik devriyesine girilmez (Huggle kullanan devriyelerle hız yarışı yapılmaz).

## İş kaydı ve çeşitlilik (her çalışmada, aday aramadan önce)
Kayıt dosyası: `/Users/kadir.balikci/PycharmProjects/vikibot/claude_kaydi.tsv` (TAB ayrılmış: tarih, beceri, madde, sonuç, not).
- **Önce kaydı oku.** Kayıtta geçen maddeyi yeniden aday yapma (Kadir adıyla verirse ya da "devam et" derse hariç).
- **Çeşitlilik:** Her çalışmada arama yöntemlerinden (aşağıda A, B, C, D) en az ikisini kullan; aynı kalıpla arka arkaya arama yapma. Aynı konu alanından (ör. üç futbol maddesi) arka arkaya vaka önerme.
- **Sonra kaydı yaz:** `tarih<TAB>vandalizm<TAB>madde<TAB>sonuç<TAB>not`. Sonuç: `geri alma önerisi`, `iyi niyetli`, `zaten düzeltilmiş`, `içerik anlaşmazlığı`, `uygulandı` (Kadir kaydettiyse). Notta fark numarası (diff) ve kullanıcı adı yer alsın.

## Argümanlar
- Sayı verilirse (ör. `vandalizm tara: 5`) o kadar *doğrulanmış* vaka hedeflenir; verilmezse 3.
- Madde verilirse (ör. `vandalizm tara: Ankara`) yalnızca o maddenin geçmişi incelenir.
- `vandalizm tara: bizim maddeler` → yalnızca iş kaydındaki ve botun `duzenleme_kaydi.tsv`'sindeki maddelerde, Kadir'in düzenlemesinden sonra gelen değişikliklere bakılır.

## 1. Aday bulma
Vikipedi API'sine `curl` ile erişilir (User-Agent ver; Türkçe parametreler için `-G --data-urlencode`).

**A. Metin kalıpları (`insource:`):** Tipik vandal ifadeleri ana ad alanında aranır. Örnek kalıplar (her çalışmada farklı birkaçını seç):
- Hakaret/övünme: `insource:/[A-ZÇĞİÖŞÜa-zçğıöşü]+ (salaktır|aptaldır|gerizekalıdır|kraldır)/`, `"kral benim"`, `"en iyisi benim"`, `"buraya yazdım"`
- Klavye karalaması: `insource:/asdasd|sdfsdf|qweqwe|ahsdj|kdfjg/`, `insource:/[a-zğüşıöç]{0,2}(sjd|jkl|hjk){2,}/`
- Kendini tanıtma: `insource:"bu madde"` + `"tarafından yazıldı"`, `"bu sayfayı ben"`, `"selam millet"`, `"merhaba arkadaşlar"`
- Küfür içeren yaygın kalıplar (bulunan vaka yaşayan kişiyse öncelikli).

Arama sonucunda gelen her maddede eşleşmenin **ne zaman ve kim tarafından** eklendiğini sayfa geçmişinden bul (`prop=revisions`, ilgili metni içeren ilk sürüm). Kaynaklı alıntı, şarkı sözü, dergi adı vb. meşru kullanımları ele.

**B. Eski, yüksek riskli, geri alınmamış düzenlemeler (ORES):** `list=recentchanges` ile 1-30 gün öncesi aralığından (`rcstart`/`rcend`) madde ad alanındaki bot dışı düzenlemeler, `rcprop=oresscores|tags|user|ids|sizes`. Ölçüt: `damaging` > 0,85 **ve** `goodfaith` < 0,4, `mw-reverted` etiketi yok. Sonra o düzenlemenin metninin sayfada **hâlâ durup durmadığını** kontrol et (sonraki sürümlerde düzeltilmiş olabilir).

**C. Sessiz sayı/olgu değişiklikleri:** Geçici hesap/IP'nin kaynak eklemeden bilgi kutusundaki sayıyı, tarihi, skoru, nüfusu değiştirdiği ve öyle kaldığı düzenlemeler (B'deki listeden `sizes` farkı küçük olanlar). Bunlar yalnızca **güvenilir bir kaynakla** eski değerin doğru olduğu gösterilebiliyorsa vandalizm sayılır; aksi halde "doğrulanamadı" denir, öneri yapılmaz.

**D. Süzgeç etiketli, geri alınmamış düzenlemeler (en verimli kaynak):** `list=recentchanges` içinde `rctag=potansiyel vandalizm` (ve benzeri süzgeç etiketleri) ile 1-30 gün öncesi; `mw-reverted` etiketi olmayanlar. 17 Ekim 2026 denemesinde tek gerçek vaka buradan geldi; ORES eşikleri tek başına çoğunlukla iyi niyetli dizi/oyuncu düzenlemeleri getiriyor.

**Eleme:** Koruma altındaki sayfalar, son 7 günde birden fazla geri almanın yaşandığı sayfalar (değişiklik savaşı), tartışma sayfasında süren anlaşmazlık.

## 2. Sınıflandırma (her aday için farkı oku)
Farkı `action=compare` ile al ve şu sınıflardan birine koy:
1. **Açık vandalizm:** Hakaret, küfür, anlamsız karalama, içerik silme (gerekçesiz bölüm boşaltma), açıkça yanlış bilgiyi bilerek ekleme, reklam/spam. → geri alma önerisi.
2. **Test düzenlemesi:** "deneme", tek harf, rastgele biçim kodu. → geri alma önerisi, uyarı olarak `Ku-vandalizm1` (yumuşak dil).
3. **İyi niyetli hata:** Yanlış yere yazılmış ama yapıcı amaçlı bilgi, biçim bozulması, kaynaksız ama makul ekleme. **Çeviri artığı:** karalama, sayfayı çeviri aracıyla oluşturan kullanıcının kendi ilk düzenlemelerinde duruyorsa (`contenttranslation` etiketi) neredeyse her zaman artık metindir. → **vandalizm değil.** Geri alma yerine düzeltme öner; uyarı yok, gerekirse dostça not.
4. **İçerik anlaşmazlığı / görüş farkı:** Kaynaklı değişiklik, ifade tercihi, siyasi/dinî ton farkı. → **asla vandalizm denmez**, öneri yapılmaz; rapora tek satır not.
5. **Emin değilim:** Öneri yapılmaz, "doğrulanamadı" olarak raporlanır.

## 3. Güncel durum ve geri alma yöntemi
- **Önce onay durumuna bak (FlaggedRevs):** `prop=flagged` ile `stable_revid` ve `pending_since` al. Vandal düzenleme onaylı sürümün *içindeyse* okuyucuya görünür ve önceliklidir. Onaylı sürümden *sonra* geliyorsa "bekleyen değişiklik"tir: okuyucu ve Kadir (varsayılan görünüm) sayfayı onaylı haliyle görür. Raporda her vakada "okuyucu şu an hangi sürümü görüyor" bilgisini ver ve en son sürüm bağlantısını (`&stable=0`) ekle. Bekleyen vakada geri alma yine yararlıdır (kuyruğu temizler) ama aciliyeti düşüktür.
- Sayfanın **en son sürümünü** kontrol et: vandalizm hâlâ duruyor mu? Başkası düzeltmişse "zaten düzeltilmiş" yaz, öneri yapma.
- **Vandal düzenleme(ler) son sürümse:** "geri al" bağlantısı hazırla:
  `https://tr.wikipedia.org/w/index.php?title=<Madde>&action=edit&undoafter=<son iyi sürüm>&undo=<son vandal sürüm>`
  (Art arda birden çok vandal düzenleme varsa `undoafter` ilk vandal düzenlemeden önceki sürüm, `undo` sonuncusu.)
- **Araya iyi niyetli düzenlemeler girmişse:** "geri al" iyi düzenlemeleri de silebilir veya çakışır. Bu durumda yalnızca vandal metni kaldıran **elle düzeltme** hazırla: kaldırılacak/geri konacak metni kod bloğunda ver.
- Aynı sayfada aynı içerik için **en fazla bir geri alma** önerilir. Geri alma geri alınırsa tartışma sayfası veya bildirim yoluna geçilir; asla ikinci kez geri alınmaz.

## 4. Uyarı (Kadir onaylarsa, kullanıcının mesaj sayfasına)
- Kullanıcının mesaj sayfasını oku: son 30 gün içinde hangi kademede uyarı almış? Bir sonraki kademeyi seç. Uyarı yoksa 1 (açık hakaret/küfürde 2 veya 3 olabilir).
- Kalıcı vandalizmde vandal çoğu zaman artık aktif değildir: **düzenleme 30 günden eskiyse ve kullanıcı o tarihten beri düzenleme yapmadıysa uyarı önerilmez** (kimse okumaz, gereksiz gürültüdür). Geçici hesaplar (`~2026-...`) ve IP'ler için de aynı kural.
- Biçim: başlık `== <Ay Yıl> ==` (yoksa yeni bölüm), metin:
  `{{subst:Ku-vandalizm<N>|<Madde adı>}} ~~~~`
  4. kademe için fark eklenebilir: `{{subst:Ku-vandalizm4|<Madde adı>|fark=<diff URL>}} ~~~~`
- İyi niyetli hatada `Ku-vandalizm` kullanılmaz; gerekiyorsa kısa, kibar bir not önerilir.

## 5. Engelleme talebi (yalnızca gerektiğinde)
Ancak şu durumlarda: kullanıcı 4. kademe uyarıdan **sonra** vandalizme devam ettiyse, ya da küfür/tehdit/kişisel bilgi yayımlama varsa (bu durumda uyarı şartı yok). Sayfa: `Vikipedi:Kullanıcı engelleme talepleri` ("Yeni talep ekle" düğmesi). Hazırlanacak metin:
```
== <GG-AA-YYYY> <Kullanıcı> ==
{{Vandal|<Kullanıcı>}}
* '''Neden:''' <Madde> sayfasında 4. kademe uyarıdan sonra süren vandalizm: <diff URL'leri>. ~~~~
```

## 6. Kadir'e çıktı biçimi
Her doğrulanmış vaka için:
1. **Madde** ve **fark** bağlantısı, düzenleme tarihi, kullanıcı (ve kaç gündür durduğu).
2. **Sınıf** ve kısa gerekçe (farktan kısa alıntıyla).
3. **Güncel durum:** hâlâ duruyor mu, araya düzenleme girmiş mi.
4. **Geri alma:** hazır "geri al" bağlantısı **veya** elle düzeltme metni.
5. **Değişiklik özeti (hazır):** Kasıt belirsizse (ör. görsel düzenleyici aksaklığı olabilecek bozulma) "vandalizm" deme: `Maddeyi bozan düzenleme geri alındı: <kısa açıklama> (YZ destekli, fark kontrol edildi)`. Açık vandalizmde `Vandalizm geri alındı: <kısa açıklama> (YZ destekli, fark kontrol edildi)`; test düzenlemesinde `Test düzenlemesi geri alındı (YZ destekli, fark kontrol edildi)`.
6. **Uyarı:** önerilen kademe ve hazır metin, ya da "uyarı önerilmez" ve nedeni.
7. **Engelleme talebi:** gerekiyorsa hazır metin.

Elenen ve sınıf 3-5'e düşen adaylar için tek satır.

## 7. Sayfayı açma
Geri alma bağlantısını veya düzenleme sayfasını Chrome'da aç (`open -a "Google Chrome" "<url>"` ya da Claude in Chrome sekmesi). Uyarı ve bildirim sayfalarını **Kadir istemeden açma**. Kaydetme, mesaj gönderme ve talep ekleme her zaman Kadir'indir.

## Sınırlar
- İçerik anlaşmazlığını, kaynaklı değişikliği, görüş farkını vandalizm sayıp geri alma önermem.
- Aynı içerik için ikinci kez geri alma önermem; üç geri dönüş kuralına yaklaşmam.
- Yaşayan kişilere yönelik iftira/küfür içeren vakaları önceliklendiririm.
- Anonim kullanıcılar hakkında aşağılayıcı ifade kullanmam (Vikipedi:Vandalları aşağılamayın).
- YZ desteğini özetten çıkarmayı önermem.
