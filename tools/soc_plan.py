#!/usr/bin/env python3
"""soc_plan.py -- top-level plan cho SoC OpenC910 (2 core) chia 4 block + top, Nangate45.
Doc: blkports.json (ket noi bit-level da elaborate), RTL (khai bao port), mem/macro_table.csv.
Ghi: plan.json (toan bo so lieu) -- cac script emit_*.py doc plan.json de sinh file cho tung nguoi.
"""
import json, collections, re, os, math, sys

RTL = '/tmp/claude-0/bt/rtl/C910_RTL_FACTORY/gen_rtl'
GEN = '/tmp/claude-0/soc/rtl_gen'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/soc/plan.json'
T = 2.5          # ns, CPU_CLK 400 MHz
TRK_H0, TRK_V0, TRK = 0.07, 0.095, 0.28   # track: ngang y=0.07+0.28k (M3 cach 1, M5 moi track); doc x=0.095+0.28k (M4,M6)

# ----------------------------------------------------------------------------- floorplan
DIE = dict(w=3601.64, h=5062.4)
MASTERS = {
  'FE':  dict(module='ct_ifu_top', w=1356.79, h=728.0,  insts=['core0_fe', 'core1_fe'],
              desc='Instruction Fetch Unit (I$ 64KB, BTB, BHT) -- 1 core'),
  'BE':  dict(module='c910_be',    w=1356.79, h=2240.0, insts=['core0_be', 'core1_be'],
              desc='Phan con lai cua core: IDU IU VFPU LSU(D$ 64KB) RTU CP0 MMU PMP BIU HAD HPCP'),
  'CIU': dict(module='ct_ciu_top', w=638.59,  h=2240.0, insts=['ciu'],
              desc='Coherence Interconnect Unit: snoop buffer, PIU x2, EBIU (AXI master ra chip)'),
  'L2C': dict(module='ct_l2c_top', w=3436.91, h=1848.0, insts=['l2c'],
              desc='L2 cache 1MB, 16-way, 2 sub-bank'),
}
INSTS = {   # vi tri goc duoi-trai (x,y) cua hop SAU khi xoay, huong
  'l2c':      dict(master='L2C', x=79.8,    y=78.4,   orient='R0', hier='x_ct_l2c_top'),
  'core0_be': dict(master='BE',  x=79.8,    y=1971.2, orient='R0', hier='x_ct_top_0/x_c910_be'),
  'ciu':      dict(master='CIU', x=1478.96, y=1971.2, orient='R0', hier='x_ct_ciu_top'),
  'core1_be': dict(master='BE',  x=2159.92, y=1971.2, orient='MY', hier='x_ct_top_1/x_c910_be'),
  'core0_fe': dict(master='FE',  x=79.8,    y=4256.0, orient='R0', hier='x_ct_top_0/x_ct_ifu_top'),
  'core1_fe': dict(master='FE',  x=2159.92, y=4256.0, orient='MY', hier='x_ct_top_1/x_ct_ifu_top'),
}
TOPLOGIC = dict(x=1478.96, y=4256.0, w=638.59, h=728.0)   # vung dat logic cua top (plic, clint, sysio, had_common, mp_clk, mp_rst)
GRID_X, GRID_Y = 5.32, 11.2

def rect(i):
    d = INSTS[i]; m = MASTERS[d['master']]
    return d['x'], d['y'], d['x'] + m['w'], d['y'] + m['h']

# ----------------------------------------------------------------------------- port declarations
def decls(path, module):
    t = re.sub(r'//[^\n]*', '', open(path).read())
    m = re.search(r'\bmodule\s+' + module + r'\b(.*?)\bendmodule', t, re.S)
    d = {}
    for mm in re.finditer(r'^\s*(input|output|inout)\s+(?:\[\s*(\d+)\s*:\s*(\d+)\s*\])?\s*(\w+)\s*;', m.group(1), re.M):
        k, a, b, n = mm.groups()
        d[n] = (k, int(a) if a else None, int(b) if b else None)
    return d
