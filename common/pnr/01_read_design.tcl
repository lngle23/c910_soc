#==== Common setting
source [file join [file dirname [info script]] 00_setup.tcl]
set R $RPT/01_read_design; file mkdir $R
setDoAssign on -buffer $CELL(assign)
set init_design_netlisttype Verilog
set init_verilog   $NETLIST
set init_top_cell  $DESIGN
set init_lef_file  $LEFS
set init_mmmc_file $SCRIPTS/mmmc.tcl
set init_pwr_net   $PWR
set init_gnd_net   $GND
init_design
source $SCRIPTS/settings.tcl
checkDesign -all -outdir $R/checkDesign
check_timing -verbose > $R/check_timing.rpt
timeDesign -prePlace -outDir $R/timing -prefix prePlace
puts "== 01: $DESIGN macro = [llength [dbGet -p2 top.insts.cell.subClass block]], instance = [llength [dbGet top.insts]]"
saveDesign $DB/01_read_design.enc
