// conn.cpp -- trace bit-level connectivity between "unit" instances of an elaborated design.
// Units = instances whose definition name is in --unit list. Above-unit scopes are walked;
// their port connections / simple continuous assigns are merged with union-find; any other
// logic in an above-unit scope is reported as "glue@<scope>".
// Output (stdout):
//   EP <set> <kind> <path> <port> <bit> <dir>      kind = U(unit) | IO | G(glue)
//   NM <set> <scope> <name> <bit>                    a net name (in some scope) belonging to the set
#include "slang/driver/Driver.h"
#include "slang/ast/Compilation.h"
#include "slang/ast/ASTVisitor.h"
#include "slang/ast/EvalContext.h"
#include "slang/ast/symbols/InstanceSymbols.h"
#include "slang/ast/symbols/PortSymbols.h"
#include "slang/ast/symbols/MemberSymbols.h"
#include "slang/ast/symbols/BlockSymbols.h"
#include "slang/ast/expressions/AssignmentExpressions.h"
#include "slang/ast/expressions/MiscExpressions.h"
#include "slang/ast/expressions/SelectExpressions.h"
#include "slang/ast/expressions/OperatorExpressions.h"
#include "slang/ast/expressions/ConversionExpression.h"
#include "slang/ast/expressions/LiteralExpressions.h"
#include <cstdio>
#include <map>
#include <set>
#include <unordered_map>
#include <optional>
using namespace slang; using namespace slang::ast; using namespace slang::driver;

struct Key { int scope; const Symbol* sym; int bit;
  bool operator==(const Key& o) const { return scope==o.scope && sym==o.sym && bit==o.bit; } };
struct KH { size_t operator()(const Key& k) const { return std::hash<const void*>()(k.sym) ^ (size_t(k.scope) * 1000003u) ^ (size_t(k.bit) * 7919u); } };
std::unordered_map<Key, int, KH> ids; std::vector<int> par; std::vector<Key> keys;
int node(const Key& k) { auto it = ids.find(k); if (it != ids.end()) return it->second; int i = par.size(); ids[k] = i; par.push_back(i); keys.push_back(k); return i; }
int find(int x) { while (par[x] != x) { par[x] = par[par[x]]; x = par[x]; } return x; }
void uni(int a, int b) { a = find(a); b = find(b); if (a != b) par[a] = b; }

struct EP { int node; char kind; std::string path, port; int bit; const char* dir; };
std::vector<EP> eps; std::vector<std::pair<int,int>> consts;
std::vector<std::string> scopeNames;
std::set<std::string> unitDefs;
const Compilation* COMP;