DECL = {
  'FE': decls(f'{RTL}/ifu/rtl/ct_ifu_top.v', 'ct_ifu_top'),
  'BE': decls(f'{GEN}/c910_be.v', 'c910_be'),
  'CIU': decls(f'{RTL}/ciu/rtl/ct_ciu_top.v', 'ct_ciu_top'),
  'L2C': decls(f'{RTL}/l2c/rtl/ct_l2c_top.v', 'ct_l2c_top'),
}
def pin_name(master, port, nbit):
    k, a, b = DECL[master][port]
    if a is None: return port
    idx = b + nbit if a >= b else b - nbit
    return f'{port}[{idx}]'

# ----------------------------------------------------------------------------- ket noi
P = json.load(open('/tmp/claude-0/soc/blkports.json'))
INST_OF_MASTER = {'core0_fe': 'FE', 'core1_fe': 'FE', 'core0_be': 'BE', 'core1_be': 'BE', 'ciu': 'CIU', 'l2c': 'L2C'}
byset = collections.defaultdict(list)
for p in P: byset[p['set']].append(p)
CLOCKS = {('FE', 'forever_cpuclk'), ('BE', 'pll_core_clk'), ('BE', 'forever_cpuclk'), ('CIU', 'forever_cpuclk'),
          ('L2C', 'forever_cpuclk'), ('L2C', 'l2c_data_clk_bank_0'), ('L2C', 'l2c_data_clk_bank_1'),
          ('L2C', 'l2c_tag_clk_bank_0'), ('L2C', 'l2c_tag_clk_bank_1')}

def partners(p):
    return set(x.split(':')[0] if x.startswith(('IO', 'toplogic')) else x for x in p['drv'] + p['loads'])

# chi lay instance dai dien de dat pin: core0_fe, core0_be, ciu, l2c
REP = {'FE': 'core0_fe', 'BE': 'core0_be', 'CIU': 'ciu', 'L2C': 'l2c'}
ports = {m: [] for m in MASTERS}
for p in P:
    if p['inst'] in REP.values():
        m = INST_OF_MASTER[p['inst']]
        q = dict(p); q['master'] = m; q['pin'] = pin_name(m, p['port'], p['bit'])
        q['partners'] = sorted(partners(p)); q['clock'] = (m, p['port']) in CLOCKS
        ports[m].append(q)

def group_of(q):
    m, pt = q['master'], set(q['partners'])
    if m == 'FE': return 'FE_BE'                                     # moi port FE deu ve BE (+ scan_en)
    if m == 'BE':
        if pt == {'core0_fe'}: return 'FE_BE'
        if pt == {'ciu'}: return 'BE_CIU'
        if pt == {'IO'} and len(q['drv'] + q['loads']) == 1: return 'BE_IO'
        return 'BE_TOP'
    if m == 'CIU':
        if pt == {'core0_be'}: return 'BE_CIU'
        if pt == {'core1_be'}: return 'BE1_CIU'
        if pt == {'l2c'}: return 'CIU_L2C'
        return 'CIU_TOP'
    if m == 'L2C':
        if pt == {'ciu'}: return 'CIU_L2C'
        return 'L2C_TOP'
for m in ports:
    for q in ports[m]: q['group'] = group_of(q)

