################################################################################
# 08_route_opt.tcl -- toi uu sau route: setup, hold, DRV
################################################################################
#==== Common setting =========================================================
source [file join [file dirname [info script]] 00_setup.tcl]
# Chua co design trong phien nay (chay rieng step) -> doc checkpoint step truoc
if {[catch {dbGet top.name} top] || $top ne $DESIGN} { restoreDesign $DB/07_route.enc.dat $DESIGN }
source $SCRIPTS/settings.tcl
#=============================================================================
set R $RPT/08_route_opt; file mkdir $R

setExtractRCMode -engine postRoute -effortLevel low
setOptMode -addInstancePrefix RTO_

optDesign -postRoute       -outDir $R/opt_setup
optDesign -postRoute -hold -outDir $R/opt_hold
optDesign -postRoute -drv  -outDir $R/opt_drv

verify_drc -limit 100000 -report $R/drc.rpt
timeDesign -postRoute       -outDir $R/timing      -prefix postRoute
timeDesign -postRoute -hold -outDir $R/timing_hold -prefix postRoute_hold
saveDesign $DB/08_route_opt.enc
