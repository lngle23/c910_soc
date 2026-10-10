################################################################################
# mmmc.tcl -- Multi-Mode Multi-Corner cho Innovus 19.1 (legacy UI)
# Duoc init_design doc; dung bien toan cuc ::LIB_TYP / ::LIB_FAST / ::SDC tu 00_setup.tcl.
#
#   AV_SETUP : typical 1.10V 25C  -> toi uu + kiem setup
#   AV_HOLD  : std cell fast 1.25V 0C + macro typical -> sua + kiem hold
# Nangate45 khong co QRC/captable -> rc corner chi co nhiet do; tool dung RC trong tech LEF.
################################################################################
create_library_set  -name LS_TYP  -timing $::LIB_TYP
create_library_set  -name LS_FAST -timing $::LIB_FAST

create_rc_corner    -name RC_TYP  -T 25
create_rc_corner    -name RC_FAST -T 0

create_delay_corner -name DC_TYP  -library_set LS_TYP  -rc_corner RC_TYP
create_delay_corner -name DC_FAST -library_set LS_FAST -rc_corner RC_FAST

create_constraint_mode -name CM_FUNC -sdc_files [list $::SDC]

create_analysis_view -name AV_SETUP -constraint_mode CM_FUNC -delay_corner DC_TYP
create_analysis_view -name AV_HOLD  -constraint_mode CM_FUNC -delay_corner DC_FAST

set_analysis_view -setup [list AV_SETUP] -hold [list AV_HOLD]