static std::optional<int64_t> cint(const Expression& e, const Scope& sc) {
  if (auto c = e.getConstant(); c && c->isInteger()) return c->integer().as<int64_t>();
  ASTContext actx(sc, LookupLocation::max);
  EvalContext ctx(actx);
  auto v = e.eval(ctx);
  if (v.isInteger()) return v.integer().as<int64_t>();
  return std::nullopt;
}
static int symWidth(const Symbol& s) {
  if (auto vs = s.as_if<ValueSymbol>()) { auto& t = vs->getType(); if (t.isUnpackedArray()) return -1; return (int)t.getBitWidth(); }
  return -1;
}
// returns bits LSB first; -1 = constant/unknown bit. ok=false -> not bit-mappable
static std::vector<int> bits(const Expression& e, int sid, const Scope& sc, bool& ok) {
  std::vector<int> r;
  switch (e.kind) {
    case ExpressionKind::NamedValue: {
      auto& s = e.as<NamedValueExpression>().symbol; int w = symWidth(s);
      if (w <= 0) { ok = false; return r; }
      for (int i = 0; i < w; i++) r.push_back(node({sid, &s, i}));
      return r; }
    case ExpressionKind::RangeSelect: {
      auto& rs = e.as<RangeSelectExpression>();
      auto base = bits(rs.value(), sid, sc, ok); if (!ok) return r;
      auto& t = rs.value().type; if (!t->hasFixedRange()) { ok = false; return r; }
      auto rng = t->getFixedRange();
      auto L = cint(rs.left(), sc), R = cint(rs.right(), sc);
      if (!L || !R) { ok = false; return r; }
      int64_t lo, hi;
      if (rs.getSelectionKind() == RangeSelectionKind::Simple) { lo = std::min(*L, *R); hi = std::max(*L, *R); }
      else if (rs.getSelectionKind() == RangeSelectionKind::IndexedUp) { lo = *L; hi = *L + *R - 1; }
      else { hi = *L; lo = *L - *R + 1; }
      for (int64_t i = lo; i <= hi; i++) {
        int idx = rng.isDescending() ? (int)(i - rng.lower()) : (int)(rng.upper() - i);
        if (idx < 0 || idx >= (int)base.size()) { ok = false; return {}; }
        r.push_back(base[idx]);
      }
      if (!rng.isDescending()) std::reverse(r.begin(), r.end());
      return r; }
    case ExpressionKind::ElementSelect: {
      auto& es = e.as<ElementSelectExpression>();
      auto& t = es.value().type; if (!t->isIntegral() || !t->hasFixedRange()) { ok = false; return r; }
      auto base = bits(es.value(), sid, sc, ok); if (!ok) return r;
      auto rng = t->getFixedRange(); auto I = cint(es.selector(), sc);
      int ew = (int)e.type->getBitWidth();
      if (!I) { ok = false; return r; }
      int idx = rng.isDescending() ? (int)(*I - rng.lower()) : (int)(rng.upper() - *I);
      for (int k = 0; k < ew; k++) { int j = idx * ew + k; if (j < 0 || j >= (int)base.size()) { ok = false; return {}; } r.push_back(base[j]); }
      return r; }
    case ExpressionKind::Concatenation: {
      auto& c = e.as<ConcatenationExpression>();
      auto ops = c.operands();
      for (int i = (int)ops.size() - 1; i >= 0; i--) { auto b = bits(*ops[i], sid, sc, ok); if (!ok) return {}; r.insert(r.end(), b.begin(), b.end()); }
      return r; }
    case ExpressionKind::Replication: {
      auto& rp = e.as<ReplicationExpression>(); auto n = cint(rp.count(), sc); if (!n) { ok = false; return r; }
      auto b = bits(rp.concat(), sid, sc, ok); if (!ok) return {};
      for (int64_t k = 0; k < *n; k++) r.insert(r.end(), b.begin(), b.end());
      return r; }
    case ExpressionKind::Conversion: {
      auto& cv = e.as<ConversionExpression>();
      auto b = bits(cv.operand(), sid, sc, ok); if (!ok) return {};
      int w = (int)e.type->getBitWidth(); if (w <= 0) { ok = false; return {}; }
      b.resize(w, -2); return b; }
    case ExpressionKind::IntegerLiteral: case ExpressionKind::UnbasedUnsizedIntegerLiteral: {
      int w = (int)e.type->getBitWidth(); if (w <= 0) w = 1;
      auto c = e.getConstant();
      if (!c) { ASTContext actx(sc, LookupLocation::max); EvalContext ctx(actx); static ConstantValue keep; keep = e.eval(ctx); c = &keep; }
      if (c && c->isInteger()) { auto& v = c->integer(); for (int i = 0; i < w; i++) { auto b = v[i]; r.push_back(b.isUnknown() ? -1 : (b.value ? -3 : -2)); } }
      else r.assign(w, -1);
      return r; }
    case ExpressionKind::Assignment: {
      auto& a = e.as<AssignmentExpression>(); return bits(a.left(), sid, sc, ok); }
    case ExpressionKind::EmptyArgument: { ok = true; return r; }
    default: ok = false; return r;
  }
}
// mark every named value in expr as glue endpoint of scope sid
static void glueRefs(const Expression& e, int sid, const char* dir) {
  e.visit(makeVisitor([&](auto&, const NamedValueExpression& nv) {
    int w = symWidth(nv.symbol); if (w <= 0) return;
    for (int i = 0; i < w; i++) eps.push_back({node({sid, &nv.symbol, i}), 'G', scopeNames[sid], std::string(nv.symbol.name), i, dir});
  }));
}

