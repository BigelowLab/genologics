#!/usr/bin/env python
DESC="""EPP script to copy the "Comments" field to the projects running notes on process termination

Denis Moreno, Science for Life Laboratory, Stockholm, Sweden
""" 
from argparse import ArgumentParser
from genologics.entities import *
from genologics.lims import Lims
from genologics.config import BASEURI,USERNAME,PASSWORD
from genologics.epp import attach_file, EppLogger

import datetime
import logging
import os
import sys
import json


def categorization(process_name):
    decision={
    "Automated Quant-iT QC (Library Validation) 4.0" : "Workset",
    "Library Pooling (MiSeq) 4.0" : "",
    "Aggregate QC (Library Validation) 4.0" : "Workset",
    "Sample Placement (Size Selection)" : "",
    "Illumina Sequencing (HiSeq X) 1.0" : "Flowcell",
    "Ligate 5' adapters (TruSeq small RNA) 1.0" : "Workset",
    "End repair, A-tailing and adapter ligation (Nextera) 4.0" : "Workset",
    "Library Normalization (Illumina SBS) 4.0" : "",
    "Bioanalyzer QC (DNA) 4.0" : "Workset",
    "Pre-Pooling (MiSeq) 4.0" : "",
    "ThruPlex library amplification" : "Workset",
    "Applications Pre-Pooling" : "",
    "Sort HiSeq Samples (HiSeq) 4.0" : "",
    "mRNA Purification, Fragmentation & cDNA synthesis (TruSeq RNA) 4.0" : "Workset",
    "HT-End repair, A-tailing and adapter ligation (TruSeq RNA) 4.0" : "Workset",
    "Size Selection (Pippin)" : "Workset",
    "End Repair, A-Tailing and Adapter Ligation (SS XT) 4.0" : "Workset",
    "Qubit QC (Library Validation) 4.0" : "Workset",
    "Library Pooling (Finished Libraries) 4.0" : "",
    "MiSeq Run (MiSeq) 4.0" : "Flowcell",
    "Automated Quant-iT QC (DNA) 4.0" : "Workset",
    "Bioanalyzer QC (Library Validation) 4.0" : "Workset",
    "Setup Workset/Plate" : "Workset",
    "Bioanalyzer Fragmentation QC (TruSeq DNA) 4.0" : "Workset",
    "Ligate 3' adapters (TruSeq small RNA) 1.0" : "Workset",
    "Qubit QC (DNA) 4.0" : "Workset",
    "Sort MiSeq Samples (MiSeq) 4.0" : "",
    "Fragment DNA (ThruPlex)" : "Workset",
    "Volume Measurement QC" : "Workset",
    "Project Summary 1.3" : "",
    "Fragment DNA (TruSeq DNA) 4.0" : "Workset",
    "NeoPrep Library QC v1.0" : "Workset",
    "Library Normalization (MiSeq) 4.0" : "",
    "Aliquot Samples for Caliper/Bioanalyzer" : "Workset",
    "qPCR QC (Library Validation) 4.0" : "Workset",
    "Applications Indexing" : "Workset",
    "CA Purification" : "Workset",
    "Size Selection (Caliper XT) 1.0" : "Workset",
    "ThruPlex template preparation and synthesis" : "Workset",
    "Enrich DNA fragments (TruSeq RNA) 4.0" : "Workset",
    "Quant-iT QC (RNA) 4.0" : "Workset",
    "End repair, size selection, A-tailing and adapter ligation (TruSeq PCR-free DNA) 4.0" : "Workset",
    "CaliperGX QC (DNA)" : "Workset",
    "Hybridize Library  (SS XT) 4.0" : "",
    "Sort HiSeq X Samples (HiSeq X) 1.0" : "",
    "Amplify Adapter-Ligated Library (SS XT) 4.0" : "",
    "Aliquot Libraries for Hybridization (SS XT)" : "",
    "Denature, Dilute and Load Sample (MiSeq) 4.0" : "Flowcell",
    "Cluster Generation (HiSeq X) 1.0" : "Flowcell",
    "Cluster Generation (Illumina SBS) 4.0" : "Flowcell",
    "Library Pooling (Illumina SBS) 4.0" : "",
    "Bioanalyzer QC (RNA) 4.0" : "Workset",
    "Pre-Pooling (Illumina SBS) 4.0" : "",
    "Reverse Transcribe (TruSeq small RNA) 1.0" : "Workset",
    "RiboZero depletion" : "Workset",
    "Amplify Captured Libraries to Add Index Tags (SS XT) 4.0" : "",
    "Library Pooling (TruSeq Small RNA) 1.0" : "",
    "Linear DNA digestion, Circularized DNA shearing and Streptavidin Bead Binding" : "Workset",
    "CaliperGX QC (RNA)" : "Workset",
    "Bcl Conversion & Demultiplexing (Illumina SBS) 4.0" : "Bioinformatics",
    "Qubit QC (Dilution Validation) 4.0" : "Workset",
    "MinElute Purification" : "",
    "Quant-iT QC (DNA) 4.0" : "Workset",
    "Aggregate QC (RNA) 4.0" : "Workset",
    "Customer Gel QC" : "Workset",
    "Quant-iT QC (Library Validation) 4.0" : "Workset",
    "Circularization" : "Workset",
    "Qubit QC (RNA) 4.0" : "Workset",
    "Illumina Sequencing (Illumina SBS) 4.0" : "Flowcell",
    "Purification (ThruPlex)" : "Workset",
    "Aliquot Samples for Qubit/Bioanalyzer" : "Workset",
    "Shear DNA (SS XT) 4.0" : "Workset",
    "Tagmentation, Strand displacement and AMPure purification" : "Workset",
    "Fragmentation & cDNA synthesis (TruSeq RNA) 4.0" : "Workset",
    "End repair, A-tailing and adapter ligation (TruSeq RNA) 4.0" : "Workset",
    "Capture And Wash (SS XT) 4.0" : "Workset",
    "Amplify by PCR and Add Index Tags (TruSeq small RNA) 1.0" : "Workset",
    "Size Selection (Robocut)" : "Workset",
    "Aggregate QC (DNA) 4.0" : "Workset",
    "Aliquot Libraries for Pooling (Small RNA)" : ""}

    return decision[process_name]



