#!/usr/bin/env python3
"""emit_spec.py -- tu plan.json sinh thu muc spec cho 5 nguoi (top + 4 block)."""
import json, os, shutil, collections, re, math, sys, csv

J = json.load(open('/tmp/claude-0/soc/plan.json'))
OUT = sys.argv[1]
T = J['T']; M = J['MASTERS']; I = J['INSTS']; P = J['ports']; DIE = J['DIE']; TL = J['TOPLOGIC']
SOC = '/tmp/claude-0/soc'
HDR = ('# AUTO-GENERATED boi top (emit_spec.py) tu ket noi RTL da elaborate -- KHONG sua tay.\n'
       '# Muon doi: bao nguoi lam top, top sinh lai va phat hanh version moi.\n')
VERSION = 'v1.0'
os.makedirs(OUT, exist_ok=True)

# =============================================================================== hang so dung chung
PG = dict(
    rail_layer='metal1',
    m4=dict(layer='metal4', width=0.48, spacing=27.52, pitch=56.0, offset=2.0),
    m7=dict(layer='metal7', width=1.40, pitch=40.0, vdd0=9.67, vss0=29.67),
    macro=dict(width=0.93, spacing=4.07, pitch=10.0, offset=2.0),
    top_m8=dict(layer='metal8', width=2.0, pitch=40.0, vdd0=100.0, vss0=120.0),
    top_m9=dict(layer='metal9', width=2.0, pitch=80.0, vdd0=140.0, vss0=180.0),
    ring=dict(width=10.0, spacing=2.0, offset=20.0),
)
CORE_INSET = dict(x=2.09, y=2.8)       # core box trong block: cach bien 11 site / 2 row
PIN = {'metal3': (0.07, 0.56), 'metal5': (0.14, 0.56), 'metal4': (0.14, 0.56), 'metal6': (0.14, 0.56)}  # (rong, sau)
CLK_LAT = {'FE': 0.35, 'BE': 0.55, 'CIU': 0.45, 'L2C': 0.40}   # ns, muc tieu insertion delay trong block
UTIL = {'FE': 0.55, 'BE': 0.60, 'CIU': 0.60, 'L2C': 0.50}
STD_EST = {'FE': 152130, 'BE': 1462057, 'CIU': 670514, 'L2C': 36188}   # um2 uoc tinh (Yosys generic, hieu chinh theo Genus LSU)
CELLS_EST = {'FE': 71000, 'BE': 680000, 'CIU': 312000, 'L2C': 17000}

def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(text)

# =============================================================================== common: macro, RTL
C = os.path.join(OUT, 'common')
for d in ('lef', 'lib', 'wrap'):
    shutil.copytree(os.path.join(SOC, 'mem', d), os.path.join(C, 'mem', d), dirs_exist_ok=True)
shutil.copy(os.path.join(SOC, 'mem', 'macro_table.csv'), os.path.join(C, 'mem', 'macro_table.csv'))
shutil.copy(os.path.join(SOC, 'gen_fakeram.py'), os.path.join(C, 'mem', 'gen_fakeram.py'))
os.makedirs(os.path.join(C, 'rtl'), exist_ok=True)
for f in ('ct_top.v', 'c910_be.v'):
    shutil.copy(os.path.join(SOC, 'rtl_gen', f), os.path.join(C, 'rtl', f))
for f in ('gated_clk_cell.v', 'BUFGCE.v'):
    shutil.copy('/tmp/claude-0/bt/runs/m_openC910/gen/rtl_override/' + f, os.path.join(C, 'rtl', f))
