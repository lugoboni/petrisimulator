#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from xml.etree import ElementTree

EXTENSION_FORMAT_ERROR_MESSAGE = "This script works only with pnml files"
NON_CHANNEL_WITH_BLACK_DOT = "A black dot was found in channel place "
NON_PROCESSED_NET_TOKEN = "A not processed net token was found"
NON_PROCESSED_TOKEN = "A not processed token was found"
DOWNLINK_NEEDS_INPUT_ARC = "A downlink transition needs an input arc"
DOWNLINK_NEEDS_INPUT_CHANNEL_PLACE = "A downlink transition needs an input channel_place"
COMMON_TOKEN_ON_CHANNEL_PLACE = "A channel place can not handle with a non net token"
ELEMENT_NET_PREFIX = "EN"
PROMELA_PRE_FUNCTIONS = [
    "#define NetPlace(d) chan d = [18] of {byte, byte}\n",
    "\n\n",
    "/*###############################################*/\n",
    "\n\n",
    "chan cha =[18] of {byte,byte}; hidden byte j, size_cha;\n",
    "\n\n",
    "/*###############################################*/\n",
    "\n\n",
    "inline consNetTok(c, p) {\n",
    "  do:: c ?? [eval(p),_] -> c ?? eval(p),_;\n",
    "    :: else -> break\n",
    "  od; skip }\n",
    "\n\n",
    "inline rmConf(l){\n",
    "  if :: pc ?? [eval(_pid),l] -> pc ?? eval(_pid),l\n",
    "     :: else fi\n",
    "}\n",
    "\n\n",
    "/*###############################################*/\n",
    "\n\n",
    "inline transpNetTok(ch, och, p){\n",
    "  do:: ch ?? [eval(p),_] ->\n",
    "       ch ?? eval(p),lt;\n",
    "       och !! p,lt;\n",
    "    :: else -> break\n",
    "  od; skip }\n",
    "\n\n",
    "/*###############################################*/\n",
    "hidden byte i;\n",
    "hidden unsigned nt:4,lt:4, nt1:4, lt1:4;\n",
    "\n\n",
    "inline recMsg(ch,f0,f1) {             /* ch - ordered \"channel, f0 - output variable, f1 - constant value */\n",
    "ch ! 0,f1;\n",
    "do :: ch ?? f0,f1;\n",
    "       if :: f0>0 ->   ch !  f0,f1; \n",
    "                       cha ! len(cha)+1,f0;\n",
    "          :: else -> break\n",
    "       fi\n",
    "od;\n",
    "\n\n",
    " /* select ( j : 1 .. size_cha); */\n",
    "\n\n",
    "    size_cha= len(cha);\n",
    "   j = 1;\n",
    "   do\n",
    "   :: j < size_cha -> j++\n",
    "   :: break\n",
    "   od\n",
    "\n\n",
    "cha ?? <eval(j),f0>;\n",
    "\n\n",
    " /* restoring the ordering of the input channel */\n",
    "  \n",
    "do :: len(cha)>0 -> \n",
    "   cha?_,nt1;\n",
    "   ch ?? eval(nt1),eval(f1);\n",
    "   ch !! nt1,f1;\n",
    "   :: else -> break\n",
    "od; \n",
    "\n\n",
    "ch ?? eval(f0),f1;   /* message selected by the receive */\n",
    "\n\n",
    "}\n",
    "\n\n",
    "/*###############################################*/\n",
    "\n\n",
    "#define sp(a,b)    set_priority(a,b)\n",
    "\n\n",
    "/*###############################################*/\n",
    "\n\n",
    "chan gbChan = [18] of {byte, byte, byte, chan};\n",
    "\n\n",
    "/*###############################################*/ \n"]

nets = None
nets_info = dict()
net_tokens_list = dict()
transition_dicts = None
place_dicts = None
sync_dict = None
transition_label_dict = None
arc_dicts = None
system_net = None
channel_places = set()
TRANSITION_TAG_MODEL_STRING = '{RefNet}transition'
PLACE_TAG_MODEL_STRING = '{RefNet}place'
ARC_TAG_MODEL_STRING = '{RefNet}arc'
fire_conditions = list()
OUTPUT_FILENAME = "NetTranslated"


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
                net_name = net_name.split('()')[0]
                nets_info[net_name]['tokens'].append(token_name)
                if token_name in net_tokens_list.keys():
                    net_tokens_list[token_name].add(net_name)
                else:
                    net_tokens_list[token_name] = set()
                    net_tokens_list[token_name].add(net_name)


