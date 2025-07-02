import python
import util.util

class Source extends PyFunctionObject {
  int depth;
  CallNode callee;

  Source() {
    depth = [1..10] and
    r_calls(this, callee, depth) and
    is_sink(callee) and
    isIncludeLocation2(this.getFunction().getLocation())
  }

  int getDepth() { result = depth }
  CallNode getCallee() { result = callee }
  // deprecated
  FunctionObject getSink() { result = callee }

  FunctionObject getAMid() {
    exists(FunctionObject mid, int k | find_mid(this, callee, mid, depth, k) | result = mid)
  }


  int getMidDepth(FunctionObject mid) {
    exists(int k | find_mid(this, callee, mid, depth, k) | result = k)
  }

  string getPathStr() {
   result = depth + "#" + 
   concat(FunctionObject mid, int k | 
       find_mid(this, callee, mid, depth, k) | 
       mid.getQualifiedName() + "@" + mid.getFunction().getLocation().getFile().getBaseName(), 
       "->" order by k) + 
   "->" + get_sink_location(callee)
  }

  CallNode getACallNode(FunctionObject mid, FunctionObject next) {
    exists(CallNode cn |
        this.getAMid() = mid and
        this.getAMid() = next and
        (
          calls_cn(mid, next, cn)
          or
          exists(FunctionInvocation fi | calls_fi(mid, next, fi) | fi.getCall() = cn)
        )
      |
        result = cn
    )
  }

  FunctionObject getAPrev(FunctionObject fo) {
    exists(FunctionObject mid | this.getAMid() = mid and calls(mid, fo) | result = mid)
  }
}



 predicate calls(FunctionObject caller, FunctionObject callee) {
   caller != callee and
   (
     exists(FunctionInvocation fi | fi.getCaller().getFunction() = caller |
       fi.getFunction() = callee
     )
     or
     method_calls(caller, callee, _)
     or
     direct_calls(caller, callee, _)
     or
     module_calls(caller, callee, _)
     or 
     add_calls(caller, callee, _)
   )
 }
 
 predicate call_node(FunctionObject caller, CallNode cn) {
  isIncludeLocation2(caller.getFunction().getLocation()) and
   caller.getFunction().getBody().getAnItem().getAChildNode+().getAFlowNode() = cn and
   not exists(Function inner | caller.getFunction().getBody().getAnItem().getAChildNode+() = inner |
     inner.getBody().getAnItem().getAChildNode+().getAFlowNode() = cn
   )
 }
 predicate definition_node(Function caller, DefinitionNode dn) {
  isIncludeLocation2(caller.getLocation()) and
  caller.getBody().getAnItem().getAChildNode+().getAFlowNode() = dn and
  not exists(Function inner | caller.getBody().getAnItem().getAChildNode+() = inner |
    inner.getBody().getAnItem().getAChildNode+().getAFlowNode() = dn
  )
}
 predicate method_calls(FunctionObject caller, FunctionObject callee, CallNode cn) {
   call_node(caller, cn) and
   exists(Class c | c.getAMethod() = caller.getFunction() and c.getAMethod() = callee.getFunction()) and
   exists(AttrNode an, NameNode nn |
     cn.getAChild() = an and an.getAChild() = nn and nn.getId() = "self"
   |
     an.getName() = callee.getName()
   )
 }
 
 predicate direct_calls(FunctionObject caller, FunctionObject callee, CallNode cn) {
  (call_node(caller, cn) and
  (callee.isBuiltin() or caller.getFunction().getEnclosingScope() = callee.getFunction().getEnclosingScope()) and
  exists(NameNode nn | cn.getAChild() = nn | nn.getId() = callee.getName())
  )
}
predicate add_calls(FunctionObject caller, FunctionObject callee, CallNode cn) {
  (call_node(caller, cn) and
  callee.getName() = "_sys_execute" and
  cn.getFunction().(AttrNode).getNode().getName() = "Process" and
  cn.getArgByName("target").(NameNode).getId() = callee.getName()
  )
}

 predicate module_calls(FunctionObject caller, FunctionObject callee, CallNode cn) {
   call_node(caller, cn) and
   exists(Class c |
     c.getAMethod() = caller.getFunction() and
     c.getEnclosingModule() = callee.getFunction().getEnclosingModule()
   ) and
   exists(NameNode nn | cn.getAChild() = nn | nn.getId() = callee.getName())
 }
 
 predicate r_calls(FunctionObject caller, CallNode callee, int depth) {
  depth = 1 and call_node(caller, callee)
  or
  depth = getDepthLimit() and
  exists(FunctionObject mid | calls(caller, mid) | r_calls(mid, callee, depth - 1))
 }


 predicate r_functionobject_calls(FunctionObject caller, FunctionObject callee, int depth) {
  depth = 1 and calls(caller, callee)
  or
  depth = getDepthLimit() and
  exists(FunctionObject mid | calls(caller, mid) | r_functionobject_calls(mid, callee, depth - 1))
 }


 bindingset[depth]
 predicate find_mid(FunctionObject caller, CallNode callee, FunctionObject mid, int depth, int k) {
   depth >= 1 and ( k = 0 and mid = caller) or (
     k > 0 and k < depth and r_functionobject_calls(caller, mid, k) and r_calls(mid, callee, depth-k)
   ) 
 }
 string getlocStr(Location loc) {
  result =
    loc.getFile().getAbsolutePath() + "$$" + loc.getStartLine().toString() + ":" +
      loc.getStartColumn().toString() + "$$" + loc.getEndLine().toString() + ":" +
      loc.getEndColumn().toString()
}

 string get_sink_location(CallNode callee){
  if not exists(AttrNode cn| cn = callee.getFunction().(AttrNode) | 1 = 1)
  then 
  result = callee.getFunction().getNode().toString() + "@" + getlocStr(callee.getLocation())
  else
    if exists(ControlFlowNode cn| cn = callee.getFunction().(AttrNode).getObject() | 1 = 1)
      then 
      result = callee.getFunction().(AttrNode).getObject().getNode().toString() + "." + callee.getFunction().(AttrNode).getNode().getName()  + "@" + getlocStr(callee.getLocation())
    else
      result = callee.getFunction().(AttrNode).getNode().getName()  + "@" + getlocStr(callee.getLocation())

 }



 bindingset[depth]
 string print_callchain(FunctionObject caller, CallNode callee, int depth) {
  result = depth + "#" + 
  concat(FunctionObject mid, int k | 
      find_mid(caller, callee, mid, depth, k) | 
      mid.getQualifiedName() + "@" + mid.getFunction().getLocation().getFile().getBaseName(), 
      "->" order by k) + 
  "->" + get_sink_location(callee)
 }

