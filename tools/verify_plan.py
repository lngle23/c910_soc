import json, collections
J=json.load(open('plan.json')); P=json.load(open('blkports.json'))
ports=J['ports']; M=J['MASTERS']; I=J['INSTS']
err=0
def bad(*a):
    global err; err+=1
    if err<20: print("LOI:",*a)
# 1. CIU core1 mapping
byset=collections.defaultdict(list)
for p in P: byset[p['set']].append(p)
ciu={ (q['port'],q['bit']):q for q in ports['CIU']}
bepin={ (q['port'],q['bit']):q for q in ports['BE']}
for q in ports['CIU']:
    if q['group']!='BE1_CIU': continue
    be1=[p for p in byset[q['set']] if p['inst']=='core1_be']
    assert len(be1)==1
    b=bepin[(be1[0]['port'],be1[0]['bit'])]
    if abs(b['y']-q['y'])>1e-6 or b['side']!='right': bad('core1 map', q['pin'], b['pin'], b['y'], q['y'])
# 2. cap FE/BE, BE/CIU, CIU/L2C cung toa do tuyet doi
def absxy(inst,q):
    d=I[inst]; m=M[d['master']]
    x=q['x'] if d['orient']=='R0' else m['w']-q['x']
    return round(d['x']+x,4), round(d['y']+q['y'],4)
for (ia,ma),(ib,mb) in [(('core0_fe','FE'),('core0_be','BE')),(('core1_fe','FE'),('core1_be','BE')),(('core0_be','BE'),('ciu','CIU')),(('core1_be','BE'),('ciu','CIU')),(('ciu','CIU'),('l2c','L2C'))]:
    A={}
    for p in P:
        if p['inst']==ia: A.setdefault(p['set'],[]).append(p)
    n=0
    for p in P:
        if p['inst']!=ib or p['set'] not in A: continue
        pa=A[p['set']][0]
        if len(set(x['inst'] for x in byset[p['set']]))>2 or pa['drv']+pa['loads']!=[ {'core0_fe':'core0_fe'}.get(ib,ib) ] and len(pa['drv']+pa['loads'])>1: continue
        qa=next(q for q in ports[ma] if q['port']==pa['port'] and q['bit']==pa['bit'])
        qb=next(q for q in ports[mb] if q['port']==p['port'] and q['bit']==p['bit'])
        xa,ya=absxy(ia,qa); xb,yb=absxy(ib,qb)
        same = abs(xa-xb)<1e-3 if qa['side'] in('top','bottom') else abs(ya-yb)<1e-3
        if not same: bad('lech',ia,qa['pin'],(xa,ya),ib,qb['pin'],(xb,yb))
        if qa['layer']!=qb['layer']: bad('khac lop',qa['pin'],qb['pin'])
        n+=1
    print(f"cap {ia}<->{ib}: {n} net thang hang")
# 3. trung vi tri, tren track, trong bien
for m,L in ports.items():
    W,H=M[m]['w'],M[m]['h']; seen={}
    for q in L:
        k=(q['side'],q['layer'],round(q['x'] if q['side'] in('top','bottom') else q['y'],3))
        if k in seen: bad('trung cho',m,q['pin'],seen[k])
        seen[k]=q['pin']
        c=q['x'] if q['side'] in('top','bottom') else q['y']
        off=0.095 if q['side'] in('top','bottom') else 0.07
        if abs(((c-off)/0.28)-round((c-off)/0.28))>1e-6: bad('lech track',m,q['pin'],c)
        L_=W if q['side'] in('top','bottom') else H
        if not(5<=c<=L_-5): bad('sat goc',m,q['pin'],c)
    names=[q['pin'] for q in L]
    if len(names)!=len(set(names)): bad('trung ten pin',m)
    print(f"{m}: {len(L)} pin OK")
# 4. IO
seen={}
for r in J['io_pins']:
    k=(r['side'],r['layer'],round(r['x'] if r['side'] in('top','bottom') else r['y'],3))
    if k in seen: bad('IO trung',r['pin'],seen[k])
    seen[k]=r['pin']
print("IO:",len(J['io_pins']))
print("TONG LOI:",err)
