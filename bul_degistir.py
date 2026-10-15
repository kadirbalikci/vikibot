#!/usr/bin/env python3
"""Türkçe Vikipedi için bul-değiştir botu.

Varsayılan olarak DENEME modunda çalışır: değişiklikleri fark (diff) olarak
gösterir, hiçbir şey kaydetmez. Gerçekten kaydetmek için -canli verin.

Kullanım örnekleri
------------------
  # Kurallar dosyasındaki her kural için arama yap, farkları göster (kaydetmez)
  python3 bul_degistir.py

  # Belirli bir sayfada dene
  python3 bul_degistir.py -page:"Ankara"

  # Bir kategorideki maddelerde, en fazla 20 sayfa, canlı + her düzenlemede onay
  python3 bul_degistir.py -cat:"Türkiye'deki müzeler" -limit:20 -canli

  # Canlı, onay sormadan (yalnızca bot onayı aldıktan sonra!)
  python3 bul_degistir.py -canli -otomatik

Seçenekler
----------
  -kurallar:DOSYA   Kurallar dosyası (varsayılan: duzeltmeler.tsv)
  -canli            Değişiklikleri gerçekten kaydet
  -otomatik         Her düzenleme için onay sorma (-canli ile birlikte)
  -sablonlar        Şablon ({{...}}) içlerinde de değiştir
  -baglantilar      [[bağlantı|etiket]] içlerinde de değiştir (dikkat!)
  -italikler        ''italik'' ve '''kalın''' metin içinde de değiştir (dikkat: eser adları)
  -enfazla:N        En fazla N düzenleme yap, sonra dur
  -limit:N          Kural başına en fazla N yeni (geçmişte olmayan) sayfa tara
  -tekrar:GUN       Taranmış bir sayfaya en erken kaç gün sonra yeniden bakılsın
                    (varsayılan: 180; 0 = bekleme yok). Yalnızca -page:/-cat:
                    vb. verilmediğinde, yani kurallardan arama yapılırken geçerli.
  -denemeler        Arama yapmadan, son deneme modu çalışmalarında değişiklik
                    bulunan (henüz kaydedilmemiş) sayfaları işle
  + Pywikibot sayfa üreteci seçenekleri: -page:, -cat:, -file:, -search:,
    -ns:, -transcludes:, -start: ... (bkz. python -m pywikibot.pagegenerators)

Geçmiş ve geri almalar
----------------------
Taranan her sayfa tarama_gecmisi.tsv'ye yazılır (bkz. gecmis.py). Buna göre:
  - Bu hesabın bir düzenlemesi geri alınmış sayfalara bir daha dokunulmaz.
    Kontrol hem geçmiş dosyasından hem de sayfa geçmişinden (mw-reverted
    etiketi) yapılır; -page: ile açıkça verilen sayfalarda da geçerlidir.
  - Daha önce düzelttiğimiz bir sayfada aynı hata yeniden çıkarsa (biri geri
    almış ya da bilerek geri koymuş olabilir) sayfa düzenlenmez, engellenir.
  - Kurallardan arama yapılırken son -tekrar günü içinde taranan sayfalar atlanır,
    arama sonuçları rastgele sıralanır ve kurallar arasında sırayla dönülür;
    böylece her çalışmada farklı sayfalar gelir.
"""
from __future__ import annotations

import csv
import datetime as dt
import random
from pathlib import Path

import pywikibot
from pywikibot import config, pagegenerators
from pywikibot.bot import ExistingPageBot, SingleSiteBot

from gecmis import ATLANDI, DENEME, DUZENLENDI, GERI_ALINDI, TEMIZ, TaramaGecmisi
from kurallar import ITALIK_ISTISNA, VARSAYILAN_ISTISNALAR, kurallari_yukle, uygula

KOK = Path(__file__).resolve().parent
DURDURMA_KONTROL_ARALIGI = 10  # her N sayfada bir durdurma sayfasına bak
VARSAYILAN_BEKLEME_GUN = 180


def hesap_adi(site) -> str | None:
    """Oturum açılmamışsa (deneme modu) user-config.py'deki adı kullanır."""
    ad = site.username() or config.usernames.get(site.family.name, {}).get(site.code)
    # BotPassword adı "Hesap@botadı" biçimindedir; düzenlemeler ana hesaptadır
    return ad.split('@')[0] if ad else None


