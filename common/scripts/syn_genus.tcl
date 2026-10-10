################################################################################
# syn_genus.tcl -- synthesis 1 block (hoac top) theo spec c910_soc. Genus 19.1, Common UI.
#
#   Cach de nhat: cd blocks/<blk> ; make syn     (Makefile tu dat cac bien duoi day)
#   export SPEC=/duong/dan/c910_soc_spec            (thu muc spec nay)
#   export C910_RTL=$SPEC/rtl/C910_RTL_FACTORY       (RTL openc910 goc, da kem trong spec)
#   export PDK=$SPEC/pdk/nangate45                   (Nangate45 lef/ lib/, da kem trong spec)
#   export BLOCK=ct_ifu_top                          (ct_ifu_top | c910_be | ct_ciu_top | ct_l2c_top | openC910)
#   genus -files $SPEC/common/scripts/syn_genus.tcl -log syn_$BLOCK
#
# Block: doc toan bo RTL, elaborate dung module cua minh, SDC = blocks/<blk>/<module>.sdc
# Top  : BLOCK=openC910, KHONG doc RTL 4 block; 4 instance resolve bang top/lib/*_prelim.lib
################################################################################
foreach v {SPEC C910_RTL PDK BLOCK} {
  if {![info exists ::env($v)]} { puts "ERROR: thieu bien moi truong $v"; exit 1 }
}
set SPEC $::env(SPEC); set PDK $::env(PDK); set BLOCK $::env(BLOCK)
array set DIR {ct_ifu_top fe c910_be be ct_ciu_top ciu ct_l2c_top l2c openC910 top}
if {![info exists DIR($BLOCK)]} { puts "ERROR: BLOCK=$BLOCK khong co trong spec"; exit 1 }
set IS_TOP [expr {$BLOCK eq "openC910"}]
set OUTD [file normalize syn_$BLOCK]; file mkdir $OUTD

set_db max_cpus_per_server [expr {[info exists ::env(NCPU)] ? $::env(NCPU) : 4}]
set_db hdl_error_on_blackbox true
set_db auto_ungroup none                 ;# giu hierarchy -> ten instance macro dung nhu spec

#---- thu vien: std cell + 15 macro SRAM (+ budget model 4 block neu la top)
set libs [concat [list $PDK/lib/Nangate45_typ.lib] [lsort [glob $SPEC/common/mem/lib/*.lib]]]
set lefs [concat [list $PDK/lef/Nangate45_tech.lef $PDK/lef/Nangate45_stdcell.lef] [lsort [glob $SPEC/common/mem/lef/*.lef]]]
if {$IS_TOP} {
  # 4 block: ETM/LEF that neu block da giao (thu muc BLOCK_LIB_DIR/BLOCK_LEF_DIR, do 'make collect' cua top tao), neu chua thi ban so bo
  set BLIB [expr {[info exists ::env(BLOCK_LIB_DIR)] ? $::env(BLOCK_LIB_DIR) : "$SPEC/top/lib"}]
  set BLEF [expr {[info exists ::env(BLOCK_LEF_DIR)] ? $::env(BLOCK_LEF_DIR) : "$SPEC/top/lef"}]
  set libs [concat $libs [lsort [concat [glob -nocomplain $BLIB/*_prelim.lib] [glob -nocomplain $BLIB/*_setup.lib]]]]
  set lefs [concat $lefs [lsort [glob $BLEF/*.lef]]]
}
read_libs $libs
read_physical -lef $lefs
foreach c {AOI211_X1 OAI211_X1 FILLCELL_X1 FILLCELL_X2 FILLCELL_X4 FILLCELL_X8 FILLCELL_X16 FILLCELL_X32 ANTENNA_X1} {
  foreach lc [get_db lib_cells */$c] { set_db $lc .dont_use true }
}

#---- RTL
set fl [expr {$IS_TOP ? "$SPEC/common/rtl/c910_top_only_rtl.f" : "$SPEC/common/rtl/c910_soc_rtl.f"}]
set files {}
set fh [open $fl r]
while {[gets $fh line] >= 0} {
  set line [string trim $line]
  if {$line eq "" || [string match "//*" $line]} continue
  set line [string map [list {${C910_RTL}} $::env(C910_RTL) {${SPEC}} $SPEC] $line]
  if {![file readable $line]} { puts "ERROR: khong doc duoc $line"; exit 1 }
  lappend files $line
}
close $fh
puts "SYN: [llength $files] file RTL"
read_hdl -v2001 $files
elaborate $BLOCK
check_design -unresolved > $OUTD/check_unresolved.rpt

#---- constraint
set sdc [expr {$IS_TOP ? "$SPEC/top/c910_soc.sdc" : "$SPEC/blocks/$DIR($BLOCK)/$BLOCK.sdc"}]
read_sdc $sdc
check_timing_intent > $OUTD/check_timing_intent.rpt

#---- synthesis
set_db syn_generic_effort medium
set_db syn_map_effort medium
set_db syn_opt_effort medium
syn_generic
syn_map
syn_opt

#---- ket qua
write_hdl > $OUTD/$BLOCK.v
write_sdc > $OUTD/$BLOCK.sdc
report_qor      > $OUTD/qor.rpt
report_area     > $OUTD/area.rpt
report_gates    > $OUTD/gates.rpt
report_timing -max_paths 50 > $OUTD/timing.rpt
#---- kiem so macro SRAM (dem trong gates.rpt)
array set WANT {ct_ifu_top 18 c910_be 14 ct_ciu_top 0 ct_l2c_top 18 openC910 0}
set nmac 0
set fh [open $OUTD/gates.rpt r]
while {[gets $fh l] >= 0} { if {[regexp {^\s*(fakeram45_\S+)\s+(\d+)\s} $l -> c n]} { incr nmac $n } }
close $fh
puts [format "SYN-CHECK: %s macro SRAM = %d (spec: %d)" [expr {$nmac == $WANT($BLOCK) ? "PASS" : "FAIL"}] $nmac $WANT($BLOCK)]
puts "SYN-DONE: $BLOCK -> $OUTD/$BLOCK.v"
exit 0
