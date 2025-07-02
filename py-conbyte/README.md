# py-conbyte 

# Requirements
- Python version >= 3.7.3
- SMT-solver installed ([Z3](https://github.com/Z3Prover/z3) or [CVC4](https://github.com/CVC4/CVC4)) 

A Python concolic testing tool running on bytecode level.

This project takes refer to the structure purposed in 
[Deconstructing Dynamic Symbolic Execution](http://research.microsoft.com/apps/pubs/?id=233035),  
[A Peer Architecture for Lightweight Symbolic Execution](http://hoheinzollern.files.wordpress.com/2008/04/seer1.pdf)
and the tool [PyExZ3](https://github.com/GroundPound/PyExZ3).   
We use the same path_to_constraints structure in our tool.
The main difference is how we instrument the code.   
PyExZ3 substitutes the formal parameters with self-defined symbolic objects
in the program to analysis. It runs the program, and records symbolic values 
for each variables and branches. One drawback of this approach is that
it did not encode operations outside these self-defined objects. For example, it
degrades to int concrete value when executing `int(<string>)` since `int()` is a
built-in function and cannot be overwritten in self-defined objects.   
Py-Conbyte instead maintains an independent symbolic environment.   
It collects the bytecodes being executed as the program runs, and
executes them simultaneously in this symbolic environment. With this approach
we have full control on encoding the program behaviors into symbolic semantics,
or easily gets the concrete value from the original program when it's hard 
to encode.



py-conbyte currently supports:
- Builtin functions: 
  - `len()`
  - `int()`
  - `str()`
  - `dict()`
  - `list()`
  - `range()`
  - `sum()`
  - `max()`
  - `min()`
  - `abs()`
- Types: 
  - Integer
  - String
  - Array
  - Dictionary
  - Class containing these types
See `test/` for supported syntaxes.   

Formal parameters of the program to analysis can only be integers,
strings, array containing integer and string.

## Installation
Make sure you have z3/cvc4 installed in your system.   
Use `pip` to install python packages.
```
$ pip install -r requirements.txt
```

## Usage
```
Usage: py-conbyte.py [options] <path to (target).py file>

Options:
  -h, --help            show this help message and exit

  Exploration Setup:
    -i INPUTS, --input=INPUTS
                        Specify initial inputs, default to './inputs.py'
    --stdin             Read inputs from stdin instead of a file
    -e ENTRY, --entry=ENTRY
                        Specify entry point, if different than (target).py
    -m ITERATION, --max_iter=ITERATION
                        Specify max iterations
    -t TIMEOUT, --timeout=TIMEOUT
                        Specify solver timeout (default = 1sec)

  Logging Configuration:
    -d, --debug         Enable debug logging
    --extract           Extract bytecode only
    -q QUERY, --query=QUERY
                        Store smt queries
    --quiet             No logging
    -l LOGFILE, --logfile=LOGFILE
                        Store log
    --json              Print JSON format to stdout

  Solver Configuration:
    -s SOLVER_TYPE, --solver=SOLVER_TYPE
                        Solver=[z3seq, z3str, trauc, cvc4], default to z3seq
```

Example:
```
 $ ./py-conbyte.py -i inputs.py test/do_numbers.py
```

