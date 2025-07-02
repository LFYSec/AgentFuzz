#!/usr/bin/env python3

import sys
import os
import logging
import dis
import inspect
from optparse import OptionParser
from optparse import OptionGroup
import time
from conbyte.function import *
from conbyte.explore import *

import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore', SyntaxWarning)
    # simulate import of module giving SyntaxWarning
    warnings.warn('bad', SyntaxWarning)



def main():
    usage = "usage: %prog [options] <path to (target).py file>"
    parser = OptionParser(usage=usage)

    # Setup
    setup_group = OptionGroup(parser, "Exploration Setup")
    setup_group.add_option("-i", "--input", dest="inputs", action="store", help="Specify initial inputs, default to \'./inputs.py\'", default="./inputs.py")
    setup_group.add_option("--stdin", dest="from_stdin", action="store_true", help="Read inputs from stdin instead of a file")
    setup_group.add_option("-e", "--entry", dest="entry", action="store", help="Specify entry point, if different than (target).py", default=None)
    setup_group.add_option("-m", "--max_iter", dest="iteration", action="store", help="Specify max iterations", default=50)
    setup_group.add_option("-t", "--timeout", dest="timeout", action="store", help="Specify solver timeout (default = 1sec)", default=None)
    setup_group.add_option("--ss", dest="ss", action="store_true", help="Special constraint for add_binays.py", default=None)
    setup_group.add_option("--tl", dest="target_line", action="store", help="Special constraint for add_binays.py", default=None)
    parser.add_option_group(setup_group)

    # Logging configuration
    logging_group = OptionGroup(parser, "Logging Configuration")
    logging_group.add_option("-d", "--debug", dest='debug', action="store_true", help="Enable debug logging")
    logging_group.add_option("--extract", dest='extract', action="store_true", help="Extract bytecode only")
    logging_group.add_option("-q", "--query", dest='query', action="store", help="Store smt queries", default=None)
    logging_group.add_option("--quiet", dest='quiet', action="store_true", help="No logging")
    logging_group.add_option("-l", "--logfile", dest='logfile', action="store", help="Store log", default=None)
    logging_group.add_option("--json", dest='get_json', action="store_true", help="Print JSON format to stdout", default=None)
    parser.add_option_group(logging_group)

    # Solver configuration
    solver_group = OptionGroup(parser, "Solver Configuration")
    solver_group.add_option("-s", "--solver", dest='solver_type', action="store", help="Solver=[z3seq, z3str, trauc, cvc4], default to z3", default="z3seq")
    parser.add_option_group(solver_group)

    (options, args) = parser.parse_args()
    if len(args) == 0 or not os.path.exists(args[0]):
        parser.error("Missing app to execute")
        sys.exit(1)

    """
    if options.solver_type != "z3" and options.solver_type != "cvc4":
        parser.error("Solver can only be z3 or cvc4")
        sys.exit(1)
    """

    if options.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logfile = options.logfile
    if logfile is not None:
        logging.basicConfig(filename=options.logfile, level=log_level, 
                            format='%(asctime)s  %(name)s\t%(levelname)s\t%(message)s', 
                            datefmt = '%m/%d/%Y %I:%M:%S %p')
    elif options.quiet:
        logging.basicConfig(filename="/dev/null")
    else:
        if options.get_json:
            logging.basicConfig(filename="/dev/null", level=log_level, 
                                format='  %(name)s\t%(levelname)s\t%(message)s')
        else:
            logging.basicConfig(level=log_level, 
                                format='  %(name)s\t%(levelname)s\t%(message)s')

    base_name = os.path.basename(args[0])
    filename = os.path.abspath(args[0])
    path = filename.replace(base_name, "")
    module = base_name.replace(".py", "")
    query = options.query

    inputs_space = {}
    if options.from_stdin:
        exec(sys.stdin.read(), inputs_space)
    else:
        inputs_file = options.inputs
        inputs_file_full = os.path.abspath(options.inputs)
        exec(open(inputs_file_full).read(), inputs_space)

    engine = ExplorationEngine(path, filename, module, options.entry, inputs_space["INI_ARGS"], query, options.solver_type, options.ss, int(options.target_line))

    if options.extract:
        engine.extract()
        return

    engine.explore(int(options.iteration), options.timeout)

    if options.quiet:
        return

    print(engine.input_sets[1])


    
