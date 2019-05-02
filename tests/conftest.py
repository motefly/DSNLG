import random
import pytest
import os 
from pathlib import Path
from nalangen import parser_from_file


ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

@pytest.fixture
def parser():
    return initialize_parser()

def initialize_parser(): 
    random.seed(1) 
    parser = parser_from_file(ROOT_DIR / "templates" / "skills.nlg") 
    return parser 


