################################################################################
# 04_place.tcl -- placement + toi uu preCTS + tie cell
################################################################################
#==== Common setting =========================================================
source [file join [file dirname [info script]] 00_setup.tcl]
# Chua co design trong phien nay (chay rieng step) -> doc checkpoint step truoc
if {[catch {dbGet top.name} top] || $top ne $DESIGN} { restoreDesign $DB/03_powerplan.enc.dat $DESIGN }
source $SCRIPTS/settings.tcl
#=============================================================================
set R $RPT/04_place; file mkdir $R

setPlaceMode -timingDriven true \
             -place_global_cong_effort high \
             -place_global_ignore_scan true \
             -place_global_place_io_pins false
setOptMode   -addInstancePrefix PLC_ -maxDensity 0.80

place_opt_design
addTieHiLo -cell $CELL(tie) -prefix TIE_

checkPlace $R/checkPlace.rpt
reportCongestion -hotSpot > $R/congestion.rpt
timeDesign -preCTS -outDir $R/timing -prefix preCTS
saveDesign $DB/04_place.enc
