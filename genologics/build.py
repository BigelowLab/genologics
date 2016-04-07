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


def check_node_args(arg):
	if not arg:
		raise IOError("{arg} needed to create node")

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
    print(Container(lims, response.attrib['uri']).info())
    return Container(lims, response.attrib['uri'])

def create_sample_node(name=None, project_uri=None, container_uri = None, 
                       well=None, date_received=None, date_completed=None):
    '''
    create sample xml node as a string

    '''
    check_node_args("name", name)
    check_node_args("project_uri", project_uri)
    check_node_args("container_uri", container_uri)
    check_node_args("well", well)
    
    if len(well.split(":")) != 2:
    	raise IOError('error creating node: well value must be in the format "row : column"')

    nmsp = 'smp:samplecreation'
    top = Element(nsmap(nmsp))
    
    sname = SubElement(top, "name")
    sname.text = name
    
    project = SubElement(top, 'project uri="%s"' % project_uri)
    
    location = SubElement(top, "location")
    container = SubElement(location, 'container uri="%s"' % container_uri)
    value = SubElement(location, "value")
    value.text = well
    
    if date_received:
        datein = SubElement(top, "date-received")
        datein.text = date_received
    if date_completed:
        dateout = SubElement(top, "date-completed")
        dateout.text = date_completed
        
    print(tostring(top))
    return tostring(top)
    
def post_sample_node(lims, xml_node):
    uri = lims.get_uri("samples")
    response = lims.post(uri, xml_node)
    print(Sample(lims, response.attrib['uri']).info())
    return Sample(lims, response.attrib['uri'])