# ----------------------------------------------------------------------------- slot helpers
def snap_up(v, off): return round(off + math.ceil((v - off) / TRK - 1e-9) * TRK, 4)
def slots(n, a, b, off, minstep=TRK):
    """n pin tren doan [a,b] (toa do tuong doi canh), 2 lop/vi tri -> list (pos, lop 0|1)."""
    npos = (n + 1) // 2
    if npos == 0: return []
    step = max(minstep, math.floor(((b - a) / max(npos, 1)) / TRK) * TRK)
    span = (npos - 1) * step
    if span > b - a + 1e-6: raise SystemExit(f'khong du cho: {n} pin tren {b - a:.1f} um')
    start = snap_up(a + ((b - a) - span) / 2, off)
    out = []
    for i in range(n):
        out.append((round(start + (i // 2) * step, 4), i % 2))
    return out
LAYERS = {'H': ('metal3', 'metal5'), 'V': ('metal4', 'metal6')}
SIDE_DIR = {'left': 'H', 'right': 'H', 'top': 'V', 'bottom': 'V'}

def natkey(q):  # port name, then bit (MSB truoc) de bus nam canh nhau
    return (q['port'], -q['bit'])

def place(qs, side, a, b, master, clock_center=True):
    """Gan toa do cho list port q tren 1 canh cua master (toa do tuong doi R0)."""
    W, H = MASTERS[master]['w'], MASTERS[master]['h']
    d = SIDE_DIR[side]; off = TRK_H0 if d == 'H' else TRK_V0
    clk = [q for q in qs if q['clock']]; sig = [q for q in qs if not q['clock']]
    res = []
    if clk and clock_center:
        mid = (a + b) / 2
        # clock o giua, lop tren (metal5/metal6), cach 3um moi ben khong co pin khac
        for k, q in enumerate(clk):
            pos = snap_up(mid + k * 12 * TRK, off); res.append((q, pos, LAYERS[d][1]))
        lo, hi = mid - 3.0, mid + 3.0 + len(clk) * 12 * TRK
        n1 = len(sig) // 2
        s1 = slots(n1, a, lo, off); s2 = slots(len(sig) - n1, hi, b, off)
        ss = s1 + s2
    else:
        ss = slots(len(sig), a, b, off)
    for q, (pos, li) in zip(sig, ss): res.append((q, pos, LAYERS[d][li]))
    for q, pos, lay in res:
        q['side'] = side; q['layer'] = lay
        if side == 'left': q['x'], q['y'] = 0.0, pos
        elif side == 'right': q['x'], q['y'] = W, pos
        elif side == 'bottom': q['x'], q['y'] = pos, 0.0
        else: q['x'], q['y'] = pos, H
    return res

def aligned(pairs_a, side_a, master_a, side_b, master_b, a, b, delta):
    """pairs: list (qa, qb) cung net; dat qa tren canh side_a cua master_a; qb cung toa do (+delta) tren side_b."""
    pairs_a.sort(key=lambda t: natkey(t[0]))
    res = place([t[0] for t in pairs_a], side_a, a, b, master_a)
    m = {id(q): q for q, _, _ in res}
    for qa, qb in pairs_a:
        qb['side'] = side_b; qb['layer'] = qa['layer']
        Wb, Hb = MASTERS[master_b]['w'], MASTERS[master_b]['h']
        if SIDE_DIR[side_b] == 'H':
            qb['y'] = round(qa['y'] + delta, 4); qb['x'] = 0.0 if side_b == 'left' else Wb
        else:
            qb['x'] = round(qa['x'] + delta, 4); qb['y'] = 0.0 if side_b == 'bottom' else Hb

# --- ghep cap theo net (set)
def by_group(m, g): return [q for q in ports[m] if q['group'] == g]
def pair(m1, g1, m2, g2):
    s2 = collections.defaultdict(list)
    for q in by_group(m2, g2): s2[q['set']].append(q)
    out, lone = [], []
    for q in by_group(m1, g1):
        if q['set'] in s2: out.append((q, s2[q['set']][0]))
        else: lone.append(q)
    return out, lone

# 1) FE bottom <-> BE top (cung x vi cung goc x)
fe_be, lone = pair('FE', 'FE_BE', 'BE', 'FE_BE')
W_FE = MASTERS['FE']['w']
aligned(fe_be, 'bottom', 'FE', 'top', 'BE', 40.0, W_FE - 40.0, 0.0)
# FE port khong noi BE (scan_en): dat rieng o goc phai canh duoi
if lone:
    place(lone, 'bottom', W_FE - 38.0, W_FE - 20.0, 'FE', clock_center=False)

# 2) BE right <-> CIU left (cung y). Doan giua cua canh.
be_ciu, lone2 = pair('BE', 'BE_CIU', 'CIU', 'BE_CIU')
assert not lone2, lone2[:3]
H_BE = MASTERS['BE']['h']
aligned(be_ciu, 'right', 'BE', 'left', 'CIU', 300.0, 1700.0, 0.0)
# CIU right edge cho core1: cung y voi pin BE (BE1 lat MY -> pin BE nam o canh trai, cung y)
ciu_core1 = by_group('CIU', 'BE1_CIU')
be_by_set = {}
for q in by_group('BE', 'BE_CIU'): be_by_set[q['set']] = q
# map set core1 -> pin BE: tim port BE tuong ung bang ten port cua CIU (core0 vs core1 cung mau)
ciu0 = {}  # (port_without_core_idx) -> y
for qa, qb in be_ciu: ciu0[(qb['port'], qb['bit'])] = qb
def core0_name(n):
    return re.sub(r'(piu|core|cpu|biu)1', r'\g<1>0', n)
miss = []
for q in ciu_core1:
    cand = ciu0.get((core0_name(q['port']), q['bit']))
    if cand is None: miss.append(q['port']); continue
    q['side'] = 'right'; q['layer'] = cand['layer']; q['x'] = MASTERS['CIU']['w']; q['y'] = cand['y']
# kiem tra: port core1 cua CIU noi toi port BE1 co cung ten voi port BE0 noi toi cand
if miss: raise SystemExit(f'CIU core1 khong ghep duoc: {sorted(set(miss))[:10]}')

# 3) CIU bottom <-> L2C top (cung x tuyet doi)
ciu_l2c, lone3 = pair('CIU', 'CIU_L2C', 'L2C', 'CIU_L2C')
assert not lone3
dx = INSTS['ciu']['x'] - INSTS['l2c']['x']
aligned(ciu_l2c, 'bottom', 'CIU', 'top', 'L2C', 8.0, MASTERS['CIU']['w'] - 8.0, dx)

# 4) BE left = IO cua core (cung y voi pin die)
place(sorted(by_group('BE', 'BE_IO'), key=natkey), 'left', 500.0, 1700.0, 'BE', clock_center=False)
# 5) BE right, doan tren = top logic / broadcast / clock pll_core_clk
place(sorted(by_group('BE', 'BE_TOP'), key=natkey), 'right', 1760.0, H_BE - 10.0, 'BE')
# 6) CIU top = IO (AXI...) + top logic
place(sorted(by_group('CIU', 'CIU_TOP'), key=natkey), 'top', 10.0, MASTERS['CIU']['w'] - 10.0, 'CIU')
# 7) L2C top, trong kenh giua CIU va core1_be
cx0 = INSTS['ciu']['x'] + MASTERS['CIU']['w'] - INSTS['l2c']['x'] + 6.0
cx1 = INSTS['core1_be']['x'] - INSTS['l2c']['x'] + 60.0   # kenh CIU-BE1 + 60um duoi BE1 (BE1 day khong co pin)
place(sorted(by_group('L2C', 'L2C_TOP'), key=natkey), 'top', cx0, cx1, 'L2C')

for m in ports:
    bad = [q['pin'] for q in ports[m] if 'x' not in q]
    if bad: raise SystemExit(f'{m}: {len(bad)} pin chua dat: {bad[:5]}')

# ----------------------------------------------------------------------------- toa do tuyet doi cua moi instance
def to_abs(inst, x, y):
    d = INSTS[inst]; m = MASTERS[d['master']]
    if d['orient'] == 'R0': return round(d['x'] + x, 4), round(d['y'] + y, 4)
    if d['orient'] == 'MY': return round(d['x'] + m['w'] - x, 4), round(d['y'] + y, 4)
    raise ValueError

# ----------------------------------------------------------------------------- IO cua chip (pin tren die)
IOS = collections.defaultdict(dict)   # ten port chip -> {bit: info}
io_eps = collections.defaultdict(list)
for p in P:
    for x in p['drv'] + p['loads']:
        if x.startswith('IO:'): io_eps[x[3:]].append(p)
# lay danh sach IO day du tu RTL openC910
D_TOP = decls(f'{RTL}/cpu/rtl/openC910.v', 'openC910')
def io_bits(n):
    k, a, b = D_TOP[n]
    if a is None: return [(n, None)]
    lo, hi = min(a, b), max(a, b)
    return [(f'{n}[{i}]', i) for i in range(lo, hi + 1)]
io_list = []
for n, (k, a, b) in D_TOP.items():
    for full, i in io_bits(n): io_list.append(dict(name=n, pin=full, dir=k, idx=i))
# block pin nao noi truc tiep toi IO: tim theo set; bit cua IO = so thu tu bit trong set (nm). Dung blkports: drv/loads
# ghi lai IO nao noi toi pin BE (core0) / CIU de canh hang
blk_of_io = {}
for m in ('BE', 'CIU'):
    for q in ports[m]:
        if q['group'] not in ('BE_IO', 'CIU_TOP'): continue
        ios = [x[3:] for x in q['drv'] + q['loads'] if x.startswith('IO:')]
        if len(ios) == 1 and len(q['drv'] + q['loads']) == 1:
            blk_of_io.setdefault((ios[0], q['set']), q)
# bit-level: blkports khong cho chi so bit cua IO -> dung conn_blk.out (EP I ...)
io_set = {}
for l in open('/tmp/claude-0/soc/conn_blk.out'):
    f = l.split()
    if f[0] == 'EP' and f[2] == 'I': io_set[(f[4], int(f[5]))] = int(f[1])
set2q = {}
for m in ('BE', 'CIU'):
    for q in ports[m]: set2q.setdefault(q['set'], q)
# set cua core1 cho IO core1 -> pin BE core0 tuong ung (doi ten core1->core0)
DIE_W, DIE_H = DIE['w'], DIE['h']
io_pins = []
left_used, right_used, top_used = [], [], []
pending_top = []
for io in io_list:
    k, a, b = D_TOP[io['name']]
    nbit = 0 if a is None else (io['idx'] - min(a, b))
    s = io_set.get((io['name'], nbit))
    q = set2q.get(s)
    rec = dict(io)
    if q is not None and q['master'] == 'BE' and q['group'] == 'BE_IO':
        ax, ay = to_abs('core0_be', q['x'], q['y'])
        rec.update(side='left', x=0.0, y=ay, layer=q['layer'], blk_pin=q['pin'], blk='core0_be')
    elif q is not None and q['master'] == 'CIU' and q['group'] == 'CIU_TOP':
        ax, ay = to_abs('ciu', q['x'], q['y'])
        rec.update(side='top', x=ax, y=DIE_H, layer=q['layer'], blk_pin=q['pin'], blk='ciu')
    else:
        rec.update(side=None)
    io_pins.append(rec)
# IO core1: tim pin BE cung ten (core1->core0) -> canh phai, cung y
by_name0 = {(r['name'], r['idx']): r for r in io_pins if r['side'] == 'left'}
for r in io_pins:
    if r['side'] is None and 'core1' in r['name']:
        r0 = by_name0.get((r['name'].replace('core1', 'core0'), r['idx']))
        if r0:
            r.update(side='right', x=DIE_W, y=r0['y'], layer=r0['layer'], blk='core1_be', blk_pin=r0['blk_pin'])
# con lai (top logic: clock, reset, plic irq, jtag, dft, sys...) -> canh tren, doan giua, tranh cho da dung
rest = [r for r in io_pins if r['side'] is None]
used_top = sorted(r['x'] for r in io_pins if r['side'] == 'top')
# doan giua canh tren: x tu TOPLOGIC.x den TOPLOGIC.x+w ; chon slot V track con trong
cands = []
x = snap_up(TOPLOGIC['x'] + 5.0, TRK_V0)
used = set(round(v, 3) for v in used_top)
while x < TOPLOGIC['x'] + TOPLOGIC['w'] - 5.0:
    cands.append(round(x, 4)); x += TRK
free = [c for c in cands if all(abs(c - u) > 0.27 for u in used_top)]
# clock dat giua, cach rong
rest.sort(key=lambda r: (r['name'] not in ('pll_cpu_clk', 'pad_had_jtg_tclk'), r['name'], r['idx'] if r['idx'] is not None else 0))
need = len(rest)
# dung buoc 2 track de thua
step = max(1, len(free) // max(need, 1))
step = min(step, 3)
pick = free[::step][:need]
if len(pick) < need: pick = free[:need]
if len(pick) < need: raise SystemExit('canh tren khong du cho IO')
# trai deu: clock o giua
mid = len(pick) // 2
order = sorted(range(len(pick)), key=lambda i: abs(i - mid))
for r, i in zip(rest, order):
    r.update(side='top', x=pick[i], y=DIE_H, layer='metal6' if r['name'] in ('pll_cpu_clk', 'pad_had_jtg_tclk') else ('metal4' if i % 2 == 0 else 'metal6'))
for r in io_pins: assert r['side'], r

# ----------------------------------------------------------------------------- macro (de xuat dat de chung minh kha thi)
MT = {}
for l in list(open('/tmp/claude-0/soc/mem/macro_table.csv'))[1:]:
    f = l.strip().split(','); MT[f[0]] = dict(w=float(f[3]), h=float(f[4]), area=float(f[5]), clk2q=float(f[6]), pins=int(f[7]))
srams = collections.defaultdict(list)
for l in open('/tmp/claude-0/soc/hier_d2.txt'):
    if not l.startswith('SRAM'): continue
    _, cell, path = l.split()
    path = path.replace('openC910/', '')
    cfg = cell.replace('ct_f_spsram_', '')
    if path.startswith('x_ct_top_0/'):
        rel = path[len('x_ct_top_0/'):].replace('x_ct_core/', '')
        mst = 'FE' if rel.startswith('x_ct_ifu_top/') else 'BE'
        if mst == 'FE': rel = rel[len('x_ct_ifu_top/'):]
    elif path.startswith('x_ct_l2c_top/'):
        mst = 'L2C'; rel = path[len('x_ct_l2c_top/'):]
    else: continue
    srams[mst].append(dict(inst=rel + '/x_sram_macro', cell='fakeram45_' + cfg))
HALO = 10.0
def shelf(master, rows):
    """rows: list of (y_bottom, [macro dict..], x_start, orient). tra ve list dat."""
    out = []
    for y0, items, x0, orient in rows:
        x = x0
        for it in items:
            mt = MT[it['cell']]
            xs = round(math.ceil(x / 0.19 - 1e-9) * 0.19, 3)
            ys = round(math.ceil(y0 / 1.4 - 1e-9) * 1.4, 3)
            out.append(dict(it, x=xs, y=ys, w=mt['w'], h=mt['h'], orient=orient))
            x = xs + mt['w'] + 2 * HALO
    return out
def take(master, pred):
    L = [s for s in srams[master] if pred(s)]
    for s in L: srams[master].remove(s)
    return L
macro_place = {}
# FE: 3 hang tu canh tren (canh ngoai), logic o duoi (sat BE)
fe_all = list(srams['FE'])
big = take('FE', lambda s: s['cell'] in ('fakeram45_2048x32', 'fakeram45_1024x64'))
r1, r2 = big[:6], big[6:]
r2 += take('FE', lambda s: s['cell'] == 'fakeram45_512x59')
r3 = take('FE', lambda s: True)
H_FE = MASTERS['FE']['h']
def fl14(v): return round(math.floor(v / 1.4 + 1e-9) * 1.4, 3)
y1 = fl14(H_FE - HALO - 193.2); y2 = fl14(y1 - 2 * HALO - 193.2); y3 = fl14(y2 - 2 * HALO - 116.2)
macro_place['FE'] = shelf('FE', [(y1, r1, HALO, 'R0'), (y2, r2, HALO, 'R0'), (y3, r3, HALO, 'R0')])
# BE: 2 hang sat canh duoi (canh nay chi co 2 net) -> logic phia tren
big = take('BE', lambda s: s['cell'] == 'fakeram45_2048x32')
rest_be = take('BE', lambda s: True)
rest_be.sort(key=lambda s: -MT[s['cell']]['h'])
def ce14(v): return round(math.ceil(v / 1.4 - 1e-9) * 1.4, 3)
r1 = ce14(HALO); r2 = ce14(r1 + 193.2 + 2 * HALO)
macro_place['BE'] = shelf('BE', [(r1, big[:6], HALO, 'R0'), (r2, big[6:] + rest_be, HALO, 'R0')])
# L2C: 2 hang macro du lieu 8192x128 o duoi; dai tren (gan CIU) cho tag/dirty + logic
dat = take('L2C', lambda s: s['cell'] == 'fakeram45_8192x128')
dat.sort(key=lambda s: s['inst'])
sb0 = [s for s in dat if 'sub_bank_0' in s['inst']]; sb1 = [s for s in dat if 'sub_bank_1' in s['inst']]
W_L2 = MASTERS['L2C']['w']; x0 = (W_L2 - 4 * 780.0) / 2 + HALO
rowA = [sb0[0], sb0[1], sb1[0], sb1[1]]; rowB = [sb0[2], sb0[3], sb1[2], sb1[3]]
tg = take('L2C', lambda s: True)
t0 = sorted([s for s in tg if 'sub_bank_0' in s['inst']], key=lambda s: (MT[s['cell']]['w'], s['inst']))
t1 = sorted([s for s in tg if 'sub_bank_1' in s['inst']], key=lambda s: (MT[s['cell']]['w'], s['inst']))
yb = ce14(ce14(HALO) + 760.2 + 2 * HALO)
ytag = round(math.floor((MASTERS['L2C']['h'] - HALO - 204.4) / 1.4) * 1.4, 3)
w_t1 = sum(MT[s['cell']]['w'] + 2 * HALO for s in t1)
macro_place['L2C'] = shelf('L2C', [(HALO, rowA, x0, 'R0'), (yb, rowB, x0, 'R0'),
                                   (ytag, t0, HALO + 10, 'R0'), (ytag, t1, W_L2 - w_t1 - 10, 'R0')])
macro_place['CIU'] = []
# kiem tra chong lan + nam trong block + khong de len pin
for m, L in macro_place.items():
    W, H = MASTERS[m]['w'], MASTERS[m]['h']
    for a in L:
        assert a['x'] >= HALO - 1e-6 and a['y'] >= HALO - 1e-6 and a['x'] + a['w'] <= W - HALO + 1e-6 and a['y'] + a['h'] <= H - HALO + 1e-6, (m, a)
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            a, b = L[i], L[j]
            if a['x'] < b['x'] + b['w'] + 2 * HALO - 1e-6 and b['x'] < a['x'] + a['w'] + 2 * HALO - 1e-6 and \
               a['y'] < b['y'] + b['h'] + 2 * HALO - 1e-6 and b['y'] < a['y'] + a['h'] + 2 * HALO - 1e-6:
                raise SystemExit(f'macro chong lan {m}: {a["inst"]} / {b["inst"]}')
assert all(not v for v in srams.values()), {k: len(v) for k, v in srams.items()}

json.dump(dict(T=T, DIE=DIE, MASTERS=MASTERS, INSTS=INSTS, TOPLOGIC=TOPLOGIC, ports=ports, io_pins=io_pins,
               macro_place=macro_place, MT=MT, GRID=[GRID_X, GRID_Y]), open(OUT, 'w'))
for m in ports:
    c = collections.Counter((q['group'], q['side']) for q in ports[m])
    print(m, dict(c))
print('IO:', collections.Counter(r['side'] for r in io_pins))
print('macro:', {m: len(v) for m, v in macro_place.items()})
