/**
 * @id py-qs/str-constraint
 * @severity warning
 * @precision low
 * @description just a simple test ql file for str constraint
 * @kind problem
 */

import call.call
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

predicate inner_contraint(CallNode sink, CallNode cn) {
  exists(DataFlow::CallCfgNode ccn, DataFlow::CallCfgNode sink_ccn, int i |
    TaintTracking::localTaint(ccn, sink_ccn.getArg(i))
  |
    sink_ccn.asCfgNode() = sink and ccn.asCfgNode() = cn
  )
}

predicate simple_match(Function f, CallNode cn) { f.getQualifiedName() = print_function(cn) }

predicate return_constraint(Function f, CallNode cn) {
  exists(Variable v, DataFlow::Node vn, DataFlow::Node rn, Return r |
    v.getScope() = f and
    r.getScope() = f and
    v.getAUse() = vn.asCfgNode() and
    DataFlow::localFlow(vn, rn) and
    r.getValue().getAFlowNode() = rn.asCfgNode()
  |
    cn.getFunction().getAChild() = v.getAUse()
  )
}

CallNode l1_constraint(CallNode sink) {
  exists(CallNode cn | inner_contraint(sink, cn) |
    cn.getFunction().(AttrNode).getName() = getStrFuncName() and result = cn
    or
    not cn.getFunction().(AttrNode).getName() = getStrFuncName() and
    exists(Function f, CallNode l1_cn | simple_match(f, cn) and return_constraint(f, l1_cn) |
      result = l1_cn
    )
  )
}

from Source s
where exists(l1_constraint(s.getCallee()))
select s, "$@", s.getCallee(),
  s.getPathStr() + "@@" +
    concat(CallNode cn |
      cn = l1_constraint(s.getCallee())
    |
      print_function(cn) + "#" + locStr(cn.getLocation()), "~"
    )
