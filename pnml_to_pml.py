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

""" parsed_place_elements =	list of tuples:
               (id, name, initialMarking{value|None}) """
parsed_place_elements = [
    (
        raw_place_elements[i].attrib['id'],
        raw_place_elements[i].find('{RefNet}name').find('{RefNet}text').text,
        raw_place_elements[i].find(
            '{RefNet}initialMarking').find('{RefNet}text').text
        if raw_place_elements[i].find('{RefNet}initialMarking') is not None
        else None
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

""" transition_dict = {'id'.value:{'name':value}} """
for transition in parsed_transition_elements:
    transition_dict[transition[0]] = dict(
        [
            ('name', transition[1])
        ])

""" arc_dict = {'source'.value:{'id'; 'target'; 'marking'}} """
for arc in parsed_arc_elements:
    arc_dict[arc[1]] = dict(
            [
                ('id', arc[0]),
                ('target', arc[2]),
                ('marking', len(arc[3]))
            ])

""" place_dict = {'id'.value:{'name'; 'marking'}} """
for place in parsed_place_elements:
    place_dict[place[0]] = dict(
        [
            ('name', place[1]),
            ('marking', place[2])
        ])


""" building pre_matrix post matrix """
transition_rows_value = len(transition_dict)
place_col_value = len(place_dict)

base_col = [0 for i in range(0, place_col_value)]

pre_matrix = [list(base_col) for i in range(0, transition_rows_value)]
post_matrix = [list(base_col) for i in range(0, transition_rows_value)]

i = 0
for transition in transition_dict:
    j = 0
    for place in place_dict:
        if place in arc_dict.keys():
            if arc_dict[place]['target'] == transition:
                pre_matrix[i][j] = arc_dict[place]['marking']
        if transition in arc_dict.keys():
            if arc_dict[transition]['target'] == place:
                post_matrix[i][j] = arc_dict[transition]['marking']
        j = j + 1
    i = i + 1


# creating promela structures
f = open(OUTPUT_FILENAME, "w")
f.write("#define R {}\n".format(transition_rows_value))
f.write("#define C {}\n".format(place_col_value))
f.write("typedef VECTOR {\n")
f.write("	byte vector[C];\n")
f.write("};\n")
f.write("VECTOR pre_matrix[R];\n")
f.write("VECTOR post_matrix[R];\n")
f.write("init {\n")

for i in range(0, transition_rows_value):
    for j in range(0, place_col_value):
        f.write("	pre_matrix[{}].vector[{}] = {};\n".format(
            i, j, pre_matrix[i][j]))

for i in range(0, transition_rows_value):
    for j in range(0, place_col_value):
        f.write("	post_matrix[{}].vector[{}] = {};\n".format(
            i, j, post_matrix[i][j]))
f.write("}\n")


f.close()
