# settings.tcl -- common setting, source sau init_design / restoreDesign
setDesignMode   -process 45
setDelayCalMode -engine aae -siAware false
setAnalysisMode -analysisType onChipVariation -cppr both
foreach dc {DC_TYP DC_FAST} {
  set_timing_derate -delay_corner $dc -late  1.05
  set_timing_derate -delay_corner $dc -early 0.95
}
setRouteMode     -earlyGlobalMinRouteLayer 2 -earlyGlobalMaxRouteLayer $TOP_LAYER
setNanoRouteMode -routeBottomRoutingLayer 2 -routeTopRoutingLayer $TOP_LAYER
setOptMode -fixFanoutLoad true -setupTargetSlack 0 -holdTargetSlack 0 -holdFixingCells $CELL(hold_fix)
setTieHiLoMode -cell $CELL(tie) -maxFanout 8
foreach c $CELL(dont_use) { setDontUse $c true }
