"""Çevrimdışı testler: python -m pytest test_kurallar.py"""
import os
os.environ.setdefault('PYWIKIBOT_NO_USER_CONFIG', '1')

from kurallar import Kural, kurallari_yukle, tr_capitalize, uygula


def u(metin, *kurallar):
    return uygula(metin, list(kurallar))[0]


def test_turkce_buyuk_harf():
    assert tr_capitalize('istanbul') == 'İstanbul'
    assert tr_capitalize('ılık') == 'Ilık'


def test_kelime_ve_bas_harf():
    k = Kural('herkez', 'herkes')
    assert u('Herkez geldi, herkez gitti.', k) == 'Herkes geldi, herkes gitti.'


def test_kelime_eki_degistirmez_kok_degistirir():
    assert u('herkezin', Kural('herkez', 'herkes')) == 'herkezin'
    assert u('herkezin, yanlızca', Kural('herkez', 'herkes', 'kok'),
             Kural('yanlız', 'yalnız', 'kok')) == 'herkesin, yalnızca'


def test_kelime_icinde_eslesmez():
    # 'birşey' kuralı 'hiçbirşey' içinde tetiklenmemeli
    assert u('hiçbirşey', Kural('birşey', 'bir şey', 'kok')) == 'hiçbirşey'


def test_kesme_isareti():
    assert u("herkez'in", Kural('herkez', 'herkes')) == "herkes'in"


def test_i_harfi():
    k = Kural('istanbulda', 'İstanbul\'da')
    assert u('İstanbulda', k) == "İstanbul'da"


def test_korunan_bolgeler():
    k = Kural('herkez', 'herkes')
    korunan = [
        '[[herkez]]', '[[Herkez (film)|herkez]]', '<ref>herkez</ref>',
        '<ref name="a">Herkez Dergisi</ref>', '{{Kitap kaynağı|başlık=Herkez}}',
        '<!-- herkez -->', '<nowiki>herkez</nowiki>', '«herkez gelsin»',
        '"herkez gelsin"', 'https://ornek.com/herkez', '[[Dosya:Herkez.jpg|küçük|herkez]]',
        '[[Kategori:Herkez]]', '<blockquote>herkez</blockquote>', '\n herkez',
    ]
    for parca in korunan:
        assert u(parca, k) == parca, parca


def test_italik_ve_kalin_korunur():
    k = Kural('süpriz', 'sürpriz', 'kok')
    assert u("|''Süpriz Ortak''", k) == "|''Süpriz Ortak''"
    assert u("'''Süpriz''' bir filmdir, süprizler", k) == "'''Süpriz''' bir filmdir, sürprizler"
    assert u("''A'' ile süpriz ve ''B''", k) == "''A'' ile sürpriz ve ''B''"
    # Türkçe kesme işareti italik sayılmaz
    assert u("Stetson'ın süprizi, Ali'nin", k) == "Stetson'ın sürprizi, Ali'nin"


def test_karisik_metin():
    k = Kural('herkez', 'herkes')
    metin = "Herkez bilir.<ref>herkez</ref> [[Ankara]]'da herkez «herkez» der."
    beklenen = "Herkes bilir.<ref>herkez</ref> [[Ankara]]'da herkes «herkez» der."
    assert u(metin, k) == beklenen


def test_sayac():
    _, uyg = uygula('herkez herkez', [Kural('herkez', 'herkes')])
    assert uyg[0][1] == 2


def test_regex():
    k = Kural(r'(\d+) ncı', r'\1.', 'regex')
    assert u('5 ncı sırada', k) == '5. sırada'


def test_sablon_istisnasi_kapatilabilir():
    k = Kural('herkez', 'herkes')
    assert uygula('{{a|herkez}}', [k], istisnalar=['comment'])[0] == '{{a|herkes}}'


def test_dosya_yukleme():
    kurallar = kurallari_yukle(os.path.join(os.path.dirname(__file__), 'duzeltmeler.tsv'))
    assert len(kurallar) >= 3