static void walk(const InstanceSymbol& inst, const std::string& path, int sid) {
  const Scope& sc = inst.body;
  for (auto& m : sc.members()) {
    if (auto ci = m.as_if<InstanceSymbol>()) {
      std::string cdef(ci->getDefinition().name), cpath = path + "/" + std::string(ci->name);
      bool isUnit = unitDefs.count(cdef) > 0;
      bool hasKids = false;
      for (auto& mm : ci->body.members()) if (mm.kind == SymbolKind::Instance) { hasKids = true; break; }
      int csid = -1;
      if (!isUnit && hasKids) { csid = scopeNames.size(); scopeNames.push_back(cpath); }
      for (auto pc : ci->getPortConnections()) {
        auto ps = pc->port.as_if<PortSymbol>(); if (!ps) continue;
        const char* dir = ps->direction == ArgumentDirection::In ? "in" : ps->direction == ArgumentDirection::Out ? "out" : "inout";
        auto ex = pc->getExpression();
        std::vector<int> pb; bool ok = true;
        if (ex) pb = bits(*ex, sid, sc, ok);
        int pw = (int)ps->getType().getBitWidth();
        if (!ok) { if (ex) glueRefs(*ex, sid, ps->direction == ArgumentDirection::Out ? "drv" : "rd"); pb.assign(pw, -1); }
        pb.resize(pw, -1);
        for (int i = 0; i < pw; i++) {
          if (isUnit) {
            int n = pb[i] >= 0 ? pb[i] : node({-2 - (int)eps.size(), ps, i});  // unconnected / constant -> private node
            eps.push_back({n, 'U', cpath, std::string(ps->name), i, dir});
            if (pb[i] <= -2) consts.push_back({n, pb[i] == -3 ? 1 : 0});
          } else if (csid >= 0 && ps->internalSymbol) {
            int in = node({csid, ps->internalSymbol, i});
            if (pb[i] >= 0) uni(in, pb[i]); else if (pb[i] <= -2) consts.push_back({in, pb[i] == -3 ? 1 : 0});
          } else {  // leaf cell that is not a unit (gated_clk_cell, BUFGCE ...) -> glue of parent scope
            if (pb[i] >= 0) eps.push_back({pb[i], 'G', path, cdef + ":" + std::string(ps->name), i, dir});
          }
        }
      }
      if (csid >= 0) walk(*ci, cpath, csid);
    } else if (auto ca = m.as_if<ContinuousAssignSymbol>()) {
      auto& a = ca->getAssignment().as<AssignmentExpression>();
      bool ok1 = true, ok2 = true;
      auto l = bits(a.left(), sid, sc, ok1); auto r = bits(a.right(), sid, sc, ok2);
      if (ok1 && ok2 && l.size() == r.size()) {
        for (size_t i = 0; i < l.size(); i++) {
          if (l[i] >= 0 && r[i] >= 0) uni(l[i], r[i]);
          else if (l[i] >= 0) { if (r[i] <= -2) consts.push_back({l[i], r[i] == -3 ? 1 : 0}); else eps.push_back({l[i], 'G', path, "const", (int)i, "drv"}); }
        }
      } else { glueRefs(a.left(), sid, "drv"); glueRefs(a.right(), sid, "rd"); }
    } else if (auto pb = m.as_if<ProceduralBlockSymbol>()) {
      pb->getBody().visit(makeVisitor([&](auto& v, const AssignmentExpression& a) { glueRefs(a.left(), sid, "drv"); glueRefs(a.right(), sid, "rd"); },
                                      [&](auto&, const NamedValueExpression& nv) {
                                        int w = symWidth(nv.symbol); if (w <= 0) return;
                                        for (int i = 0; i < w; i++) eps.push_back({node({sid, &nv.symbol, i}), 'G', path, std::string(nv.symbol.name), i, "rd"}); }));
    }
  }
}

int main(int argc, char** argv) {
  Driver driver; driver.addStandardArgs();
  std::vector<std::string> units;
  driver.cmdLine.add("--unit", units, "unit definition names");
  if (!driver.parseCommandLine(argc, argv)) return 1;
  if (!driver.processOptions()) return 1;
  if (!driver.parseAllSources()) return 1;
  for (auto& u : units) unitDefs.insert(u);
  auto comp = driver.createCompilation(); COMP = comp.get();
  comp->getRoot();
  for (auto inst : comp->getRoot().topInstances) {
    std::string dn(inst->getDefinition().name);
    if (dn.rfind("ct_f_spsram", 0) == 0 || dn == "CLKGATETST_X1") continue;
    std::string p(inst->name);
    scopeNames.push_back(p);
    // top ports -> IO endpoints
    for (auto pm : inst->body.getPortList()) {
      auto ps = pm->as_if<PortSymbol>(); if (!ps || !ps->internalSymbol) continue;
      int w = (int)ps->getType().getBitWidth();
      const char* dir = ps->direction == ArgumentDirection::In ? "in" : ps->direction == ArgumentDirection::Out ? "out" : "inout";
      for (int i = 0; i < w; i++) eps.push_back({node({0, ps->internalSymbol, i}), 'I', p, std::string(ps->name), i, dir});
    }
    walk(*inst, p, 0);
  }
  for (auto& e : eps) printf("EP %d %c %s %s %d %s\n", find(e.node), e.kind, e.path.c_str(), e.port.c_str(), e.bit, e.dir);
  for (auto& c : consts) printf("CV %d %d\n", find(c.first), c.second);
  for (size_t i = 0; i < keys.size(); i++) if (keys[i].scope >= 0)
    printf("NM %d %s %s %d\n", find(i), scopeNames[keys[i].scope].c_str(), std::string(keys[i].sym->name).c_str(), keys[i].bit);
  return 0;
}
