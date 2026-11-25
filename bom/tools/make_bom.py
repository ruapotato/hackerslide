#!/usr/bin/env python3
"""Build bom/bom.csv from the generated netlists and re-query every JLCPCB part code.

Usage: python3 bom/tools/make_bom.py            (run from anywhere; needs network access, no account)

Board parts come from hardware/<board>/netlist.json (the LCSC / MPN fields on every symbol).  Price, stock and
basic/extended status are read from JLCPCB's public parts search and stamped with today's date.  Parts that are
not on a board (module, display, battery, hardware) are listed in OFF_BOARD below with the page they were read
from; their prices are NOT re-queried by this script.
"""
import csv
import datetime
import json
import os
import time
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
BOARDS = ('carrier', 'keyboard')
API = 'https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList'
TODAY = datetime.date.today().isoformat()

# item, maker, MPN, qty per device, unit price USD, source URL, date read, status, note
OFF_BOARD = [
    ('Compute module (2 GB, Wi-Fi, no eMMC)', 'LuckFox', 'Core3566102000', 1, 83.99, 'https://www.luckfox.com/EN-Core3566', '2026-11-24',
     'in stock', 'every eMMC SKU was out of stock; boots from microSD'),
    ('Display 4.0" 480x800 IPS DSI + touch', 'Focus LCDs', 'E40RB-I-MW430-CB', 1, 77.20, 'https://focuslcds.com/product/e40rb-i-mw430-cb/', '2026-11-24',
     '10 in stock, Recommended for New Designs', 'ST7701S + GT911'),
    ('Battery pack 1S2P LiPo 2800 mAh min with PCM and NTC', 'BAK', 'LP-454965-2P-3M', 1, None,
     'https://uk.farnell.com/bak/lp-454965-2p-3m/battery-lithium-ion-3-7v-3000mah/dp/2401855', '',
     'Farnell 2401855: stock and price NOT verified (about EUR 24 seen at a reseller, April 2026)',
     'max 9.5 x 50 x 68 mm; 5.6 A max discharge, 1.4 A max charge; datasheet farnell.com/datasheets/1806914.pdf'),
    ('M2.5 SMT spacer 1.5 mm (module)', 'Wurth Elektronik', '9774015151R', 4, 0.47, 'https://jlcpcb.com/partdetail/C5353804', '2026-11-24',
     '1851 at JLC', 'on the carrier BOM as H1-H4'),
    ('M1.6 SMT spacer 1.5 mm (top plate)', 'Wurth Elektronik', '9774015633R', 4, 1.46, 'https://jlcpcb.com/partdetail/C22431491', '2026-11-24',
     '0 at JLC: buy elsewhere, hand solder', 'keyboard H1-H4'),
    ('Wi-Fi antenna, U.FL', '', '', 1, None, '', '', 'estimate', 'included with the Wi-Fi SKU per LuckFox; not verified'),
    ('N52 disc magnet 6 x 1 mm', '', '', 4, None, '', '', 'estimate', 'body detents'),
    ('N52 disc magnet 6 x 2 mm', '', '', 2, None, '', '', 'estimate', 'tray detents'),
    ('N52 disc magnet 5 x 2 mm', '', '', 1, None, '', '', 'estimate', 'slider sense magnet'),
    ('M2 heat-set insert 3.2 x 3 mm + M2 screw', '', '', 2, None, '', '', 'estimate', 'body screws'),
    ('M2.5 x 4 screw (module to spacers)', '', '', 4, None, '', '', 'estimate', ''),
    ('M1.6 x 3 screw (top plate)', '', '', 4, None, '', '', 'estimate', ''),
    ('Thermal pad / copper shim 14 x 14 x 0.4 mm', '', '', 1, None, '', '', 'estimate', 'thickness follows config.THERMAL_GAP'),
    ('Cover/keycaps/enclosure prints', '', '', 1, None, '', '', 'estimate', 'FDM for the fit mule'),
]


