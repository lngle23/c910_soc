#==== Common setting
source [file join [file dirname [info script]] 00_setup.tcl]
if {[catch {dbGet top.name} top] || $top ne $DESIGN} { restoreDesign $DB/04_place.enc.dat $DESIGN }
source $SCRIPTS/settings.tcl
set R $RPT/05_cts; file mkdir $R
set_ccopt_property buffer_cells       $CELL(cts_buf)
set_ccopt_property inverter_cells     $CELL(cts_inv)
set_ccopt_property clock_gating_cells $CELL(cts_icg)
set_ccopt_property target_max_trans   0.15
set_ccopt_property target_skew        0.10
create_route_type -name CLK_RT -bottom_preferred_layer metal4 -top_preferred_layer metal7
set_ccopt_property route_type CLK_RT -net_type trunk
set_ccopt_property route_type CLK_RT -net_type leaf
create_ccopt_clock_tree_spec -file $R/ccopt.spec
source $R/ccopt.spec
if {$DESIGN eq "c910_be"} {
  # Spec: BE lai clock cho FE qua port forever_cpuclk. Phia sau port con ~0.05 (day top) + 0.35 (FE) = 0.40 ns,
  # nen bao CCOpt coi port nay da co san 0.40 ns -> clock ra toi port som (~0.15 ns) de flop FE ngang flop BE.
  set_ccopt_property insertion_delay 0.40 -pin forever_cpuclk
}
ccopt_design -cts
report_ccopt_clock_trees -file $R/clock_trees.rpt
report_ccopt_skew_groups -file $R/skew_groups.rpt
timeDesign -postCTS       -outDir $R/timing      -prefix postCTS
timeDesign -postCTS -hold -outDir $R/timing_hold -prefix postCTS_hold
saveDesign $DB/05_cts.enc
