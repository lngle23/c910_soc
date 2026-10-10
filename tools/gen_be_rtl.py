#!/usr/bin/env python3
"""gen_be_rtl.py -- tach ct_top thanh 2 partition: ct_ifu_top (FE) + c910_be (BE).
Doc conn.out (ket noi bit-level da elaborate bang slang), ghi:
  ct_top.v   : cung ten, cung port voi ct_top goc; chi con 2 instance (x_ct_ifu_top, x_c910_be)
  c910_be.v  : wrapper moi chua 13 unit con lai cua core (ct_core bi lam phang)
Chi dung cho core 0 (core 1 la cung module ct_top).
"""
import collections, re, sys, os
CONN, RTL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CORE = 'openC910/x_ct_top_0'
SC_TOP, SC_CORE = CORE, CORE + '/x_ct_core'
FE = 'x_ct_ifu_top'
BE_UNITS = ['x_ct_idu_top', 'x_ct_iu_top', 'x_ct_vfpu_top', 'x_ct_lsu_top', 'x_ct_rtu_top', 'x_ct_cp0_top',
            'x_ct_mmu_top', 'x_ct_pmp_top', 'x_ct_biu_top', 'x_ct_had_private_top', 'x_ct_hpcp_top',
            'x_ct_rst_top', 'x_ct_clk_top']

def decls(path):
    d, order = {}, []
    t = re.sub(r'//[^\n]*', '', open(path).read())
    for m in re.finditer(r'^\s*(input|output|inout|wire|reg)\s+(?:\[\s*(\d+)\s*:\s*(\d+)\s*\])?\s*(\w+)\s*;', t, re.M):
        k, a, b, n = m.groups()
        if n not in d:
            d[n] = (k, int(a) if a else 0, int(b) if b else 0)
            if k in ('input', 'output', 'inout'): order.append(n)
    return d, order
D_TOP, TOP_PORTS = decls(os.path.join(RTL, 'cpu/rtl/ct_top.v'))
D_CORE, _ = decls(os.path.join(RTL, 'cpu/rtl/ct_core.v'))
def idx(dec, name, i):
    _, a, b = dec[name]
    return b + i if a >= b else b - i

sets_ep = collections.defaultdict(list); sets_nm = collections.defaultdict(list); sets_cv = {}
for l in open(CONN):
    f = l.split()
    if f[0] == 'EP': sets_ep[int(f[1])].append((f[2], f[3], f[4], int(f[5]), f[6]))
    elif f[0] == 'NM': sets_nm[int(f[1])].append((f[2], f[3], int(f[4])))
    elif f[0] == 'CV': sets_cv[int(f[1])] = f[2]

def part(path):
    if not path.startswith(CORE + '/'): return None
    leaf = path.split('/')[-1]
    if leaf == FE: return 'FE'
    if leaf in BE_UNITS: return 'BE'
    raise SystemExit('unit la trong core: ' + path)

# Thong tin tung set lien quan toi core 0
info = {}
for s, eps in sets_ep.items():
    parts = set()
    for k, p, port, b, d in eps:
        if k == 'U' and part(p): parts.add(part(p))
    nms = sets_nm.get(s, [])
    topname = [(n, b) for sc, n, b in nms if sc == SC_TOP and n in TOP_PORTS]
    if not parts and not topname: continue
    info[s] = dict(parts=parts, eps=[e for e in eps if e[0] == 'U' and part(e[1])], topport=topname,
                   topnm=[(n, b) for sc, n, b in nms if sc == SC_TOP],
                   corenm=[(n, b) for sc, n, b in nms if sc == SC_CORE], cv=sets_cv.get(s))

# Ten chuan cho moi set (bit-level)
def canon(s):
    i = info[s]
    if i['topport']: n, b = sorted(i['topport'])[0]; return n, idx(D_TOP, n, b), 'top'
    if i['corenm']:
        n, b = sorted(i['corenm'])[0]
        return n, (idx(D_CORE, n, b) if n in D_CORE else b), 'core'
    if i['topnm']:
        n, b = sorted(i['topnm'])[0]
        return n, (idx(D_TOP, n, b) if n in D_TOP else b), 'top'
    return None
names = {s: canon(s) for s in info}
# kiem tra trung ten
seen = {}
for s, c in names.items():
    if c is None: continue
    key = (c[0], c[1])
    if key in seen and seen[key] != s: raise SystemExit(f'trung ten {key}')
    seen[key] = s

