# DSNLG

This repo is based on json parsing, and is used to generate the natural language for dialogue system.

## Strategy
The program searches the pre-defition in json file and find the one cover all of the request solts and inform solts given in actions, 
and then output the defined natural language; If the slots cannot be matched completely, 
the program will find the one matching the slots as much as possible, 
the output sentence will be marked "incomplete: " in the head.

## Usage
```python
nlg_model = nlg()
# this is the path of json file, which is the predefined nl-act pairs.
diaact_nl_pairs = './data/dia_act_nl_pairs.v6.json'
# loading the json file
nlg_model.load_predefine_act_nl_pairs(diaact_nl_pairs)
# define a example action
agent_action = {}
agent_action['diaact'] = 'inform'
agent_action['inform_slots'] = {'starttime': '9:10 pm'}
agent_action['request_slots'] = {}
# generate the natural language for this action
res = nlg_model.convert_diaact_to_nl(agent_action, 'agt')
```

## Json Definition
You can also add some new nl-act pairs into the json file.

For example, the intent is "inform", you can add a new block containing "request_slots", "nl" and "inform_slots".
```
"inform": [
      {
        "request_slots": [], 
        "nl": {
          "agt": "$moviename$ is available.", 
          "usr": "I want to watch $moviename$."
        }, 
        "inform_slots": [
          "moviename"
        ]
      }, 
      {
        "request_slots": [], 
        "nl": {
          "agt": "yes, please", 
          "usr": "yes"
        }, 
        "inform_slots": [
          "ticket"
        ]
      },
      ...,
      {add here like the above ones...}
      ]
```
