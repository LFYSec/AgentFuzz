import os
import subprocess

DB_HOME = "/path/to/database"
arg_dbname = "TaskWeaver"
QUERY_HOME = './ql'
SARIF_HOME = './sarif'
arg_os = None


def analyze_db(query, db, target):
    abdb = os.path.join(DB_HOME, db)
    abquery = os.path.join(QUERY_HOME, query)
    abtarget = os.path.join(SARIF_HOME, target)
    cmd = ["codeql", "database", "analyze", "--rerun", "--format", "sarif-latest", "--sarif-add-snippets", "--max-paths=200", "--output", abtarget, abdb, abquery]
    print(cmd)
    subprocess.run(args=cmd)



db = arg_dbname
filename = arg_dbname
if arg_os:
    filename = filename + "-" + arg_os
ql = "get_if.ql"

if_sarif = filename + "-if.sarif"
location_sarif = filename + "-location.sarif"
dsc_sarif = filename + "-dsc.sarif"
analyze_db("get_if.ql", db, if_sarif)
analyze_db("get_callchain_and_location.ql", db, location_sarif)
analyze_db("get_dataflow_str_constraint.ql", db, dsc_sarif)

run = True

output_dir = os.path.join("output", db)
if arg_os:
    output_dir = os.path.join(output_dir, arg_os)
cmd = ["python", "generate_hook.py", "--filename", os.path.join(SARIF_HOME, location_sarif), "--enter_hook_path", os.path.join(output_dir, "enter_hook.json"), "--oracle_path", os.path.join(output_dir, "oracle.json")]
print(cmd)
if run: 
    subprocess.run(cmd)
cmd = ["python", "generate_if.py", "--filename", os.path.join(SARIF_HOME, if_sarif), "--output", os.path.join(output_dir, db + "-if.json")]
print(cmd)
if run:
    subprocess.run(cmd)
cmd = ["python", "generate_dsc.py", "--filename", os.path.join(SARIF_HOME, dsc_sarif), "--output", os.path.join(output_dir, db + "-dsc.json")]
print(cmd)
if run:
    subprocess.run(cmd)