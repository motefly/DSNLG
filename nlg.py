'''
Created on Oct 17, 2016
Modified on Aug 12, 2019

--dia_act_nl_pairs.v6.json: agt and usr have their own NL.


@author: xiul, zhenhui
'''

import pickle
import copy, argparse, json
import numpy as np

import dialog_config

class nlg:
    def __init__(self):
        pass
    
    def post_process(self, pred_template, slot_val_dict, slot_dict):
        """ post_process to fill the slot in the template sentence """
        
        sentence = pred_template
        suffix = "_PLACEHOLDER"
        
        for slot in slot_val_dict.keys():
            slot_vals = slot_val_dict[slot]
            slot_placeholder = slot + suffix
            if slot == 'result' or slot == 'numberofpeople': continue
            if slot_vals == dialog_config.NO_VALUE_MATCH: continue
            tmp_sentence = sentence.replace(slot_placeholder, slot_vals, 1)
            sentence = tmp_sentence
                
        if 'numberofpeople' in slot_val_dict.keys():
            slot_vals = slot_val_dict['numberofpeople']
            slot_placeholder = 'numberofpeople' + suffix
            tmp_sentence = sentence.replace(slot_placeholder, slot_vals, 1)
            sentence = tmp_sentence
    
        for slot in slot_dict.keys():
            slot_placeholder = slot + suffix
            tmp_sentence = sentence.replace(slot_placeholder, '')
            sentence = tmp_sentence
            
        return sentence
    
    def convert_diaact_to_nl(self, dia_act, turn_msg):
        """ Convert Dia_Act into NL: Rule + Model """
        
        sentence = ""
        boolean_in = False
        
        # remove I do not care slot in task(complete)
        if dia_act['diaact'] == 'inform' and 'taskcomplete' in dia_act['inform_slots'].keys() and dia_act['inform_slots']['taskcomplete'] != dialog_config.NO_VALUE_MATCH:
            inform_slot_set = dia_act['inform_slots'].keys()
            for slot in inform_slot_set:
                if dia_act['inform_slots'][slot] == dialog_config.I_DO_NOT_CARE: del dia_act['inform_slots'][slot]
        
        if dia_act['diaact'] in self.diaact_nl_pairs['dia_acts'].keys():
            for ele in self.diaact_nl_pairs['dia_acts'][dia_act['diaact']]:
                # match the set accurately, or have no answer
                if set(ele['inform_slots']) == set(dia_act['inform_slots'].keys()) and set(ele['request_slots']) == set(dia_act['request_slots'].keys()):
                    sentence = self.diaact_to_nl_slot_filling(dia_act, ele['nl'][turn_msg])
                    boolean_in = True
                    break
                
        if not boolean_in:
            MAX_Match = 0
            ans = None
            if dia_act['diaact'] in self.diaact_nl_pairs['dia_acts'].keys():
                for ele in self.diaact_nl_pairs['dia_acts'][dia_act['diaact']]:
                    # match the items as much as possible
                    cur_Match = len(set(ele['inform_slots']) & set(dia_act['inform_slots'].keys())) + len(set(ele['request_slots']) & set(dia_act['request_slots'].keys()))
                    if cur_Match > MAX_Match:
                        ans = ele
                sentence = 'Incomplete: ' +self.diaact_to_nl_slot_filling(dia_act, ans['nl'][turn_msg])
                boolean_in = True

        if dia_act['diaact'] == 'inform' and 'taskcomplete' in dia_act['inform_slots'].keys() and dia_act['inform_slots']['taskcomplete'] == dialog_config.NO_VALUE_MATCH:
            sentence = "Oh sorry, there is no ticket available."
        
        if boolean_in == False: sentence = "Sorry, cannot find corresponding response."
        return sentence
        
    def diaact_to_nl_slot_filling(self, dia_act, template_sentence):
        """ Replace the slots with its values """
        
        sentence = template_sentence
        counter = 0
        for slot in dia_act['inform_slots'].keys():
            slot_val = dia_act['inform_slots'][slot]
            if slot_val == dialog_config.NO_VALUE_MATCH:
                sentence = slot + " is not available!"
                break
            elif slot_val == dialog_config.I_DO_NOT_CARE:
                counter += 1
                sentence = sentence.replace('$'+slot+'$', '', 1)
                continue
            
            sentence = sentence.replace('$'+slot+'$', slot_val, 1)
        
        if counter > 0 and counter == len(dia_act['inform_slots']):
            sentence = dialog_config.I_DO_NOT_CARE
        
        return sentence
    
    def load_predefine_act_nl_pairs(self, path):
        """ Load some pre-defined Dia_Act&NL Pairs from file """
        
        self.diaact_nl_pairs = json.load(open(path, 'rb'))
        
        for key in self.diaact_nl_pairs['dia_acts'].keys():
            for ele in self.diaact_nl_pairs['dia_acts'][key]:
                ele['nl']['usr'] = ele['nl']['usr']
                ele['nl']['agt'] = ele['nl']['agt']

if __name__ == "__main__":
    nlg_model = nlg()
    diaact_nl_pairs = './data/dia_act_nl_pairs.v6.json'
    nlg_model.load_predefine_act_nl_pairs(diaact_nl_pairs)

    agent_action = {}

    # agent_action['diaact'] = 'inform'
    # agent_action['inform_slots'] = {'city': 'seattle',
    #                                 'numberofpeople': '2',
    #                                 'theater': 'regal meridian 16',
    #                                 'date': 'tomorrow',
    #                                 'starttime': '9:10 pm',
    #                                 'moviename': 'zootopia',
    #                                 'taskcomplete': 'Ticket Available',
    #                                 'moviename': 'zootopia'}
    # agent_action['request_slots'] = {}
    
    # agent_action['diaact'] = 'inform'
    # agent_action['inform_slots'] = {'starttime': '9:10 pm'}
    # agent_action['request_slots'] = {}
    
    agent_action['diaact'] = 'request'
    agent_action['inform_slots'] = {'numberofpeople': '2',
                                    'moviename': 'the big short'}
    agent_action['request_slots'] = {'ticket': 'UNK'}
    res = nlg_model.convert_diaact_to_nl(agent_action, 'agt')
    print(res)