def plug_function_name_with_sync_transitions(transition_dict, sync_dict, transition_label_dict, lid):
    label = lid
    for transition in transition_dict.keys():
        if transition_dict[transition]['uplink']:
            for uplink in transition_dict[transition]['uplink']:
                name = uplink.split(
                    " ")[1] if " " in uplink else uplink.split(":")[1]
                if name in sync_dict.keys():
                    sync_dict[name]['transitions'].append(transition)
                    transition_label_dict[transition] = sync_dict[name]['label']
                else:
                    sync_dict[name] = dict()
                    sync_dict[name]['transitions'] = list()
                    label += 1
                    sync_dict[name]['label'] = label
                    sync_dict[name]['transitions'].append(transition)
                    transition_label_dict[transition] = sync_dict[name]['label']
        if transition_dict[transition]['downlink']:
            for downlink in transition_dict[transition]['downlink']:
                name = downlink.split(
                    " ")[1] if " " in downlink else downlink.split(":")[1]
                if name in sync_dict.keys():
                    sync_dict[name]['transitions'].append(transition)
                    transition_label_dict[transition] = sync_dict[name]['label']
                else:
                    sync_dict[name] = dict()
                    sync_dict[name]['transitions'] = list()
                    label += 1
                    sync_dict[name]['label'] = label
                    sync_dict[name]['transitions'].append(transition)
                    transition_label_dict[transition] = sync_dict[name]['label']
    return label


def init(OUTPUT_FILENAME):
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
        nets_info[net]['id'] = 0

    EXTENSIONS = [splited_filename[1]
                  for splited_filename in splited_filenames]

    OUTPUT_FILENAME = OUTPUT_FILENAME + ".pml"

    for EXTENSION in EXTENSIONS:
        if EXTENSION != 'pnml':
            raise Exception(EXTENSION_FORMAT_ERROR_MESSAGE)

    initial_trees = [(ElementTree.parse(INPUT_FILE), INPUT_FILE.split('.')[0])
                     for INPUT_FILE in INPUT_FILES]
    for tree in initial_trees:
        nets_info[tree[1]]['id'] = tree[0].find('{RefNet}net').attrib['id']

    return ([(initial_tree[0].getroot()[0], initial_tree[1]) for initial_tree in initial_trees],
            OUTPUT_FILENAME,
            transition_dicts,
            place_dicts,
            arc_dicts,
            BASE_FILENAMES[0])


def parse_transitions(root):
    transition_dict = dict()
    raw_transition_elements = list(root[0].iter(TRANSITION_TAG_MODEL_STRING))

    parsed_transition_elements = [
        (
            nets_info[root[1]]['id'] + raw_transition_elements[i].attrib['id'],
            extract_feature(raw_transition_elements[i], 'name'),
            extract_feature(raw_transition_elements[i], 'create'),
            extract_feature(raw_transition_elements[i], 'uplink'),
            extract_feature(raw_transition_elements[i], 'downlink'),

        )
        for i in range(0, len(raw_transition_elements))]

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

    parsed_place_elements = [
        [
            nets_info[root[1]]['id'] + raw_place_elements[i].attrib['id'],
            extract_feature(raw_place_elements[i], 'name'),
            extract_feature(raw_place_elements[i], 'initialMarking')
        ]
        for i in range(0, len(raw_place_elements))]

    for place in parsed_place_elements:
        marking = dict()
        if place[2]:
            for mark in place[2]:
                if mark in marking.keys():
                    marking[mark] = marking[mark] + 1
                else:
                    marking[mark] = 1
        place[2] = marking

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
            nets_info[root[1]]['id'] + raw_arc_elements[i].attrib['id'],
            nets_info[root[1]]['id'] + raw_arc_elements[i].attrib['source'],
            nets_info[root[1]]['id'] + raw_arc_elements[i].attrib['target'],
            make_mark_dict(raw_arc_elements[i])
        )
        for i in range(0, len(raw_arc_elements))]

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


def check_channel_non_channel_places(non_channel):
    for place in non_channel:
        if place in channel_places:
            raise Exception(NON_CHANNEL_WITH_BLACK_DOT + place)


def parse_channel_places(place_dicts, arc_dicts, system_net):
    not_channel = list()
    for place in place_dicts[system_net].keys():
        arcs = get_arc_by_target(place, arc_dicts[system_net])
        for arc in arcs:
            for token in arc[1]['marking'].keys():
                if token in net_tokens_list.keys():
                    channel_places.add(place)
                else:
                    not_channel.append(place)
    check_channel_non_channel_places(not_channel)


