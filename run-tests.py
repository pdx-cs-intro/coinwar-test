#!/usr/bin/python3
# Test a Coin Wars program
# Bart Massey 2021

import argparse, os, re, shutil, subprocess, sys

# Deal with command-line arguments.
parser = argparse.ArgumentParser(description='Coin War tester.')
parser.add_argument(
    '--warn', '-w',
    help='warn on non-tests',
    action="store_true",
)
parser.add_argument(
    '--file', '-f',
    help='supply file argument instead of using stdin',
    action="store_true",
)
parser.add_argument(
    '--program', '-p',
    help='program path',
    default="coin-war.py",
)
parser.add_argument(
    '--srcdir', '-s',
    help='directory for given tests (cwtests)',
    default="cwtests",
)
parser.add_argument(
    '--testdir', '-t',
    help='temp directory for built tests (.tests)',
    default=".tests",
)
args = parser.parse_args()

# Source of tests to be run.
srcdir = args.srcdir

# Tests to be run in input format.
testdir = args.testdir

# Clear out old tests and rebuild them.
shutil.rmtree(testdir, ignore_errors=True)
os.mkdir(testdir)
testpat = re.compile(r"(test-[0-9]*)\.txt")
for test in sorted(os.listdir(srcdir)):
    # Check that test is actually a test filename.
    matched = testpat.fullmatch(test)
    if not matched:
        if args.warn:
            print(f"ignoring {test}")
        continue
    testname = matched[1]

    # Process the testfile.
    print(f"{testname}: ", end="")
    with open(f"{srcdir}/{test}", "r") as testfile:
        testlines = [ l.strip() for l in testfile ]
    testpath = f"{testdir}/{test}"
    with open(testpath, "w") as testfile:
        print("position", file=testfile)
        for l in testlines[:2]:
            print(l, file=testfile)
    expected = testlines[2]

    # Run the test.
    inputstr = None
    cmd = ["python", args.program]
    if args.file:
        cmd.append(testpath)
    else:
        with open(testpath, "r") as f:
            inputstr = f.read()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        input=inputstr,
    )

    # Show test result.
    if result.returncode != 0:
        print(f"failed with exit status {result.returncode}")
        print(result.stderr, end="")
        continue
    output = result.stdout.split("\n")
    if len(output) < 2:
        print("failed to produce output")
        continue
    got = output[-2].strip()
    if expected != got:
        print(f"expected {expected} got {got}")
    else:
        print("passed")
