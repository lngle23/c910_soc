################################################################################
# block.mk -- Makefile chung cho 4 block cua c910_soc. Moi blocks/<blk>/Makefile chi dat BLOCK roi include file nay.
#   make help      xem cac lenh
################################################################################
_MK_DIR  := $(dir $(lastword $(MAKEFILE_LIST)))
SPEC     ?= $(abspath $(_MK_DIR)/../..)
C910_RTL ?= $(SPEC)/rtl/C910_RTL_FACTORY
PDK      ?= $(SPEC)/pdk/nangate45
NCPU     ?= 4
SHELL    := /bin/bash
WORK     ?= work
GENUS    ?= genus
INNOVUS  ?= innovus
BLKDIR   := $(notdir $(CURDIR))
export SPEC C910_RTL PDK BLOCK NCPU

PNR      := $(SPEC)/common/pnr
STEPS    := 01_read_design 02_floorplan 03_powerplan 04_place 05_cts 06_cts_opt 07_route 08_route_opt 09_finish
NETLIST  := $(WORK)/syn_$(BLOCK)/$(BLOCK).v

.PHONY: help syn pnr gui check deliver clean $(foreach s,$(STEPS),$(firstword $(subst _, ,$(s))))

help:
	@echo "Block $(BLOCK)   (SPEC=$(SPEC))"
	@echo "  make syn           synthesis Genus  -> $(WORK)/syn_$(BLOCK)/"
	@echo "  make pnr           PnR 01..09 (moi buoc 1 phien Innovus, dung ngay khi loi) -> $(WORK)/db, reports, outputs"
	@echo "  make 05            chi chay buoc 05 (tu doc checkpoint buoc 04)"
	@echo "  make pnr FROM=04   chay tu buoc 04 den 09"
	@echo "  make gui STEP=04   mo Innovus GUI voi checkpoint buoc 04"
	@echo "  make check         nghiem thu LEF abstract voi spec (check_lef_vs_spec.py)"
	@echo "  make deliver       chep file ban giao vao $(SPEC)/deliver/$(BLOCK)/ cho top"
	@echo "  make clean         xoa $(WORK)/"

$(WORK):
	mkdir -p $(WORK)

#---- synthesis
syn: | $(WORK)
	cd $(WORK) && $(GENUS) -files $(SPEC)/common/scripts/syn_genus.tcl -log syn_$(BLOCK)
	@grep -h "SYN-CHECK\|SYN-DONE" $(WORK)/syn_$(BLOCK).log || (echo "!!! synthesis khong xong, xem $(WORK)/syn_$(BLOCK).log"; exit 1)

#---- PnR: moi buoc 1 phien Innovus batch; buoc chi dat khi tao duoc checkpoint
define run_step
	@test -f $(NETLIST) || (echo "!!! chua co netlist $(NETLIST): chay make syn truoc"; exit 1)
	@$(if $(2),test -d $(WORK)/db/$(2).enc.dat || (echo "!!! chua co checkpoint $(2): chay buoc truoc ($(2)) truoc"; exit 1))
	@echo ">>> $(1)  $$(date +%H:%M:%S)"
	@rm -rf $(WORK)/db/$(1).enc $(WORK)/db/$(1).enc.dat
	cd $(WORK) && mkdir -p logs && $(INNOVUS) -no_gui -batch -files $(PNR)/$(1).tcl -log logs/$(1) > logs/$(1).stdout 2>&1 || true
	@test -d $(WORK)/db/$(1).enc.dat || (echo "!!! $(1) loi -- xem $(WORK)/logs/$(1).log:"; grep -m5 -n "^\*\*ERROR" $(WORK)/logs/$(1).log | grep -v IMPOAX; tail -15 $(WORK)/logs/$(1).log; exit 1)
	@echo "    $(1) xong -> $(WORK)/db/$(1).enc"
endef
PREV_01_read_design :=
PREV_02_floorplan   := 01_read_design
PREV_03_powerplan   := 02_floorplan
PREV_04_place       := 03_powerplan
PREV_05_cts         := 04_place
PREV_06_cts_opt     := 05_cts
PREV_07_route       := 06_cts_opt
PREV_08_route_opt   := 07_route
PREV_09_finish      := 08_route_opt
$(foreach s,$(STEPS),$(eval $(firstword $(subst _, ,$(s))): ; $$(call run_step,$(s),$(PREV_$(s)))))

FROM ?= 01
pnr:
	@for s in $(STEPS); do n=$${s%%_*}; [ $$((10#$$n)) -lt $$((10#$(FROM))) ] && continue; $(MAKE) --no-print-directory $$n || exit 1; done
	@echo "=== PnR xong. File ban giao: $(WORK)/outputs/"

STEP ?= 09
gui:
	cd $(WORK) && STEP_NAME=$(filter $(STEP)_%,$(STEPS)) $(INNOVUS) -init $(PNR)/gui_open.tcl -log logs/gui

#---- ban giao
check:
	python3 $(SPEC)/common/scripts/check_lef_vs_spec.py $(WORK)/outputs/$(BLOCK).lef \
	        $(CURDIR)/$(BLOCK)_ports.csv $(CURDIR)/$(BLOCK)_prelim.lef

deliver: check
	mkdir -p $(SPEC)/deliver/$(BLOCK)
	cp $(WORK)/outputs/$(BLOCK).lef $(WORK)/outputs/$(BLOCK)_setup.lib $(WORK)/outputs/$(BLOCK)_hold.lib \
	   $(WORK)/outputs/$(BLOCK).pnr.v $(WORK)/outputs/$(BLOCK).def $(WORK)/outputs/$(BLOCK).spef $(SPEC)/deliver/$(BLOCK)/
	@echo "Da giao: $(SPEC)/deliver/$(BLOCK)/"

clean:
	rm -rf $(WORK)
