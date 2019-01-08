#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from xml.etree import ElementTree

EXTENSION_FORMAT_ERROR_MESSAGE = "This script works only with pnml files"

nets = None
nets_info = dict()
transition_dicts = None
place_dicts = None
arc_dicts = None
TRANSITION_TAG_MODEL_STRING = '{RefNet}transition'
PLACE_TAG_MODEL_STRING = '{RefNet}place'
ARC_TAG_MODEL_STRING = '{RefNet}arc'
fire_conditions = list()


def extract_feature(thing, feature):
    feature_string = '{RefNet}' + feature
    if thing.find(feature_string) is not None:
        features = thing.findall(feature_string)
        return [item.find('{RefNet}text').text for item in features]
    else:
        return 0

def plug_nets_names_with_token_names(transition_dict):
    for transition in transition_dict.keys():
        if transition_dict[transition]['create']:
            for instance in transition_dict[transition]['create']:
                token_name = instance.split(':')[0]
                net_name = instance.split(' ')[-1]
                nets_info[net_name]['tokens'].append(token_name)

def init():
    args = sys.argv[1:]
    
    INPUT_FILES = [str(arg) for arg in args]
    splited_filenames = [INPUT_FILE.split('.') for INPUT_FILE in INPUT_FILES]

    for splited_filename in splited_filenames:
        if len(splited_filename) < 2:
            raise Exception(EXTENSION_FORMAT_ERROR_MESSAGE)

    BASE_FILENAMES = [splited_filename[0]
                      for splited_filename in splited_filenames]

    nets = BASE_FILENAMES
    transition_dicts = dict.fromkeys(nets, 0)
    place_dicts = dict.fromkeys(nets, 0)
    arc_dicts = dict.fromkeys(nets, 0)

    net_label = 1

    for net in nets:
        if 'SN' not in net:
            nets_info[net] = dict()
            nets_info[net]['label'] = net_label
            net_label += 1
            nets_info[net]['tokens'] = list()
        else:
            nets_info[net] = dict() if net not in nets_info.keys() else None
            nets_info[net]['tokens'] = list()

    EXTENSIONS = [splited_filename[1]
                  for splited_filename in splited_filenames]

    OUTPUT_FILENAME = BASE_FILENAMES[0] + ".pml"

    for EXTENSION in EXTENSIONS:
        if EXTENSION != 'pnml':
            raise Exception(EXTENSION_FORMAT_ERROR_MESSAGE)

    initial_trees = [(ElementTree.parse(INPUT_FILE), INPUT_FILE.split('.')[0])
                     for INPUT_FILE in INPUT_FILES]

    return ([(initial_tree[0].getroot()[0], initial_tree[1]) for initial_tree in initial_trees],
    OUTPUT_FILENAME,
    transition_dicts,
    place_dicts,
    arc_dicts)


def parse_transitions(root):
    transition_dict = dict()
    raw_transition_elements = list(root[0].iter(TRANSITION_TAG_MODEL_STRING))

    """ parsed_transition_elements = list of tuples: (id, name) """
    parsed_transition_elements = [
        (
            raw_transition_elements[i].attrib['id'],
            extract_feature(raw_transition_elements[i], 'name'),
            extract_feature(raw_transition_elements[i], 'create'),
            extract_feature(raw_transition_elements[i], 'uplink'),
            extract_feature(raw_transition_elements[i], 'downlink'),

        )
        for i in range(0, len(raw_transition_elements))]

    """ transition_dict = {'id'.value:{'name':value; matrix_id}}} """
    for transition in parsed_transition_elements:
        transition_dict[transition[0]] = dict(
            [
                ('name', transition[1]),
                ('create', transition[2]),
                ('uplink', transition[3]),
                ('downlink', transition[4]),
            ])

    transition_dicts[root[1]] = transition_dict


def parse_places(root):
    place_dict = dict()
    raw_place_elements = list(root[0].iter(PLACE_TAG_MODEL_STRING))

    """ parsed_place_elements = list of tuples:
                   (id, name, initialMarking{value|None}) """
    parsed_place_elements = [
        (
            raw_place_elements[i].attrib['id'],
            extract_feature(raw_place_elements[i], 'name'),
            extract_feature(raw_place_elements[i], 'initialMarking')
        )
        for i in range(0, len(raw_place_elements))]

    """ place_dict = {'id'.value:{'name'; 'marking'; matrix_id}} """
    for place in parsed_place_elements:
        place_dict[place[0]] = dict(
            [
                ('name', place[1]),
                ('marking', place[2]),
            ])

    place_dicts[root[1]] = place_dict


