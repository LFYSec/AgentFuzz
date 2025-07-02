/**
 * @id py-qs/caller
 * @severity warning
 * @precision low
 * @description just a simple test ql file for caller
 * @kind problem
 */

 import call.call
 import util.util
 from Source source
 select source, "$@", "$@",  source.getPathStr()