def parse_net_tokens(transition_dicts):
    for net in transition_dicts.keys():
        plug_nets_names_with_token_names(transition_dicts[net])


def parse_connected_transitions(transition_dicts):
    sync_dict = dict()
    transition_label_dict = dict()
    lid = 0
    for net in transition_dicts.keys():
        lid = plug_function_name_with_sync_transitions(
            transition_dicts[net], sync_dict, transition_label_dict, lid)

    return sync_dict, transition_label_dict


def define_fire_conditions(transition_dict, arc_dict, place_dict):
    fire_conditions = dict()
    for transition_key in transition_dict.keys():
        arcs = get_arc_by_target(transition_key, arc_dict)
        uplink = transition_dict[transition_key]['uplink']
        downlink = transition_dict[transition_key]['downlink']
        create = transition_dict[transition_key]['create']
        if transition_key in transition_label_dict.keys():
            label = transition_label_dict[transition_key]
        else:
            label = 0

        fire_conditions[transition_key] = {
            'arcs': arcs,
            'create': create,
            'label': label,
            'conditions': list()
        }

        general_condition = list()
        if uplink:
            fire_uplink_condition = "gbChan ? _,eval(_pid),{0},pc".format(
                label)
            fire_conditions[transition_key]['conditions'].append(fire_uplink_condition)

            condition = "empty(gbChan) && !pc ?? [eval(_pid),{0}]".format(
                label)

            general_condition.append(condition)

        elif downlink:
            if arcs:
                origins = list()
                for arc in arcs:
                    if arc[0] in channel_places:
                        origin = place_dict[arc[0]]['name'][0]
                        origins.append(origin)

                if origins:
                    condition = "empty(gbChan) "
                    for origin in origins:
                        condition = condition + \
                            "&& {0} ?? [_,{1}] ".format(origin, label)
                    general_condition.append(condition)
                else:
                    raise Exception(DOWNLINK_NEEDS_INPUT_CHANNEL_PLACE)

            else:
                raise Exception(DOWNLINK_NEEDS_INPUT_ARC)

        else:

            condition = "empty(gbChan)"
            general_condition.append(condition)

        if arcs:
            for arc in arcs:
                if arc[1]['marking'].keys():
                    for mark in arc[1]['marking'].keys():
                        if mark not in net_tokens_list.keys():
                            origin = place_dict[arc[0]]['name'][0]
                            condition = origin + " > " + \
                                str(arc[1]['marking'][mark])
                            general_condition.append(condition)

                        elif mark in net_tokens_list.keys() and arc[0] in channel_places:
                            pass  # avaliar
                        elif mark not in net_tokens_list.keys() and arc[0] in channel_places:
                            raise Exception(COMMON_TOKEN_ON_CHANNEL_PLACE)
                        else:
                            raise Exception(NON_PROCESSED_TOKEN)

                else:
                    if arc[0] not in channel_places:
                        origin = place_dict[arc[0]]['name'][0]
                        condition = origin + " > " + '0'
                        general_condition.append(condition)

                    else:
                        general_condition.append("1")  # avaliar

        else:  # If there's no arc inciding on the transition
            condition = "1"
            general_condition.append(condition)

        fire_condition = ""
        for condition in general_condition:
            fire_condition = fire_condition + " && " + condition
        fire_condition = fire_condition[4:]

        fire_conditions[transition_key]['conditions'].append(fire_condition)

    return fire_conditions


def test_arcs_channel_place(arcs):
    for arc in arcs:
        if arc[0] in channel_places:
            return True