def is_drv(e): return e[4] == 'out'
# Port cua c910_be: set co BE va (FE hoac port ct_top)
be_ports = {}   # name -> {'bits': set(idx), 'dir': set()}
fe_be_wires = {}
for s, i in info.items():
    if 'BE' not in i['parts']: continue
    crosses = ('FE' in i['parts']) or bool(i['topport'])
    if not crosses: continue
    n, b, _ = names[s]
    be_drv = any(is_drv(e) and part(e[1]) == 'BE' for e in i['eps'])
    p = be_ports.setdefault(n, {'bits': set(), 'dir': set()})
    p['bits'].add(b); p['dir'].add('output' if be_drv else 'input')
bad = {n: p for n, p in be_ports.items() if len(p['dir']) > 1}
if bad: raise SystemExit(f'port 2 chieu: {list(bad)[:5]}')

def rng_of(n, bits):
    if n in D_TOP and D_TOP[n][0] in ('input', 'output', 'inout'): _, a, b = D_TOP[n]; return a, b
    if n in D_CORE: _, a, b = D_CORE[n]; return a, b
    return max(bits), min(bits)
def rstr(a, b): return '' if a == b == 0 else f'[{a}:{b}]'

def bitref(n, b, dec_rng):
    a, lo = dec_rng
    return n if a == lo == 0 else f'{n}[{b}]'

def conn_expr(bitlist):
    """bitlist: MSB..LSB list of (name, idx, isvec) or ('const', v) or None -> verilog concat, gom day lien tiep."""
    parts = []
    for it in bitlist:
        if parts and it and parts[-1][0] == 'run' and it[0] != 'const' and parts[-1][1] == it[0] and parts[-1][3] - 1 == it[1] and it[2]:
            parts[-1][3] = it[1]; continue
        if it is None: parts.append(['z']); continue
        if it[0] == 'const': parts.append(['c', it[1]]); continue
        n, b, isvec = it
        parts.append(['run', n, b, b] if isvec else ['sc', n])
    out = []
    for p in parts:
        if p[0] == 'z': out.append("1'bz")
        elif p[0] == 'c': out.append(f"1'b{p[1]}")
        elif p[0] == 'sc': out.append(p[1])
        else: out.append(f'{p[1]}[{p[2]}]' if p[2] == p[3] else f'{p[1]}[{p[2]}:{p[3]}]')
    return out[0] if len(out) == 1 else '{' + ', '.join(out) + '}'

# ---- c910_be: wire noi bo + instance cac unit
unit_ports = collections.defaultdict(lambda: collections.defaultdict(dict))  # unit -> port -> bit -> set
unit_pdir = collections.defaultdict(dict)
for s, i in info.items():
    for k, p, port, b, d in i['eps']:
        unit_ports[p.split('/')[-1]][port][b] = s
        unit_pdir[p.split('/')[-1]][port] = d

be_int = {}
for s, i in info.items():
    if i['parts'] == {'BE'} and not i['topport']:
        n, b, _ = names[s] if names[s] else (f'be_nc_{s}', 0, '')
        if names[s] is None: names[s] = (n, b, 'nc')
        be_int.setdefault(n, set()).add(b)
fe_wires = {}
for s, i in info.items():
    if 'FE' in i['parts'] and 'BE' in i['parts'] and not i['topport']:
        n, b, _ = names[s]; fe_wires.setdefault(n, set()).add(b)
fe_only = {}
for s, i in info.items():
    if i['parts'] == {'FE'} and not i['topport'] and names[s] is None:
        names[s] = (f'fe_nc_{s}', 0, 'nc')

def bit_item(s, scope_rng):
    n, b, _ = names[s]
    r = scope_rng(n)
    return (n, b, not (r[0] == r[1] == 0))

def emit_inst(lines, mod, inst, unit_leaf, scope_rng, port_order):
    lines.append(f'{mod} {inst} (')
    cs = []
    for port in port_order:
        bits = unit_ports[unit_leaf].get(port, {})
        if not bits: cs.append(f'  .{port:<40s} ()'); continue
        w = max(bits) + 1
        items = []
        for bi in range(w - 1, -1, -1):
            s = bits.get(bi)
            if s is None: items.append(None); continue
            i = info[s]
            if i['cv'] is not None and len(i['eps']) == 1 and not i['topport']: items.append(('const', i['cv'])); continue
            items.append(bit_item(s, scope_rng))
        cs.append(f'  .{port:<40s} ({conn_expr(items)})')
    lines.append(',\n'.join(cs)); lines.append(');')