def main(lims, args):
    

    comment=False

    noteobj={}
    pro=Process(lims, id=args.pid)
    if 'Comments' in pro.udf and pro.udf['Comments'] is not '':
        key=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        noteobj[key]={}
        note="Comment from {0} ({1}) : \n{2}".format(pro.type.name, '[LIMS](https://genologics.scilifelab.se/clarity/work-details/{0})'.format(pro.id.split('-')[1]), pro.udf['Comments'])
        noteobj[key]['note']=note
        noteobj[key]['user']="{0} {1}".format(pro.technician.first_name,pro.technician.last_name)
        noteobj[key]['email']=pro.technician.email
        noteobj[key]['category']=categorization(pro.type.name)

        #find the correct projects.
        samples=set()
        projects=set()
        for inp in pro.all_inputs():
            #bitwise or to add inp.samples to samplesas a set
            samples |= set(inp.samples)
        for sam in samples:
            if sam.project:
                projects.add(sam.project)

        for proj in projects:
            if 'Running Notes' in proj.udf:
                existing_notes=json.loads(proj.udf['Running Notes'])
                for key in noteobj:
                    existing_notes[key]=noteobj[key]
                proj.udf['Running Notes']=json.dumps(existing_notes)
            else:
                proj.udf['Running Notes']=json.dumps(noteobj) 
            proj.put()
            
if __name__=="__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('--pid',
                        help='Lims id for current Process')
    args = parser.parse_args()

    lims = Lims(BASEURI, USERNAME, PASSWORD)
    lims.check_version()

    main(lims, args)
