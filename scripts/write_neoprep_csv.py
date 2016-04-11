#!/usr/bin/env python
DESC="""EPP used to create csv files for the nanoprep robot"""
import datetime
import logging
import re
import os

from argparse import ArgumentParser
from genologics.lims import Lims
from genologics.config import BASEURI,USERNAME,PASSWORD
from genologics.entities import *
from genologics.epp import attach_file


def generate_header(step,atype='D'):
    #generates an almost static header
    header="[Header]\nIEMFileVersion,4\nDate,{date}\nWorkflow,NeoPrep\nApplication,NeoPrep\n"\
    "Assay,TruSeq {atype}NA\nNotes,IEMTemplate\nOperator,{operator}\nRun Name,SciLifeTemplate\nChemistry Default\n\n[Reads]\n\n"\
    "[Settings]\n\n".format(date=datetime.datetime.now().strftime("%d/%m/%Y"), operator=step.technician.first_name, atype=atype)
    if atype == 'D':
        header+="[Data]\nSample_Name,Sample_Well,I7_Index_ID,index,Insert Size\n"
    else:
        header+="[Data]\nSample_Name,Sample_Well,I7_Index_ID,index\n"

    return header


def generate_data(step):
    logger=logging.getLogger(__name__)
    proto_pattern=re.compile("([3,5]50)")
    #contents of the rows will be taken from both input and output artifacts
    data=""
    required_lines=16
    written_lines=0
    for inout in step.input_output_maps:
        inp=inout[0]['uri']
        out=inout[1]['uri']
        if out.type == "Analyte":
            try:
                #samplename
                sname=out.samples[0].name
            except:
                logger.error("Cannot find the sample of output analyte {0}".format(out.id))
                return None

            try:
                #well number
                location=out.location[1]
                row=location.split(':')[0]
                col=location.split(':')[1]
                #neoprep expects wells to be 1-16, lims has A1-B8
                well=(ord(row)-64)+((int(col)-1)*8)#turns A1, B1 ... B8 into 1,2 ... 16
            except:
                logger.error("Cannot find the location of analyte {0}".format(out.id))
                return None
            try:
                #regent label (barcode) name and sequence
                reglab_name=out.reagent_labels[0]
                reglab_seq=lims.get_reagent_types(name=reglab_name)[0].sequence
            except:
                logger.error("Cannot find the reagent label of output analyte {0}".format(out.id))
                return None
            try:
                #insert size
                matches=proto_pattern.search(inp.udf['Covaris Protocol'])
                ins_size=matches.group(1)
            except:
                logger.error("Cannot find the insert size of analyte {0} ({1})".format(inp.id, sname))
                ins_size='350'


            if reglab_name == 'D':
                data+="{0},{1},{2},{3},{4}\n".format(sname, well, reglab_name, reglab_seq, ins_size)
                written_lines+=1
            else:
                data+="{0},{1},{2},{3}\n".format(sname, well, reglab_name, reglab_seq)
                written_lines+=1

    if written_lines<required_lines:
        if reglab_name == 'D':
            data+="X,X,X,X,X\n"*(required_lines - written_lines)
        else:
            data+="X,X,X,X\n"*(required_lines - written_lines)

    header=generate_header(step, reglab_name[1])
    return header+data
        


def generate_csv(lims,step_id, logfile):
    logger=setupLog(logfile)
    pro=Process(lims, id=step_id)
    data=generate_data(pro)
    with open("neoprep_input.csv", 'wb') as f:
        f.write(data)
    for out in pro.all_outputs():
        #attach the csv file 
        if out.name=="Input CSV File":
            attach_file(os.path.join(os.getcwd(), "neoprep_input.csv"), out)
        if out.name=="Log File":
            attach_file(os.path.join(os.getcwd(), logfile), out)

def setupLog(logfile):
        mainlog = logging.getLogger(__name__)
        mainlog.setLevel(level=logging.INFO)
        mfh = logging.FileHandler(logfile)
        mft = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        mfh.setFormatter(mft)
        mainlog.addHandler(mfh)
        return mainlog


if __name__ == "__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('--pid',
                        help='Lims id for current Process')
    parser.add_argument('--log', default="write_neoprep_csv.log",
                        help='logfile for this epp')
    args = parser.parse_args()

    lims = Lims(BASEURI, USERNAME, PASSWORD)
    lims.check_version()
    generate_csv(lims, args.pid, args.log)
