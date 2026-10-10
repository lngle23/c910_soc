# Mo GUI voi checkpoint 1 buoc:  STEP_NAME=04_place innovus -init $SPEC/common/pnr/gui_open.tcl  (make gui STEP=04)
source [file join [file dirname [info script]] 00_setup.tcl]
restoreDesign $DB/$::env(STEP_NAME).enc.dat $DESIGN
source $SCRIPTS/settings.tcl
win
