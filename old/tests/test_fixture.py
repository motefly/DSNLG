import pytest
import random
from pathlib import Path
from tempfile import NamedTemporaryFile
import filecmp
import os
import sys
sys.path.append("..")
from generate import parser_from_file, generate_sentences, write_results
from node import Node
import logging 

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
EXPECTED_DIR = ROOT_DIR / "tests" / "expected"

random.seed(1)

def compare_results(expected, results):
    if not os.path.isfile(expected):
        logging.warning("The expected file does not exist.")
    elif filecmp.cmp(expected, results):
        logging.debug("%s is accepted." % expected)
        return 
    content = Path(results).read_text()
    print("The test %s failed." % expected)
    print("Should I accept the results?")
    print(content)
    while True:
        try:
            keep = input("[y/n]")
        except OSError:
            assert False, "The test failed. Run directly this file to accept the result"
        if keep.lower() in ["y", "yes"]:
            Path(expected).write_text(content)
            break
        elif keep.lower() in ["n", "no"]:
            assert False, "The test failed and you did not accept the answer."
            break
        else:
            print("Please answer by yes or no.")


def create_fixture_data():
    """ This should be run carefully as it overwrites the expected results """
    pass

def test_example_iot_root():
    parser = parser_from_file(ROOT_DIR / "examples" / "iot.nlg")
    flats, trees = generate_sentences(parser, Node("%"), 1)
    tmp = NamedTemporaryFile(delete=False)
    write_results(flats, trees, output=tmp.name)
    compare_results(EXPECTED_DIR / "iot_root.test", tmp.name)

def test_example_iot_tokyo():
    parser = parser_from_file(ROOT_DIR / "examples" / "iot.nlg")
    flats, trees = generate_sentences(parser, Node("%"), 1)
    tmp = NamedTemporaryFile(delete=False)
    write_results(flats, trees, output=tmp.name)
    compare_results(EXPECTED_DIR / "iot_tokyo.test", tmp.name)


if __name__ == "__main__":
    from inspect import getmembers, isfunction
    def istest(o):
        return isfunction(o[1]) and  o[0].startswith("test")

    [o[1]() for o in getmembers(sys.modules[__name__]) \
            if istest(o)]