class BulDegistirBot(SingleSiteBot, ExistingPageBot):
    """Kurallar dosyasındaki düzeltmeleri uygulayan bot."""

    use_redirects = False       # yönlendirmeleri atla
    use_disambigs = None        # anlam ayrımı sayfalarını ayrıca filtreleme

    update_options = {
        'kurallar': [],
        'istisnalar': [],
        'enfazla': 0,
        'kayit': '',
        'gecmis': None,
        'bekleme': 0,
    }

    def setup(self):
        self._taranan = 0
        self._duzenlenen = 0
        self._atlanan = 0
        self.durdurma_sayfasi = None
        self.gecmis: TaramaGecmisi = self.opt.gecmis
        self.kullanici = hesap_adi(self.site)
        if self.site.username() and self.kullanici:
            self.durdurma_sayfasi = pywikibot.Page(
                self.site, f'Kullanıcı:{self.kullanici}/Durdur')
        kayit = Path(self.opt.kayit)
        yeni = not kayit.exists()
        self._kayit_f = open(kayit, 'a', encoding='utf-8', newline='')
        self._kayit = csv.writer(self._kayit_f, delimiter='\t')
        if yeni:
            self._kayit.writerow(['zaman', 'mod', 'sayfa', 'değişiklikler', 'sonuç'])

    def teardown(self):
        self._kayit_f.close()
        self.gecmis.kapat()
        pywikibot.info(
            f'\n<<lightgreen>>Bitti: {self._taranan} sayfa tarandı, '
            f'{self._duzenlenen} sayfada değişiklik '
            f'{"kaydedildi" if not config.simulate else "bulundu (deneme modu)"}, '
            f'{self._atlanan} sayfa geçmiş/geri alma nedeniyle atlandı.')

    # -- güvenlik -----------------------------------------------------------

    def _durdurulsun_mu(self) -> bool:
        """Kullanıcı:<bot>/Durdur sayfasında 'DUR' yazıyorsa çalışmayı keser."""
        if not self.durdurma_sayfasi:
            return False
        try:
            metin = self.durdurma_sayfasi.get(force=True)
        except pywikibot.exceptions.NoPageError:
            return False
        return 'DUR' in metin

    def _geri_alinmis_mi(self, page) -> bool:
        """Bu hesabın sayfadaki düzenlemelerinden biri geri alınmış mı?

        MediaWiki geri alınan düzenlemeleri (rollback, undo, elle geri alma)
        mw-reverted etiketiyle işaretler.
        """
        if not self.kullanici:
            return False
        veri = self.site.simple_request(
            action='query', prop='revisions', titles=page.title(),
            rvprop='tags', rvuser=self.kullanici, rvlimit='max').submit()
        sayfalar = veri.get('query', {}).get('pages', {})
        if isinstance(sayfalar, dict):
            sayfalar = sayfalar.values()
        return any('mw-reverted' in r.get('tags', [])
                   for p in sayfalar for r in p.get('revisions', []))

    def skip_page(self, page) -> bool:
        if super().skip_page(page):
            return True
        if page.namespace() != 0:
            pywikibot.warning(f'{page} madde ad alanında değil, atlanıyor.')
            return True
        neden = self.gecmis.atla_nedeni(page.title(), self.opt.bekleme)
        if neden:
            pywikibot.info(f'{page} atlanıyor: {neden}.')
            self._atlanan += 1
            return True
        if self._geri_alinmis_mi(page):
            pywikibot.warning(f'{page}: bu hesabın bir düzenlemesi geri alınmış, '
                              'bir daha dokunulmayacak.')
            self.gecmis.yaz(page.title(), GERI_ALINDI, 'sayfa geçmişinde mw-reverted')
            self._atlanan += 1
            return True
        if not page.botMayEdit():
            pywikibot.warning(f'{page} {{{{bots}}}}/{{{{nobots}}}} ile botlara kapalı.')
            self.gecmis.yaz(page.title(), ATLANDI, 'bots/nobots')
            return True
        if page.protection().get('edit'):
            pywikibot.warning(f'{page} düzenlemeye koruma altında, atlanıyor.')
            self.gecmis.yaz(page.title(), ATLANDI, 'koruma')
            return True
        return False

    # -- asıl iş ---------------------------------------------------------------

    def treat_page(self):
        self._taranan += 1
        if self._taranan % DURDURMA_KONTROL_ARALIGI == 1 and self._durdurulsun_mu():
            pywikibot.error('Durdurma sayfasında DUR bulundu. Bot durduruluyor.')
            self.stop()
            return

        sayfa = self.current_page
        eski = sayfa.text
        yeni, uygulanan = uygula(eski, self.opt.kurallar,
                                 self.opt.istisnalar, site=self.site)
        if not uygulanan:
            self.gecmis.yaz(sayfa.title(), TEMIZ)
            return

        ozet_parca = ', '.join(
            f'{k.ozet}' + (f' (×{n})' if n > 1 else '') for k, n in uygulanan)

        geri_gelen = self.gecmis.geri_gelen_duzeltmeler(
            sayfa.title(), [k.ozet for k, _ in uygulanan])
        if geri_gelen:
            # Düzelttiğimiz bir hata geri gelmiş: biri geri almış ya da bilerek
            # geri koymuş olabilir. Tekrar düzeltmek değişiklik savaşına döner.
            liste = ', '.join(sorted(geri_gelen))
            pywikibot.warning(f'{sayfa} daha önce düzeltilmişti ama aynı hata yeniden '
                              f'görünüyor ({liste}). Sayfaya bir daha dokunulmayacak.')
            self.gecmis.yaz(sayfa.title(), GERI_ALINDI, f'hata geri gelmiş: {liste}')
            self._atlanan += 1
            return
        ozet = f'Yazım düzeltmesi (yarı otomatik): {ozet_parca}'
        if len(ozet) > 480:
            ozet = ozet[:477] + '...'

        kaydedildi = self.put_current(yeni, summary=ozet, minor=True,
                                      bot=True, show_diff=True,
                                      apply_cosmetic_changes=False)
        self._kayit.writerow([
            dt.datetime.now().isoformat(timespec='seconds'),
            'deneme' if config.simulate else 'canlı',
            sayfa.title(), ozet_parca,
            'kaydedildi' if kaydedildi else 'kaydedilmedi'])
        self._kayit_f.flush()

        if config.simulate:
            self.gecmis.yaz(sayfa.title(), DENEME, ozet_parca)
        elif kaydedildi:
            self.gecmis.yaz(sayfa.title(), DUZENLENDI, ozet_parca)
        else:
            self.gecmis.yaz(sayfa.title(), ATLANDI, f'kaydedilmedi: {ozet_parca}')

        if kaydedildi or config.simulate:
            self._duzenlenen += 1
        if self.opt.enfazla and self._duzenlenen >= self.opt.enfazla:
            pywikibot.info(f'-enfazla:{self.opt.enfazla} sınırına ulaşıldı.')
            self.stop()


