################################################################################
# 00_setup.tcl -- flow PnR CHUNG cho 4 block cua c910_soc (Innovus 19.1, legacy UI)
# Bien moi truong:
#   SPEC   thu muc c910_soc_spec        PDK  thu muc Nangate45 (co lef/ lib/)
#   BLOCK  ct_ifu_top | c910_be | ct_ciu_top | ct_l2c_top
#   NETLIST (tuy chon) netlist Genus, mac dinh ./syn_$BLOCK/$BLOCK.v
# Chay trong thu muc lam viec rieng cua block; db/ reports/ outputs/ tao o day.
################################################################################
foreach v {SPEC PDK BLOCK} { if {![info exists ::env($v)]} { puts "ERROR: thieu bien moi truong $v"; exit 1 } }
set SPECD  $::env(SPEC)
set PDKD   $::env(PDK)
set DESIGN $::env(BLOCK)
array set BLKDIR {ct_ifu_top fe c910_be be ct_ciu_top ciu ct_l2c_top l2c}
if {![info exists BLKDIR($DESIGN)]} { puts "ERROR: BLOCK=$DESIGN khong phai block cua spec"; exit 1 }
set BDIR    $SPECD/blocks/$BLKDIR($DESIGN)
set SCRIPTS [file normalize [file dirname [info script]]]
set ROOT    [pwd]
set DB  $ROOT/db ; set RPT $ROOT/reports ; set OUT $ROOT/outputs
file mkdir $DB $RPT $OUT

set NETLIST [expr {[info exists ::env(NETLIST)] ? $::env(NETLIST) : "$ROOT/syn_$DESIGN/$DESIGN.v"}]
set SDC     $BDIR/$DESIGN.sdc
set MACRO_LEF [lsort [glob $SPECD/common/mem/lef/*.lef]]
set MACRO_LIB [lsort [glob $SPECD/common/mem/lib/*.lib]]
set LEFS     [concat [list $PDKD/lef/Nangate45_tech.lef $PDKD/lef/Nangate45_stdcell.lef] $MACRO_LEF]
set LIB_TYP  [concat [list $PDKD/lib/Nangate45_typ.lib]  $MACRO_LIB]
set LIB_FAST [concat [list $PDKD/lib/Nangate45_fast.lib] $MACRO_LIB]
set PWR VDD ; set GND VSS
set SITE FreePDK45_38x28_10R_NP_162NW_34O
set TOP_LAYER 7          ;# block chi route toi metal7 (metal8-10 la cua top)

set CELL(dont_use) {AOI211_X1 OAI211_X1 FILLCELL_X1 FILLCELL_X2 FILLCELL_X4 FILLCELL_X8 FILLCELL_X16 FILLCELL_X32 ANTENNA_X1}
set CELL(assign)   BUF_X1
set CELL(tie)      {LOGIC1_X1 LOGIC0_X1}
set CELL(filler)   {FILLCELL_X32 FILLCELL_X16 FILLCELL_X8 FILLCELL_X4 FILLCELL_X2 FILLCELL_X1}
set CELL(antenna)  ANTENNA_X1
set CELL(cts_buf)  {CLKBUF_X1 CLKBUF_X2 CLKBUF_X3 BUF_X4 BUF_X8}
set CELL(cts_inv)  {INV_X1 INV_X2 INV_X4 INV_X8}
set CELL(cts_icg)  {CLKGATETST_X1 CLKGATETST_X2 CLKGATETST_X4 CLKGATETST_X8}
set CELL(hold_fix) {BUF_X1 BUF_X2 CLKBUF_X1 CLKBUF_X2}
setMultiCpuUsage -localCpu [expr {[info exists ::env(NCPU)] ? $::env(NCPU) : 4}]
