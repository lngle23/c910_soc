#!/usr/bin/env python3
"""Ve floorplan toan chip + tung block tu plan.json -> PNG/SVG."""
import json, sys, os, collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
J = json.load(open('/tmp/claude-0/soc/plan.json'))
OUT = sys.argv[1]
M, I, DIE, TL = J['MASTERS'], J['INSTS'], J['DIE'], J['TOPLOGIC']
COL = {'FE': '#7aa6d8', 'BE': '#8cc49a', 'CIU': '#e6b26a', 'L2C': '#c9a0dc'}
GCOL = {'FE_BE': '#1f5fa8', 'BE_CIU': '#2f8a3f', 'BE1_CIU': '#2f8a3f', 'CIU_L2C': '#8a3fa8', 'BE_IO': '#c0392b',
        'BE_TOP': '#d35400', 'CIU_TOP': '#d35400', 'L2C_TOP': '#d35400'}

def macro_abs(inst, a):
    d = I[inst]; m = M[d['master']]
    if d['orient'] == 'R0': return d['x'] + a['x'], d['y'] + a['y']
    return d['x'] + m['w'] - a['x'] - a['w'], d['y'] + a['y']

def pin_abs(inst, q):
    d = I[inst]; m = M[d['master']]
    x = q['x'] if d['orient'] == 'R0' else m['w'] - q['x']
    return d['x'] + x, d['y'] + q['y']

fig, ax = plt.subplots(figsize=(9, 12.6), dpi=130)
ax.add_patch(Rectangle((0, 0), DIE['w'], DIE['h'], fill=False, lw=1.6, ec='black'))
ax.add_patch(Rectangle((TL['x'], TL['y']), TL['w'], TL['h'], fc='#f2f2f2', ec='#888', lw=0.8, ls='--'))
ax.text(TL['x'] + TL['w'] / 2, TL['y'] + TL['h'] / 2, 'top logic\nPLIC CLINT\nSYSIO HAD\nclk/rst gen', ha='center', va='center', fontsize=7.5, color='#444')
for k, d in I.items():
    m = M[d['master']]
    ax.add_patch(Rectangle((d['x'], d['y']), m['w'], m['h'], fc=COL[d['master']], ec='black', lw=1.0, alpha=0.55))
    for a in J['macro_place'][d['master']]:
        x, y = macro_abs(k, a)
        ax.add_patch(Rectangle((x, y), a['w'], a['h'], fc='#555', ec='#222', lw=0.3, alpha=0.55))
    lab = f"{k}\n{m['module']}  [{d['orient']}]\n{m['w']:.0f} x {m['h']:.0f} um"
    ty = d['y'] + m['h'] * (0.62 if d['master'] in ('BE', 'CIU') else 0.25 if d['master'] == 'FE' else 0.5)
    if d['master'] == 'L2C': ty = d['y'] + m['h'] - 120
    ax.text(d['x'] + m['w'] / 2, ty, lab, ha='center', va='center', fontsize=8, weight='bold')
# pin: ve chu ky ngan theo nhom
rep = {'FE': ['core0_fe', 'core1_fe'], 'BE': ['core0_be', 'core1_be'], 'CIU': ['ciu'], 'L2C': ['l2c']}
for m, insts in rep.items():
    for inst in insts:
        for q in J['ports'][m][::3]:
            x, y = pin_abs(inst, q)
            c = GCOL.get(q['group'], '#d35400')
            ax.plot([x], [y], marker='s', ms=0.8, color=c, lw=0)
for r in J['io_pins'][::2]:
    ax.plot([r['x']], [r['y']], marker='s', ms=0.9, color='black', lw=0)
ax.set_xlim(-60, DIE['w'] + 60); ax.set_ylim(-60, DIE['h'] + 60); ax.set_aspect('equal')
ax.set_title(f"c910_soc floorplan  --  die {DIE['w']:.2f} x {DIE['h']:.2f} um ({DIE['w'] * DIE['h'] / 1e6:.2f} mm2), Nangate45", fontsize=10)
ax.set_xlabel('x (um)'); ax.set_ylabel('y (um)')
from matplotlib.lines import Line2D
leg = [Line2D([0], [0], marker='s', color='w', markerfacecolor=c, ms=7, label=l) for l, c in
       [('pin FE<->BE', GCOL['FE_BE']), ('pin BE<->CIU', GCOL['BE_CIU']), ('pin CIU<->L2C', GCOL['CIU_L2C']),
        ('pin BE<->IO chip', GCOL['BE_IO']), ('pin -> top logic / IO', GCOL['BE_TOP']), ('IO chip', 'black'), ('macro SRAM', '#555')]]
ax.legend(handles=leg, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4, fontsize=7.5, frameon=False)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'floorplan_soc.png'))
plt.savefig(os.path.join(OUT, 'floorplan_soc.svg'))
print('ok')
