#!/usr/bin/env python3
"""emit_lib.py -- Liberty SO BO (budget model) cho moi block, de top synthesize + STA khi block chua giao ETM.
setup(lib) = T - ext - L ; clk->Q(lib) = T - ext + L   (L = muc tieu insertion delay cua block, ext = ngan sach ngoai block)
"""
import csv, json, os, re, sys, collections
J = json.load(open('/tmp/claude-0/soc/plan.json'))
OUT = sys.argv[1]; T = J['T']; M = J['MASTERS']
SUM = json.load(open('/tmp/claude-0/soc/summary.json'))
CLKPIN = {'FE': 'forever_cpuclk', 'BE': 'pll_core_clk', 'CIU': 'forever_cpuclk', 'L2C': 'forever_cpuclk'}
for m, info in M.items():
    mod = info['module']; L_ = SUM[m]['clk_lat']
    rows = list(csv.DictReader(open(os.path.join(OUT, 'blocks', m.lower(), f'{mod}_ports.csv'))))
    ports = collections.OrderedDict()
    for r in rows:
        mm = re.match(r'(\w+)\[(\d+)\]$', r['pin'])
        base, idx = (mm.group(1), int(mm.group(2))) if mm else (r['pin'], None)
        ports.setdefault(base, []).append((idx, r))
    widths = sorted(set(len(v) for v in ports.values() if v[0][0] is not None))
    s = [f'/* Budget model so bo cua {mod} -- sinh tu spec (emit_lib.py). Thay bang ETM that (do_extract_model) khi block giao. */',
         f'library({mod}_prelim) {{', '  delay_model : table_lookup;', '  time_unit : "1ns";', '  voltage_unit : "1V";',
         '  current_unit : "1uA";', '  leakage_power_unit : "1nw";', '  capacitive_load_unit (1,ff);', '  pulling_resistance_unit : "1kohm";',
         '  nom_process : 1;', '  nom_temperature : 25;', '  nom_voltage : 1.1;',
         '  operating_conditions(typical) { process : 1; temperature : 25; voltage : 1.1; tree_type : balanced_tree; }',
         '  default_operating_conditions : typical;', '  default_max_transition : 0.15;',
         '  input_threshold_pct_rise : 50; input_threshold_pct_fall : 50; output_threshold_pct_rise : 50; output_threshold_pct_fall : 50;',
         '  slew_lower_threshold_pct_rise : 20; slew_upper_threshold_pct_rise : 80; slew_lower_threshold_pct_fall : 20; slew_upper_threshold_pct_fall : 80;']
    # bus types theo (msb,lsb)
    btypes = {}
    for base, v in ports.items():
        if v[0][0] is None: continue
        idx = [i for i, _ in v]; key = (max(idx), min(idx))
        if key not in btypes:
            btypes[key] = f'bus_{key[0]}_{key[1]}'
            s += [f'  type ({btypes[key]}) {{', '    base_type : array;', '    data_type : bit;', f'    bit_width : {key[0] - key[1] + 1};',
                  f'    bit_from : {key[0]};', f'    bit_to : {key[1]};', '    downto : true;', '  }']
    s += [f'  cell({mod}) {{', f'    area : {info["w"] * info["h"]:.1f};', '    dont_use : true;', '    dont_touch : true;', '    interface_timing : true;']
    clk = CLKPIN[m]
    def arcs(r, ind):
        bt, d = r['budget_type'], r['dir']
        sp = ' ' * ind
        if bt in ('clk',):
            return []
        if bt in ('case0', 'false', 'async', 'mcp3'):
            return []          # khong co arc: duong tinh/async, top rang buoc bang SDC chip
        ext = float(r['ext_delay_ns']); Tr = float(r['ref_period_ns'] or T)   # AXI: V_SYS_CLK = 2T
        if d == 'in':
            st = max(0.05, Tr - ext - L_)
            return [f'{sp}timing() {{', f'{sp}  related_pin : "{clk}";', f'{sp}  timing_type : setup_rising;',
                    f'{sp}  rise_constraint(scalar) {{ values("{st:.3f}"); }}', f'{sp}  fall_constraint(scalar) {{ values("{st:.3f}"); }}', f'{sp}}}',
                    f'{sp}timing() {{', f'{sp}  related_pin : "{clk}";', f'{sp}  timing_type : hold_rising;',
                    f'{sp}  rise_constraint(scalar) {{ values("{-L_ + 0.05:.3f}"); }}', f'{sp}  fall_constraint(scalar) {{ values("{-L_ + 0.05:.3f}"); }}', f'{sp}}}']
        cq = Tr - ext + L_
        return [f'{sp}timing() {{', f'{sp}  related_pin : "{clk}";', f'{sp}  timing_type : rising_edge;',
                f'{sp}  cell_rise(scalar) {{ values("{cq:.3f}"); }}', f'{sp}  cell_fall(scalar) {{ values("{cq:.3f}"); }}',
                f'{sp}  rise_transition(scalar) {{ values("0.100"); }}', f'{sp}  fall_transition(scalar) {{ values("0.100"); }}', f'{sp}}}']
    for base, v in ports.items():
        r0 = v[0][1]; d = 'input' if r0['dir'] == 'in' else 'output'
        if v[0][0] is None:
            s += [f'    pin({base}) {{', f'      direction : {d};']
            if r0['budget_type'] == 'clk' and d == 'input': s.append('      clock : true;')
            s.append('      capacitance : 2.0;' if d == 'input' else '      max_capacitance : 100.0;')
            if m == 'BE' and base == 'forever_cpuclk' and d == 'output':
                s += ['      timing() {', '        related_pin : "pll_core_clk";', '        timing_sense : positive_unate;', '        timing_type : combinational;',
                      '        cell_rise(scalar) { values("0.150"); }', '        cell_fall(scalar) { values("0.150"); }',
                      '        rise_transition(scalar) { values("0.080"); }', '        fall_transition(scalar) { values("0.080"); }', '      }']
            else:
                s += arcs(r0, 6)
            s.append('    }')
        else:
            idx = [i for i, _ in v]; key = (max(idx), min(idx))
            kinds = set((r['budget_type'], r['ext_delay_ns']) for _, r in v)
            s += [f'    bus({base}) {{', f'      bus_type : {btypes[key]};', f'      direction : {d};',
                  '      capacitance : 2.0;' if d == 'input' else '      max_capacitance : 100.0;']
            if len(kinds) == 1:
                s += arcs(r0, 6)
            else:
                for i, r in sorted(v, key=lambda t: -t[0]):
                    s += [f'      pin({base}[{i}]) {{'] + arcs(r, 8) + ['      }']
            s.append('    }')
    s += ['  }', '}']
    p = os.path.join(OUT, 'blocks', m.lower(), f'{mod}_prelim.lib')
    open(p, 'w').write('\n'.join(s) + '\n')
    os.makedirs(os.path.join(OUT, 'top', 'lib'), exist_ok=True)
    open(os.path.join(OUT, 'top', 'lib', f'{mod}_prelim.lib'), 'w').write('\n'.join(s) + '\n')
    print(m, mod, len(ports), 'port', os.path.getsize(p) // 1024, 'KB')