string print_function(CallNode cn) {
  exists(AttrNode fan | first_attrnode(cn.getFunction(), fan) |
    result =
      fan.getObject().(NameNode).getId() + "." +
        concat(AttrNode an |
          an = cn.getFunction().getAChild*()
        |
          an.getName(), "." order by an.getLocation().getEndColumn()
        )
  )
}

predicate first_attrnode(ControlFlowNode cfn, AttrNode an) {
  an = cfn.getAChild*() and
  an.getLocation().getEndColumn() =
    rank[1](int i, AttrNode x | x = cfn.getAChild*() and i = x.getLocation().getEndColumn() | i)
}

 predicate calls_cn(FunctionObject caller, FunctionObject callee, CallNode cn) {
  caller != callee and
  (
    method_calls(caller, callee, cn)
    or
    direct_calls(caller, callee, cn)
    or
    module_calls(caller, callee, cn)
    or
    add_calls(caller, callee, cn)
  )
 }

 predicate calls_fi(FunctionObject caller, FunctionObject callee, FunctionInvocation fi) {
  caller != callee and
  (fi.getCaller().getFunction() = caller and fi.getFunction() = callee)
}

predicate is_sink(CallNode cn) {
    (
      cn.getFunction().(AttrNode).getNode().getName() = "submit" and
      cn.getArg(0).(AttrNode).getNode().getName() = "run" and 
      cn.getArg(0).(AttrNode).getNode().getObject().toString() = "subprocess"
    ) or
    (
      cn.getFunction().(AttrNode).getNode().getName() = "execute_code"
    ) or
    (
      cn.getFunction().(AttrNode).getNode().getName() = "Popen" and
      cn.getFunction().(AttrNode).getObject().getNode().toString() = "subprocess"
    )
    or
    (
      cn.getFunction().(AttrNode).getNode().getName() in ["request","get"] and
      (
      exists(With wi, CallNode cn2, NameNode nn |
          wi.getScope() = cn.getScope() and
          nn = wi.getAChildNode().getAFlowNode() and
          cn2 = wi.getAChildNode().getAFlowNode() |
          nn.getId() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
          cn2.getFunction().(AttrNode).getNode().getName() in ["AsyncClient", "ClientSession","Session"]
          // and  cn2.getFunction().(AttrNode).getObject().getNode().toString() in ["aiohttp", "httpx","requests"]
          )
        or
        exists( DefinitionNode dn |
          definition_node(cn.getFunction().(AttrNode).getNode().getScope().(Function), dn) | 
          dn.getNode().toString() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
          dn.getValue().(CallNode).getFunction().(AttrNode).getNode().getName() in ["AsyncClient", "ClientSession","Session"]
          // and dn.getValue().(CallNode).getFunction().(AttrNode).getObject().getNode().toString() in ["aiohttp", "httpx","requests"]
        )
      )
    )
    or
    (
      cn.getFunction().(AttrNode).getNode().getName() in ["arun"] and
      (
      exists(With wi, CallNode cn2, NameNode nn |
          wi.getScope() = cn.getScope() and
          nn = wi.getAChildNode().getAFlowNode() and
          cn2 = wi.getAChildNode().getAFlowNode() |
          nn.getId() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
          cn2.getFunction().getNode().toString() in ["AsyncWebCrawler"]
          )
        or
        exists( DefinitionNode dn |
          definition_node(cn.getFunction().(AttrNode).getNode().getScope().(Function), dn) | 
          dn.getNode().toString() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
          dn.getValue().(CallNode).getFunction().getNode().toString() in ["AsyncWebCrawler"])
      )
    )
    or 
    (
      cn.getFunction().(NameNode).getNode().toString() = "eval"
    )
    or 
    (
      cn.getFunction().(NameNode).getNode().toString() = "exec"
    )
    or
    (
      cn.getFunction().(AttrNode).getNode().getName() = "run" and
     exists( DefinitionNode dn |
       definition_node(cn.getFunction().(AttrNode).getNode().getScope().(Function), dn) | 
       dn.getNode().toString() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
        dn.getValue().(CallNode).getNode().getFunc().toString() = "ShellTool")
    )
    or 
    (
      cn.getFunction().(AttrNode).getNode().getName() = "execute" and
     exists( DefinitionNode dn |
       definition_node(cn.getFunction().(AttrNode).getNode().getScope().(Function), dn) | 
       dn.getNode().toString() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
       print_function(dn.getValue().(CallNode)).matches("%.cursor") )
    )
    or
    (
      cn.getFunction().(AttrNode).getNode().getName() = "run" and
      cn.getFunction().(AttrNode).getObject().getNode().toString() = "subprocess"
    )
    or
    (
      cn.getFunction().(AttrNode).getNode().getName() in ["get", "post", "request"] and
      cn.getFunction().(AttrNode).getObject().getNode().toString() = "requests"
    )
    or
    (
      cn.getFunction().(AttrNode).getNode().getName() = "system" and
      cn.getFunction().(AttrNode).getObject().getNode().toString() = "os"
    )
    or
    (
      cn.getFunction().(AttrNode).getNode().getName() = "run" and
      exists( DefinitionNode dn |
        definition_node(cn.getFunction().(AttrNode).getNode().getScope*().(Function), dn) | 
        dn.getNode().toString() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
         dn.getValue().(CallNode).getNode().getFunc().toString() = "PythonREPL")
    )
    or
    (
      cn.getFunction().(AttrNode).getNode().getName() = "run_cell" and
      exists( DefinitionNode dn |
        definition_node(cn.getFunction().(AttrNode).getNode().getScope().(Function), dn) | 
        dn.getNode().toString() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
         dn.getValue().(CallNode).getNode().getFunc().toString() = "get_ipython")
    )
    or
    (
      cn.getFunction().getNode().toString() = "GitLoader"
    )
    or
    (
      cn.getFunction().(AttrNode).getNode().getName() in ["run", "invoke"] and
      exists( DefinitionNode dn |
        definition_node(cn.getFunction().(AttrNode).getNode().getScope().(Function), dn) | 
        dn.getNode().toString() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
        dn.getValue().(CallNode).getFunction().(AttrNode).getNode().getName() = "from_llm" and
        dn.getValue().(CallNode).getFunction().(AttrNode).getObject().getNode().toString() in ["SQLDatabaseChain", "SQLDatabaseSequentialChain"])
    )
    or
    print_function(cn).matches("%session.execute")
    or
    print_function(cn).matches("connection.execute")
    or
    print_function(cn).matches("jinja.from_string")
    or
    (cn.getFunction().(AttrNode).getNode().getName() = "load" and
      exists( DefinitionNode dn |
        definition_node(cn.getFunction().(AttrNode).getNode().getScope*().(Function), dn) | 
        dn.getNode().toString() = cn.getFunction().(AttrNode).getObject().getNode().toString() and
         dn.getValue().(CallNode).getNode().getFunc().toString() in ["AsyncHtmlLoader", "WebBaseLoader"])
    )
    or
    (
      exists(ParameterDefinition pd, AttrNode an | pd.getScope() = cn.getScope() and pd.getAnnotation() = an| 
      cn.getFunction().(AttrNode).getNode().getName() = "request" and
      pd.getName() =  cn.getFunction().(AttrNode).getObject().getNode().toString() and
      an.getNode().getName().matches("%Client") and an.getObject().getNode().toString() = "httpx")
    )
}
