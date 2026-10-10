################################################################################
# 07_route.tcl -- route chi tiet (NanoRoute), sua antenna
################################################################################
#==== Common setting =========================================================
source [file join [file dirname [info script]] 00_setup.tcl]
# Chua co design trong phien nay (chay rieng step) -> doc checkpoint step truoc
if {[catch {dbGet top.name} top] || $top ne $DESIGN} { restoreDesign $DB/06_cts_opt.enc.dat $DESIGN }
source $SCRIPTS/settings.tcl
#=============================================================================
set R $RPT/07_route; file mkdir $R

setNanoRouteMode -routeWithTimingDriven true \
                 -routeWithSiDriven false \
                 -drouteFixAntenna true \
                 -routeInsertAntennaDiode true \
                 -routeAntennaCellName $CELL(antenna) \
                 -drouteUseMultiCutViaEffort medium

routeDesign -globalDetail

verify_drc -limit 100000 -report $R/drc.rpt
verifyConnectivity -type regular -noAntenna -report $R/connectivity.rpt

# Khong co QRC cho Nangate45 -> extract bang RC trong tech LEF
setExtractRCMode -engine postRoute -effortLevel low
timeDesign -postRoute       -outDir $R/timing      -prefix postRoute
timeDesign -postRoute -hold -outDir $R/timing_hold -prefix postRoute_hold
saveDesign $DB/07_route.enc
