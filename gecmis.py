"""Tarama geçmişi: aynı sayfalara tekrar tekrar bakmamak ve geri alınan
düzenlemeleri yinelememek için.

Her taranan sayfa tarama_gecmisi.tsv'ye bir satır olarak yazılır:
    zaman<TAB>sayfa<TAB>sonuç<TAB>not

Sonuçlar:
    temiz        Aramada çıktı ama düzeltilecek bir şey yoktu (eşleşme kaynak,
                 italik, şablon gibi dokunulmayan bir bölgedeydi)
    düzenlendi   Canlı modda değişiklik kaydedildi
    deneme       Deneme modunda değişiklik bulundu (kaydedilmedi)
    geri_alındı  Bu sayfadaki bir düzenlememiz geri alınmış; bir daha dokunulmaz
    atlandı      Koruma, {{bots}} vb. nedeniyle atlandı

Bu modül siteye bağlanmaz; çevrimdışı test edilebilir.
"""
from __future__ import annotations

import csv
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path

BASLIK = ['zaman', 'sayfa', 'sonuç', 'not']

TEMIZ = 'temiz'
DUZENLENDI = 'düzenlendi'
DENEME = 'deneme'
GERI_ALINDI = 'geri_alındı'
ATLANDI = 'atlandı'

# Bekleme süresi dolana kadar yeniden taranmayan sonuçlar.
# 'deneme' sayılmaz: deneme modunda bulunan bir sayfa canlı modda işlenebilmeli.
BEKLETEN_SONUCLAR = {TEMIZ, DUZENLENDI, ATLANDI}


def ozetleri_ayir(metin: str) -> set[str]:
    """'yanlız → yalnız (×2), hiç bir → hiçbir' -> {'yanlız → yalnız', 'hiç bir → hiçbir'}"""
    return {re.sub(r'\s*\(×\d+\)$', '', p.strip())
            for p in metin.split(', ') if p.strip()}


@dataclass
class Kayit:
    zaman: dt.datetime
    sonuc: str


class TaramaGecmisi:
    def __init__(self, yol: str | Path, eski_kayit: str | Path | None = None):
        """yol: tarama_gecmisi.tsv. eski_kayit: duzenleme_kaydi.tsv (varsa,
        oradaki canlı düzenlemeler de geçmişe sayılır)."""
        self.yol = Path(yol)
        self.son: dict[str, Kayit] = {}
        self.engelli: set[str] = set()
        self.duzenlenen: dict[str, set[str]] = {}
        if self.yol.exists():
            self._oku(self.yol)
        if eski_kayit and Path(eski_kayit).exists():
            self._eski_kaydi_oku(Path(eski_kayit))
        self._f = None
        self._yazici = None

    # -- okuma ---------------------------------------------------------------

    def _isle(self, sayfa: str, zaman: dt.datetime, sonuc: str, not_: str = '') -> None:
        if sonuc == GERI_ALINDI:
            self.engelli.add(sayfa)
        if sonuc == DUZENLENDI:
            self.duzenlenen.setdefault(sayfa, set()).update(ozetleri_ayir(not_))
        onceki = self.son.get(sayfa)
        if onceki is None or zaman >= onceki.zaman:
            self.son[sayfa] = Kayit(zaman, sonuc)

    def _oku(self, yol: Path) -> None:
        with open(yol, encoding='utf-8', newline='') as f:
            for satir in csv.DictReader(f, delimiter='\t'):
                try:
                    zaman = dt.datetime.fromisoformat(satir['zaman'])
                except (KeyError, TypeError, ValueError):
                    continue
                self._isle(satir['sayfa'], zaman, satir['sonuç'], satir.get('not') or '')

    def _eski_kaydi_oku(self, yol: Path) -> None:
        """duzenleme_kaydi.tsv: zaman, mod, sayfa, değişiklikler, sonuç."""
        with open(yol, encoding='utf-8', newline='') as f:
            for satir in csv.DictReader(f, delimiter='\t'):
                if satir.get('mod') != 'canlı' or satir.get('sonuç') != 'kaydedildi':
                    continue
                try:
                    zaman = dt.datetime.fromisoformat(satir['zaman'])
                except (KeyError, TypeError, ValueError):
                    continue
                self._isle(satir['sayfa'], zaman, DUZENLENDI,
                           satir.get('değişiklikler') or '')

    # -- kararlar ------------------------------------------------------------

    def atla_nedeni(self, sayfa: str, bekleme_gun: int,
                    simdi: dt.datetime | None = None) -> str | None:
        """Sayfa atlanmalıysa nedenini, atlanmamalıysa None döner."""
        if sayfa in self.engelli:
            return 'daha önce bir düzenlememiz geri alınmış'
        kayit = self.son.get(sayfa)
        if kayit is None or kayit.sonuc not in BEKLETEN_SONUCLAR:
            return None
        simdi = simdi or dt.datetime.now()
        if bekleme_gun > 0 and simdi - kayit.zaman < dt.timedelta(days=bekleme_gun):
            gun = (simdi - kayit.zaman).days
            return f'{gun} gün önce tarandı ({kayit.sonuc})'
        return None

    def son_sonucu(self, sonuc: str) -> list[str]:
        """Son taramadaki sonucu verilen sonuç olan sayfalar (eskiden yeniye)."""
        return [ad for ad, k in sorted(self.son.items(), key=lambda x: x[1].zaman)
                if k.sonuc == sonuc]

    def geri_gelen_duzeltmeler(self, sayfa: str, ozetler) -> set[str]:
        """Bu sayfada daha önce yaptığımız düzeltmelerden hangileri yeniden
        gerekiyor? (Boş küme: hiçbiri, yani yalnızca yeni kurallar uygulanıyor.)"""
        return self.duzenlenen.get(sayfa, set()) & set(ozetler)

    # -- yazma ---------------------------------------------------------------

    def yaz(self, sayfa: str, sonuc: str, not_: str = '') -> None:
        if self._f is None:
            yeni = not self.yol.exists()
            self._f = open(self.yol, 'a', encoding='utf-8', newline='')
            self._yazici = csv.writer(self._f, delimiter='\t')
            if yeni:
                self._yazici.writerow(BASLIK)
        zaman = dt.datetime.now().replace(microsecond=0)
        self._yazici.writerow([zaman.isoformat(), sayfa, sonuc, not_])
        self._f.flush()
        self._isle(sayfa, zaman, sonuc, not_)

    def kapat(self) -> None:
        if self._f is not None:
            self._f.close()
            self._f = None
