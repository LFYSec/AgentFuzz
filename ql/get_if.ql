/**
 * @id py-qs/bb-l7
 * @severity warning
 * @precision low
 * @description just a simple test ql file for if
 * @kind problem
 */

 import call.call
 import util.util
 
 class FunctionBlock extends BasicBlock {
   Function f;
 
   FunctionBlock() { this.getScope() = f }
 
   Function getFunction() { result = f }
 }
 
 class TestBlock extends FunctionBlock {
   If stmt;
   int n;
 
   TestBlock() {
     this.getNode(n) = stmt.getTest().getAFlowNode() and
     isIncludeLocation2(this.getScope().getLocation())
   }
 
   ControlFlowNode getTest() { result = stmt.getTest().getAFlowNode() }
 }
 
 predicate edges(BasicBlock bb, BasicBlock pred) {
   exists(TestBlock tb | pred = tb | bb.getAPredecessor*() = tb)
   or
   icfg_edge(pred, bb)
 }
 
 predicate icfg_edge(BasicBlock b1, BasicBlock b2) {
   exists(Source source, FunctionObject caller, FunctionObject callee|
     (b1.contains(source.getACallNode(caller, callee)))
   |
   b2.contains(source.getCallee())
   )
 }
 
 string locStr(Location loc) {
   result =
     loc.getFile().getAbsolutePath() + "#" + loc.getStartLine().toString() + ":" +
       loc.getStartColumn().toString() + "#" + loc.getEndLine().toString() + ":" +
       loc.getEndColumn().toString()
 }
 
 from BasicBlock bb, Source source, int n
 where
   isIncludeLocation2(bb.getScope().getLocation()) and
   source.getCallee() = bb.getNode(n)
 select bb, "$@", source,
   source.getPathStr() + "@@" + concat(TestBlock tb, Location loc |
     edges*(bb, tb) and loc = tb.getTest().getLocation()
   |
     tb.getFunction().getQualifiedName() + "#" + locStr(loc), "->"
   )
 