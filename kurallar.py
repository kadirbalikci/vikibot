"""Bul-değiştir kuralları: yükleme ve vikimetne güvenli uygulama.

Bu modül siteye bağlanmaz; bu sayede çevrimdışı test edilebilir.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

from pywikibot import textlib

# ---------------------------------------------------------------------------
# Türkçe büyük/küçük harf dönüşümü (Python'un str.upper() i→I yapar, yanlış)
# ---------------------------------------------------------------------------

def tr_upper(s: str) -> str:
    return s.replace('i', 'İ').replace('ı', 'I').upper()


def tr_lower(s: str) -> str:
    return s.replace('İ', 'i').replace('I', 'ı').lower()


def tr_capitalize(s: str) -> str:
    return tr_upper(s[:1]) + s[1:] if s else s


# ---------------------------------------------------------------------------
# Dokunulmayacak bölgeler
# ---------------------------------------------------------------------------

# Pywikibot'un yerleşik istisnaları (etiket adları da geçerli)
VARSAYILAN_ISTISNALAR: list[str] = [
    'comment',        # <!-- ... -->
    'nowiki', 'pre', 'source', 'syntaxhighlight', 'code', 'math', 'chem',
    'ref',            # kaynaklar (makale/kitap başlıkları özgün yazımla kalmalı)
    'blockquote', 'poem', 'score', 'timeline', 'gallery', 'mapframe',
    'template',       # {{...}} içleri (parametre adları, alıntılar)
    'hyperlink',      # URL'ler
    'link',           # [[hedef|etiket]] — hedef sayfa adları bozulmasın
    'startspace',     # boşlukla başlayan satırlar (ön biçimli)
]

# Site gerektirmeyen ek regex istisnaları (Türkçe ad alanları dahil)
EK_ISTISNALAR = [
    # [[Dosya:...]] / [[Kategori:...]] (içinde iç içe bağlantı olabilir)
    re.compile(
        r'\[\[\s*(?:Dosya|File|Resim|Image|Kategori|Category)\s*:'
        r'[^\[\]]*(?:\[\[[^\[\]]*\]\][^\[\]]*)*\]\]',
        re.IGNORECASE),
    # Alıntılar: «...», "...", “...”, „...“ (tek paragraf içinde)
    re.compile(r'«[^»\n]*»'),
    re.compile(r'"[^"\n]*"'),
    re.compile(r'“[^”\n]*”'),
    re.compile(r'„[^“”\n]*[“”]'),
    # Dosya adına benzeyen ifadeler (ör. herkez.jpg)
    re.compile(r'[\w\-.]+\.(?:jpe?g|png|svg|gif|tiff?|webm|ogg|ogv|pdf)\b',
               re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Kurallar
# ---------------------------------------------------------------------------

@dataclass
class Kural:
    bul: str
    degistir: str
    tip: str = 'kelime'          # kelime | kok | metin | regex
    not_: str = ''
    desen: re.Pattern = field(init=False, repr=False)

    def __post_init__(self):
        if self.tip == 'regex':
            self.desen = re.compile(self.bul)
        elif self.tip == 'metin':
            self.desen = re.compile(re.escape(self.bul))
        elif self.tip in ('kelime', 'kok'):
            # Baş harf büyük/küçük her iki biçimi de yakala
            ilk = self.bul[:1]
            ilk_sinif = f'[{re.escape(tr_lower(ilk))}{re.escape(tr_upper(ilk))}]'
            govde = re.escape(self.bul[1:])
            # \w Unicode'dur; ç, ğ, ı, ö, ş, ü harflerini de kapsar.
            # Kesme işaretinden sonraki ekleri (herkez'in) de yakalamak için
            # yalnızca harf/rakam sınırı kullanılır.
            # 'kok' tipinde sonrasında ek gelebilir (herkez+in, herkez+e)
            son = '' if self.tip == 'kok' else r'(?![\w])'
            self.desen = re.compile(rf'(?<![\w]){ilk_sinif}{govde}{son}')
        else:
            raise ValueError(f'Bilinmeyen kural tipi: {self.tip!r}')

    def _yerine(self, m: re.Match) -> str:
        if self.tip == 'regex':
            return m.expand(self.degistir)
        if self.tip in ('kelime', 'kok'):
            bulunan = m.group(0)
            if bulunan[:1] != self.bul[:1] and bulunan[:1] == tr_upper(self.bul[:1]):
                return tr_capitalize(self.degistir)
        return self.degistir

    def arama_sorgusu(self) -> str:
        """CirrusSearch için aday sayfa sorgusu."""
        if self.tip == 'regex':
            return f'insource:/{self.bul}/'
        return f'insource:"{self.bul}"'

    @property
    def ozet(self) -> str:
        return f'{self.bul} → {self.degistir}' if self.tip != 'regex' else (self.not_ or self.bul)


def kurallari_yukle(yol: str | Path) -> list[Kural]:
    """TSV dosyası: bul<TAB>değiştir[<TAB>tip[<TAB>not]]. # ile başlayan satırlar yorum."""
    kurallar = []
    with open(yol, encoding='utf-8', newline='') as f:
        for no, satir in enumerate(csv.reader(f, delimiter='\t'), 1):
            if not satir or not satir[0].strip() or satir[0].lstrip().startswith('#'):
                continue
            if len(satir) < 2:
                raise ValueError(f'{yol}:{no}: en az iki sütun gerekli')
            bul, degistir = satir[0], satir[1]
            tip = (satir[2].strip() if len(satir) > 2 and satir[2].strip() else 'kelime')
            not_ = satir[3].strip() if len(satir) > 3 else ''
            if bul == degistir:
                raise ValueError(f'{yol}:{no}: bul ve değiştir aynı')
            kurallar.append(Kural(bul, degistir, tip, not_))
    return kurallar


def uygula(metin: str, kurallar: list[Kural],
           istisnalar: list | None = None, site=None) -> tuple[str, list[tuple[Kural, int]]]:
    """Kuralları uygular. (yeni_metin, [(kural, değişiklik_sayısı), ...]) döner."""
    istisnalar = list(VARSAYILAN_ISTISNALAR if istisnalar is None else istisnalar)
    istisnalar += EK_ISTISNALAR
    if site is not None:
        istisnalar += ['interwiki', 'file', 'category']
    uygulanan = []
    for k in kurallar:
        sayac = 0

        def say(m, k=k):
            nonlocal sayac
            sayac += 1
            return k._yerine(m)

        yeni = textlib.replaceExcept(metin, k.desen, say, istisnalar, site=site)
        if sayac and yeni != metin:
            uygulanan.append((k, sayac))
            metin = yeni
    return metin, uygulanan
