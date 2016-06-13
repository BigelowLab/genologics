#!/usr/bin/env python
DESC = """EPP script to calculate molar concentration given the 
weight concentration, in Clarity LIMS. Before updating the artifacts, 
the script verifies that 'Concentration' and 'Size (bp)' udf:s are not blank,
 and that the 'Conc. units' field is 'ng/ul' for each artifact. Artifacts 
that do not fulfill the requirements, will not be updated.

Written by Johannes Alneberg, Science for Life Laboratory, Stockholm, Sweden
""" 

from argparse import ArgumentParser

from genologics.lims import Lims
from genologics.config import BASEURI,USERNAME,PASSWORD

from genologics.entities import Process
from genologics.epp import EppLogger

import logging
import sys

def apply_calculations(lims, artifacts, conc_udf, size_udf, unit_udf, epp_logger):
    for artifact in artifacts:
        logging.info(("Updating: Artifact id: {0}, "
                     "Concentration: {1}, Size: {2}, ").format(artifact.id, 
                                                        artifact.udf[conc_udf],
                                                        artifact.udf[size_udf]))
        factor = 1e6 / (328.3 * 2 * artifact.udf[size_udf])
        artifact.udf[conc_udf] = artifact.udf[conc_udf] * factor
        artifact.udf[unit_udf] = 'nM'
        artifact.put()
        logging.info('Updated {0} to {1}.'.format(conc_udf,
                                                 artifact.udf[conc_udf]))
def check_udf_is_defined(artifacts, udf):
    """ Filter and Warn if udf is not defined for any of artifacts. """
    filtered_artifacts = []
    incorrect_artifacts = []
    for artifact in artifacts:
        if (udf in artifact.udf) and artifact.udf[udf] != 0:
            filtered_artifacts.append(artifact)
        else:
            logging.warning(("Found artifact for sample {0} with {1} "
                             "undefined/blank, skipping").format(artifact.samples[0].name, udf))
            incorrect_artifacts.append(artifact)
    return filtered_artifacts, incorrect_artifacts


def check_udf_has_value(artifacts, udf, value):
    """ Filter artifacts on undefined udf or if udf has wrong value. """
    filtered_artifacts = []
    incorrect_artifacts = []
    for artifact in artifacts:
        if udf in artifact.udf and (artifact.udf[udf] == value):
            filtered_artifacts.append(artifact)
        elif udf in artifact.udf:
            incorrect_artifacts.append(artifact)
            logging.warning(("Filtered out artifact for sample: {0}"
                          ", due to wrong {1}").format(artifact.samples[0].name, udf))
        else:
            incorrect_artifacts.append(artifact)
            logging.warning(("Filtered out artifact for sample: {0}"
                          ", due to undefined/blank {1}").format(artifact.samples[0].name, udf))

    return filtered_artifacts, incorrect_artifacts

def main(lims, args, epp_logger):
    p = Process(lims, id = args.pid)
    udf_check = 'Conc. Units'
    value_check = 'ng/ul'
    concentration_udf = 'Concentration'
    size_udf = 'Size (bp)'

    if args.aggregate:
        artifacts = p.all_inputs(unique=True)
    else:
        all_artifacts = p.all_outputs(unique=True)
        artifacts = filter(lambda a: a.output_type == "ResultFile", all_artifacts)

    correct_artifacts, no_concentration = check_udf_is_defined(artifacts, concentration_udf)
    correct_artifacts, no_size = check_udf_is_defined(correct_artifacts, size_udf)
    correct_artifacts, wrong_value = check_udf_has_value(correct_artifacts, udf_check, value_check)

    apply_calculations(lims, correct_artifacts, concentration_udf, size_udf, udf_check, epp_logger)

    d = {'ca': len(correct_artifacts),
         'ia': len(wrong_value) + len(no_size) + len(no_concentration)}

    abstract = ("Updated {ca} artifact(s), skipped {ia} artifact(s) with "
                "wrong and/or blank values for some udfs.").format(**d)

    print >> sys.stderr, abstract # stderr will be logged and printed in GUI


if __name__ == "__main__":
    # Initialize parser with standard arguments and description
    parser = ArgumentParser(description=DESC)
    parser.add_argument('--pid',
                        help='Lims id for current Process')
    parser.add_argument('--log', default=sys.stdout,
                        help=('File name for standard log file, '
                              'for runtime information and problems.'))
    parser.add_argument('--aggregate', action='store_true',
                        help=("Use this tag if your process is aggregating "
                              "results. The default behaviour assumes it is "
                              "the output artifact of type analyte that is "
                              "modified while this tag changes this to using "
                              "input artifacts instead"))

    args = parser.parse_args()

    lims = Lims(BASEURI, USERNAME, PASSWORD)
    lims.check_version()
    with EppLogger(args.log, lims=lims, prepend=True) as epp_logger:
        main(lims, args, epp_logger)
