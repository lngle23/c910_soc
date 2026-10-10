#!/usr/bin/env python3
"""gen_fakeram.py -- sinh macro SRAM "fakeram45_<D>x<W>" DUNG KICH THUOC (1 SRAM logic = 1 macro),
giong cach memory compiler sinh, theo dung kieu bsg_fakeram cua platform nangate45:
  - pin tin hieu: canh TRAI, metal3, tren track metal3 (pitch 0.14, offset 0.07), cach nhau 2 track
  - nguon: strap metal4 doc VSS/VDD xen ke, pitch 3.36, rong 0.28
  - OBS: metal1..metal3 toan bo (tru cua so pin metal3), metal4 tru strap
  - kich thuoc: W boi so 0.19 (site), H boi so 1.4 (row)
Area / timing la mo hinh noi suy tu 12 macro fakeram45 co san trong PDK -- KHONG phai so that.
Sinh: lef/fakeram45_<cfg>.lef, lib/fakeram45_<cfg>.lib, wrap/ct_f_spsram_<cfg>.v
"""
import math, os, sys

OUT = sys.argv[1]
CFGS = sys.argv[2:] or "1024x64 128x16 2048x32 256x196 256x23 256x84 512x144 512x22 512x44 512x52 512x54 512x59 512x7 512x96 8192x128".split()
for d in ('lef', 'lib', 'wrap'): os.makedirs(os.path.join(OUT, d), exist_ok=True)

SITE_W, ROW_H = 0.19, 1.40
PIN_W, PIN_PITCH, PIN_OFF = 0.07, 0.28, 0.07      # metal3: width 0.07, track 0.14 -> dung moi track thu 2
PG_W, PG_PITCH, PG_OFF = 0.28, 3.36, 1.96          # metal4 straps (giong fakeram45 goc)
EDGE = 2.10                                        # le tren/duoi cho strap
def snap(v, g): return round(math.ceil(v / g - 1e-9) * g, 3)

# noi suy clk->Q theo log2(so bit) tu cac macro co san (64x7 ... 2048x39)
PTS = [(math.log2(64 * 7), 0.164), (math.log2(2048), 0.188), (math.log2(6144), 0.234),
       (math.log2(32768), 0.305), (math.log2(79872), 0.435)]
def clk2q(bits):
    x = math.log2(bits)
    if x <= PTS[0][0]: return PTS[0][1]
    for (x0, y0), (x1, y1) in zip(PTS, PTS[1:]):
        if x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return PTS[-1][1] + 0.08 * (x - PTS[-1][0])

def geometry(depth, width):
    aw = max(1, (depth - 1).bit_length())
    bits = depth * width
    area_t = 0.55 * bits + 1000.0
    npin = 3 * width + aw + 3
    h_pin = npin * PIN_PITCH + 4 * 3 * PIN_PITCH + 2 * EDGE      # + khe giua 4 nhom pin
    side = math.sqrt(area_t)
    H = snap(max(h_pin, side), ROW_H)
    W = snap(max(area_t / H, 4 * PG_PITCH), SITE_W)
    return aw, W, H

def pins_layout(depth, width, aw):
    groups = [('w_mask_in', width, 'INPUT'), ('rd_out', width, 'OUTPUT'), ('wd_in', width, 'INPUT'),
              ('addr_in', aw, 'INPUT'), ('we_in', 0, 'INPUT'), ('ce_in', 0, 'INPUT'), ('clk', 0, 'INPUT')]
    y = EDGE + PIN_OFF  # tam pin dau tien nam tren track metal3 (0.07 + k*0.14)
    y = round(math.ceil((y - PIN_OFF) / 0.14) * 0.14 + PIN_OFF, 3)
    out = []
    for gi, (n, w, d) in enumerate(groups):
        if w == 0:
            out.append((n, d, y)); y = round(y + PIN_PITCH, 3)
        else:
            for i in range(w):
                out.append((f'{n}[{i}]', d, y)); y = round(y + PIN_PITCH, 3)
        if gi < 3: y = round(y + 3 * PIN_PITCH, 3)
    return out, y