def define_fire_actions(fire_conditions, arc_dict, place_dict, transition_dict, net_name):
    fire_actions = list()
    for transition in transition_dict.keys():
        for condition in fire_conditions[transition]['conditions']:
            sentences = list()

            if "!pc" in condition:
                wait_sentences = list()
                sentence = "pc !! _pid, {};\n".format(fire_conditions[transition]['label'])
                wait_sentences.append(sentence)
                sentence = "printf(\"Transicao " + \
                    "{} em espera".format(transition) + "\\n\\n\");\n"
                wait_sentences.append(sentence)
                fire_actions.append([condition, wait_sentences])
                continue

            elif "_,eval(_pid)" in condition:
                sentence = "printf(\"Transicao " + \
                    "{} disparada".format(transition) + "\\n\\n\");\n"
                sentences.append(sentence)
            if arc_dict[transition]:
                for arc in arc_dict[transition]:
                    dest_place = place_dict[arc['target']]['name'][0]
                    if arc['target'] in channel_places:
                        if arc['marking']:
                            if fire_conditions[transition]['create']:
                                for new_instance in fire_conditions[transition]['create']:
                                    net = new_instance.split("()")[0][-1]
                                    token = new_instance.split("()")[0][0]
                                    if token in arc['marking']:
                                        # checar mark do arco
                                        element_net_name = ELEMENT_NET_PREFIX + \
                                            str(net)
                                        sentence = "nt = run {1}({0}); {0} !! nt, 15;".format(
                                            dest_place, element_net_name)
                                        sentence.format(
                                            dest_place, element_net_name)
                                        sentences.append(sentence)
                                        sentence = "printf(\"Produzindo net tokens \\n\\n\");"
                                        sentences.append(sentence)
                                    else:
                                        pass
                        else:
                            pass

                        if test_arcs_channel_place(fire_conditions[transition]['arcs']):
                            for origin_arc in fire_conditions[transition]['arcs']:
                                if origin_arc[0] in channel_places:
                                    origin_name = place_dict[origin_arc[0]
                                                             ]['name'][0]

                                    if origin_arc[1]['marking']:
                                        if arc['marking']:
                                            for mark in origin_arc[1]['marking']:
                                                if mark in arc['marking'] and mark in net_tokens_list:
                                                    sentence = "recMsg({0}, nt, {1});".format(
                                                        origin_name, fire_conditions[transition]['label'])
                                                    sentences.append(sentence)
                                                    sentence = "transpNetTok({0},{1},nt);".format(
                                                        origin_name, dest_place)
                                                    sentences.append(sentence)
                                                    sentence = "gbChan !! 6-5, nt,1,{};".format(
                                                        dest_place)
                                                    sentences.append(sentence)
                                                    sentence = "sp(nt, 5);"
                                                    sentences.append(sentence)
                                                    sentence = "printf(\"{0} Recebendo {1} \\n\\n\");".format(
                                                        dest_place,
                                                        mark)
                                                    sentences.append(sentence)
                                                else:
                                                    pass
                                        else:
                                            for mark in origin_arc[1]['marking']:
                                                if mark in net_tokens_list:
                                                    sentence = "consNetTok({0}, {1});".format(
                                                        origin_name, fire_conditions[transition]['label'])
                                                    sentences.append(sentence)
                                                    sentence = "printf(\" Consuming {1} from {0} \\n\\n\");".format(
                                                        origin_name, mark)
                                                    sentences.append(sentence)

                                    else:
                                        if arc['marking']:
                                            pass

                                        else:
                                            pass

                        else:
                            pass

                    elif arc['target'] not in channel_places and "!pc" not in condition:

                        if arc['marking'].keys():
                            for mark in arc['marking'].keys():
                                if mark not in net_tokens_list.keys():
                                    sentence = "{0} = {0} + {1};".format(
                                        dest_place, arc['marking'][mark])
                                    sentences.append(sentence)
                        else:
                            sentence = "{0} = {0} + 1;".format(dest_place)
                            sentences.append(sentence)

                        for origin_arc in fire_conditions[transition]['arcs']:
                            origin_name = place_dict[origin_arc[0]]['name'][0]
                            if origin_arc[0] in channel_places:
                                if origin_arc[1]['marking']:
                                    for mark in origin_arc[1]['marking']:
                                        if mark in net_tokens_list:
                                            transp = False
                                            for arc in arc_dict[transition]:
                                                if mark in arc['marking']:
                                                    transp = True
                                                    break
                                            if not transp:
                                                sentence = "consNetTok({0}, {1});".format(
                                                    origin_name, fire_conditions[transition]['label'])
                                                sentences.append(sentence)
                                                sentence = "printf(\" Consuming {1} from {0} \\n\\n\");".format(
                                                    origin_name, mark)
                                                sentences.append(sentence)
                                            else:
                                                pass
                                        else:
                                            pass
                                else:
                                    pass
                            else:
                                if origin_arc[1]['marking']:
                                    for mark in origin_arc[1]['marking']:
                                        sentence = "{0} = {0} - {1};".format(
                                            origin_name, origin_arc[1]['marking'][mark])
                                        sentences.append(sentence)
                                else:
                                    sentence = "{0} = {0} - 1;".format(origin_name)
                                    sentences.append(sentence)
            else:
                if test_arcs_channel_place(fire_conditions[transition]['arcs']):
                    for origin_arc in fire_conditions[transition]['arcs']:
                        origin_name = place_dict[origin_arc[0]]['name'][0]
                        if origin_arc[0] in channel_places:
                            if origin_arc[1]['marking']:
                                for mark in origin_arc[1]['marking']:
                                    if mark in net_tokens_list:
                                        sentence = "consNetTok({0}, {1});".format(
                                            origin_name, fire_conditions[transition]['label'])
                                        sentences.append(sentence)
                                        sentence = "printf(\" Consuming {1} from {0} \\n\\n\");".format(
                                            origin_name, mark)
                                        sentences.append(sentence)

                                    else:
                                        raise Exception(NON_CHANNEL_WITH_BLACK_DOT)

                            else:
                                pass
                        else:
                            if origin_arc[1]['marking']:
                                for mark in origin_arc[1]['marking']:
                                    sentence = "{0} = {0} - {1};".format(
                                        origin_name, origin_arc[1]['marking'][mark])
                                    sentences.append(sentence)
                            else:
                                sentence = "{0} = {0} - 1;".format(origin_name)
                                sentences.append(sentence)


            fire_actions.append([condition, sentences])

    return fire_actions


