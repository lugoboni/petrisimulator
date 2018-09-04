#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from xml.etree import ElementTree

EXTENSION_FORMAT_ERROR_MESSAGE = "This script works only with pnml files"


INPUT_FILE = str(sys.argv[1])
splited_filename = INPUT_FILE.split('.')

if len(splited_filename) < 2:
    raise Exception(EXTENSION_FORMAT_ERROR_MESSAGE)

BASE_FILENAME = splited_filename[0]

EXTENSION = splited_filename[1]

OUTPUT_FILENAME = BASE_FILENAME + ".pml"

if EXTENSION != 'pnml':
    raise Exception(EXTENSION_FORMAT_ERROR_MESSAGE)

TRANSITION_TAG_MODEL_STRING = '{RefNet}transition'
PLACE_TAG_MODEL_STRING = '{RefNet}place'
ARC_TAG_MODEL_STRING = '{RefNet}arc'

transition_dict = dict()
place_dict = dict()
arc_dict = dict()


initial_tree = ElementTree.parse(INPUT_FILE)

root = initial_tree.getroot()[0]

raw_transition_elements = list(root.iter(TRANSITION_TAG_MODEL_STRING))

""" parsed_transition_elements = list of tuples: (id, name) """
parsed_transition_elements = [
    (
        raw_transition_elements[i].attrib['id'],
        raw_transition_elements[i].find(
            '{RefNet}name').find('{RefNet}text').text
    )
    for i in range(0, len(raw_transition_elements))]

raw_place_elements = list(root.iter(PLACE_TAG_MODEL_STRING))

""" parsed_place_elements = list of tuples:
               (id, name, initialMarking{value|None}) """
parsed_place_elements = [
    (
        raw_place_elements[i].attrib['id'],
        raw_place_elements[i].find('{RefNet}name').find('{RefNet}text').text,
        len(raw_place_elements[i].findall(
            '{RefNet}initialMarking'))
        if raw_place_elements[i].find('{RefNet}initialMarking') is not None
        else 0
    )
    for i in range(0, len(raw_place_elements))]

raw_arc_elements = list(root.iter(ARC_TAG_MODEL_STRING))

""" parsed_arc_elements = list of tuples:
               (id, name, inscription{value|None}) """
parsed_arc_elements = [
    (
        raw_arc_elements[i].attrib['id'],
        raw_arc_elements[i].attrib['source'],
        raw_arc_elements[i].attrib['target'],
        [j.find('{RefNet}text').text
         if j.find('{RefNet}text') is not None
         else 1
         for j in raw_arc_elements[i].findall('{RefNet}inscription')]

    )
    for i in range(0, len(raw_arc_elements))]

place_to_transition = dict()
""" transition_dict = {'id'.value:{'name':value; matrix_id}}} """
for transition in parsed_transition_elements:
    transition_dict[transition[0]] = dict(
        [
            ('name', transition[1]),
        ])
    place_to_transition[transition[0]] = []
""" arc_dict = {'source'.value:{'id'; 'target'; 'marking':token count}} """
for arc in parsed_arc_elements:
    if arc[1] in arc_dict.keys():
        arc_dict[arc[1]].append(dict(
                [
                    ('id', arc[0]),
                    ('target', arc[2]),
                    ('marking', len(arc[3]))
                ])
        )

    else:
        arc_dict[arc[1]] = [dict(
                [
                    ('id', arc[0]),
                    ('target', arc[2]),
                    ('marking', len(arc[3]))
                ])]

""" place_dict = {'id'.value:{'name'; 'marking'; matrix_id}} """
for place in parsed_place_elements:
    place_dict[place[0]] = dict(
        [
            ('name', place[1]),
            ('marking', place[2]),
        ])


def get_arc_by_target(target):
    out = list()
    for arc_key in arc_dict.keys():
        for arc in arc_dict[arc_key]:
            if arc['target'] == target:
                out.append((arc_key, arc))
    return out



fire_conditions = list()
for transition_key in transition_dict.keys():
    fire_t = dict({'cost': [], 'fire': [], 'name' : transition_dict[transition_key]['name']})
    arcs_with_target_transition = get_arc_by_target(transition_key)
    for arc in arcs_with_target_transition:
        fs = "p" + str(place_dict[arc[0]]['name']) + \
            " >= " + str(arc[1]['marking'])
        name = "p" + str(place_dict[arc[0]]['name'])
        cs = name + " = " + name + \
            " - " + str(arc[1]['marking'])
        fire_t['cost'].append((fs, cs))
    for arc in arc_dict[transition_key]:
        name = "p"+str(place_dict[arc['target']]['name'])
        ds =  name +" = " + name + " + " + str(arc['marking'])
        fire_t['fire'].append(ds)
    fire_conditions.append(fire_t)

def create_fire_sentences_strings():
    sentences = list()
    for condition in fire_conditions:
        stout = "::atomic{"
        stcondition = ""
        stoperation = ""
        while len(condition['cost']) > 0:
            popped_cost = condition['cost'].pop()
            stcondition += popped_cost[0]
            stoperation += popped_cost[1] +"; "
            if len(condition['cost']) > 0:
                stcondition += " && "
        stout += stcondition +" -> "+ stoperation

        for statement in condition['fire']:
            stout = stout + statement + "; "

        stout = stout + "printf(\"Firing {}\\n\");".format(condition['name']) + "}"
        sentences.append(stout)
    return sentences

# creating promela structures
f = open(OUTPUT_FILENAME, "w")
f.write("active proctype P() {\n")
for key in place_dict.keys():
    f.write("byte p{} = {};\n".format(place_dict[key]['name'], place_dict[key]['marking']))


lines_to_copy = create_fire_sentences_strings()
f.write("do{}\n".format(lines_to_copy.pop()))
for line in lines_to_copy:
    f.write("  {}\n".format(line))
f.write("od")

f.write("}\n")


f.close()
