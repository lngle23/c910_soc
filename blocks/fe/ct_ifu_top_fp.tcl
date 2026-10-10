# AUTO-GENERATED boi top (emit_spec.py) tu ket noi RTL da elaborate -- KHONG sua tay.
# Muon doi: bao nguoi lam top, top sinh lai va phat hanh version moi.

# ct_ifu_top floorplan theo spec v1.0. Dung SAU init_design (legacy UI, Innovus 19.1).
set _SPEC_DIR [file dirname [info script]]
# Kich thuoc block = kich thuoc top cap (khong duoc doi): 1356.79 x 728 um
floorPlan -site FreePDK45_38x28_10R_NP_162NW_34O -b {0 0 1356.79 728  0 0 1356.79 728  2.09 2.8 1354.7 725.2}
source [file join $_SPEC_DIR ct_ifu_top_pins.tcl]
# metal8..metal10 thuoc ve top (PG + route tren block) -> cam trong block
createRouteBlk -box {0 0 1356.79 728} -layer {metal8 metal9 metal10} -name TOP_ONLY_LAYERS
setNanoRouteMode -routeTopRoutingLayer 7 -routeBottomRoutingLayer 2
setRouteMode -earlyGlobalMaxRouteLayer 7 -earlyGlobalMinRouteLayer 2
# Giu 1 dai 1.4um sat bien khong dat std cell (cho pin + PG)
createPlaceBlockage -box {0 0 1356.79 4.199999999999999} -type hard -name EDGE_B
createPlaceBlockage -box {0 723.8 1356.79 728} -type hard -name EDGE_T
# Macro: dung vi tri goi y (co the thay bang vi tri cua ban)
source [file join $_SPEC_DIR ct_ifu_top_macro_suggest.tcl]
addHaloToBlock 10 10 10 10 -allBlock
cutRow
puts "FP-SPEC: ct_ifu_top 1356.79x728 xong"
