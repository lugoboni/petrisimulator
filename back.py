            if transition in arc_dict.keys():
                for arc in arc_dict[transition]:
                    if arc not in arc_dict.keys():                
                        dest_place = place_dict[arc['target']]['name'][0]
                        if condition[3]: # if create


                        if condition[0]:
                            origin_name = place_dict[condition[0]]['name'][0]
                            if condition[0] in channel_places and arc['target'] in channel_places:
                                sentence = "recMsg({0}, nt, {1});".format(origin_name, condition[5])
                                sentences.append(sentence)
                                sentence = "transpNetTok({0},{1},nt);".format(origin_name, dest_place)
                                sentences.append(sentence)
                                sentence = "gbChan !! 6-5, nt,1,{};".format(dest_place)
                                sentences.append(sentence)
                                sentence = "sp(nt, 5);"
                                sentences.append(sentence)
                                sentence = "printf(\"{0} Recebendo {1} \\n\\n\");".format(
                                    dest_place,
                                    condition[4].keys()[0]) #sempre o primeiro?
                                sentences.append(sentence)

                            if condition[0] not in channel_places and "!pc" not in condition[-1]:
                                if condition[4] and condition[4].keys():
                                    for mark in condition[4].keys():
                                        if mark not in net_tokens_list.keys():
                                            sentence = "{0} = {0} - {1};".format(origin_name, condition[4][mark])
                                            sentences.append(sentence)
                                            break
                                else:
                                    sentence = "{0}--;".format(origin_name)
                                    sentences.append(sentence)               



                        if "!pc" in condition[-1]:
                            sentence = "pc !! _pid, {};\n".format(condition[5])
                            sentences.append(sentence)
                            sentence = "printf(\"Transicao EN"+"{} em espera".format(net_name)+"\\n\\n\");\n"
                            sentences.append(sentence)

                        if "_,eval(_pid)" in condition[-1]:
                            sentence = "printf(\"Transicao EN"+"{} disparada".format(net_name)+"\\n\\n\");\n"
                            sentences.append(sentence)                
            else:
                sentences.append("-+-+-+-+-+-+-+-+-+-+-+-+-=-+-+-+")