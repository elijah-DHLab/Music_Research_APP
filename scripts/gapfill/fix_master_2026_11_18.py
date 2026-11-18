"""Apply the 2026-11-18 identity corrections to the V2 works-and-performers master list (Drive xlsx).
Edits cells in place (openpyxl) on the 'performers' sheet; nothing else changes.
Usage: python fix_master_2026_11_18.py IN.xlsx OUT.xlsx
"""
import sys
import openpyxl

TAG = 'manual_fix_2026_11_18'
WD = lambda q: {'wikidata_id': q, 'wikidata_url': 'https://www.wikidata.org/wiki/' + q}
NESS = dict(WD('Q118289471'), entity_type='אדם', wikidata_description='ראפרית ישראלית', gender='נקבה', birth_or_inception_year='2002',
            death_year='', birth_or_origin_country='ישראל', birth_or_formation_city='אשדוד', citizenship='ישראל', genres='', hewiki_title='')
FIX = {  # performer_name -> new values (every value verified on wikidata.org, 2026-11-18)
    'V': dict(WD('Q18388296'), entity_type='אדם', wikidata_description='זמר, מלחין ורקדן דרום-קוריאני, חבר בלהקת הקיי-פופ BTS', gender='זכר',
              birth_or_inception_year='1995', death_year='', birth_or_origin_country='קוריאה הדרומית', birth_or_formation_city='טגו',
              citizenship='קוריאה הדרומית', genres='קיי-פופ | נאו סול', hewiki_title=''),          # was Q54919 (VIAF)
    'Black Sabbath': dict(WD('Q47670'), entity_type='להקה / הרכב', wikidata_description='להקת הבי מטאל בריטית', gender='',
                          birth_or_inception_year='', death_year='', birth_or_origin_country='', birth_or_formation_city='',
                          citizenship='', genres='', hewiki_title=''),                                  # was Q742626 (Heaven & Hell)
    'Ness': NESS, 'Daniel Ness': NESS,                                                                  # were empty
    'Stilla': dict(WD('Q118289474'), entity_type='אדם', wikidata_description='ראפר ישראלי', gender='זכר', birth_or_inception_year='1998',
                   death_year='', birth_or_origin_country='ישראל', birth_or_formation_city='', citizenship='ישראל', genres='', hewiki_title=''),
}


def main(src, dst):
    wb = openpyxl.load_workbook(src)
    ws = wb['performers']
    head = [c.value for c in ws[1]]; col = {h: i + 1 for i, h in enumerate(head)}
    done = []
    for r in range(2, ws.max_row + 1):
        name = ws.cell(r, col['performer_name']).value
        if name in FIX:
            for k, v in FIX[name].items(): ws.cell(r, col[k]).value = v or None
            ws.cell(r, col['metadata_status']).value = TAG
            done.append(name)
    wb.save(dst)
    print('fixed', done, 'missing', sorted(set(FIX) - set(done)))


if __name__ == '__main__':
    main(*sys.argv[1:3])
