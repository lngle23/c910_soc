#==== Common setting
source [file join [file dirname [info script]] 00_setup.tcl]
if {[catch {dbGet top.name} top] || $top ne $DESIGN} { restoreDesign $DB/02_floorplan.enc.dat $DESIGN }
source $SCRIPTS/settings.tcl
#==== PG theo spec (strap metal7 co dinh)
source $BDIR/${DESIGN}_pg.tcl
saveDesign $DB/03_powerplan.enc
