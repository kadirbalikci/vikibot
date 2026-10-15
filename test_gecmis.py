"""Çevrimdışı testler: python -m pytest test_gecmis.py"""
import datetime as dt

from gecmis import (DENEME, DUZENLENDI, GERI_ALINDI, TEMIZ, TaramaGecmisi,
                    ozetleri_ayir)

SIMDI = dt.datetime(2026, 10, 15, 12, 0)


def gecmis_yaz(tmp_path, satirlar, eski=None):
    yol = tmp_path / 'tarama_gecmisi.tsv'
    yol.write_text('zaman\tsayfa\tsonuç\tnot\n' + ''.join(
        '\t'.join(s) + '\n' for s in satirlar), encoding='utf-8')
    eski_yol = None
    if eski is not None:
        eski_yol = tmp_path / 'duzenleme_kaydi.tsv'
        eski_yol.write_text('zaman\tmod\tsayfa\tdeğişiklikler\tsonuç\n' + ''.join(
            '\t'.join(s) + '\n' for s in eski), encoding='utf-8')
    return TaramaGecmisi(yol, eski_kayit=eski_yol)


def test_ozetleri_ayir():
    assert ozetleri_ayir('yanlız → yalnız (×2), hiç bir → hiçbir') == {
        'yanlız → yalnız', 'hiç bir → hiçbir'}
    assert ozetleri_ayir('') == set()


def test_geri_alinan_sayfa_hep_atlanir(tmp_path):
    g = gecmis_yaz(tmp_path, [('2020-01-01T00:00:00', 'A', GERI_ALINDI, '')])
    assert g.atla_nedeni('A', bekleme_gun=0, simdi=SIMDI)
    assert g.atla_nedeni('A', bekleme_gun=180, simdi=SIMDI)


def test_yakinda_taranan_bekleme_suresince_atlanir(tmp_path):
    g = gecmis_yaz(tmp_path, [('2026-10-01T00:00:00', 'A', TEMIZ, '')])
    assert g.atla_nedeni('A', bekleme_gun=180, simdi=SIMDI)
    assert g.atla_nedeni('A', bekleme_gun=10, simdi=SIMDI) is None
    assert g.atla_nedeni('A', bekleme_gun=0, simdi=SIMDI) is None


def test_deneme_sonucu_canli_calismayi_engellemez(tmp_path):
    g = gecmis_yaz(tmp_path, [('2026-10-14T00:00:00', 'A', DENEME, 'x → y')])
    assert g.atla_nedeni('A', bekleme_gun=180, simdi=SIMDI) is None


def test_hic_taranmamis_sayfa_atlanmaz(tmp_path):
    g = gecmis_yaz(tmp_path, [])
    assert g.atla_nedeni('B', bekleme_gun=180, simdi=SIMDI) is None


def test_ayni_duzeltme_geri_gelirse_yakalanir_yeni_kural_serbest(tmp_path):
    g = gecmis_yaz(tmp_path, [
        ('2026-10-01T00:00:00', 'A', DUZENLENDI, 'entellektüel → entelektüel')])
    assert g.geri_gelen_duzeltmeler('A', ['entellektüel → entelektüel']) == {
        'entellektüel → entelektüel'}
    assert g.geri_gelen_duzeltmeler('A', ['malesef → maalesef']) == set()


def test_eski_duzenleme_kaydi_gecmise_sayilir(tmp_path):
    g = gecmis_yaz(tmp_path, [], eski=[
        ('2026-10-14T07:47:41', 'canlı', 'Nasreddin Hoca bibliyografyası',
         'entellektüel → entelektüel', 'kaydedildi'),
        ('2026-09-22T22:14:20', 'deneme', 'Go', 'yanlız → yalnız', 'kaydedildi'),
    ])
    assert g.geri_gelen_duzeltmeler(
        'Nasreddin Hoca bibliyografyası', ['entellektüel → entelektüel'])
    assert g.atla_nedeni('Nasreddin Hoca bibliyografyası', 180, simdi=SIMDI)
    # deneme modundaki kayıtlar sayılmaz
    assert g.atla_nedeni('Go', 180, simdi=SIMDI) is None


def test_yaz_dosyaya_ekler_ve_hemen_gecerli_olur(tmp_path):
    g = gecmis_yaz(tmp_path, [])
    g.yaz('C', GERI_ALINDI, 'test')
    g.kapat()
    assert g.atla_nedeni('C', 0)
    yeniden = TaramaGecmisi(tmp_path / 'tarama_gecmisi.tsv')
    assert 'C' in yeniden.engelli


def test_son_sonucu_deneme_sayfalarini_verir(tmp_path):
    g = gecmis_yaz(tmp_path, [
        ('2026-10-14T00:00:00', 'A', DENEME, 'x → y'),
        ('2026-10-14T01:00:00', 'B', DENEME, 'x → y'),
        ('2026-10-14T02:00:00', 'B', DUZENLENDI, 'x → y'),
        ('2026-10-14T03:00:00', 'C', TEMIZ, ''),
    ])
    assert g.son_sonucu(DENEME) == ['A']
