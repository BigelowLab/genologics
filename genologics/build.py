#!usr/bin/env python

from __future__ import print_function
import re
import urlparse
import datetime
import time
from xml.etree.ElementTree import Element, SubElement, Comment, tostring 
import logging
from genologics.entities import *
from genologics.lims import *



def create_container_node(lims, type_uri = None, name = None):
    '''
    create container xml node, output as string
    Args:
        lims: genologics.lims session
        type_uri (uri as str): uri of desired container type
        name (str): optional 
    Returns:
        xml formatted string
    '''
    if not type_uri:
        raise IOError("type_uri needed to create container node")

    type_name = Containertype(lims, uri=type_uri).name
    nmsp = 'con:container'
    top = Element(nsmap(nmsp)) 
    cname = SubElement(top, 'name')
    if name:
        cname.text = name
    ctype = SubElement(top, 'type uri="%s" name="%s"' % (type_uri, type_name))
    print(tostring(top))
    return tostring(top)
    

def post_container_node(lims, xml_node):
    '''
    post container xml node to lims
    Args:
        lims: genologics.lims session
        xml_node (str): xml-formatted string with all needed info to post
    Returns:
        ElementTree xml response
    '''
    uri = lims.get_uri("containers")
    response = lims.post(uri, xml_node)
    print(Container(lims, response.attrib['uri']).info()
    return(response)