def jlc(code):
    req = urllib.request.Request(API, data=json.dumps({'keyword': code, 'currentPage': 1, 'pageSize': 5}).encode(),
                                 headers={'content-type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    for c in (d.get('data') or {}).get('componentPageInfo', {}).get('list') or []:
        if c['componentCode'] == code:
            return c
    return None


def price_at(c, qty):
    best = None
    for p in sorted(c.get('componentPrices') or [], key=lambda p: p['startNumber']):
        if p['startNumber'] <= max(qty, 1) or best is None:
            best = p['productPrice']
    return best


def main():
    rows, cache = [], {}
    for board in BOARDS:
        comps = json.load(open(os.path.join(ROOT, 'hardware', board, 'netlist.json')))['components']
        groups = {}
        for c in comps:
            if not c.get('in_bom', True):
                continue
            f = c['fields']
            key = (f.get('LCSC', ''), f.get('MPN', ''), c['value'], c['footprint'], bool(c.get('dnp')))
            groups.setdefault(key, []).append(c['ref'])
        for (lcsc, mpn, value, fp, dnp), refs in sorted(groups.items(), key=lambda kv: kv[1][0]):
            info = None
            if lcsc:
                if lcsc not in cache:
                    try:
                        cache[lcsc] = jlc(lcsc)
                    except Exception as e:           # network trouble: keep the row, mark it
                        cache[lcsc] = {'error': str(e)}
                    time.sleep(0.35)
                info = cache[lcsc]
            ok = info and 'error' not in info
            qty = len(refs)
            rows.append({
                'board': board, 'refs': ' '.join(sorted(refs, key=lambda r: (r.rstrip('0123456789'), int('0' + ''.join(ch for ch in r if ch.isdigit()))))),
                'qty': qty, 'fitted': 'DNP' if dnp else 'yes', 'value': value, 'footprint': fp.split(':')[-1],
                'maker': (info['componentBrandEn'] if ok else ''), 'mpn': mpn,
                'lcsc': lcsc,
                'jlc_type': ({'base': 'basic', 'expand': 'extended'}.get(info['componentLibraryType'], info['componentLibraryType']) if ok else ''),
                'unit_price_usd': (price_at(info, qty * 5) if ok else ''),      # price break for a run of 5 boards
                'stock': (info['stockCount'] if ok else ''),
                'source_url': (f'https://jlcpcb.com/partdetail/{lcsc}' if lcsc else ''),
                'date_checked': TODAY if ok else '',
                'status': ('in stock' if ok and info['stockCount'] > 0 else 'OUT OF STOCK' if ok else
                           'not found at JLC' if lcsc else 'not a purchased part' if not mpn or 'solder' in mpn else 'buy elsewhere'),
            })
    for (item, maker, mpn, qty, price, url, date, status, note) in OFF_BOARD:
        rows.append({'board': 'device', 'refs': item, 'qty': qty, 'fitted': 'yes', 'value': note, 'footprint': '', 'maker': maker,
                     'mpn': mpn, 'lcsc': '', 'jlc_type': '', 'unit_price_usd': '' if price is None else price, 'stock': '',
                     'source_url': url, 'date_checked': date, 'status': status})
    out = os.path.join(ROOT, 'bom', 'bom.csv')
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # summary
    for board in BOARDS:
        br = [r for r in rows if r['board'] == board and r['fitted'] == 'yes']
        cost = sum(float(r['unit_price_usd'] or 0) * r['qty'] for r in br)
        ext = len({r['lcsc'] for r in br if r['jlc_type'] == 'extended'})
        miss = [r['refs'] for r in br if r['status'] not in ('in stock', 'not a purchased part')]
        low = [(r['mpn'], r['stock']) for r in br if r['stock'] != '' and int(r['stock']) < 500]
        print(f'{board}: {len(br)} lines, {sum(r["qty"] for r in br)} parts, parts cost ${cost:.2f}, {ext} extended part types')
        print('   not in stock / not at JLC:', miss)
        print('   stock below 500:', low)
    print('wrote', out)


if __name__ == '__main__':
    main()