def varsayilan_uretec(site, kurallar, limit, gecmis, bekleme):
    """Kurallardan insource: aramaları üretip aday sayfaları birleştirir.

    Arama sonuçları rastgele sıralanır ve kurallar arasında sırayla dönülür
    (her kuraldan bir sayfa), böylece -enfazla sınırı tek bir kurala harcanmaz.
    Geçmişe göre atlanacak sayfalar sayfa içeriği hiç yüklenmeden elenir;
    -limit yalnızca yeni sayfaları sayar.
    """
    kurallar = list(kurallar)
    random.shuffle(kurallar)
    aramalar = []
    for k in kurallar:
        sorgu = k.arama_sorgusu()
        pywikibot.info(f'<<lightblue>>Aranıyor: {sorgu}')
        aramalar.append([iter(site.search(sorgu, namespaces=[0], sort='random')), 0])

    gorulen = set()
    elenen = 0
    while aramalar:
        for arama in list(aramalar):
            sonuclar, verilen = arama
            for sayfa in sonuclar:
                baslik = sayfa.title()
                if baslik in gorulen:
                    continue
                gorulen.add(baslik)
                if gecmis.atla_nedeni(baslik, bekleme):
                    elenen += 1
                    continue
                yield sayfa
                arama[1] = verilen + 1
                break
            else:
                aramalar.remove(arama)
                continue
            if limit and arama[1] >= limit:
                aramalar.remove(arama)
    pywikibot.info(f'<<lightblue>>Aramalar bitti; {elenen} sayfa geçmişe göre elendi.')


