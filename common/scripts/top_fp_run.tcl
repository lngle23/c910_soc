# make fp (top): doc design, floorplan die + 6 block + IO + hanh lang day, PG toan chip, luu db/top_fp.enc
source [file join $::env(SPEC) top top_init.tcl]
source $::env(SPEC)/top/c910_soc_fp.tcl
source $::env(SPEC)/top/c910_soc_pg.tcl
checkFPlan -reportUtil -outFile top_checkFPlan.rpt
file mkdir db
saveDesign db/top_fp.enc
puts "TOP-FP-DONE"
