#!/usr/bin/env python3
"""Türkçe Vikipedi için bul-değiştir botu.

Varsayılan olarak DENEME modunda çalışır: değişiklikleri fark (diff) olarak
gösterir, hiçbir şey kaydetmez. Gerçekten kaydetmek için -canli verin.

Kullanım örnekleri
------------------
  # Kurallar dosyasındaki her kural için arama yap, farkları göster (kaydetmez)
  python bul_degistir.py

  # Belirli bir sayfada dene
  python bul_degistir.py -page:"Ankara"

  # Bir kategorideki maddelerde, en fazla 20 sayfa, canlı + her düzenlemede onay
  python bul_degistir.py -cat:"Türkiye'deki müzeler" -limit:20 -canli

  # Canlı, onay sormadan (yalnızca bot onayı aldıktan sonra!)
  python bul_degistir.py -canli -otomatik

Seçenekler
----------
  -kurallar:DOSYA   Kurallar dosyası (varsayılan: duzeltmeler.tsv)
  -canli            Değişiklikleri gerçekten kaydet
  -otomatik         Her düzenleme için onay sorma (-canli ile birlikte)
  -sablonlar        Şablon ({{...}}) içlerinde de değiştir
  -baglantilar      [[bağlantı|etiket]] içlerinde de değiştir (dikkat!)
  -enfazla:N        En fazla N düzenleme yap, sonra dur
  -limit:N          En fazla N sayfa tara (Pywikibot sayfa üreteci seçeneği)
  + Pywikibot sayfa üreteci seçenekleri: -page:, -cat:, -file:, -search:,
    -ns:, -transcludes:, -start: ... (bkz. python -m pywikibot.pagegenerators)
"""
from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

import pywikibot
from pywikibot import config, pagegenerators
from pywikibot.bot import ExistingPageBot, SingleSiteBot

from kurallar import VARSAYILAN_ISTISNALAR, kurallari_yukle, uygula

KOK = Path(__file__).resolve().parent
DURDURMA_KONTROL_ARALIGI = 10  # her N sayfada bir durdurma sayfasına bak


class BulDegistirBot(SingleSiteBot, ExistingPageBot):
    """Kurallar dosyasındaki düzeltmeleri uygulayan bot."""

    use_redirects = False       # yönlendirmeleri atla
    use_disambigs = None        # anlam ayrımı sayfalarını ayrıca filtreleme

    update_options = {
        'kurallar': [],
        'istisnalar': [],
        'enfazla': 0,
        'kayit': '',
    }

    def setup(self):
        self._taranan = 0
        self._duzenlenen = 0
        self.durdurma_sayfasi = None
        kullanici = self.site.username()
        if kullanici:
            # BotPassword adı "Hesap@botadı" biçimindedir; sayfa ana hesaptadır
            kullanici = kullanici.split('@')[0]
            self.durdurma_sayfasi = pywikibot.Page(
                self.site, f'Kullanıcı:{kullanici}/Durdur')
        kayit = Path(self.opt.kayit)
        yeni = not kayit.exists()
        self._kayit_f = open(kayit, 'a', encoding='utf-8', newline='')
        self._kayit = csv.writer(self._kayit_f, delimiter='\t')
        if yeni:
            self._kayit.writerow(['zaman', 'mod', 'sayfa', 'değişiklikler', 'sonuç'])

    def teardown(self):
        self._kayit_f.close()
        pywikibot.info(
            f'\n<<lightgreen>>Bitti: {self._taranan} sayfa tarandı, '
            f'{self._duzenlenen} sayfada değişiklik '
            f'{"kaydedildi" if not config.simulate else "bulundu (deneme modu)"}.')

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

    def skip_page(self, page) -> bool:
        if super().skip_page(page):
            return True
        if page.namespace() != 0:
            pywikibot.warning(f'{page} madde ad alanında değil, atlanıyor.')
            return True
        if not page.botMayEdit():
            pywikibot.warning(f'{page} {{{{bots}}}}/{{{{nobots}}}} ile botlara kapalı.')
            return True
        if page.protection().get('edit'):
            pywikibot.warning(f'{page} düzenlemeye koruma altında, atlanıyor.')
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
            return

        ozet_parca = ', '.join(
            f'{k.ozet}' + (f' (×{n})' if n > 1 else '') for k, n in uygulanan)
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

        if kaydedildi or config.simulate:
            self._duzenlenen += 1
        if self.opt.enfazla and self._duzenlenen >= self.opt.enfazla:
            pywikibot.info(f'-enfazla:{self.opt.enfazla} sınırına ulaşıldı.')
            self.stop()


def varsayilan_uretec(site, kurallar, limit):
    """Kurallardan insource: aramaları üretip aday sayfaları birleştirir."""
    gorulen = set()
    for k in kurallar:
        sorgu = k.arama_sorgusu()
        pywikibot.info(f'<<lightblue>>Aranıyor: {sorgu}')
        for sayfa in site.search(sorgu, namespaces=[0], total=limit or None):
            if sayfa.title() not in gorulen:
                gorulen.add(sayfa.title())
                yield sayfa


def main(*args: str) -> None:
    secenekler = {
        'kurallar_dosyasi': str(KOK / 'duzeltmeler.tsv'),
        'canli': False, 'otomatik': False,
        'sablonlar': False, 'baglantilar': False, 'enfazla': 0,
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
        elif ad in ('canli', 'otomatik', 'sablonlar', 'baglantilar'):
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

    uretec = uretec_fabrikasi.getCombinedGenerator(preload=True)
    if uretec is None:
        uretec = pagegenerators.PreloadingGenerator(
            varsayilan_uretec(site, kurallar, uretec_fabrikasi.limit))

    bot = BulDegistirBot(
        site=site, generator=uretec,
        kurallar=kurallar, istisnalar=istisnalar,
        enfazla=secenekler['enfazla'],
        kayit=str(KOK / 'duzenleme_kaydi.tsv'),
        always=secenekler['otomatik'] or not secenekler['canli'],
    )
    bot.run()


if __name__ == '__main__':
    main()