def main(*args: str) -> None:
    secenekler = {
        'kurallar_dosyasi': str(KOK / 'duzeltmeler.tsv'),
        'canli': False, 'otomatik': False,
        'sablonlar': False, 'baglantilar': False, 'italikler': False, 'enfazla': 0,
        'tekrar': VARSAYILAN_BEKLEME_GUN, 'denemeler': False,
    }
    yerel_argumanlar = pywikibot.handle_args(args)
    site = pywikibot.Site('tr', 'wikipedia')
    uretec_fabrikasi = pagegenerators.GeneratorFactory(site)

    for arg in yerel_argumanlar:
        if uretec_fabrikasi.handle_arg(arg):
            continue
        ad, _, deger = arg.lstrip('-').partition(':')
        if ad == 'kurallar':
            secenekler['kurallar_dosyasi'] = deger
        elif ad == 'enfazla':
            secenekler['enfazla'] = int(deger)
        elif ad == 'tekrar':
            secenekler['tekrar'] = int(deger)
        elif ad in ('canli', 'otomatik', 'sablonlar', 'baglantilar', 'italikler',
                    'denemeler'):
            secenekler[ad] = True
        else:
            pywikibot.error(f'Bilinmeyen seçenek: {arg}')
            return

    kurallar = kurallari_yukle(secenekler['kurallar_dosyasi'])
    if not kurallar:
        pywikibot.error('Kurallar dosyasında kural yok.')
        return
    pywikibot.info(f'{len(kurallar)} kural yüklendi.')

    istisnalar = list(VARSAYILAN_ISTISNALAR)
    if secenekler['sablonlar']:
        istisnalar.remove('template')
    if secenekler['baglantilar']:
        istisnalar.remove('link')
    if secenekler['italikler']:
        istisnalar.remove(ITALIK_ISTISNA)

    # Güvenlik: -canli verilmedikçe hiçbir şey kaydedilmez
    if not secenekler['canli']:
        config.simulate = True
        pywikibot.info('<<yellow>>DENEME MODU: hiçbir değişiklik kaydedilmeyecek. '
                       'Kaydetmek için -canli ekleyin.')
    else:
        site.login()
    if secenekler['canli'] and secenekler['otomatik'] and not site.has_right('bot'):
        pywikibot.error('Hesabın bot yetkisi yok; -otomatik kullanılamaz. '
                        'Onay alana kadar -otomatik olmadan (tek tek onaylayarak) çalışın.')
        return

    gecmis = TaramaGecmisi(KOK / 'tarama_gecmisi.tsv',
                           eski_kayit=KOK / 'duzenleme_kaydi.tsv')
    pywikibot.info(f'Geçmiş: {len(gecmis.son)} sayfa, '
                   f'{len(gecmis.engelli)} sayfa geri alma nedeniyle engelli.')

    uretec = uretec_fabrikasi.getCombinedGenerator(preload=True)
    if uretec is None and secenekler['denemeler']:
        basliklar = gecmis.son_sonucu(DENEME)
        pywikibot.info(f'Deneme modunda değişiklik bulunan {len(basliklar)} sayfa işlenecek.')
        uretec = pagegenerators.PreloadingGenerator(
            pywikibot.Page(site, b) for b in basliklar)
        bekleme = 0
    elif uretec is None:
        # Kurallardan arama: bekleme süresi uygulanır, sonuçlar rastgele gelir
        bekleme = secenekler['tekrar']
        uretec = pagegenerators.PreloadingGenerator(
            varsayilan_uretec(site, kurallar, uretec_fabrikasi.limit, gecmis, bekleme))
    else:
        # Sayfalar açıkça verildi: yalnızca geri alma engeli uygulanır
        bekleme = 0

    bot = BulDegistirBot(
        site=site, generator=uretec,
        kurallar=kurallar, istisnalar=istisnalar,
        enfazla=secenekler['enfazla'],
        kayit=str(KOK / 'duzenleme_kaydi.tsv'),
        gecmis=gecmis, bekleme=bekleme,
        always=secenekler['otomatik'] or not secenekler['canli'],
    )
    bot.run()


if __name__ == '__main__':
    main()
