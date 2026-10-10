# c910_soc_spec v1.0: spec chia openC910 cho 5 người (1 top + 4 block)

Đọc `SPEC.md` trước (bản giống tài liệu spec online). Thư mục này chứa mọi file mà spec nhắc tới.

```
Makefile                    make check-env / syn-all / pnr-all
rtl/C910_RTL_FACTORY/       RTL openC910 gốc (440 file trong filelist) + LICENSE_openc910
pdk/nangate45/              Nangate45: lef tech/stdcell, lib typ/fast/slow + LICENSE
deliver/                    nơi block owner giao file cho top (make deliver)
SPEC.md                     spec đầy đủ: phân chia, floorplan, pin, PG, clock, timing, macro, bàn giao
common/
  floorplan_soc.png/.svg    hình floorplan toàn chip
  rtl/c910_soc_rtl.f        filelist RTL cho 4 block (dùng ${C910_RTL} và ${SPEC})
  make/block.mk top.mk      phần chung của Makefile; blocks/<blk>/Makefile và top/Makefile chỉ include
  rtl/c910_top_only_rtl.f   filelist cho top (không có RTL của 4 block)
  rtl/ct_top.v c910_be.v    ct_top sinh lại (FE + BE) và wrapper BE mới
  rtl/gated_clk_cell.v BUFGCE.v   bản ASIC (ICG CLKGATETST_X1)
  mem/lef lib wrap          15 macro SRAM fakeram45_<D>x<W> + wrapper ct_f_spsram 1:1
  scripts/syn_genus.tcl     synthesis Genus 19.1 cho 1 block hoặc top
  scripts/check_lef_vs_spec.py    top dùng để nghiệm thu LEF block giao
blocks/fe   (ct_ifu_top)    blocks/be (c910_be)    blocks/ciu (ct_ciu_top)    blocks/l2c (ct_l2c_top)
  <module>.sdc              ngân sách timing
  <module>_fp.tcl           floorPlan + pin + chặn metal8-10 + macro gợi ý + halo + cutRow
  <module>_pins.tcl/.def    vị trí từng pin;  <module>_ports.csv: bảng tra cứu (partner, budget)
  <module>_pg.tcl           lưới nguồn (offset metal7 cố định)
  <module>_macros.csv / _macro_suggest.tcl
  <module>_prelim.lef/.lib  abstract + budget model sơ bộ (top dùng)
top/
  c910_soc_fp.tcl           die + đặt 6 instance block + vùng logic top + IO
  c910_soc_io_pins.tcl/.csv 1336 IO
  c910_soc_pg.tcl           ring metal9/10, metal8/9 toàn die, metal4/7 trong kênh, via xuống metal7 block
  c910_soc.sdc              SDC chip (giống SDC synthesis openC910)
  lef/ lib/                 abstract + budget model sơ bộ của 4 block
  block_placement.csv  top_stdcell_areas.csv
  pnr/                      flow PnR chung cho block (01..09, run_all.tcl), dựa trên flow LSU
top/top_init.tcl            đọc design top (netlist chip + LEF/lib 4 block + MMMC)
top/wire_corridors.csv, c910_soc_corridors.tcl   5 hành lang dây giữa các cặp pin thẳng hàng
tools/                      script đã sinh ra spec (tham khảo; chạy lại cần slang + RTL gốc)
```

## Chạy (Makefile)

Gói này tự đủ: RTL openC910 (`rtl/`), Nangate45 (`pdk/`), macro SRAM (`common/mem/`). Không cần đặt biến môi trường;
chỉ cần `genus`, `innovus`, `python3` trong PATH (`make check-env` ở thư mục gốc để kiểm tra).

**Block owner** (thay `fe` bằng `be`, `ciu`, `l2c`):
```sh
cd c910_soc_spec/blocks/fe
make help
make syn          # Genus -> work/syn_ct_ifu_top/ ; log phải có "SYN-CHECK: PASS" và "SYN-DONE"
make pnr          # Innovus 01..09, mỗi bước 1 phiên batch, dừng ngay khi lỗi -> work/db, work/reports, work/outputs
make 05           # chỉ chạy 1 bước (cần checkpoint bước trước)
make pnr FROM=04  # chạy từ bước 04 tới 09
make gui STEP=04  # mở GUI xem checkpoint bước 04
make deliver      # nghiệm thu LEF với spec rồi chép LEF/ETM/netlist/DEF/SPEF vào deliver/ct_ifu_top/
```
Không đổi kích thước block, vị trí pin, strap metal7. Log từng bước: `work/logs/<bước>.log`.

**Top owner**:
```sh
cd c910_soc_spec/top
make collect      # lấy LEF/lib 4 block: bản đã giao trong deliver/ nếu có, chưa có thì bản sơ bộ
make syn          # synthesis openC910 (4 block là cell trong lib)
make fp           # Innovus: die, đặt 6 block, IO, hành lang dây, PG -> work/db/top_fp.enc
make gui
make check        # nghiệm thu LEF các block đã giao
```
Top KHÔNG phải chờ block: lần đầu dùng bản sơ bộ (budget model). Khi block giao, chạy lại `make collect`
rồi `make syn` (tuỳ chọn, để tối ưu logic top theo timing thật) và STA/PnR top với ETM + LEF thật.

Muốn dùng RTL/PDK ở chỗ khác: `make syn C910_RTL=... PDK=...`.

## Đã kiểm

- RTL `ct_top.v` + `c910_be.v` mới: elaborate lại toàn chip, 39.330/39.330 net khớp từng bit với RTL gốc.
- Filelist spec elaborate được openC910: 82 macro, 6983 ICG; tên 82 instance macro khớp hierarchy.
- Pin: mọi cặp net giữa hai block thẳng hàng (FE↔BE 1822, BE↔CIU 863×2, CIU↔L2C 2842), không trùng chỗ, tất cả trên track.
- Macro gợi ý không chồng lấn, giữ halo 10 µm; LEF/LIB/wrapper SRAM khớp nhau.
- Mọi pin nằm trên track của top ở cả 6 instance, kể cả 2 instance lật MY (0/18.463 lệch).
- Mọi script Tcl (spec, flow PnR chung, top_init, Genus) chạy qua Innovus/Genus giả lập: 0 lỗi, mọi file tham chiếu đều tồn tại. Chưa chạy trên tool thật.
- Makefile: chạy thử trọn syn → pnr 01..09 → deliver → top collect/syn/fp/check với tool giả, trên bản giải nén ở thư mục khác.
- Đã qua một vòng rà soát độc lập; các lỗi tìm được đã sửa (lưới đặt core1, hành lang dây, lib AXI, latency trước CTS, CTS clock BE→FE, option LEF abstract, flow PnR/MMMC).
