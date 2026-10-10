#!/usr/bin/env python3
"""check_lef_vs_spec.py -- top dung de NGHIEM THU LEF abstract ma block giao.
So voi spec: SIZE, ten pin, chieu, layer, toa do tam pin (sai so 0.005um), strap PG metal7.

  python3 check_lef_vs_spec.py <block.lef> <spec>/blocks/<blk>/<module>_ports.csv [<spec>/blocks/<blk>/<module>_prelim.lef]

Tham so 3 (tuy chon): LEF so bo cua spec, de lay SIZE + vi tri strap PG chuan.
Thoat 0 = DAT, 1 = KHONG DAT (in danh sach loi).
"""
import csv, re, sys

def parse_lef(path):
    t = open(path).read()
    m = re.search(r'\bMACRO\s+(\S+)(.*?)\bEND\s+\1\b', t, re.S)
    if not m: raise SystemExit(f'khong thay MACRO trong {path}')
    name, body = m.group(1), m.group(2)
    size = tuple(float(v) for v in re.search(r'\bSIZE\s+([\d.]+)\s+BY\s+([\d.]+)', body).groups())
    pins = {}
    for pm in re.finditer(r'^\s*PIN\s+(\S+)\s*\n(.*?)^\s*END\s+\1\s*$', body, re.S | re.M):
        pn, pb = pm.group(1), pm.group(2)
        d = re.search(r'DIRECTION\s+(\w+)', pb)
        shapes = []
        layer = None
        for line in pb.splitlines():
            lm = re.match(r'\s*LAYER\s+(\S+)\s*;', line)
            if lm: layer = lm.group(1)
            rm = re.match(r'\s*RECT\s+(?:MASK\s+\d+\s+)?([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)', line)
            if rm: shapes.append((layer, tuple(float(v) for v in rm.groups())))
        pins[pn] = dict(dir=d.group(1) if d else '', shapes=shapes)
    return name, size, pins

def main():
    lef, pcsv = sys.argv[1], sys.argv[2]
    ref = sys.argv[3] if len(sys.argv) > 3 else None
    name, size, pins = parse_lef(lef)
    errs = []
    if ref:
        rname, rsize, rpins = parse_lef(ref)
        if rname != name: errs.append(f'ten MACRO {name} != spec {rname}')
        if abs(size[0] - rsize[0]) > 1e-3 or abs(size[1] - rsize[1]) > 1e-3: errs.append(f'SIZE {size} != spec {rsize}')
        for net in ('VDD', 'VSS'):
            want = sorted(round((s[1][1] + s[1][3]) / 2, 2) for s in rpins[net]['shapes'] if s[0] == 'metal7')
            got = sorted(round((s[1][1] + s[1][3]) / 2, 2) for s in pins.get(net, {'shapes': []})['shapes'] if s[0] == 'metal7')
            missing = [y for y in want if not any(abs(y - g) < 0.01 for g in got)]
            if missing: errs.append(f'{net}: thieu {len(missing)}/{len(want)} strap metal7 (vd y={missing[:3]})')
    # Block khong duoc chan metal8..metal10 (top can de strap metal8/9 va route tren block)
    lefbody = open(lef).read()
    obs = re.search(r'\bOBS\b(.*?)\bEND\b', lefbody, re.S)
    if obs:
        bad = sorted(set(re.findall(r'LAYER\s+(metal8|metal9|metal10)\b', obs.group(1))))
        if bad: errs.append(f'OBS tren {bad}: block khong duoc chan metal8-10 (xem lai routing blockage / write_lef_abstract -specifyTopLayer metal7)')
    rows = list(csv.DictReader(open(pcsv)))
    spec_names = set()
    for r in rows:
        pn = r['pin']; spec_names.add(pn)
        if pn not in pins: errs.append(f'thieu pin {pn}'); continue
        p = pins[pn]
        want_dir = 'INPUT' if r['dir'] == 'in' else 'OUTPUT'
        if p['dir'] != want_dir: errs.append(f'{pn}: DIRECTION {p["dir"]} != {want_dir}')
        x, y = float(r['x_um']), float(r['y_um'])
        ok = False
        for lay, (x0, y0, x1, y1) in p['shapes']:
            if lay != r['layer']: continue
            if r['side'] in ('left', 'right'):
                if abs((y0 + y1) / 2 - y) < 0.005 and x0 - 1e-3 <= x <= x1 + 1e-3: ok = True
            else:
                if abs((x0 + x1) / 2 - x) < 0.005 and y0 - 1e-3 <= y <= y1 + 1e-3: ok = True
        if not ok: errs.append(f'{pn}: vi tri/layer khac spec (spec {r["layer"]} @ {x},{y}; LEF {p["shapes"][:1]})')
    extra = [p for p in pins if p not in spec_names and p not in ('VDD', 'VSS')]
    if extra: errs.append(f'{len(extra)} pin thua khong co trong spec (vd {extra[:3]})')
    print(f'{name}: {len(rows)} pin spec, {len(pins)} pin trong LEF, {len(errs)} loi')
    for e in errs[:40]: print('  LOI:', e)
    sys.exit(1 if errs else 0)

if __name__ == '__main__':
    main()