def create_initial_marking(place_dict):
    initial_marking = list()
    for key in place_dict:
        if key in channel_places:
            for mark in place_dict[key]['marking'].keys():
                if mark not in net_tokens_list.keys():
                    raise Exception(NON_PROCESSED_TOKEN)
            create_net_place = "NetPlace({});\n".format(
                place_dict[key]['name'][0])
            initial_marking.append(create_net_place)
        else:
            if place_dict[key]['marking'].keys():
                for mark in place_dict[key]['marking'].keys():
                    if mark not in net_tokens_list.keys():
                        marking = "byte {0} = {1};\n".format(
                            place_dict[key]['name'][0],
                            place_dict[key]['marking'][mark])
                        initial_marking.append(marking)
            else:
                marking = "byte {0} = {1};\n".format(
                    place_dict[key]['name'][0],
                    0)
                initial_marking.append(marking)

    return(initial_marking)


def generate_promela_code():
    f = open(OUTPUT_FILENAME, "w")
    for line in PROMELA_PRE_FUNCTIONS:
        f.write(line)
    for net in nets_info.keys():
        initial_marking = create_initial_marking(place_dicts[net])
        conditions = define_fire_conditions(
            transition_dicts[net],
            arc_dicts[net],
            place_dicts[net])
        actions = define_fire_actions(
            conditions,
            arc_dicts[net],
            place_dicts[net],
            transition_dicts[net],
            net)
        if net in system_net:
            for mark in initial_marking:
                f.write(mark)
            f.write("init {\n\n")
            f.write("   atomic{\n")
            f.write("       printf(\"SN setting initial marking\\n\\n\");\n")
            f.write("   }\n\n")
            f.write("   endl: do\n")
            for action in actions:
                f.write("       ::atomic{" + " {} ->\n".format(action[0]))
                f.write("           sp(_pid,6);\n")
                for production in action[1]:
                    f.write("           {}\n".format(production))
                f.write("           sp(_pid,1);\n")
                f.write("       }\n\n")
            f.write("   od\n")
            f.write("}\n")
        else:
            net_name = ELEMENT_NET_PREFIX + net
            f.write("proctype {} (chan pc)".format(net_name))
            f.write("{\n")
            for mark in initial_marking:
                f.write("   {}".format(mark))
            f.write("   endl: do\n")
            for action in actions:
                f.write("       ::atomic {" + "{} ->\n".format(action[0]))
                for production in action[1]:
                    f.write("           {}\n".format(production))
                f.write("       }\n\n")
            f.write("   od\n")
            f.write("}\n\n")
            f.write("/*###############################################*/\n\n")
    f.close()


roots, OUTPUT_FILENAME, transition_dicts, place_dicts, arc_dicts, system_net = init(
    OUTPUT_FILENAME)

for root in roots:
    parse_transitions(root)
    parse_places(root)
    parse_arcs(root)

parse_net_tokens(transition_dicts)
sync_dict, transition_label_dict = parse_connected_transitions(
    transition_dicts)
parse_channel_places(place_dicts, arc_dicts, system_net)
generate_promela_code()
