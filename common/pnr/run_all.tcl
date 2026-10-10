# innovus -init $SPEC/common/pnr/run_all.tcl -log pnr_$BLOCK   (chay trong thu muc lam viec cua block)
set S [file normalize [file dirname [info script]]]
foreach f {01_read_design 02_floorplan 03_powerplan 04_place 05_cts 06_cts_opt 07_route 08_route_opt 09_finish} { source $S/$f.tcl }
