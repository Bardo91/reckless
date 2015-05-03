#!/usr/bin/python3

import sys
from sys import argv, stderr, stdout
from getopt import gnu_getopt
import numpy as np

ALL_LIBS = ['nop', 'reckless', 'stdio', 'fstream', 'pantheios', 'spdlog']
ALL_TESTS = ['periodic_calls', 'call_burst', 'write_files', 'mandelbrot']
THREADED_TESTS = {'call_burst', 'mandelbrot'}

def main():
    opts, args = gnu_getopt(argv[1:], 'l:t:c:h', ['libs=', 'tests=', 'threads=', 'help'])
    libs = None
    tests = None
    threads = None
    show_help = len(args) != 0

    for option, value in opts:
        if option in ('-l', '--libs'):
            libs = [lib.strip() for lib in value.split(',')]
        elif option in ('-t', '--tests'):
            tests = [test.strip() for test in value.split(',')]
        elif option in ('-c', '--threads'):
            threads = parse_ranges(value)
        elif option in ('-h', '--help'):
            show_help = True

    if show_help:
        stderr.write(
            'usage: statistics.py [OPTIONS]\n'
            'where OPTIONS are:\n'
            '-t,--tests    TESTS      comma-separated list of tests to plot\n'
            '-l,--libs     LIBS       comma-separated list of libs to plot\n'
            '-c,--threads  THREADS    thread-counts to include in a comma-separated list (e.g. 1-2,4)\n'
            '-h,--help        show this help\n'
            'Available libraries: {}\n'
            'Available tests: {}\n'.format(
                ','.join(ALL_LIBS), ','.join(ALL_TESTS)))
        return 1
    
    if libs is None:
        libs = sorted(ALL_LIBS)
    if tests is None:
        tests = sorted(ALL_TESTS)
    if threads is None:
        threads = list(range(1, 5))

    make_stats(libs, tests, threads)
    return 0

def parse_ranges(s):
    ranges = s.split(',')
    result = []
    for r in ranges:
        parts = r.split('-')
        if len(parts)>2:
            raise ValueError("Invalid range specification: " + r)
        start=int(parts[0])
        if len(parts) == 2:
            end=int(parts[1])
        else:
            end = start
        start, end = min(start, end), max(start, end)
        result.extend(list(range(start, end+1)))
    return result
        
def make_stats(libs, tests, threads_list):
    def single_file_stats(filename, columns):
        with open(filename, 'r') as f:
            data = f.readlines()
        data = np.array([float(x) for x in data])
        low, high = np.percentile(data, [25, 75])
        mean = np.mean(data)
        mad = np.mean(np.absolute(data - mean))
        std = np.std(data)
        cols = [mean, high - low, mad, std]
        cols = ["%.0f" % x for x in cols]
        columns.extend(cols)
    
    rows = [["Library", "Ticks", "IQR", "MAD", "Std deviation"]]
    for test in tests:
        for lib in libs:
            columns = []
            if len(lib) > 1:
                columns.append(lib)
            base_name = []
            if test in THREADED_TESTS:
                for threads in threads_list:
                    name = base_name[:]
                    filename = "results/%s_%s_%d.txt" % (lib, test, threads)
                    single_file_stats(filename, columns)
            else:
                filename = "results/%s_%s.txt" % (lib, test)
                single_file_stats(filename, columns)
            rows.append(columns)
    
    
    colwidths = [0]*len(rows[0])
    for row in rows:
        widths = [len(x) for x in row]
        colwidths = [max(a, b) for a,b in zip(colwidths, widths)]
    first_row = True
    for row in rows:
        first_col = True
        for col, width in zip(row, colwidths):
            if not first_col:
                stdout.write(' | ')
            first_col = False
            stdout.write(' '*(width - len(col)))
            stdout.write(col)
        stdout.write('\n')
        if first_row:
            line = ['-'*w for w in colwidths]
            line = '-|-'.join(line) + '\n'
            stdout.write(line)
            first_row = False

if __name__ == "__main__":
    sys.exit(main())