# filelist: lay tu flow Genus da chay duoc, thay ct_top.v, SRAM wrapper -> 1:1
fl = []
for l in open('/tmp/claude-0/bt/runs/m_openC910/gen/rtl_files.f'):
    l = l.strip()
    if not l: continue
    if l.endswith('/cpu/rtl/ct_top.v'):
        fl += ['${SPEC}/common/rtl/ct_top.v', '${SPEC}/common/rtl/c910_be.v']; continue
    if '/rtl_override/' in l: fl.append('${SPEC}/common/rtl/' + os.path.basename(l)); continue
    if '/mem/nangate45/' in l: fl.append('${SPEC}/common/mem/wrap/' + os.path.basename(l)); continue
    fl.append(l.replace('/tmp/claude-0/bt/rtl/C910_RTL_FACTORY', '${C910_RTL}'))
w(os.path.join(C, 'rtl', 'c910_soc_rtl.f'),
  '// Filelist chung cho MOI nguoi (Genus doc het, elaborate dung module cua minh).\n'
  '// ${C910_RTL}: thu muc C910_RTL_FACTORY trong openc910 goc;  ${SPEC}: thu muc spec nay.\n'
  '// Thu tu quan trong: cpu_cfig.h phai doc dau tien (cac `define dung cho file sau).\n' + '\n'.join(fl) + '\n')

# =============================================================================== helpers
def pins_of(m): return P[m]
def side_of_pin_abs(q): return q['side']
def fmt(v): return f'{v:.4f}'.rstrip('0').rstrip('.')

def pin_rect(q, W, H):
    wd, dp = PIN[q['layer']]
    x, y, s = q['x'], q['y'], q['side']
    if s == 'left': return (0.0, y - wd / 2, dp, y + wd / 2)
    if s == 'right': return (W - dp, y - wd / 2, W, y + wd / 2)
    if s == 'bottom': return (x - wd / 2, 0.0, x + wd / 2, dp)
    return (x - wd / 2, H - dp, x + wd / 2, H)

def m7_straps(W, H):
    s = []
    c = PG['m7']; y = c['vdd0']
    while y + c['width'] / 2 < H - 1.0:
        s.append(('VDD', y)); y += c['pitch']
    y = c['vss0']
    while y + c['width'] / 2 < H - 1.0:
        s.append(('VSS', y)); y += c['pitch']
    return sorted(s, key=lambda t: t[1])

def budget(m, q):
    """(kieu, gia tri ns, clock) cho 1 port. kieu: clk | bb | top | sys | async | dbg."""
    if q['clock']: return ('clk', None, None)
    pt = set(q['partners'])
    io = [x[3:] for x in q['drv'] + q['loads'] if x.startswith('IO:')]
    names = set(io)
    if q['port'] in ('pad_yy_icg_scan_en', 'pad_yy_scan_mode', 'pad_yy_scan_enable'): return ('case0', None, None)
    if q['port'] in ('pad_yy_mbist_mode',): return ('false', None, None)
    async_ports = {'pad_core_hartid', 'pad_xx_apb_base', 'pad_core_rvba', 'pad_core_rst_b', 'pad_cpu_rst_b',
                   'pad_yy_scan_rst_b', 'cpurst_b', 'ir_corex_wdata', 'sm_update_dr', 'sm_update_ir', 'x_regs_serial_data',
                   'pad_l2c_data_mbist_clk_ratio', 'pad_l2c_tag_mbist_clk_ratio', 'pad_cpu_l2cache_flush_req'}
    if q['port'] in async_ports or any(n.endswith('_rst_b') for n in names): return ('async', 10.0, None)
    if m == 'BE' and q['port'] in ('pad_biu_me_int', 'pad_biu_ms_int', 'pad_biu_mt_int', 'pad_biu_se_int', 'pad_biu_ss_int', 'pad_biu_st_int'):
        return ('mcp3', 3 * T, None)
    if names and all(n.startswith(('pad_biu_', 'biu_pad_')) or n in ('axim_clk_en',) for n in names):
        if q['dir'] == 'in': return ('sys', round(0.4 * 2 * T + 0.1 * T, 3), 'V_SYS_CLK')
        return ('sys', round(0.6 * 2 * T + 0.1 * T, 3), 'V_SYS_CLK')
    if names and all(re.match(r'core\d_pad_(retire|mstatus)', n) for n in names): return ('dbg', round(0.5 * T, 3), 'V_CPU_CLK')
    if names: return ('top', round(0.6 * T, 3), 'V_CPU_CLK')
    if pt - {'core0_fe', 'core0_be', 'core1_fe', 'core1_be', 'ciu', 'l2c'} or len(pt) > 1: return ('top', round(0.6 * T, 3), 'V_CPU_CLK')
    return ('bb', round(0.5 * T, 3), 'V_CPU_CLK')

