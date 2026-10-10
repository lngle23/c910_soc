#==== Common setting
source [file join [file dirname [info script]] 00_setup.tcl]
if {[catch {dbGet top.name} top] || $top ne $DESIGN} { restoreDesign $DB/08_route_opt.enc.dat $DESIGN }
source $SCRIPTS/settings.tcl
set R $RPT/09_finish; file mkdir $R
setExtractRCMode -engine postRoute -effortLevel low
addFiller -cell $CELL(filler) -prefix FILLER
ecoRoute
verify_drc -limit 100000 -report $R/drc.rpt
verifyConnectivity -type all -noAntenna -report $R/connectivity.rpt
verifyProcessAntenna -report $R/antenna.rpt
timeDesign -postRoute       -outDir $R/timing      -prefix final
timeDesign -postRoute -hold -outDir $R/timing_hold -prefix final_hold
#==== Ban giao cho top
saveNetlist $OUT/$DESIGN.pnr.v
saveNetlist $OUT/$DESIGN.pnr.pg.v -includePowerGround -includePhysicalCell $CELL(filler)
defOut -floorplan -netlist -routing $OUT/$DESIGN.def
rcOut -spef $OUT/$DESIGN.spef -rc_corner RC_TYP
write_sdf -view AV_SETUP $OUT/$DESIGN.sdf
# LEF abstract: lop tren cung cua block = metal7, PG pin = strap metal7 (top dat via metal8 xuong day)
write_lef_abstract -specifyTopLayer metal7 -PGpinLayers {metal7} -stripePin $OUT/$DESIGN.lef
# ETM cho STA cua top (goc setup va hold)
do_extract_model -view AV_SETUP $OUT/${DESIGN}_setup.lib
do_extract_model -view AV_HOLD  $OUT/${DESIGN}_hold.lib
puts "== Nghiem thu: python3 \$SPEC/common/scripts/check_lef_vs_spec.py $OUT/$DESIGN.lef $BDIR/${DESIGN}_ports.csv $BDIR/${DESIGN}_prelim.lef"
saveDesign $DB/09_finish.enc
