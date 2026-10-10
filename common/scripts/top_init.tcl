################################################################################
# top_init.tcl -- doc design TOP c910_soc (top module openC910) vao Innovus 19.1, legacy UI.
#   cd <thu muc lam viec top> ; innovus -init $SPEC/top/top_init.tcl -log top
# Bien moi truong: SPEC, PDK ; NETLIST (mac dinh ./syn_openC910/openC910.v)
# BLOCK_LEF_DIR / BLOCK_LIB_DIR: thu muc LEF/ETM that cua 4 block (mac dinh: ban prelim trong spec)
################################################################################
foreach v {SPEC PDK} { if {![info exists ::env($v)]} { puts "ERROR: thieu bien moi truong $v"; exit 1 } }
set SPECD $::env(SPEC); set PDKD $::env(PDK)
set NETLIST [expr {[info exists ::env(NETLIST)] ? $::env(NETLIST) : "[pwd]/syn_openC910/openC910.v"}]
set BLEF [expr {[info exists ::env(BLOCK_LEF_DIR)] ? $::env(BLOCK_LEF_DIR) : "$SPECD/top/lef"}]
set BLIB [expr {[info exists ::env(BLOCK_LIB_DIR)] ? $::env(BLOCK_LIB_DIR) : "$SPECD/top/lib"}]
set LEFS [concat [list $PDKD/lef/Nangate45_tech.lef $PDKD/lef/Nangate45_stdcell.lef] \
                 [lsort [glob $SPECD/common/mem/lef/*.lef]] [lsort [glob $BLEF/*.lef]]]
# block da giao: <module>_setup.lib / <module>_hold.lib ; chua giao: <module>_prelim.lib (dung cho ca 2 goc)
set ::LIB_TYP  [concat [list $PDKD/lib/Nangate45_typ.lib]  [lsort [glob -nocomplain $BLIB/*_setup.lib $BLIB/*_prelim.lib]]]
set ::LIB_FAST [concat [list $PDKD/lib/Nangate45_fast.lib] [lsort [glob -nocomplain $BLIB/*_hold.lib $BLIB/*_prelim.lib]]]
set ::SDC $SPECD/top/c910_soc.sdc
set mmmc [file join [pwd] top_mmmc.tcl]
set fh [open $mmmc w]
puts $fh {create_library_set  -name LS_TYP  -timing $::LIB_TYP
create_library_set  -name LS_FAST -timing $::LIB_FAST
create_rc_corner    -name RC_TYP  -T 25
create_rc_corner    -name RC_FAST -T 0
create_delay_corner -name DC_TYP  -library_set LS_TYP  -rc_corner RC_TYP
create_delay_corner -name DC_FAST -library_set LS_FAST -rc_corner RC_FAST
create_constraint_mode -name CM_FUNC -sdc_files [list $::SDC]
create_analysis_view -name AV_SETUP -constraint_mode CM_FUNC -delay_corner DC_TYP
create_analysis_view -name AV_HOLD  -constraint_mode CM_FUNC -delay_corner DC_FAST
set_analysis_view -setup [list AV_SETUP] -hold [list AV_HOLD]}
close $fh
setDoAssign on -buffer BUF_X1
set init_design_netlisttype Verilog
set init_verilog   $NETLIST
set init_top_cell  openC910
set init_lef_file  $LEFS
set init_mmmc_file $mmmc
set init_pwr_net   VDD
set init_gnd_net   VSS
init_design
setDesignMode -process 45
setAnalysisMode -analysisType onChipVariation -cppr both
puts "TOP-INIT: [llength [dbGet -p2 top.insts.cell.subClass block]] instance macro/block (mong doi 6 block + 0 SRAM o top)"
# tiep theo: source $SPECD/top/c910_soc_fp.tcl ; source $SPECD/top/c910_soc_pg.tcl  (make fp lam san)
