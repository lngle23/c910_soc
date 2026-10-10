#!/usr/bin/env python3
"""emit_top.py -- file cho nguoi lam TOP: floorplan die, dat block, IO pin, PG toan chip, SDC top, stub blackbox."""
import json, os, re, shutil, collections, csv, sys
sys.path.insert(0, '/tmp/claude-0/soc')
J = json.load(open('/tmp/claude-0/soc/plan.json'))
OUT = sys.argv[1]
T = J['T']; M = J['MASTERS']; I = J['INSTS']; DIE = J['DIE']; TL = J['TOPLOGIC']; IOP = J['io_pins']
SOC = '/tmp/claude-0/soc'
HDR = ('# AUTO-GENERATED boi top (emit_top.py) -- spec v1.0. Doi gi thi sinh lai, khong sua tay.\n')
TOPD = os.path.join(OUT, 'top')
os.makedirs(TOPD, exist_ok=True)
def fmt(v): return f'{v:.4f}'.rstrip('0').rstrip('.')
def w(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(s)

# ------------------------------------------------------------------ bang dat block
with open(os.path.join(TOPD, 'block_placement.csv'), 'w', newline='') as fh:
    cw = csv.writer(fh)
    cw.writerow(['instance_top', 'module', 'block', 'x_um', 'y_um', 'orient', 'w_um', 'h_um', 'x2_um', 'y2_um'])
    for k, d in I.items():
        m = M[d['master']]
        cw.writerow([d['hier'], m['module'], d['master'], d['x'], d['y'], d['orient'], m['w'], m['h'],
                     round(d['x'] + m['w'], 3), round(d['y'] + m['h'], 3)])
# ------------------------------------------------------------------ prelim LEF cua block (ban copy)
for mname, m in M.items():
    src = os.path.join(OUT, 'blocks', mname.lower(), f"{m['module']}_prelim.lef")
    os.makedirs(os.path.join(TOPD, 'lef'), exist_ok=True)
    shutil.copy(src, os.path.join(TOPD, 'lef', f"{m['module']}_prelim.lef"))

# ------------------------------------------------------------------ floorplan top
W, H = DIE['w'], DIE['h']
L = [HDR, '# Floorplan TOP c910_soc (top module = openC910). Legacy UI, Innovus 19.1.',
     '# Netlist top: openC910 synthesize bang common/scripts/syn_genus.tcl voi BLOCK=openC910 (4 block = cell trong top/lib/*_prelim.lib).',
     '# Block duoc doc nhu macro tu LEF (ban prelim trong top/lef/, sau thay bang LEF that block giao).',
     'set _TOP_DIR [file dirname [info script]]',
     f'# Die {fmt(W)} x {fmt(H)} um. Core = toan die tru le 19.95/19.6 (cho ring PG)',
     f'floorPlan -site FreePDK45_38x28_10R_NP_162NW_34O -b {{0 0 {fmt(W)} {fmt(H)}  0 0 {fmt(W)} {fmt(H)}  19.95 19.6 {fmt(W - 19.95)} {fmt(H - 19.6)}}}',
     '# --- dat 6 instance block (toa do = goc duoi-trai cua hop SAU khi lat). Luoi dat: x boi so 5.32, y boi so 11.2']
for k, d in I.items():
    L.append(f"placeInstance {d['hier']} {fmt(d['x'])} {fmt(d['y'])} {d['orient']} -fixed   ;# {k} ({M[d['master']]['module']})")
L += ['# --- halo quanh block: khong dat cell top sat bien block', 'addHaloToBlock 5 5 5 5 -allBlock', 'cutRow',
      '# --- logic rieng cua top dat trong vung giua phia tren (giua core0_fe va core1_fe)']
for mod in ('x_plic_top', 'x_ct_clint_top', 'x_ct_sysio_top', 'x_ct_had_common_top', 'x_ct_mp_clk_top', 'x_ct_mp_rst_top', 'x_rmu_top'):
    L.append(f"createGuide {mod} {fmt(TL['x'])} {fmt(TL['y'])} {fmt(TL['x'] + TL['w'])} {fmt(TL['y'] + TL['h'])}")
L += ['# --- hanh lang day giua 2 block (top/wire_corridors.csv): KHONG dat cell, KHONG strap PG cua top (chi de route thang)',
      'source [file join $_TOP_DIR c910_soc_corridors.tcl]',
      '# --- IO pin cua chip', 'source [file join $_TOP_DIR c910_soc_io_pins.tcl]',
      '# --- top route metal2..metal10; tren block chi con metal8..metal10 (LEF block chan metal1..metal7)',
      'setNanoRouteMode -routeTopRoutingLayer 10 -routeBottomRoutingLayer 2',
      'puts "FP-TOP: xong"']
w(os.path.join(TOPD, 'c910_soc_fp.tcl'), '\n'.join(L) + '\n')

# ------------------------------------------------------------------ IO pin
L = [HDR, f'# {len(IOP)} pin IO cua chip. Pin core0 o canh trai, core1 canh phai (cung y voi pin BE), con lai canh tren.',
     'setPinAssignMode -pinEditInBatch true']
for r in sorted(IOP, key=lambda r: (r['side'], r['x'] if r['side'] == 'top' else r['y'])):
    side = {'left': 'Left', 'right': 'Right', 'top': 'Top', 'bottom': 'Bottom'}[r['side']]
    wd = 0.07 if r['layer'] == 'metal3' else 0.14
    L.append(f"editPin -pin {{{r['pin']}}} -layer {r['layer']} -side {side} -assign {{{fmt(r['x'])} {fmt(r['y'])}}} "
             f"-pinWidth {wd} -pinDepth 0.56 -fixedPin 1 -fixOverlap 0")
L += ['setPinAssignMode -pinEditInBatch false', f'puts "PIN-TOP: {len(IOP)} IO"']
w(os.path.join(TOPD, 'c910_soc_io_pins.tcl'), '\n'.join(L) + '\n')
with open(os.path.join(TOPD, 'c910_soc_io_pins.csv'), 'w', newline='') as fh:
    cw = csv.writer(fh); cw.writerow(['pin', 'dir', 'side', 'layer', 'x_um', 'y_um', 'noi_toi_block', 'pin_block'])
    for r in sorted(IOP, key=lambda r: r['pin']):
        cw.writerow([r['pin'], r['dir'], r['side'], r['layer'], fmt(r['x']), fmt(r['y']), r.get('blk', 'top_logic'), r.get('blk_pin', '')])

# ------------------------------------------------------------------ hanh lang day (pin 2 block thang hang qua kenh)
P = J['ports']
def pabs(inst, q):
    d = I[inst]; m = M[d['master']]
    x = q['x'] if d['orient'] == 'R0' else m['w'] - q['x']
    return d['x'] + x, d['y'] + q['y']
def span(inst, master, group):
    return [pabs(inst, q) for q in P[master] if q['group'] == group]
CORR = []
for core, fe, be in (('core0', 'core0_fe', 'core0_be'), ('core1', 'core1_fe', 'core1_be')):
    xs = [x for x, y in span(fe, 'FE', 'FE_BE')]
    CORR.append((f'FE_BE_{core}', min(xs) - 1.0, I[be]['y'] + M['BE']['h'], max(xs) + 1.0, I[fe]['y']))
    ys = [y for x, y in span(be, 'BE', 'BE_CIU')]
    if I[be]['orient'] == 'R0':
        CORR.append((f'BE_CIU_{core}', I[be]['x'] + M['BE']['w'], min(ys) - 1.0, I['ciu']['x'], max(ys) + 1.0))
    else:
        CORR.append((f'BE_CIU_{core}', I['ciu']['x'] + M['CIU']['w'], min(ys) - 1.0, I[be]['x'], max(ys) + 1.0))
xs = [x for x, y in span('ciu', 'CIU', 'CIU_L2C')]
CORR.append(('CIU_L2C', min(xs) - 1.0, I['l2c']['y'] + M['L2C']['h'], max(xs) + 1.0, I['ciu']['y']))
CORR = [(c[0],) + tuple(round(v, 3) for v in c[1:]) for c in CORR]
with open(os.path.join(TOPD, 'wire_corridors.csv'), 'w') as fh:
    fh.write('name,x1,y1,x2,y2\n')
    for c in CORR: fh.write(','.join(str(v) for v in c) + '\n')
def subtract(rects, holes):
    out = list(rects)
    for hx0, hy0, hx1, hy1 in holes:
        nxt = []
        for x0, y0, x1, y1 in out:
            if hx1 <= x0 or hx0 >= x1 or hy1 <= y0 or hy0 >= y1: nxt.append((x0, y0, x1, y1)); continue
            if hx0 > x0: nxt.append((x0, y0, hx0, y1))
            if hx1 < x1: nxt.append((hx1, y0, x1, y1))
            cx0, cx1 = max(x0, hx0), min(x1, hx1)
            if hy0 > y0: nxt.append((cx0, y0, cx1, hy0))
            if hy1 < y1: nxt.append((cx0, hy1, cx1, y1))
        out = nxt
    return out

# ------------------------------------------------------------------ vung std cell cua top
CORE = (19.95, 19.6, DIE['w'] - 19.95, DIE['h'] - 19.6)
HALO_T = 5.0
blks = []
for k, d in I.items():
    m = M[d['master']]; blks.append((d['x'] - HALO_T, d['y'] - HALO_T, d['x'] + m['w'] + HALO_T, d['y'] + m['h'] + HALO_T))
xs = sorted(set([CORE[0], CORE[2]] + [b[0] for b in blks] + [b[2] for b in blks]))
xs = [x for x in xs if CORE[0] <= x <= CORE[2]]
free = []
for x0, x1 in zip(xs, xs[1:]):
    cov = sorted((b[1], b[3]) for b in blks if b[0] < x1 - 1e-6 and b[2] > x0 + 1e-6)
    y = CORE[1]
    for a, b in cov:
        if a > y + 1e-6: free.append((x0, y, x1, a))
        y = max(y, b)
    if y < CORE[3] - 1e-6: free.append((x0, y, x1, CORE[3]))
# gop cac o lien ke cung khoang y
merged = []
for r in sorted(free, key=lambda r: (r[1], r[3], r[0])):
    if merged and abs(merged[-1][1] - r[1]) < 1e-6 and abs(merged[-1][3] - r[3]) < 1e-6 and abs(merged[-1][2] - r[0]) < 1e-6:
        merged[-1] = (merged[-1][0], r[1], r[2], r[3])
    else: merged.append(r)
merged = subtract(merged, [c[1:] for c in CORR])
TOP_AREAS = [tuple(round(v, 3) for v in r) for r in merged if r[2] - r[0] >= 10 and r[3] - r[1] >= 10]
with open(os.path.join(TOPD, 'top_stdcell_areas.csv'), 'w') as fh:
    fh.write('x1,y1,x2,y2,area_um2\n')
    for r in TOP_AREAS: fh.write('%s,%s,%s,%s,%.0f\n' % (*r, (r[2] - r[0]) * (r[3] - r[1])))

# ------------------------------------------------------------------ PG top
g8, g9 = dict(width=2.0, pitch=40.0, off=100.0), dict(width=2.0, pitch=80.0, off=140.0)
L = [HDR, '# Luoi nguon TOP. Phan lop:',
     '#   block : metal1 rail, metal4 doc (56), metal7 ngang (40, tam VDD y=9.67+40k / VSS 29.67+40k tuong doi goc block)',
     '#   top   : ring metal9/metal10 quanh core; metal8 doc pitch 40 phu CA DIE (de len block, via xuong metal7 cua block);',
     '#           metal9 ngang pitch 80; vung std cell cua top (kenh + vung logic top) dung lai luat cua block.',
     'set NETS {VDD VSS}',
     'globalNetConnect VDD -type pgpin -pin VDD -all -override',
     'globalNetConnect VSS -type pgpin -pin VSS -all -override',
     'globalNetConnect VDD -type tiehi -all -override',
     'globalNetConnect VSS -type tielo -all -override',
     '# 1) ring quanh core (nam trong le 19.95/19.6 giua die va core)',
     'addRing -nets $NETS -type core_rings -follow core -layer {top metal9 bottom metal9 left metal10 right metal10} \\',
     '  -width {top 5 bottom 5 left 5 right 5} -spacing {top 2 bottom 2 left 2 right 2} -offset {top 2 bottom 2 left 2 right 2}',
     '# 2) rail metal1 cho std cell cua top (chi co row o kenh va vung logic top, da cutRow duoi block)',
     'sroute -connect {corePin} -nets $NETS -corePinTarget {firstAfterRowEnd} -allowJogging 0 -allowLayerChange 1 -layerChangeRange {metal1 metal10}',
     '# 3) metal4 + metal7 cho vung std cell top (addStripe tu bo qua vung bi macro/block chan)',
     'setAddStripeMode -stacked_via_bottom_layer metal1 -stacked_via_top_layer metal10',
     '# chi trong vung std cell cua top (top/top_stdcell_areas.csv) -- KHONG chay metal4/metal7 cua top len block']
for r in TOP_AREAS:
    a = f'{{{r[0]} {r[1]} {r[2]} {r[3]}}}'
    if r[2] - r[0] >= 30:
        L.append(f'addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {a}')
    else:
        L.append(f'addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing {round((r[2]-r[0])/2-0.48-1,2)} -set_to_set_distance 56 -start_from left -start_offset 1 -area {a}')
    if r[3] - r[1] >= 30:
        L.append(f'addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {a}')
    else:
        L.append(f'addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing {round((r[3]-r[1])/2-1.4-1,2)} -set_to_set_distance 40 -start_from bottom -start_offset 1 -area {a}')
L += [
     '# 4) metal8 doc phu ca die, metal9 ngang -- via chi xuong toi metal7 (khong cam via xuyen qua kenh/hanh lang)',
     'setAddStripeMode -stacked_via_bottom_layer metal7 -stacked_via_top_layer metal10',
     f"addStripe -nets $NETS -layer metal8 -direction vertical -width {g8['width']} -spacing {g8['pitch'] / 2 - g8['width']} "
     f"-set_to_set_distance {g8['pitch']} -start_from left -start_offset {g8['off']}",
     f"addStripe -nets $NETS -layer metal9 -direction horizontal -width {g9['width']} -spacing {g9['pitch'] / 2 - g9['width']} "
     f"-set_to_set_distance {g9['pitch']} -start_from bottom -start_offset {g9['off']}",
     '# 5) via metal7 (PG pin cua block) <-> metal8 cua top tai moi giao diem',
     'editPowerVia -add_vias 1 -bottom_layer metal7 -top_layer metal8 -nets $NETS',
     'verifyConnectivity -type special -nets $NETS -noAntenna -report top_pg_connectivity.rpt',
     'puts "PG-TOP: xong"']
w(os.path.join(TOPD, 'c910_soc_pg.tcl'), '\n'.join(L) + '\n')

# ------------------------------------------------------------------ SDC top (tu SDC openC910 da dung o synthesis)
src = open('/tmp/claude-0/bt/runs/m_openC910/gen/openC910.sdc').read()
src = re.sub(r'^set_units.*$', 'set_units -time 1ns -capacitance 1fF   ;# (spec) gia tri trong file nay la ns / fF', src, flags=re.M)
src = re.sub(r'^(#.*)\bpF\b(.*)$', r'\1fF\2', src, flags=re.M)
src = src.replace('set PARAM(output_load)           {0.0046}', 'set PARAM(output_load)           {4.6}  ;# fF')
assert '{4.6}' in src
w(os.path.join(TOPD, 'c910_soc.sdc'), HDR + '# SDC CHIP (top = openC910). Giong SDC da dung o synthesis openC910 (2.5ns, AXI = CPU/2, L2C MCP 2).\n' + src)

# ------------------------------------------------------------------ filelist cho synthesis top
# Top KHONG doc RTL cua 4 block: cac instance do duoc resolve bang top/lib/<module>_prelim.lib (va sau la ETM that).
fl = open(os.path.join(OUT, 'common', 'rtl', 'c910_soc_rtl.f')).read().splitlines()
drop = ('/ifu/rtl/ct_ifu_top.v', '/c910_be.v', '/ciu/rtl/ct_ciu_top.v', '/l2c/rtl/ct_l2c_top.v')
top_fl = [l for l in fl if not l.endswith(drop)]
assert len(fl) - len(top_fl) == 4, len(fl) - len(top_fl)
w(os.path.join(OUT, 'common', 'rtl', 'c910_top_only_rtl.f'), '\n'.join(top_fl) + '\n')
print('top: xong', len(IOP), 'IO')
L = [HDR, '# Hanh lang day: pin 2 block nam thang hang qua kenh -> giu trong cho route thang. Khong dat cell, khong strap PG top.']
for n, x0, y0, x1, y1 in CORR:
    L.append(f'createPlaceBlockage -box {{{x0} {y0} {x1} {y1}}} -type hard -name CORR_{n}')
w(os.path.join(TOPD, 'c910_soc_corridors.tcl'), '\n'.join(L) + '\n')
print('corridors:', [(c[0], round(c[3]-c[1],1), round(c[4]-c[2],1)) for c in CORR])