def busify(names):
    """gom ten pin bit thanh pattern ten[*] cho SDC gon."""
    d = collections.OrderedDict()
    for n in names:
        m = re.match(r'(\w+)\[(\d+)\]$', n)
        b = m.group(1) if m else n
        d.setdefault(b, []).append(n)
    out = []
    for b, L in d.items():
        out.append(f'{b}[*]' if '[' in L[0] else b)
    return out

def port_full_set(m):
    """port -> list cac bit (de biet bus co bi chia o nhieu loai budget khong)."""
    d = collections.defaultdict(list)
    for q in P[m]: d[q['port']].append(q)
    return d

# =============================================================================== moi block
SUMMARY = {}
for m, info in M.items():
    mod = info['module']; W, H = info['w'], info['h']
    B = os.path.join(OUT, 'blocks', m.lower())
    qs = sorted(P[m], key=lambda q: (q['side'], q['x'] if q['side'] in ('top', 'bottom') else q['y'], q['layer']))
    # ---------------- ports csv
    os.makedirs(B, exist_ok=True)
    with open(os.path.join(B, f'{mod}_ports.csv'), 'w', newline='') as fh:
        cw = csv.writer(fh)
        cw.writerow(['pin', 'dir', 'side', 'layer', 'x_um', 'y_um', 'group', 'partners', 'budget_type', 'ext_delay_ns', 'ref_clock', 'ref_period_ns'])
        for q in sorted(P[m], key=lambda q: q['pin']):
            bt, v, ck = budget(m, q)
            cw.writerow([q['pin'], q['dir'], q['side'], q['layer'], fmt(q['x']), fmt(q['y']), q['group'],
                         '+'.join(q['partners']), bt, '' if v is None else v, ck or '', 2 * T if ck == 'V_SYS_CLK' else (T if ck else '')])
    # ---------------- editPin
    L = [HDR, f'# {mod}: dat {len(qs)} pin dung toa do spec {VERSION}. Chay SAU floorPlan.',
         '# Moi pin da nam tren track (ngang: y=0.07+0.28k ; doc: x=0.095+0.28k). KHONG dung -snap.',
         'setPinAssignMode -pinEditInBatch true']
    for q in qs:
        wd, dp = PIN[q['layer']]
        side = {'left': 'Left', 'right': 'Right', 'top': 'Top', 'bottom': 'Bottom'}[q['side']]
        L.append(f'editPin -pin {{{q["pin"]}}} -layer {q["layer"]} -side {side} -assign {{{fmt(q["x"])} {fmt(q["y"])}}} '
                 f'-pinWidth {wd} -pinDepth {dp} -fixedPin 1 -fixOverlap 0')
    L.append('setPinAssignMode -pinEditInBatch false')
    L.append(f'puts "PIN-SPEC: da dat {len(qs)} pin cho {mod} ({VERSION})"')
    w(os.path.join(B, f'{mod}_pins.tcl'), '\n'.join(L) + '\n')
    # ---------------- DEF (DIEAREA + PINS)
    dbu = 2000
    D = [f'VERSION 5.8 ;', 'DIVIDERCHAR "/" ;', 'BUSBITCHARS "[]" ;', f'DESIGN {mod} ;', f'UNITS DISTANCE MICRONS {dbu} ;',
         f'DIEAREA ( 0 0 ) ( {round(W * dbu)} {round(H * dbu)} ) ;', f'PINS {len(qs) + 2} ;']
    for q in qs:
        x0, y0, x1, y1 = pin_rect(q, W, H)
        cx, cy = q['x'], q['y']
        D.append(f'  - {q["pin"]} + NET {q["pin"]} + DIRECTION {"INPUT" if q["dir"] == "in" else "OUTPUT"} + USE '
                 f'{"CLOCK" if q["clock"] else "SIGNAL"}\n    + LAYER {q["layer"]} ( {round((x0 - cx) * dbu)} {round((y0 - cy) * dbu)} ) '
                 f'( {round((x1 - cx) * dbu)} {round((y1 - cy) * dbu)} ) + FIXED ( {round(cx * dbu)} {round(cy * dbu)} ) N ;')
    for net in ('VDD', 'VSS'):
        D.append(f'  - {net} + NET {net} + SPECIAL + DIRECTION INOUT + USE {"POWER" if net == "VDD" else "GROUND"} ;')
    D += ['END PINS', 'END DESIGN']
    w(os.path.join(B, f'{mod}_pins.def'), '\n'.join(D) + '\n')
    # ---------------- abstract LEF so bo (cho top dung truoc khi block giao LEF that)
    st = m7_straps(W, H)
    L = ['VERSION 5.7 ;', 'BUSBITCHARS "[]" ;', 'DIVIDERCHAR "/" ;', f'MACRO {mod}', '  CLASS BLOCK ;', f'  FOREIGN {mod} 0 0 ;',
         '  ORIGIN 0 0 ;', f'  SIZE {fmt(W)} BY {fmt(H)} ;', '  SYMMETRY X Y ;']
    for q in sorted(P[m], key=lambda q: q['pin']):
        x0, y0, x1, y1 = pin_rect(q, W, H)
        L += [f'  PIN {q["pin"]}', f'    DIRECTION {"INPUT" if q["dir"] == "in" else "OUTPUT"} ;',
              f'    USE {"CLOCK" if q["clock"] else "SIGNAL"} ;', '    PORT', f'      LAYER {q["layer"]} ;',
              f'        RECT {x0:.3f} {y0:.3f} {x1:.3f} {y1:.3f} ;', '    END', f'  END {q["pin"]}']
    for net, use in (('VDD', 'POWER'), ('VSS', 'GROUND')):
        L += [f'  PIN {net}', '    DIRECTION INOUT ;', f'    USE {use} ;', '    PORT', '      LAYER metal7 ;']
        L += [f'        RECT 0.000 {y - 0.7:.3f} {W:.3f} {y + 0.7:.3f} ;' for n, y in st if n == net]
        L += ['    END', f'  END {net}']
    ring = 0.7
    L += ['  OBS', '    LAYER metal1 ;', f'      RECT 0 0 {W:.3f} {H:.3f} ;', '    LAYER metal2 ;', f'      RECT 0 0 {W:.3f} {H:.3f} ;']
    for lay in ('metal3', 'metal4', 'metal5', 'metal6'):
        L += [f'    LAYER {lay} ;', f'      RECT {ring} {ring} {W - ring:.3f} {H - ring:.3f} ;']
    L += ['    LAYER metal7 ;']
    prev = 0.0
    for n, y in st:
        L.append(f'      RECT 0 {prev:.3f} {W:.3f} {y - 0.7 - 0.4:.3f} ;'); prev = y + 0.7 + 0.4
    L.append(f'      RECT 0 {prev:.3f} {W:.3f} {H:.3f} ;')
    L += ['  END', f'END {mod}', '', 'END LIBRARY']
    w(os.path.join(B, f'{mod}_prelim.lef'), '\n'.join(L) + '\n')
    # ---------------- macro
    mp = J['macro_place'][m]
    with open(os.path.join(B, f'{mod}_macros.csv'), 'w', newline='') as fh:
        cw = csv.writer(fh); cw.writerow(['instance', 'cell', 'w_um', 'h_um', 'goi_y_x', 'goi_y_y', 'goi_y_orient'])
        for a in mp: cw.writerow([a['inst'], a['cell'], a['w'], a['h'], a['x'], a['y'], a['orient']])
    L = [HDR, f'# {mod}: vi tri macro GOI Y (top da kiem: khong chong lan, du cho logic, halo 10um).',
         '# Block owner DUOC doi, mien la: <= 20 macro, nam trong block, khong che pin, giu halo.']
    for a in mp:
        L.append(f'placeInstance {a["inst"]} {a["x"]} {a["y"]} {a["orient"]} -fixed')
    w(os.path.join(B, f'{mod}_macro_suggest.tcl'), '\n'.join(L) + '\n')
    # ---------------- floorplan
    cx, cy = CORE_INSET['x'], CORE_INSET['y']
    L = [HDR, f'# {mod} floorplan theo spec {VERSION}. Dung SAU init_design (legacy UI, Innovus 19.1).',
         'set _SPEC_DIR [file dirname [info script]]',
         f'# Kich thuoc block = kich thuoc top cap (khong duoc doi): {fmt(W)} x {fmt(H)} um',
         f'floorPlan -site FreePDK45_38x28_10R_NP_162NW_34O -b {{0 0 {fmt(W)} {fmt(H)}  0 0 {fmt(W)} {fmt(H)}  '
         f'{cx} {cy} {fmt(W - cx)} {fmt(H - cy)}}}',
         f'source [file join $_SPEC_DIR {mod}_pins.tcl]',
         '# metal8..metal10 thuoc ve top (PG + route tren block) -> cam trong block',
         f'createRouteBlk -box {{0 0 {fmt(W)} {fmt(H)}}} -layer {{metal8 metal9 metal10}} -name TOP_ONLY_LAYERS',
         'setNanoRouteMode -routeTopRoutingLayer 7 -routeBottomRoutingLayer 2',
         'setRouteMode -earlyGlobalMaxRouteLayer 7 -earlyGlobalMinRouteLayer 2',
         '# Giu 1 dai 1.4um sat bien khong dat std cell (cho pin + PG)',
         f'createPlaceBlockage -box {{0 0 {fmt(W)} {cy + 1.4}}} -type hard -name EDGE_B',
         f'createPlaceBlockage -box {{0 {fmt(H - cy - 1.4)} {fmt(W)} {fmt(H)}}} -type hard -name EDGE_T']
    if mp:
        L += ['# Macro: dung vi tri goi y (co the thay bang vi tri cua ban)',
              f'source [file join $_SPEC_DIR {mod}_macro_suggest.tcl]',
              'addHaloToBlock 10 10 10 10 -allBlock', 'cutRow']
    L.append(f'puts "FP-SPEC: {mod} {fmt(W)}x{fmt(H)} xong"')
    w(os.path.join(B, f'{mod}_fp.tcl'), '\n'.join(L) + '\n')
    # ---------------- PG
    c4, c7, cm = PG['m4'], PG['m7'], PG['macro']
    L = [HDR, f'# {mod}: luoi nguon theo spec {VERSION}. Top se dat metal8 doc qua block va noi xuong STRAP METAL7 cua block.',
         '# BAT BUOC giu: lop, be rong, pitch, offset metal7 (top dua vao do de dat via). Duoc them strap, khong duoc bot.',
         'set NETS {VDD VSS}',
         'globalNetConnect VDD -type pgpin -pin VDD -all -override',
         'globalNetConnect VSS -type pgpin -pin VSS -all -override',
         'globalNetConnect VDD -type tiehi -all -override',
         'globalNetConnect VSS -type tielo -all -override',
         '# 1) rail metal1 theo row (khong co ring trong block)',
         'sroute -connect {corePin} -nets $NETS -allowJogging 0 -allowLayerChange 0',
         '# 2) metal4 doc: VDD/VSS cach nhau nua pitch, khong cham canh tren/duoi (pin metal4 o do)',
         'setAddStripeMode -stacked_via_bottom_layer metal1 -stacked_via_top_layer metal7',
         f'addStripe -nets $NETS -layer metal4 -direction vertical -width {c4["width"]} -spacing {c4["spacing"]} '
         f'-set_to_set_distance {c4["pitch"]} -start_from left -start_offset {c4["offset"]} '
         f'-area {{0 1.4 {fmt(W)} {fmt(H - 1.4)}}}',
         '# 3) metal7 ngang, CO DINH: tam VDD y=' + f'{c7["vdd0"]}+{c7["pitch"]}k, tam VSS y={c7["vss0"]}+{c7["pitch"]}k, rong {c7["width"]}, keo het be rong block']
    for n, y in m7_straps(W, H):
        L.append(f'addStripe -nets {n} -layer metal7 -direction horizontal -width {c7["width"]} '
                 f'-area {{0 {y - 0.7:.3f} {fmt(W)} {y + 0.7:.3f}}} -set_to_set_distance {c7["pitch"]} -start_from bottom -start_offset 0')
    if mp:
        L += ['# 4) tren moi macro: metal5 ngang + metal6 doc pitch 10 (noi strap metal4 trong macro len metal7)',
              '# macro = instance co cell CLASS BLOCK (cach dem nay da chay dung tren Innovus 19.1 cua nhom: macros=11 o LSU)',
              'set _macros [dbGet -p2 top.insts.cell.subClass block]',
              'if {$_macros eq "0x0" || $_macros eq ""} { set _macros [dbGet -p2 top.insts.cell.baseClass block] }',
              'if {$_macros eq "0x0"} { set _macros {} }',
              'puts "PG-SPEC: [llength $_macros] macro"',
              'foreach inst $_macros {',
              '  set box [lindex [dbGet $inst.box] 0]',
              f'  addStripe -nets $NETS -layer metal5 -direction horizontal -area $box -width {cm["width"]} -spacing {cm["spacing"]} -set_to_set_distance {cm["pitch"]} -start_from bottom -start_offset {cm["offset"]}',
              f'  addStripe -nets $NETS -layer metal6 -direction vertical   -area $box -width {cm["width"]} -spacing {cm["spacing"]} -set_to_set_distance {cm["pitch"]} -start_from left   -start_offset {cm["offset"]}',
              '}',
              'sroute -connect {blockPin} -nets $NETS -blockPinTarget {nearestTarget} -allowLayerChange 1 -layerChangeRange {metal4 metal7}']
    L += [f'verifyConnectivity -type special -nets $NETS -noAntenna -report {mod}_pg_connectivity.rpt',
          f'puts "PG-SPEC: {mod} xong"']
    w(os.path.join(B, f'{mod}_pg.tcl'), '\n'.join(L) + '\n')
    # ---------------- SDC
    groups = collections.defaultdict(list)
    for q in P[m]:
        bt, v, ck = budget(m, q)
        groups[(bt, v, ck, q['dir'])].append(q['pin'])
    allbits = collections.defaultdict(set)
    for q in P[m]: allbits[q['port']].add(q['pin'])
    def compact(pins):
        byp = collections.defaultdict(set)
        for pn in pins: byp[re.sub(r'\[\d+\]$', '', pn)].add(pn)
        out = []
        for port, s in sorted(byp.items()):
            if s == allbits[port] and len(s) > 1: out.append(f'{port}[*]')
            else: out += sorted(s)
        return out
    clocks = sorted(set(q['pin'] for q in P[m] if q['clock']))
    L = [HDR, f'# SDC block {mod} -- ngan sach timing tu top ({VERSION}). Don vi: ns, fF (= don vi lib Nangate45).',
         '# Khong co set_units: Genus va Innovus deu hieu theo don vi thu vien.',
         f'# Chu ky CPU_CLK = {T} ns. Ngan sach port giua 2 block: moi block {int(50)}% chu ky, day top nam trong phan 10% du cua ben nhan.',
         'set_units -time 1ns -capacitance 1fF   ;# gia tri ben duoi la ns / fF (Genus doc set_units; Innovus dung don vi lib = ns/fF, cung ket qua)',
         'set_max_fanout 32 [current_design]', 'set_max_transition 0.15 [current_design]']
    main_clk = {'FE': 'forever_cpuclk', 'BE': 'pll_core_clk', 'CIU': 'forever_cpuclk', 'L2C': 'forever_cpuclk'}[m]
    L += [f'create_clock -name CPU_CLK -period {T} [get_ports {main_clk}]',
          f'create_clock -name V_CPU_CLK -period {T}',
          f'set_input_transition 0.05 [get_ports {{{" ".join(c for c in clocks if any(q["pin"] == c and q["dir"] == "in" for q in P[m]))}}}]',
          f'# Clock ao (IO) va clock that (truoc CTS) cung co do tre = muc tieu insertion delay cua block ({CLK_LAT[m]} ns).',
          '# Sau CTS (set_propagated_clock / ccopt) do tre that thay cho gia tri ly tuong cua clock that; clock ao giu nguyen.',
          f'set_clock_latency {CLK_LAT[m]} [get_clocks V_CPU_CLK]',
          f'set_clock_latency {CLK_LAT[m]} [get_clocks CPU_CLK]']
    if m == 'CIU':
        L += [f'create_clock -name V_SYS_CLK -period {2 * T}', f'set_clock_latency {CLK_LAT[m]} [get_clocks V_SYS_CLK]',
              'set_multicycle_path -from [get_clocks CPU_CLK] -to [get_clocks V_SYS_CLK] -setup 2 -start',
              'set_multicycle_path -from [get_clocks CPU_CLK] -to [get_clocks V_SYS_CLK] -hold 1 -start',
              'set_multicycle_path -from [get_clocks V_SYS_CLK] -to [get_clocks CPU_CLK] -setup 2 -end',
              'set_multicycle_path -from [get_clocks V_SYS_CLK] -to [get_clocks CPU_CLK] -hold 1 -end']
    if m == 'L2C':
        for kind in ('DATA', 'TAG'):
            for i in (0, 1):
                L.append(f'create_clock -name L2C_{kind}_MEM_CLOCK_{i} -period {2 * T} -waveform {{0 {T / 2}}} '
                         f'[get_ports l2c_{kind.lower()}_clk_bank_{i}]')
            L += [f'set_multicycle_path -from [get_clocks {{L2C_{kind}_MEM_CLOCK_0 L2C_{kind}_MEM_CLOCK_1}}] -to [get_clocks CPU_CLK] -setup 2 -end',
                  f'set_multicycle_path -from [get_clocks {{L2C_{kind}_MEM_CLOCK_0 L2C_{kind}_MEM_CLOCK_1}}] -to [get_clocks CPU_CLK] -hold 1 -end']
        L.append('# Clock bo nho duoc gate o top (x_ct_mp_clk_top), cung pha voi CPU_CLK -> cung nhom dong bo')
        L.append(f'set_clock_latency {CLK_LAT[m]} [get_clocks {{L2C_DATA_MEM_CLOCK_0 L2C_DATA_MEM_CLOCK_1 L2C_TAG_MEM_CLOCK_0 L2C_TAG_MEM_CLOCK_1}}]')
    ins = [q['pin'] for q in P[m] if q['dir'] == 'in' and not q['clock']]
    L.append(f'set_driving_cell -lib_cell BUF_X2 -pin Z [get_ports {{{" ".join(busify(sorted(ins)))}}}]')
    outs_bb = [q['pin'] for q in P[m] if q['dir'] == 'out' and budget(m, q)[0] == 'bb']
    outs_other = [q['pin'] for q in P[m] if q['dir'] == 'out' and budget(m, q)[0] != 'bb']
    if outs_bb: L.append(f'set_load 5.0 [get_ports {{{" ".join(compact(outs_bb))}}}]   ;# fF, pin doi dien block ben canh')
    if outs_other: L.append(f'set_load 10.0 [get_ports {{{" ".join(compact(outs_other))}}}]  ;# fF, di xa hon trong top')
    for (bt, v, ck, d), pins in sorted(groups.items(), key=lambda t: (t[0][0], t[0][3])):
        plist = '{' + ' '.join(compact(pins)) + '}'
        if bt in ('bb', 'top', 'sys', 'dbg'):
            cmd = 'set_input_delay' if d == 'in' else 'set_output_delay'
            L.append(f'# {bt}: {len(pins)} bit {d}')
            L.append(f'{cmd} -max {v} -clock {ck} [get_ports {plist}]')
            L.append(f'{cmd} -min 0 -clock {ck} [get_ports {plist}]')
        elif bt == 'async':
            cmd = 'set_input_delay' if d == 'in' else 'set_output_delay'
            L.append(f'# async/tinh: {len(pins)} bit -- max_delay {v} ns nhu SDC goc, khong kiem hold')
            L.append(f'{cmd} 0 -clock V_CPU_CLK [get_ports {plist}]')
            if d == 'in':
                L.append(f'set_max_delay {v} -from [get_ports {plist}]'); L.append(f'set_false_path -hold -from [get_ports {plist}]')
            else:
                L.append(f'set_max_delay {v} -to [get_ports {plist}]'); L.append(f'set_false_path -hold -to [get_ports {plist}]')
        elif bt == 'mcp3':
            L.append(f'# ngat tu PLIC/CLINT: SDC goc cho {v} ns')
            L.append(f'set_input_delay 0 -clock V_CPU_CLK [get_ports {plist}]')
            L.append(f'set_max_delay {v} -from [get_ports {plist}]')
        elif bt == 'case0':
            L.append(f'set_case_analysis 0 [get_ports {plist}]')
        elif bt == 'false':
            L.append(f'set_false_path -from [get_ports {plist}]')
    L += ['set_clock_uncertainty -setup 0.10 [all_clocks]', 'set_clock_uncertainty -hold 0.05 [all_clocks]']
    w(os.path.join(B, f'{mod}.sdc'), '\n'.join(L) + '\n')
    # ---------------- so lieu tong hop
    cnt = collections.Counter(budget(m, q)[0] for q in P[m])
    macro_area = sum(a['w'] * a['h'] for a in mp)
    SUMMARY[m] = dict(module=mod, w=W, h=H, area=W * H, ports=len(P[m]),
                      pin_in=sum(1 for q in P[m] if q['dir'] == 'in'), pin_out=sum(1 for q in P[m] if q['dir'] == 'out'),
                      macros=len(mp), macro_area=macro_area, std_est=STD_EST[m], cells_est=CELLS_EST[m],
                      util_est=STD_EST[m] / (W * H - sum((a['w'] + 20) * (a['h'] + 20) for a in mp)),
                      budget=dict(cnt), sides=dict(collections.Counter(q['side'] for q in P[m])),
                      clocks=clocks, insts=info['insts'], clk_lat=CLK_LAT[m])

json.dump(SUMMARY, open(os.path.join(SOC, 'summary.json'), 'w'), indent=1)
for m, s in SUMMARY.items():
    print(f"{m:4s} {s['module']:12s} {s['w']:8.2f} x {s['h']:8.2f}  macro={s['macros']:2d}  pins={s['ports']}  util_est={s['util_est']:.2f}  {s['budget']}")
