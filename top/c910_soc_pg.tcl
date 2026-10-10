# AUTO-GENERATED boi top (emit_top.py) -- spec v1.0. Doi gi thi sinh lai, khong sua tay.

# Luoi nguon TOP. Phan lop:
#   block : metal1 rail, metal4 doc (56), metal7 ngang (40, tam VDD y=9.67+40k / VSS 29.67+40k tuong doi goc block)
#   top   : ring metal9/metal10 quanh core; metal8 doc pitch 40 phu CA DIE (de len block, via xuong metal7 cua block);
#           metal9 ngang pitch 80; vung std cell cua top (kenh + vung logic top) dung lai luat cua block.
set NETS {VDD VSS}
globalNetConnect VDD -type pgpin -pin VDD -all -override
globalNetConnect VSS -type pgpin -pin VSS -all -override
globalNetConnect VDD -type tiehi -all -override
globalNetConnect VSS -type tielo -all -override
# 1) ring quanh core (nam trong le 19.95/19.6 giua die va core)
addRing -nets $NETS -type core_rings -follow core -layer {top metal9 bottom metal9 left metal10 right metal10} \
  -width {top 5 bottom 5 left 5 right 5} -spacing {top 2 bottom 2 left 2 right 2} -offset {top 2 bottom 2 left 2 right 2}
# 2) rail metal1 cho std cell cua top (chi co row o kenh va vung logic top, da cutRow duoi block)
sroute -connect {corePin} -nets $NETS -corePinTarget {firstAfterRowEnd} -allowJogging 0 -allowLayerChange 1 -layerChangeRange {metal1 metal10}
# 3) metal4 + metal7 cho vung std cell top (addStripe tu bo qua vung bi macro/block chan)
setAddStripeMode -stacked_via_bottom_layer metal1 -stacked_via_top_layer metal10
# chi trong vung std cell cua top (top/top_stdcell_areas.csv) -- KHONG chay metal4/metal7 cua top len block
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {74.8 19.6 3521.71 73.4}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {74.8 19.6 3521.71 73.4}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {19.95 19.6 74.8 5042.8}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {19.95 19.6 74.8 5042.8}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {3521.71 19.6 3581.69 5042.8}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {3521.71 19.6 3581.69 5042.8}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {74.8 1931.4 1441.59 1966.2}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {74.8 1931.4 1441.59 1966.2}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {1473.96 1931.4 1598.455 1966.2}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {1473.96 1931.4 1598.455 1966.2}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {1998.055 1931.4 2122.55 1966.2}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {1998.055 1931.4 2122.55 1966.2}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {2154.92 1931.4 3521.71 1966.2}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {2154.92 1931.4 3521.71 1966.2}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {1441.59 1931.4 1473.96 2306.55}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {1441.59 1931.4 1473.96 2306.55}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {1441.59 3636.03 1473.96 5042.8}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {1441.59 3636.03 1473.96 5042.8}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {2122.55 1931.4 2154.92 2306.55}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {2122.55 1931.4 2154.92 2306.55}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {2122.55 3636.03 2154.92 5042.8}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {2122.55 3636.03 2154.92 5042.8}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {74.8 4216.2 182.495 4251.0}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {74.8 4216.2 182.495 4251.0}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {1408.655 4216.2 1441.59 4251.0}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {1408.655 4216.2 1441.59 4251.0}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {2154.92 4216.2 2187.855 4251.0}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {2154.92 4216.2 2187.855 4251.0}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {3414.015 4216.2 3521.71 4251.0}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {3414.015 4216.2 3521.71 4251.0}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {1473.96 4216.2 2122.55 5042.8}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {1473.96 4216.2 2122.55 5042.8}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {74.8 4989.0 1441.59 5042.8}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {74.8 4989.0 1441.59 5042.8}
addStripe -nets $NETS -layer metal4 -direction vertical -width 0.48 -spacing 27.52 -set_to_set_distance 56 -start_from left -start_offset 2 -area {2154.92 4989.0 3521.71 5042.8}
addStripe -nets $NETS -layer metal7 -direction horizontal -width 1.4 -spacing 18.6 -set_to_set_distance 40 -start_from bottom -start_offset 2 -area {2154.92 4989.0 3521.71 5042.8}
# 4) metal8 doc phu ca die, metal9 ngang -- via chi xuong toi metal7 (khong cam via xuyen qua kenh/hanh lang)
setAddStripeMode -stacked_via_bottom_layer metal7 -stacked_via_top_layer metal10
addStripe -nets $NETS -layer metal8 -direction vertical -width 2.0 -spacing 18.0 -set_to_set_distance 40.0 -start_from left -start_offset 100.0
addStripe -nets $NETS -layer metal9 -direction horizontal -width 2.0 -spacing 38.0 -set_to_set_distance 80.0 -start_from bottom -start_offset 140.0
# 5) via metal7 (PG pin cua block) <-> metal8 cua top tai moi giao diem
editPowerVia -add_vias 1 -bottom_layer metal7 -top_layer metal8 -nets $NETS
verifyConnectivity -type special -nets $NETS -noAntenna -report top_pg_connectivity.rpt
puts "PG-TOP: xong"