UNIT_MOD = {'x_ct_idu_top': 'ct_idu_top', 'x_ct_iu_top': 'ct_iu_top', 'x_ct_vfpu_top': 'ct_vfpu_top', 'x_ct_lsu_top': 'ct_lsu_top',
            'x_ct_rtu_top': 'ct_rtu_top', 'x_ct_cp0_top': 'ct_cp0_top', 'x_ct_mmu_top': 'ct_mmu_top', 'x_ct_pmp_top': 'ct_pmp_top',
            'x_ct_biu_top': 'ct_biu_top', 'x_ct_had_private_top': 'ct_had_private_top', 'x_ct_hpcp_top': 'ct_hpcp_top',
            'x_ct_rst_top': 'ct_rst_top', 'x_ct_clk_top': 'ct_clk_top', 'x_ct_ifu_top': 'ct_ifu_top'}

def unit_port_order(leaf):
    # thu tu port theo khai bao module con
    mod = UNIT_MOD[leaf]
    for root, _, fs in os.walk(RTL):
        if mod + '.v' in fs:
            _, order = decls(os.path.join(root, mod + '.v')); return order
    raise SystemExit('khong thay ' + mod)

HDR = '// AUTO-GENERATED by gen_be_rtl.py tu RTL OpenC910 goc -- KHONG sua tay.\n'
# c910_be.v
be_rng = {}
for n, p in be_ports.items(): be_rng[n] = rng_of(n, p['bits'])
for n, bs in be_int.items(): be_rng[n] = rng_of(n, bs) if n in D_CORE or n in D_TOP else (max(bs), min(bs))
L = [HDR, '// c910_be = ct_top tru ct_ifu_top: idu iu vfpu lsu rtu cp0 (tu ct_core) + mmu pmp biu had_private hpcp rst clk (tu ct_top)',
     'module c910_be (']
pnames = sorted(be_ports)
L.append(',\n'.join('  ' + n for n in pnames)); L.append(');')
for n in pnames:
    a, b = be_rng[n]; L.append(f'{list(be_ports[n]["dir"])[0]:6s} {rstr(a, b):10s} {n};')
for n in sorted(be_int):
    if n in be_ports: raise SystemExit('ten wire trung port ' + n)
    a, b = be_rng[n]; L.append(f'wire   {rstr(a, b):10s} {n};')
for u in BE_UNITS:
    L.append('')
    emit_inst(L, UNIT_MOD[u], u, u, lambda n: be_rng[n], unit_port_order(u))
L.append('endmodule')
open(os.path.join(OUT, 'c910_be.v'), 'w').write('\n'.join(L) + '\n')

# ct_top.v moi
top_rng = {n: (D_TOP[n][1], D_TOP[n][2]) for n in TOP_PORTS}
for n, bs in fe_wires.items():
    if n in top_rng: raise SystemExit('wire FE-BE trung port ct_top ' + n)
    top_rng[n] = rng_of(n, bs)
for s, (n, b, k) in list(names.items()):
    if k == 'nc' and n.startswith('fe_nc_'): top_rng[n] = (0, 0)
L = [HDR, '// ct_top (cung port voi ban goc) = 2 partition: x_ct_ifu_top (FE) + x_c910_be (BE)', 'module ct_top (']
L.append(',\n'.join('  ' + n for n in TOP_PORTS)); L.append(');')
for n in TOP_PORTS:
    k, a, b = D_TOP[n]; L.append(f'{k:6s} {rstr(a, b):10s} {n};')
for n in sorted(fe_wires): a, b = top_rng[n]; L.append(f'wire   {rstr(a, b):10s} {n};')
for n in sorted(k for k in top_rng if k.startswith('fe_nc_')): L.append(f'wire              {n};')
L.append('')
emit_inst(L, 'ct_ifu_top', 'x_ct_ifu_top', 'x_ct_ifu_top', lambda n: top_rng[n], unit_port_order('x_ct_ifu_top'))
L.append('')
# instance c910_be: moi port noi vao ten cung ten (port ct_top hoac wire FE-BE)
L.append('c910_be x_c910_be (')
L.append(',\n'.join(f'  .{n:<40s} ({n})' for n in pnames)); L.append(');')
L.append('endmodule')
open(os.path.join(OUT, 'ct_top.v'), 'w').write('\n'.join(L) + '\n')
# bao cao
nb_in = sum(len(p['bits']) for p in be_ports.values() if 'input' in p['dir'])
nb_out = sum(len(p['bits']) for p in be_ports.values() if 'output' in p['dir'])
print(f'c910_be: {len(be_ports)} port ({nb_in} bit vao, {nb_out} bit ra), {len(be_int)} wire noi bo')
print(f'ct_top : {len(TOP_PORTS)} port, {len(fe_wires)} wire FE<->BE')
