################################################################################
# 06_cts_opt.tcl -- toi uu sau CTS: setup roi hold
################################################################################
#==== Common setting =========================================================
source [file join [file dirname [info script]] 00_setup.tcl]
# Chua co design trong phien nay (chay rieng step) -> doc checkpoint step truoc
if {[catch {dbGet top.name} top] || $top ne $DESIGN} { restoreDesign $DB/05_cts.enc.dat $DESIGN }
source $SCRIPTS/settings.tcl
#=============================================================================
set R $RPT/06_cts_opt; file mkdir $R

setOptMode -addInstancePrefix CTO_

optDesign -postCTS       -outDir $R/opt_setup
optDesign -postCTS -hold -outDir $R/opt_hold

checkPlace $R/checkPlace.rpt
timeDesign -postCTS       -outDir $R/timing      -prefix postCTS
timeDesign -postCTS -hold -outDir $R/timing_hold -prefix postCTS_hold
saveDesign $DB/06_cts_opt.enc
