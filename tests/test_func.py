from nalangen import *
from nalangen.node import Node
from nalangen.parse import parse_dict
import logging

logging.basicConfig(level='DEBUG')

def test_from_dict(parser):
    """ Generate a sentence with parameters given as a dictionary """
    node = Node("%")
    params = {"%object1.%color": "blue",
              "%object1.%type": "cup",
              "%object2.%color": "white",
              "%object2.%type": "cube",
              "%object3.%color": "red",
              "%object3.%type": "cube"}
    context = node.add(parse_dict(params))
    print(context)
    flats, trees = generate_sentences(parser, context, 1)
    result = flats[0].raw_str
    assert "the blue cup" in result
    assert "the white cube" in result
    assert "green" not in result
























