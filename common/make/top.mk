################################################################################
# Makefile cua TOP (c910_soc, top module openC910).   make help
################################################################################
SPEC     ?= $(abspath $(CURDIR)/..)
C910_RTL ?= $(SPEC)/rtl/C910_RTL_FACTORY
PDK      ?= $(SPEC)/pdk/nangate45
NCPU     ?= 4
SHELL    := /bin/bash
WORK     ?= work
GENUS    ?= genus
INNOVUS  ?= innovus
BLOCK    := openC910
MODS     := ct_ifu_top c910_be ct_ciu_top ct_l2c_top
BLOCK_LEF_DIR := $(abspath $(WORK))/blocks/lef
BLOCK_LIB_DIR := $(abspath $(WORK))/blocks/lib
export SPEC C910_RTL PDK BLOCK NCPU BLOCK_LEF_DIR BLOCK_LIB_DIR

.PHONY: help collect syn fp gui check clean

help:
	@echo "Top c910_soc   (SPEC=$(SPEC))"
	@echo "  make collect   gom LEF/lib 4 block vao $(WORK)/blocks: ban da giao ($(SPEC)/deliver/<module>/) neu co, chua co thi ban so bo"
	@echo "  make syn       synthesis openC910 (4 block la cell trong lib o tren) -> $(WORK)/syn_openC910/"
	@echo "  make fp        Innovus: doc design, floorplan die, dat 6 block, IO, hanh lang day, PG -> $(WORK)/db/top_fp.enc"
	@echo "  make gui       mo GUI voi $(WORK)/db/top_fp.enc"
	@echo "  make check     nghiem thu LEF cac block da giao"
	@echo "  make clean"

collect:
	@mkdir -p $(BLOCK_LEF_DIR) $(BLOCK_LIB_DIR)
	@rm -f $(BLOCK_LEF_DIR)/*.lef $(BLOCK_LIB_DIR)/*.lib
	@for m in $(MODS); do d=$(SPEC)/deliver/$$m; \
	  if [ -f $$d/$$m.lef ] && [ -f $$d/$${m}_setup.lib ]; then \
	    cp $$d/$$m.lef $(BLOCK_LEF_DIR)/; cp $$d/$${m}_setup.lib $$d/$${m}_hold.lib $(BLOCK_LIB_DIR)/; echo "  $$m: BAN DA GIAO"; \
	  else \
	    cp $(SPEC)/top/lef/$${m}_prelim.lef $(BLOCK_LEF_DIR)/; cp $(SPEC)/top/lib/$${m}_prelim.lib $(BLOCK_LIB_DIR)/; echo "  $$m: ban so bo (budget model)"; \
	  fi; done

syn: collect
	cd $(WORK) && $(GENUS) -files $(SPEC)/common/scripts/syn_genus.tcl -log syn_openC910
	@grep -h "SYN-CHECK\|SYN-DONE" $(WORK)/syn_openC910.log || (echo "!!! synthesis top khong xong, xem $(WORK)/syn_openC910.log"; exit 1)

fp: collect
	@test -f $(WORK)/syn_openC910/openC910.v || (echo "!!! chua co netlist top: make syn truoc"; exit 1)
	cd $(WORK) && $(INNOVUS) -no_gui -batch -files $(SPEC)/top/top_fp_run.tcl -log top_fp > top_fp.stdout 2>&1 || true
	@grep -q TOP-FP-DONE $(WORK)/top_fp.log && echo "=== top fp xong -> $(WORK)/db/top_fp.enc" || (echo "!!! loi, xem $(WORK)/top_fp.log"; tail -15 $(WORK)/top_fp.log; exit 1)

gui:
	cd $(WORK) && $(INNOVUS) -init $(SPEC)/top/top_gui.tcl -log top_gui

check:
	@for m in $(MODS); do case $$m in ct_ifu_top) b=fe;; c910_be) b=be;; ct_ciu_top) b=ciu;; ct_l2c_top) b=l2c;; esac; \
	  f=$(SPEC)/deliver/$$m/$$m.lef; if [ -f $$f ]; then python3 $(SPEC)/common/scripts/check_lef_vs_spec.py $$f \
	  $(SPEC)/blocks/$$b/$${m}_ports.csv $(SPEC)/blocks/$$b/$${m}_prelim.lef; else echo "$$m: chua giao"; fi; done

clean:
	rm -rf $(WORK)
