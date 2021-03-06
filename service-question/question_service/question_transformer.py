

import re
from functools import reduce


def recognize_project_request(message_text,channel_id,mention=False):
    """
    Try to find a project configuration event in a string
    :param message_text:
    :param channel_id:
    :return:
    """
    project_setup = [
        "project setup"
        "setup"
        "setup project"
        "setup git"
        "setup repository"
        "repository setup"
        "git setup"
        "channel setup"
        "setup channel"
    ]
    if any(message_text in s for s in project_setup):
        # self.publish("sofia.channel.{0}.messages.RequestProjectConfig".format(channel_id), {"msh": "test"})
        return  {   'channel': u'sofia.channel.{0}.messages.RequestProjectConfig'.format(channel_id),
                    'data': {}
                }
    else:
        return None


def recognize_namepsace(message_text, channel_id,mention=False):
    """
    Try to find namespaces in the message
    :param message_text:
    :param channel_id:
    :return:
    """
    splits = message_text.split(" ")

    #check for namespace pattern
    namespaces = map(lambda part: re.search("^([a-z_]{1}[a-z0-9_]*(\.[a-z_]{1}[a-z0-9_]*)+)$", part),splits)
    namespaces = filter(lambda x: x is not None, namespaces)

    namespaces  = map(lambda x: x.group(), namespaces)
    namespaces_events  = map(lambda x:
                              {'channel': u'sofia.channel.{0}.messages.Namespace'.format(channel_id),
                               'data': {"namespace": x}
                              }
                             , namespaces)

    namespaces_events = list(namespaces_events)
    #check for questions like "show me namespace gui"

    splits = list(splits)
    for split in splits:
        if(split =="namespace"):
            index = splits.index(split)
            if len(splits) >= index+1:
                nextWord = splits[index+1]
                if len([c for c in nextWord if not c.islower()]) == 0 and len(nextWord.split(".")) == 1:
                    namespaces_events.append(
                               {'channel': u'sofia.channel.{0}.messages.Namespace'.format(channel_id),
                               'data': {"namespace": nextWord}
                              })

    return list(namespaces_events)

def recognize_class_name(message_text, channel_id, mention=False):
    """
    Try to find class names (camelcase based)  in  a string
    :param message_text:
    :param channel_id:
    :return:
    """
    splits = message_text.split(" ")
    splits = map(lambda part: re.search("[A-Z]([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|[a-z0-9]*[A-Z][A-Z0-9]*[a-z])[A-Za-z0-9]*", part),splits)
    splits = filter(lambda x: x is not None, splits)
    classNames = map(lambda x: x.group(), splits)
    events = map(lambda x:  {'channel': u'sofia.channel.{0}.messages.ClassName'.format(channel_id),
                               'data': {"className": x}
                              }, classNames)

    return list(events)


def recognize_events_from_str(message_text, channel_id,mention=False):
    """
    Try to recognize as many as possible events from a string
    :param message_text:
    :param channel_id:
    :return: List oft events
    """

    events = list()

    events.append(recognize_project_request(message_text,channel_id,mention))
    events.append(recognize_namepsace(message_text,channel_id,mention))
    events.append(recognize_class_name(message_text,channel_id,mention))
    events.append(recognize_more_info(message_text,channel_id,mention))

    # flattern event list (transfrom list [[{},{}],[{}],{}] into [{},{},{}]
    results = list()
    for event in events:
        if isinstance(event, list):
            for e in event:
                if isinstance(e,object):
                    results.append(e)
        elif event is not None:
            print(event)
            results.append(event)

    #Return list of events
    return results

def recognize_more_info(message_text, channel_id,mention):

    text = message_text.lower()
    if mention:
        cases = [
            "more info ",
            "give me more ",
            "info please ",
            "information please",
            "could you tell me more ",
            "tell me more "
        ]
        if any(message_text.lower().find(s) <=0 for s in cases):

            namespace = recognize_namepsace(message_text,channel_id,mention)
            classes = recognize_class_name(message_text,channel_id,mention)
            type = 'unknown'
            if(len(namespace) >= 1):
                type = 'namespace'
            if(len(classes) >= 1):
                type = 'class'

            return {'channel': u'sofia.channel.{0}.messages.MoreInfo'.format(channel_id),
                    'data': {'type': type}
                    }
        else:
            return None