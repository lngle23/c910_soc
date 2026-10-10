# AUTO-GENERATED boi top (emit_top.py) -- spec v1.0. Doi gi thi sinh lai, khong sua tay.

# Floorplan TOP c910_soc (top module = openC910). Legacy UI, Innovus 19.1.
# Netlist top: openC910 synthesize bang common/scripts/syn_genus.tcl voi BLOCK=openC910 (4 block = cell trong top/lib/*_prelim.lib).
# Block duoc doc nhu macro tu LEF (ban prelim trong top/lef/, sau thay bang LEF that block giao).
set _TOP_DIR [file dirname [info script]]
# Die 3601.64 x 5062.4 um. Core = toan die tru le 19.95/19.6 (cho ring PG)
floorPlan -site FreePDK45_38x28_10R_NP_162NW_34O -b {0 0 3601.64 5062.4  0 0 3601.64 5062.4  19.95 19.6 3581.69 5042.8}
# --- dat 6 instance block (toa do = goc duoi-trai cua hop SAU khi lat). Luoi dat: x boi so 5.32, y boi so 11.2
placeInstance x_ct_l2c_top 79.8 78.4 R0 -fixed   ;# l2c (ct_l2c_top)
placeInstance x_ct_top_0/x_c910_be 79.8 1971.2 R0 -fixed   ;# core0_be (c910_be)
placeInstance x_ct_ciu_top 1478.96 1971.2 R0 -fixed   ;# ciu (ct_ciu_top)
placeInstance x_ct_top_1/x_c910_be 2159.92 1971.2 MY -fixed   ;# core1_be (c910_be)
placeInstance x_ct_top_0/x_ct_ifu_top 79.8 4256 R0 -fixed   ;# core0_fe (ct_ifu_top)
placeInstance x_ct_top_1/x_ct_ifu_top 2159.92 4256 MY -fixed   ;# core1_fe (ct_ifu_top)
# --- halo quanh block: khong dat cell top sat bien block
addHaloToBlock 5 5 5 5 -allBlock
cutRow
# --- logic rieng cua top dat trong vung giua phia tren (giua core0_fe va core1_fe)
createGuide x_plic_top 1478.96 4256 2117.55 4984
createGuide x_ct_clint_top 1478.96 4256 2117.55 4984
createGuide x_ct_sysio_top 1478.96 4256 2117.55 4984
createGuide x_ct_had_common_top 1478.96 4256 2117.55 4984
createGuide x_ct_mp_clk_top 1478.96 4256 2117.55 4984
createGuide x_ct_mp_rst_top 1478.96 4256 2117.55 4984
createGuide x_rmu_top 1478.96 4256 2117.55 4984
# --- hanh lang day giua 2 block (top/wire_corridors.csv): KHONG dat cell, KHONG strap PG cua top (chi de route thang)
source [file join $_TOP_DIR c910_soc_corridors.tcl]
# --- IO pin cua chip
source [file join $_TOP_DIR c910_soc_io_pins.tcl]
# --- top route metal2..metal10; tren block chi con metal8..metal10 (LEF block chan metal1..metal7)
setNanoRouteMode -routeTopRoutingLayer 10 -routeBottomRoutingLayer 2
puts "FP-TOP: xong"
