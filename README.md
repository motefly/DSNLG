# nalgenarg

A natural language generation language, intended for creating training data using parametrized vectors.
The parser was built in a very similar project [nalgene](https://github.com/spro/nalgene).
This project differentiates itself by using different structures in the grammar. 

## Overview

Nalgenarg generates pairs of sentences and grammar trees by a random walk through a grammar file.

* Sentence: the natural language sentence, e.g. "turn on the light"
* Tree: a nested list of tokens ([an s-expression](https://en.wikipedia.org/wiki/S-expression)) generated alongside the sentence, e.g.

	```
    ( %setDeviceState
        ( $device.name light )
        ( $device.state on ) ) )
	```

## Usage

```
$ python generate.py --help 
usage: generate.py [-h] [--root ROOT] [--json JSON] [--log LOG] [-n N]
                   [--output OUTPUT] [--seed SEED]
                   template

positional arguments:
  template         Template file's path containing grammar structure

optional arguments:
  -h, --help       show this help message and exit
  --root ROOT      Root command
  --json JSON
  --log LOG
  -n N             Number of sentences to produce
  --output OUTPUT  Output file to save generated sentences
  --seed SEED      Seed for randomness

```

By default, the utility is loading a sentence from a ramdomly-chosen node contained in the template file. But this node can be specified using   `--root`:

```
$ python generate.py templates/skills.nlg --root buildTower2
> Put the yellow shape on top of the blue cube.
( %buildTower2
    ( %put (0, 0, 1) )
    ( %object1 (1, 3, 3)
        ( %color (2, 2, 1) )
        ( %type (3, 3, 1)
            ( %cube (3, 3, 1) ) ) )
    ( %location_top (4, 6, 3) )
    ( %object2 (7, 9, 3)
        ( %color (8, 8, 1) )
        ( %type (9, 9, 1)
            ( %cube (9, 9, 1) ) ) ) )
--------------------------------------------------------------------------------
```

Generated sentences can be saved inside a file whose path is given in `--output`.

## Generated sentences from specific parameters 

You can also supply values from a JSON file:

```
$ cat tests/buildTower.json
{
        "%object1.%color": "red",
        "%object2.%type": "cube",
        "%object2.%color": "red"
}

$ python generate.py templates/skills.nlg --root buildTower2 --json tests/buildTower.json
> Move the red cup atop of the red cube.
( %
    ( %buildTower2 (0, 8, 9)
        ( %put (0, 0, 1) )
        ( %object1 (1, 3, 3)
            ( %object1.%color (2, 2, 1) red )
            ( %type (3, 3, 1)
                ( %cup (3, 3, 1) ) ) )
        ( %location_top (4, 5, 2) )
        ( %object2 (6, 8, 3)
            ( %object2.%color (7, 7, 1) red )
            ( %object2.%type (8, 8, 1) cube ) ) ) )
--------------------------------------------------------------------------------
```


## Syntax

A .nlg nalgene grammar file is a set of sections separated by a blank line. Every section takes this shape:

```
node_name
    sequence 1
    sequence 2
```

A word in the sequence might begin by "%". In this case, the parser will search for its corresponding node in the grammar file. For example:

```
%
    %greeting
    %farewell
    %greeting and %farewell

%greeting
    hey there
    hi

%farewell
    goodbye
    bye
```

The generator might output:

```
> hey there and bye
( %
    ( %greeting )
    ( %farewell ) )
```

#### Basic generation walkthrough

Here's how the generator arrived at this specific sentence and tree pair:

* Start at start node `%`, with an empty output sentence `""` and tree `( % )`
* Randomly choose a token sequence, in this case the 3rd: `%greeting and %farewell`
* The first token is a phrase token `%greeting`, so
    * Add a new sub-tree `( %greeting )` to the parent tree
    * Look up the token sequences for `%greeting`
    * Choose one, in this case `hey there`
        * For both of these regular word tokens, add to the output sentence (but not to the tree)
* At this point the output sentence is `"hey there"` and the parse tree is `( % ( %greeting ) )`
* The second token is a regular word `"and"`, so add it to the output sentence
* The third token is another phrase `%farewell`, so
    * Add a new sub-tree `( %farewell )` to the parent tree
    * Look up the token sequences for `%farewell`
    * Choose one, in this case `bye`
        * Add to the output sentence
        * Now the output sentence is `"hey there and bye"`
* No more tokens, so we're done

## Homonyms

Sometimes, we want to specify several nodes having different properties. We can do it easily with trailing digits:

```
%object
    the %color %type

%buildTower
    the %object1 goes on top of %object2
```



## Optional tokens

Tokens with a `?` at the end will be used only 50% of the time.

```
%findFood
    ~find $price? $food ~near $location
```

```
> find me sushi in san francisco
( %
    ( %findFood
        ( $food sushi )
        ( $location san francisco ) ) )

> tell me the cheap fried chicken around tokyo
( %
    ( %findFood
        ( $price cheap )
        ( $food fried chicken )
        ( $location tokyo ) ) )
```



