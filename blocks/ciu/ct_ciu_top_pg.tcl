# AUTO-GENERATED boi top (emit_spec.py) tu ket noi RTL da elaborate -- KHONG sua tay.
# Muon doi: bao nguoi lam top, top sinh lai va phat hanh version moi.

# ct_ciu_top: luoi nguon theo spec v1.0. Top se dat metal8 doc qua block va noi xuong STRAP METAL7 cua block.
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
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56.0 -start_from left -start_offset 2.0 -area {0 1.4 638.59 2238.6}
# 3) metal7 ngang, CO DINH: tam VDD y=9.67+40.0k, tam VSS y=29.67+40.0k, rong 1.4, keo het be rong block
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 8.970 638.59 10.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 28.970 638.59 30.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 48.970 638.59 50.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 68.970 638.59 70.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 88.970 638.59 90.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 108.970 638.59 110.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 128.970 638.59 130.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 148.970 638.59 150.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 168.970 638.59 170.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 188.970 638.59 190.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 208.970 638.59 210.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 228.970 638.59 230.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 248.970 638.59 250.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 268.970 638.59 270.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 288.970 638.59 290.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 308.970 638.59 310.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 328.970 638.59 330.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 348.970 638.59 350.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 368.970 638.59 370.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 388.970 638.59 390.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 408.970 638.59 410.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 428.970 638.59 430.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 448.970 638.59 450.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 468.970 638.59 470.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 488.970 638.59 490.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 508.970 638.59 510.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 528.970 638.59 530.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 548.970 638.59 550.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 568.970 638.59 570.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 588.970 638.59 590.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 608.970 638.59 610.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 628.970 638.59 630.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 648.970 638.59 650.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 668.970 638.59 670.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 688.970 638.59 690.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 708.970 638.59 710.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 728.970 638.59 730.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 748.970 638.59 750.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 768.970 638.59 770.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 788.970 638.59 790.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 808.970 638.59 810.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 828.970 638.59 830.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 848.970 638.59 850.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 868.970 638.59 870.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 888.970 638.59 890.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 908.970 638.59 910.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 928.970 638.59 930.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 948.970 638.59 950.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 968.970 638.59 970.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 988.970 638.59 990.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1008.970 638.59 1010.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1028.970 638.59 1030.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1048.970 638.59 1050.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1068.970 638.59 1070.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1088.970 638.59 1090.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1108.970 638.59 1110.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1128.970 638.59 1130.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1148.970 638.59 1150.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1168.970 638.59 1170.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1188.970 638.59 1190.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1208.970 638.59 1210.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1228.970 638.59 1230.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1248.970 638.59 1250.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1268.970 638.59 1270.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1288.970 638.59 1290.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1308.970 638.59 1310.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1328.970 638.59 1330.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1348.970 638.59 1350.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1368.970 638.59 1370.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1388.970 638.59 1390.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1408.970 638.59 1410.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1428.970 638.59 1430.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1448.970 638.59 1450.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1468.970 638.59 1470.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1488.970 638.59 1490.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1508.970 638.59 1510.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1528.970 638.59 1530.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1548.970 638.59 1550.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1568.970 638.59 1570.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1588.970 638.59 1590.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1608.970 638.59 1610.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1628.970 638.59 1630.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1648.970 638.59 1650.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1668.970 638.59 1670.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1688.970 638.59 1690.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1708.970 638.59 1710.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1728.970 638.59 1730.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1748.970 638.59 1750.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1768.970 638.59 1770.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1788.970 638.59 1790.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1808.970 638.59 1810.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1828.970 638.59 1830.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1848.970 638.59 1850.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1868.970 638.59 1870.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1888.970 638.59 1890.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1908.970 638.59 1910.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1928.970 638.59 1930.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1948.970 638.59 1950.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 1968.970 638.59 1970.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 1988.970 638.59 1990.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 2008.970 638.59 2010.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 2028.970 638.59 2030.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 2048.970 638.59 2050.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 2068.970 638.59 2070.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 2088.970 638.59 2090.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 2108.970 638.59 2110.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 2128.970 638.59 2130.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 2148.970 638.59 2150.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 2168.970 638.59 2170.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 2188.970 638.59 2190.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VDD -layer metal7 -direction horizontal -width 1.4 -area {0 2208.970 638.59 2210.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
addStripe -nets VSS -layer metal7 -direction horizontal -width 1.4 -area {0 2228.970 638.59 2230.370} -set_to_set_distance 40.0 -start_from bottom -start_offset 0
verifyConnectivity -type special -nets $NETS -noAntenna -report ct_ciu_top_pg_connectivity.rpt
puts "PG-SPEC: ct_ciu_top xong"
