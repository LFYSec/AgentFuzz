import python

// deprecated
predicate isIncludeLocation(Location loc) {
    not exists(loc.toString().indexOf("test")) 
    and not exists(loc.toString().indexOf("miniconda")) 
    and not exists(loc.toString().indexOf("demo")) 
    and not exists(loc.toString().indexOf("example"))
    and not exists(loc.toString().indexOf("qltracer"))
    and not exists(loc.toString().indexOf("newrepo"))
    and not exists(loc.toString().indexOf("Python39"))
 }

 string locStr(Location loc) {
   result =
     loc.getFile().getAbsolutePath() + "#" + loc.getStartLine().toString() + ":" +
       loc.getStartColumn().toString() + "#" + loc.getEndLine().toString() + ":" +
       loc.getEndColumn().toString()
 }

 predicate isIncludeLocation2(Location loc) {
    isIncludeLocationStr(loc.toString())
 }

 bindingset[s]
 predicate isIncludeLocationStr(string s) {
    forall(string black | black = getBlacklist()| not s.matches("%" + black + "%"))
 }

 string getBlacklist() {
    result = ["test", "miniconda", "demo", "example", "qltracer", "newrepo", "Python39"]
 }

 string getStrFuncName() {
   result = ["split", "index", "rindex"]
 }

 int getDepthLimit() {
   result = [2..20]
 }