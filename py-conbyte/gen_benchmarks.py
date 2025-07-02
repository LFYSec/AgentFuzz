#!/usr/bin/env python3.7

import sys
import os
from subprocess import Popen, PIPE, STDOUT

def main(target):
    pys = ["target_int/leetcode_int/add_binary.py",
           "target_int/leetcode_int/addStrings.py",
           "target_int/leetcode_int/numDecodings.py",
           "target_int/leetcode_int/restoreIpAddresses.py",
           "target_int/leetcode_int/validIPAddress.py",
           "target_int/leetcode_int/validWordAbbreviation.py",
           "target_int/lib_int/datetime__parse_hh_mm_ss_ff.py",
           "target_int/lib_int/datetime__parse_isoformat_date.py",
           "target_int/lib_int/distutils_get_build_version.py",
           "target_int/lib_int/email__parsedate_tz.py",
           "target_int/lib_int/http_parse_request.py",
           "target_int/lib_int/nntplib__parse_datetime.py",
           "target_int/lib_int/smtpd_parseargs.py",
           "target_int/lib_int/wsgiref_check_status.py",
           "target_int/lib_int/ipaddress__ip_int_from_string.py",
           ]

    inputs = ["[\"1001\", \"111\"]",
              "[\"14950\", \"385769\"]",
              "[\"215381249207226\"]",
              "[\"25525511135\"]",
              "[\"172.16.254.1\"]",
              "[\"internationalization\", \"i12iz4n\"]",
              "[\"12:01:23.123456\"]",
              "[\"2019-07-19\"]",
              "[\"MSC v.1912 abc\"]",
              "[\"Mon, 16 Nov 2009 13:32:02 +0100\"]",
              "[\"HTTP/1.0\"]",
              "[\"20190723121212\"]",
              "[\"localhost:8025\", \"localhost:25\"]",
              "[\"200 ok\"]",
              "[\"2001:0db8:85a3:0:0:8A2E:0370:7334\"]"
             ]
    index = 0
    for py in pys:
        b_path = "benchmarks/py-conbyte_%s/%s" % (target, py.replace("target_int/", "").replace(".py", "").replace("/", "-"))
        os.system("mkdir -p %s" % b_path)
        cmd = "./py-conbyte.py --stdin -s %s -m 300 -t 3 -q %s " % (target, b_path)
        if "add_binary" in py:
            cmd += " --ss "
        cmd += py
        print(cmd)
        try:
            process = Popen(cmd, shell=True, stdin=PIPE)
        except subprocess.CalledProcessError as e:
            print(e.output)
        
        process.communicate(input=("INI_ARGS = %s" % inputs[index]).encode())
        index += 1





if __name__ == '__main__':
    main(sys.argv[1])