def lef(name, depth, width):
    aw, W, H = geometry(depth, width)
    pins, ytop = pins_layout(depth, width, aw)
    assert ytop < H - EDGE + 1e-6, (name, ytop, H)
    L = ['VERSION 5.7 ;', 'BUSBITCHARS "[]" ;', f'MACRO {name}', f'  FOREIGN {name} 0 0 ;', '  SYMMETRY X Y R90 ;',
         f'  SIZE {W:.3f} BY {H:.3f} ;', '  CLASS BLOCK ;']
    for pn, d, yc in pins:
        L += [f'  PIN {pn}', f'    DIRECTION {d} ;', '    USE SIGNAL ;', '    SHAPE ABUTMENT ;', '    PORT', '      LAYER metal3 ;',
              f'      RECT 0.000 {yc - PIN_W / 2:.3f} {PIN_W:.3f} {yc + PIN_W / 2:.3f} ;', '    END', f'  END {pn}']
    straps = {'VSS': [], 'VDD': []}
    x = PG_OFF
    while x + PG_W + PG_PITCH / 2 + PG_W < W - 1.0:
        straps['VSS'].append(x); straps['VDD'].append(round(x + PG_PITCH / 2, 3)); x = round(x + PG_PITCH, 3)
    for net, use in (('VSS', 'GROUND'), ('VDD', 'POWER')):
        L += [f'  PIN {net}', '    DIRECTION INOUT ;', f'    USE {use} ;', '    PORT', '      LAYER metal4 ;']
        L += [f'      RECT {x0:.3f} {EDGE:.3f} {x0 + PG_W:.3f} {H - EDGE:.3f} ;' for x0 in straps[net]]
        L += ['    END', f'  END {net}']
    L += ['  OBS', '    LAYER metal1 ;', f'    RECT 0 0 {W:.3f} {H:.3f} ;', '    LAYER metal2 ;', f'    RECT 0 0 {W:.3f} {H:.3f} ;',
          '    LAYER metal3 ;', f'    RECT {PIN_W:.3f} 0 {W:.3f} {H:.3f} ;']
    ys = [yc for _, _, yc in pins]
    prev = 0.0
    for yc in ys:
        L.append(f'    RECT 0 {prev:.3f} {PIN_W:.3f} {yc - PIN_W / 2 - 0.065:.3f} ;'); prev = yc + PIN_W / 2 + 0.065
    L.append(f'    RECT 0 {prev:.3f} {PIN_W:.3f} {H:.3f} ;')
    L += ['    LAYER metal4 ;', f'    RECT 0 0 {W:.3f} {EDGE:.3f} ;', f'    RECT 0 {H - EDGE:.3f} {W:.3f} {H:.3f} ;']
    allx = sorted(straps['VSS'] + straps['VDD'])
    prev = 0.0
    for x0 in allx:
        L.append(f'    RECT {prev:.3f} {EDGE:.3f} {x0:.3f} {H - EDGE:.3f} ;'); prev = x0 + PG_W
    L.append(f'    RECT {prev:.3f} {EDGE:.3f} {W:.3f} {H - EDGE:.3f} ;')
    L += ['    LAYER OVERLAP ;', f'    RECT 0 0 {W:.3f} {H:.3f} ;', '  END', f'END {name}', '', 'END LIBRARY']
    return '\n'.join(L) + '\n', W, H, aw

