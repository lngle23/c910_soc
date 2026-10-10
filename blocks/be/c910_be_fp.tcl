# AUTO-GENERATED boi top (emit_spec.py) tu ket noi RTL da elaborate -- KHONG sua tay.
# Muon doi: bao nguoi lam top, top sinh lai va phat hanh version moi.

# c910_be floorplan theo spec v1.0. Dung SAU init_design (legacy UI, Innovus 19.1).
set _SPEC_DIR [file dirname [info script]]
# Kich thuoc block = kich thuoc top cap (khong duoc doi): 1356.79 x 2240 um
floorPlan -site FreePDK45_38x28_10R_NP_162NW_34O -b {0 0 1356.79 2240  0 0 1356.79 2240  2.09 2.8 1354.7 2237.2}
source [file join $_SPEC_DIR c910_be_pins.tcl]
# metal8..metal10 thuoc ve top (PG + route tren block) -> cam trong block
createRouteBlk -box {0 0 1356.79 2240} -layer {metal8 metal9 metal10} -name TOP_ONLY_LAYERS
setNanoRouteMode -routeTopRoutingLayer 7 -routeBottomRoutingLayer 2
setRouteMode -earlyGlobalMaxRouteLayer 7 -earlyGlobalMinRouteLayer 2
# Giu 1 dai 1.4um sat bien khong dat std cell (cho pin + PG)
createPlaceBlockage -box {0 0 1356.79 4.199999999999999} -type hard -name EDGE_B
createPlaceBlockage -box {0 2235.8 1356.79 2240} -type hard -name EDGE_T
# Macro: dung vi tri goi y (co the thay bang vi tri cua ban)
source [file join $_SPEC_DIR c910_be_macro_suggest.tcl]
addHaloToBlock 10 10 10 10 -allBlock
cutRow
puts "FP-SPEC: c910_be 1356.79x2240 xong"
