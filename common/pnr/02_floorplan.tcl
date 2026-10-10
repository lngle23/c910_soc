#==== Common setting
source [file join [file dirname [info script]] 00_setup.tcl]
if {[catch {dbGet top.name} top] || $top ne $DESIGN} { restoreDesign $DB/01_read_design.enc.dat $DESIGN }
source $SCRIPTS/settings.tcl
#==== Floorplan theo spec: kich thuoc, pin, chan metal8-10, macro goi y, halo, cutRow
source $BDIR/${DESIGN}_fp.tcl
checkFPlan -reportUtil -outFile $RPT/checkFPlan.rpt
saveDesign $DB/02_floorplan.enc