def parse_arcs(root):
    arc_dict = dict()
    raw_arc_elements = list(root[0].iter(ARC_TAG_MODEL_STRING))

    """ parsed_arc_elements = list of tuples:
                   (id, name, inscription{value|None}) """
    def make_mark_dict(arc):
        mark_dict = dict()
        for mark in arc.findall('{RefNet}inscription'):
            if mark in mark_dict.keys():
                mark_dict[mark.find('{RefNet}text').text] += 1
            else:
                mark_dict[mark.find('{RefNet}text').text] = 1
        return mark_dict
    parsed_arc_elements = [
        (
            raw_arc_elements[i].attrib['id'],
            raw_arc_elements[i].attrib['source'],
            raw_arc_elements[i].attrib['target'],
            make_mark_dict(raw_arc_elements[i])
        )
        for i in range(0, len(raw_arc_elements))]

    """ arc_dict = {'source'.value:{'id'; 'target'; 'marking':token count}} """
    for arc in parsed_arc_elements:
        if arc[1] in arc_dict.keys():
            arc_dict[arc[1]].append(dict(
                    [
                        ('id', arc[0]),
                        ('target', arc[2]),
                        ('marking', arc[3])
                    ])
            )

        else:
            arc_dict[arc[1]] = [dict(
                    [
                        ('id', arc[0]),
                        ('target', arc[2]),
                        ('marking', arc[3])
                    ])]

    arc_dicts[root[1]] = arc_dict


def get_arc_by_target(target, arcs):
    out = list()
    for arc_key in arcs.keys():
        for arc in arcs[arc_key]:
            if arc['target'] == target:
                out.append((arc_key, arc))
    return out

def parse_net_tokens(transition_dicts):
    for net in transition_dicts.keys():
        plug_nets_names_with_token_names(transition_dicts[net])

def define_fire_conditions(net, transition_dict, arc_dict, place_dict):
    fire_conditions = dict()
    for transition_key in transition_dict.keys():
        arcs = get_arc_by_target(transition_key, arc_dict)
        conditions = list()
        for arc in arcs:
            for mark in arc['marking'].keys():
                if mark == '[]':
                    origin = str(place_dict[arc[0]]['name'])
                    condition = origin + " > " + str(arc['marking'][mark])
                    conditions.append(condition)
                elif mark.upper() in nets:
                    origin = str(place_dict[arc[0]]['name'])
                    condition = origin + " ?? [_" + str(arc['marking'][mark])


# def print_places_status():
#     out = "Places status: "
#     repr_places = ""
#     name_places = ""
#     for key in sorted(place_dict.keys()):
#         repr_places += "p" + place_dict[key]['name'] + " = %d "
#         name_places += "p" + place_dict[key]['name'] + ", "
#     repr_places = repr_places[:-1] + "\", "
#     name_places = name_places[:-2]
#     out = out + repr_places + name_places
#     return out


def create_fire_sentences_strings():
    sentences = list()
    for condition in fire_conditions:
        stout = "::atomic{"
        stcondition = ""
        stoperation = ""
        while len(condition['cost']) > 0:
            popped_cost = condition['cost'].pop()
            stcondition += popped_cost[0]
            stoperation += popped_cost[1] + "; "
            if len(condition['cost']) > 0:
                stcondition += " && "
        stout += stcondition + " -> " + stoperation

        for statement in condition['fire']:
            stout = stout + statement + "; "

        stout = stout + "printf(\"\\nFiring {} ->  {});".format(
            condition['name'], print_places_status()) + "}"
        sentences.append(stout)
    return sentences


def generate_promela_code():
    # creating promela structures
    f = open(OUTPUT_FILENAME, "w")
    f.write("active proctype P() {\n")
    for key in sorted(place_dict.keys()):
        f.write("byte p{} = {};\n".format(
            place_dict[key]['name'], place_dict[key]['marking']))

    lines_to_copy = create_fire_sentences_strings()
    f.write("do{}\n".format(lines_to_copy.pop()))
    for line in lines_to_copy:
        f.write("  {}\n".format(line))
    f.write("od")

    f.write("}\n")

    f.close()


roots, OUTPUT_FILENAME, transition_dicts, place_dicts, arc_dicts = init()

for root in roots:
    parse_transitions(root)
    parse_places(root)
    parse_arcs(root)

parse_net_tokens(transition_dicts)
print(place_dicts)
print(transition_dicts)
print(arc_dicts)
print(nets_info)
# define_fire_conditions()
# generate_promela_code()


#processar tokens por nome rede
#atribuir etiqueta a transições relacionadas
#Downlink SN1 ?? [_,1]
#uplink !pc ?? [eval(_pid),2]
#      gbChan ? _,eval(_pid),2,pc
# Comparar arcos dos lugares com net tokens para saber se é um canal
#quando lugar recebe net token e black dot gerar erro