from pathlib import Path
from parse import *
import os
import json
from argparse import ArgumentParser
import logging

all_punctuation = ';:,.!?'
end_punctuation = '.!?'


def walk_tree(root, current, context, start_w=0):
    """ Generate tokens up to $value level """

    logging.debug('[%d walk_tree] current %s context %s '
            % (start_w, str(current.key), str(context)))

    try:
        seq = random.choice(current)
    except Exception as e:
        logging.error('Exception walking from current', current, context)
        raise e

    flat = Node('>')
    tree = Node(current.key)

    # TODO: Remove?
    if seq.is_leaf:
        print('flat seq', seq)
        flat.add(seq)
        tree.add(seq)
        print('tree flat', tree)
        return flat, tree

    for child in seq:
        logging.debug('[%d walk_tree child] %s' % (start_w, child))
        child_key = child.key

        # Optionally skip optional tokens
        if child_key.endswith('?'):
            child_key = child_key[:-1]
            if random.random() < 0.5:
                continue

        # Expandable word, e.g. %phrase or ~synonym
        if child_key.startswith(('%', '~', '$', '@')):
            sub_context = context[child_key]  \
                if context is not None and child_key in context \
                else None

            try:
                sub_flat, sub_tree = walk_tree(root, sub_context or root[child_key], context, start_w)
            except Exception as e:
                logging.error('Exception walking from current %s %s %s'
                        % (current, child_key, str(context)))
                raise e

            # Add words to flat tree
            flat.merge(sub_flat)

            # Adjust position based on number of tokens
            len_w = len(sub_flat)
            sub_tree.position = (start_w, start_w + len_w - 1, len_w)
            start_w += len_w

            # Add to (or merge with) tree
            if not child_key.startswith('~'):
                if root[child_key].passthrough:
                    tree.merge(sub_tree)
                else:
                    tree.add(sub_tree)
            else:
                if tree.type == 'value':
                    tree.merge(sub_flat)

        # Terminal node, e.g. a word
        else:
            has_value_parent, parent_line = current.has_parent('value')
            start_w += 1
            len_w = 1
            if has_value_parent:
                tree.type = 'value'
                tree.key = '.'.join(parent_line)
                tree.add(child_key)
            elif current.type == 'value':
                tree.add(child_key)
            flat.add(child_key)

    return flat, tree

def fix_sentence(sentence):
    return fix_capitalization(fix_punctuation(fix_newlines(fix_spacing(sentence))))

def fix_capitalization(sentence):
    return ''.join(map(lambda s: s.capitalize(), re.split(r'([' + end_punctuation + ']\s*)', sentence)))

def fix_punctuation(sentence):
    fixed = re.sub(r'\s([' + all_punctuation + '])', r'\1', sentence).strip()
    if fixed[-1:] not in end_punctuation:
        fixed = fixed + '.'
    return fixed

def fix_newlines(sentence):
    return re.sub(r'\s*\\n\s*', '\n\n', sentence).strip()

def fix_spacing(sentence):
    return re.sub(r'\s+', ' ', sentence)

def parser_from_file(filename):
    """ Load a parser from a .nlg file """
    if not os.path.isfile(filename):
        raise ValueError("The specified file does not exist")
    parsed = parse_file(filename)
    parsed.map_leaves(tokenize_leaf)
    return parsed

def generate_sentences(parsed, context=Node('%'), n=1):
    """ Generate random sentences from a parser """ 
    key = context.key
    flats, trees = [], []

    for i in range(n):
        f, t = walk_tree(parsed, parsed[key], context[key])
        flats.append(f)
        trees.append(t)

    return flats, trees

def write_results(flats, trees, output=Path("")):
    """ Write results on output. If output's path is empty, we just print the results"""

    if output == Path(""):
        for flat, tree in zip(flats, trees):
            print('>', fix_sentence(flat.raw_str))
            print(tree)
            print('-' * 80)
    else:
        with open(output, "w+") as f:
            for flat, tree in zip(flats, trees):
                f.write('\n>%s' % fix_sentence(flat.raw_str))
                f.write('\n%s' % tree)
                f.write('\n' + '-' * 80)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("template", type=Path, default=Path(""), 
            help="Template file's path containing grammar structure")
    parser.add_argument("--root", type=str, default="",
            help="Root command")
    parser.add_argument("--json", type=Path, default=Path(""))
    parser.add_argument("--log", type=str, default="INFO")
    parser.add_argument("-n", type=int, default=1, 
            help="Number of sentences to produce")
    parser.add_argument("--output", type=Path, default=Path(""),
            help="Output file to save generated sentences")
    parser.add_argument("--seed", type=int, default=None,
            help="Seed for randomness")

    known, unknown = parser.parse_known_args()
    
    numeric_level = getattr(logging, known.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % known.log)
    logging.basicConfig(level=numeric_level)
    
    logging.debug("Parameters:%s" % known)
    logging.debug("Context:%s" % unknown)
 
    random.seed(a=known.seed)

    root_context = Node('%')

    if known.root != "":
        logging.debug("Node is %s" % known.root)
        root_context = Node("%" + known.root)

    if unknown != []:
        logging.debug("Adding CLI context")
        root_context = root_context.add(parse_dict(unknown))

    if known.json != Path(""):
        if not os.path.isfile(known.json):
            logging.error("The specified json file does not exist")
            sys.exit()
        logging.debug("Adding JSON context")
        dict_json = json.load(open(known.json))
        root_context = root_context.add(parse_dict(dict_json))

    if not os.path.isfile(known.template):
            logging.error("The specified template file does not exist")
            sys.exit()
 
    filename = os.path.realpath(known.template)
    parser = parser_from_file(filename)
    flats, trees = generate_sentences(parser, root_context, known.n)
    write_results(flats, trees, known.output) 


