# AUTO-GENERATED boi top (emit_spec.py) tu ket noi RTL da elaborate -- KHONG sua tay.
# Muon doi: bao nguoi lam top, top sinh lai va phat hanh version moi.

# ct_l2c_top: luoi nguon theo spec v1.0. Top se dat metal8 doc qua block va noi xuong STRAP METAL7 cua block.
# BAT BUOC giu: lop, be rong, pitch, offset metal7 (top dua vao do de dat via). Duoc them strap, khong duoc bot.
set NETS {VDD VSS}
globalNetConnect VDD -type pgpin -pin VDD -all -override
globalNetConnect VSS -type pgpin -pin VSS -all -override
globalNetConnect VDD -type tiehi -all -override
globalNetConnect VSS -type tielo -all -override
# 1) rail metal1 theo row (khong co ring trong block)
sroute -connect {corePin} -nets $NETS -allowJogging 0 -allowLayerChange 0
# 2) metal4 doc: VDD/VSS cach nhau nua pitch, khong cham canh tren/duoi (pin metal4 o do)
setAddStripeMode -stacked_via_bottom_layer metal1 -stacked_via_top_layer metal7
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56.0 -start_from left -start_offset 2.0 -area {0 1.4 3436.91 1846.6}
# 3) metal7 ngang, CO DINH: tam VDD y=9.67+40.0k, tam VSS y=29.67+40.0k, rong 1.4, keo het be rong block
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 8.970 3436.91 10.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 28.970 3436.91 30.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 48.970 3436.91 50.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 68.970 3436.91 70.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 88.970 3436.91 90.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 108.970 3436.91 110.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 128.970 3436.91 130.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 148.970 3436.91 150.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 168.970 3436.91 170.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 188.970 3436.91 190.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 208.970 3436.91 210.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 228.970 3436.91 230.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 248.970 3436.91 250.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 268.970 3436.91 270.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 288.970 3436.91 290.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 308.970 3436.91 310.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 328.970 3436.91 330.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 348.970 3436.91 350.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 368.970 3436.91 370.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 388.970 3436.91 390.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 408.970 3436.91 410.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 428.970 3436.91 430.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 448.970 3436.91 450.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 468.970 3436.91 470.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 488.970 3436.91 490.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 508.970 3436.91 510.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 528.970 3436.91 530.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 548.970 3436.91 550.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 568.970 3436.91 570.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 588.970 3436.91 590.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 608.970 3436.91 610.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 628.970 3436.91 630.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 648.970 3436.91 650.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 668.970 3436.91 670.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 688.970 3436.91 690.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 708.970 3436.91 710.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 728.970 3436.91 730.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 748.970 3436.91 750.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 768.970 3436.91 770.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 788.970 3436.91 790.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 808.970 3436.91 810.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 828.970 3436.91 830.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 848.970 3436.91 850.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 868.970 3436.91 870.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 888.970 3436.91 890.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 908.970 3436.91 910.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 928.970 3436.91 930.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 948.970 3436.91 950.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 968.970 3436.91 970.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 988.970 3436.91 990.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1008.970 3436.91 1010.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1028.970 3436.91 1030.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1048.970 3436.91 1050.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1068.970 3436.91 1070.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1088.970 3436.91 1090.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1108.970 3436.91 1110.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1128.970 3436.91 1130.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1148.970 3436.91 1150.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1168.970 3436.91 1170.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1188.970 3436.91 1190.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1208.970 3436.91 1210.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1228.970 3436.91 1230.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1248.970 3436.91 1250.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1268.970 3436.91 1270.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1288.970 3436.91 1290.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1308.970 3436.91 1310.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1328.970 3436.91 1330.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1348.970 3436.91 1350.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1368.970 3436.91 1370.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1388.970 3436.91 1390.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1408.970 3436.91 1410.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1428.970 3436.91 1430.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1448.970 3436.91 1450.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1468.970 3436.91 1470.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1488.970 3436.91 1490.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1508.970 3436.91 1510.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1528.970 3436.91 1530.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1548.970 3436.91 1550.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1568.970 3436.91 1570.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1588.970 3436.91 1590.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1608.970 3436.91 1610.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1628.970 3436.91 1630.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1648.970 3436.91 1650.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1668.970 3436.91 1670.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1688.970 3436.91 1690.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1708.970 3436.91 1710.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1728.970 3436.91 1730.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1748.970 3436.91 1750.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1768.970 3436.91 1770.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1788.970 3436.91 1790.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1808.970 3436.91 1810.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1828.970 3436.91 1830.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
# 4) tren moi macro: metal5 ngang + metal6 doc pitch 10 (noi strap metal4 trong macro len metal7)
# macro = instance co cell CLASS BLOCK (cach dem nay da chay dung tren Innovus 19.1 cua nhom: macros=11 o LSU)
set _macros [dbGet -p2 top.insts.cell.subClass block]
if {$_macros eq "0x0" || $_macros eq ""} { set _macros [dbGet -p2 top.insts.cell.baseClass block] }
if {$_macros eq "0x0"} { set _macros {} }
puts "PG-SPEC: [llength $_macros] macro"
foreach inst $_macros {
  set box [lindex [dbGet $inst.box] 0]
  addStripe -nets $NETS -layer metal5 -direction horizontal -area $box -width 0.93 -spacing 4.07 -set_to_set_distance 10.0 -start_from bottom -start_offset 2.0
  addStripe -nets $NETS -layer metal6 -direction vertical   -area $box -width 0.93 -spacing 4.07 -set_to_set_distance 10.0 -start_from left   -start_offset 2.0
}
sroute -connect {blockPin} -nets $NETS -blockPinTarget {nearestTarget} -allowLayerChange 1 -layerChangeRange {metal4 metal7}
verifyConnectivity -type special -nets $NETS -noAntenna -report ct_l2c_top_pg_connectivity.rpt
puts "PG-SPEC: ct_l2c_top xong"
