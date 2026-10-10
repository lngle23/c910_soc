################################################################################
# Makefile goc cua c910_soc_spec.   make help
# Moi nguoi thuong lam trong thu muc cua minh: blocks/fe, blocks/be, blocks/ciu, blocks/l2c, top
################################################################################
BLKS := fe be ciu l2c
.PHONY: help syn-all pnr-all check-env
help:
	@echo "  cd blocks/<fe|be|ciu|l2c> && make help    (block owner)"
	@echo "  cd top && make help                      (top owner)"
	@echo "  make check-env    kiem tra genus/innovus/python3 co trong PATH"
	@echo "  make syn-all      synthesis ca 4 block lan luot (lau, BE la lau nhat)"
	@echo "  make pnr-all      PnR ca 4 block lan luot"
check-env:
	@for t in genus innovus python3; do printf "%-8s " $$t; command -v $$t || echo "KHONG THAY"; done
syn-all:
	@for b in $(BLKS); do $(MAKE) -C blocks/$$b syn || exit 1; done
pnr-all:
	@for b in $(BLKS); do $(MAKE) -C blocks/$$b pnr || exit 1; done
