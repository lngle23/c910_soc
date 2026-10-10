#!/bin/bash
# Sinh lai toan bo thu muc spec tu dau
set -e
cd /tmp/claude-0/soc
O=/tmp/claude-0/soc/spec_out/c910_soc_spec
rm -rf spec_out
python3 soc_plan.py plan.json > /dev/null
python3 verify_plan.py | tail -1
python3 emit_spec.py $O
python3 emit_lib.py $O > /dev/null
python3 emit_top.py $O
mkdir -p $O/common/scripts && cp templates/*.tcl templates/*.py $O/common/scripts/
python3 draw_fp.py $O/common > /dev/null
cp templates/README.md templates/SPEC.md $O/
# --- RTL openC910 goc (chi cac file trong filelist) + license
python3 - <<'PY'
import os, shutil
O='/tmp/claude-0/soc/spec_out/c910_soc_spec'; SRC='/tmp/claude-0/bt/rtl/C910_RTL_FACTORY'
n=0
for l in open(O+'/common/rtl/c910_soc_rtl.f'):
    l=l.strip()
    if l.startswith('${C910_RTL}/'):
        rel=l[len('${C910_RTL}/'):]; d=os.path.join(O,'rtl','C910_RTL_FACTORY',rel)
        os.makedirs(os.path.dirname(d),exist_ok=True); shutil.copy(os.path.join(SRC,rel),d); n+=1
shutil.copy('/home/claude/c910_genus_nangate45/rtl/LICENSE_openc910',O+'/rtl/LICENSE_openc910')
print('RTL:',n,'file')
PY
# --- Nangate45 (chi file can dung) + license
P=/home/claude/c910_genus_nangate45/pdk/nangate45
mkdir -p $O/pdk/nangate45/lef $O/pdk/nangate45/lib
cp $P/lef/Nangate45_tech.lef $P/lef/Nangate45_stdcell.lef $O/pdk/nangate45/lef/
cp $P/lib/Nangate45_typ.lib $P/lib/Nangate45_fast.lib $P/lib/Nangate45_slow.lib $O/pdk/nangate45/lib/
cp $P/LICENSE $P/README_platform.md $O/pdk/nangate45/
# --- Makefile
mkdir -p $O/common/make && cp templates/make/block.mk templates/make/top.mk $O/common/make/
cp templates/make/root.mk $O/Makefile
for b in fe:ct_ifu_top be:c910_be ciu:ct_ciu_top l2c:ct_l2c_top; do d=${b%%:*}; m=${b##*:}
  printf '# Block %s (%s). Lenh: make help\nBLOCK := %s\ninclude ../../common/make/block.mk\n' $d $m $m > $O/blocks/$d/Makefile; done
printf '# Top c910_soc. Lenh: make help\ninclude ../common/make/top.mk\n' > $O/top/Makefile
cp templates/top_fp_run.tcl templates/top_gui.tcl $O/top/
mkdir -p $O/deliver && echo "Block owner: make deliver chep file ban giao vao day (deliver/<module>/). Top: make collect doc tu day." > $O/deliver/README.txt
mkdir -p $O/common/pnr && cp templates/pnr/*.tcl $O/common/pnr/ && cp templates/top_init.tcl $O/top/
mkdir -p $O/tools && cp soc_plan.py verify_plan.py emit_spec.py emit_lib.py emit_top.py gen_be_rtl.py gen_fakeram.py draw_fp.py conn.cpp build_spec.sh plan.json $O/tools/
rm -rf $O/common/rtl/blackbox
cd spec_out && rm -f ../c910_soc_spec.zip && zip -qr ../c910_soc_spec.zip c910_soc_spec && cd ..
ls -la c910_soc_spec.zip
echo BUILD-OK