def lib(name, depth, width, aw, area):
    bits = depth * width
    cq = clk2q(bits); mp = round(cq * 0.92, 3); pw = round(0.16 * math.sqrt(bits) * 1.2, 3); setup = 0.050
    def con(pin, bus):
        hdr = f'    bus({pin})   {{\n        bus_type : {name}_{bus};\n' if bus else f'    pin({pin}){{\n'
        return (hdr + '        direction : input;\n        capacitance : 5.000;\n' +
                ''.join(f'        timing() {{\n            related_pin : clk;\n            timing_type : {tt} ;\n'
                        f'            rise_constraint(scalar) {{\n                values ("{setup:.3f}");\n            }}\n'
                        f'            fall_constraint(scalar) {{\n                values ("{setup:.3f}");\n            }}\n        }}\n'
                        for tt in ('setup_rising', 'hold_rising')) + '    }\n')
    s = f'''library({name}) {{
    technology (cmos);
    delay_model : table_lookup;
    revision : 1.0;
    comment : "SRAM gia (mo hinh) -- sinh boi gen_fakeram.py, KHONG phai memory compiler";
    time_unit : "1ns";
    voltage_unit : "1V";
    current_unit : "1uA";
    leakage_power_unit : "1nw";
    nom_process : 1;
    nom_temperature : 25.000;
    nom_voltage : 1.1;
    capacitive_load_unit (1,ff);
    pulling_resistance_unit : "1kohm";
    operating_conditions(tt_1.0_25.0) {{
        process : 1;
        temperature : 25.000;
        voltage : 1.1;
        tree_type : balanced_tree;
    }}
    default_cell_leakage_power : 0;
    default_fanout_load : 1;
    default_inout_pin_cap : 0.0;
    default_input_pin_cap : 0.0;
    default_output_pin_cap : 0.0;
    default_max_transition : 0.227;
    default_operating_conditions : tt_1.0_25.0;
    default_leakage_power_density : 0.0;
    slew_derate_from_library : 1.000;
    slew_lower_threshold_pct_fall : 20.000;
    slew_upper_threshold_pct_fall : 80.000;
    slew_lower_threshold_pct_rise : 20.000;
    slew_upper_threshold_pct_rise : 80.000;
    input_threshold_pct_fall : 50.000;
    input_threshold_pct_rise : 50.000;
    output_threshold_pct_fall : 50.000;
    output_threshold_pct_rise : 50.000;
    lu_table_template({name}_mem_out_slew_template) {{
        variable_1 : total_output_net_capacitance;
            index_1 ("1000, 1001");
    }}
    library_features(report_delay_calculation);
    type ({name}_DATA) {{
        base_type : array ;
        data_type : bit ;
        bit_width : {width};
        bit_from : {width - 1};
        bit_to : 0 ;
        downto : true ;
    }}
    type ({name}_ADDRESS) {{
        base_type : array ;
        data_type : bit ;
        bit_width : {aw};
        bit_from : {aw - 1};
        bit_to : 0 ;
        downto : true ;
    }}
cell({name}) {{
    area : {area:.3f};
    interface_timing : true;
    memory() {{
        type : ram;
        address_width : {aw};
        word_width : {width};
    }}
    pin(clk)   {{
        direction : input;
        capacitance : 25.000;
        clock : true;
        min_period           : {mp:.3f} ;
        internal_power(){{
            rise_power(scalar) {{
                values ("{pw:.3f}")
            }}
            fall_power(scalar) {{
                values ("{pw:.3f}")
            }}
        }}
    }}
    bus(rd_out)   {{
        bus_type : {name}_DATA;
        direction : output;
        max_capacitance : 500.000;
        memory_read() {{
            address : addr_in;
        }}
        timing() {{
            related_pin : "clk" ;
            timing_type : rising_edge;
            timing_sense : non_unate;
            cell_rise(scalar) {{
                values ("{cq:.3f}");
            }}
            cell_fall(scalar) {{
                values ("{cq:.3f}");
            }}
            rise_transition({name}_mem_out_slew_template) {{
                index_1 ("5.000, 500.000");
                values ("0.009, 0.227")
            }}
            fall_transition({name}_mem_out_slew_template) {{
                index_1 ("5.000, 500.000");
                values ("0.009, 0.227")
            }}
        }}
    }}
{con('we_in', None)}{con('ce_in', None)}{con('addr_in', 'ADDRESS')}{con('wd_in', 'DATA')}{con('w_mask_in', 'DATA')}    cell_leakage_power : {bits * 0.0005:.3f};
}}

}}
'''
    return s, cq

def wrapper(cfg, depth, width, aw):
    return f'''// AUTO-GENERATED by gen_fakeram.py -- ct_f_spsram_{cfg} = 1 macro fakeram45_{cfg} (1:1)
// Doi cuc tinh: CEN/GWEN/WEN cua C910 tich cuc muc thap; fakeram tich cuc muc cao.
module ct_f_spsram_{cfg} (A, CEN, CLK, D, GWEN, Q, WEN);
  input  [{aw - 1}:0] A;
  input          CEN;
  input          CLK;
  input  [{width - 1}:0] D;
  input          GWEN;
  input  [{width - 1}:0] WEN;
  output [{width - 1}:0] Q;
  fakeram45_{cfg} x_sram_macro (
    .clk(CLK), .ce_in(~CEN), .we_in(~GWEN), .addr_in(A),
    .wd_in(D), .w_mask_in(~WEN), .rd_out(Q));
endmodule
'''

rows = []
for cfg in CFGS:
    d, w = map(int, cfg.split('x'))
    name = f'fakeram45_{cfg}'
    L, W, H, aw = lef(name, d, w)
    open(os.path.join(OUT, 'lef', name + '.lef'), 'w').write(L)
    s, cq = lib(name, d, w, aw, W * H)
    open(os.path.join(OUT, 'lib', name + '.lib'), 'w').write(s)
    open(os.path.join(OUT, 'wrap', f'ct_f_spsram_{cfg}.v'), 'w').write(wrapper(cfg, d, w, aw))
    rows.append((name, d, w, W, H, W * H, cq, 3 * w + aw + 3))
with open(os.path.join(OUT, 'macro_table.csv'), 'w') as fh:
    fh.write('macro,depth,width,width_um,height_um,area_um2,clk2q_ns,signal_pins\n')
    for r in rows: fh.write('%s,%d,%d,%.3f,%.3f,%.1f,%.3f,%d\n' % r)
for r in rows: print('%-22s %6d x %-4d  %8.2f x %8.2f um  area %10.1f  clk2q %.3f  pins %d' % r)
