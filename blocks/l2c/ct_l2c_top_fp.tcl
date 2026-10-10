# AUTO-GENERATED boi top (emit_spec.py) tu ket noi RTL da elaborate -- KHONG sua tay.
# Muon doi: bao nguoi lam top, top sinh lai va phat hanh version moi.

# ct_l2c_top floorplan theo spec v1.0. Dung SAU init_design (legacy UI, Innovus 19.1).
set _SPEC_DIR [file dirname [info script]]
# Kich thuoc block = kich thuoc top cap (khong duoc doi): 3436.91 x 1848 um
floorPlan -site FreePDK45_38x28_10R_NP_162NW_34O -b {0 0 3436.91 1848  0 0 3436.91 1848  2.09 2.8 3434.82 1845.2}
source [file join $_SPEC_DIR ct_l2c_top_pins.tcl]
# metal8..metal10 thuoc ve top (PG + route tren block) -> cam trong block
createRouteBlk -box {0 0 3436.91 1848} -layer {metal8 metal9 metal10} -name TOP_ONLY_LAYERS
setNanoRouteMode -routeTopRoutingLayer 7 -routeBottomRoutingLayer 2
setRouteMode -earlyGlobalMaxRouteLayer 7 -earlyGlobalMinRouteLayer 2
# Giu 1 dai 1.4um sat bien khong dat std cell (cho pin + PG)
createPlaceBlockage -box {0 0 3436.91 4.199999999999999} -type hard -name EDGE_B
createPlaceBlockage -box {0 1843.8 3436.91 1848} -type hard -name EDGE_T
# Macro: dung vi tri goi y (co the thay bang vi tri cua ban)
source [file join $_SPEC_DIR ct_l2c_top_macro_suggest.tcl]
addHaloToBlock 10 10 10 10 -allBlock
cutRow
puts "FP-SPEC: ct_l2c_top 3436.91x1848 xong"
