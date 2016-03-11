"""Written by Isak Sylvin. isak.sylvin@scilifelab.se"""

import sys

class Thresholds():
    def __init__(self, instrument, chemistry, paired, read_length):
        self.Q30 = None
        self.exp_lane_clust = None
        
        #Check that only valid values are entered
        self.valid_instruments = ['miseq', 'hiseq', 'HiSeqX']
        self.valid_chemistry = ['MiSeq', 'HiSeq Rapid Flow Cell v1','HiSeq Rapid Flow Cell v2', 
                             'TruSeq Rapid Flow Cell v2', 'TruSeq Rapid Flow Cell v3', 'HiSeq Flow Cell v4', 'HiSeqX v2.5']
        
        if not instrument in self.valid_instruments or not chemistry in self.valid_chemistry:
            sys.exit("Detected instrument, chemistry and/or read_setup are not classed as valid in bcl_thresholds.py")
        else:
            self.set_Q30(instrument, chemistry, paired, read_length)
            self.set_exp_lane_clust(instrument, chemistry, paired, read_length)
    
    """Q30 values are derived from governing document 1244:4"""
    #A lot of cases are still unhandled; also usage of the paired parameter is not apparent
    def set_Q30(self, instrument, chemistry, paired, read_length):
        if instrument == 'miseq':
            if chemistry == 'MiSeq':
                if read_length >= 250:
                    self.Q30 = 60
                elif read_length >= 150:
                    self.Q30 = 70
                elif read_length >= 100:
                    self.Q30 = 75
                elif read_length < 100:
                    self.Q30 = 80
        elif instrument == 'hiseq':
            #Rapid run flowcell
            if chemistry in ['HiSeq Rapid Flow Cell v1','HiSeq Rapid Flow Cell v2', "TruSeq Rapid Flow Cell v2", "TruSeq Rapid Flow Cell v1"] :
                if read_length >= 150:
                    self.Q30 = 75
                elif read_length >= 100:
                    self.Q30 = 80
                elif read_length >= 50:
                    self.Q30 = 85
            #v3
            elif chemistry == 'HiSeq Flow Cell v3':
                if read_length >= 100:
                    self.Q30 = 80
                elif read_length >= 50:
                    self.Q30 = 85
            #v4
            elif chemistry == 'HiSeq Flow Cell v4':
                if read_length >= 125:
                    self.Q30 = 80
                        
        elif instrument == 'HiSeqX':
            if chemistry == 'HiSeqX v2.5':
                if read_length >= 150:
                    self.Q30 = 75
        if not self.Q30:
            sys.exit("Can't set Q30. Detected setup is classed as valid but has no thresholds set in bcl_thresholds.py")
    
    """Expected lanes per cluster are derived from undemultiplex_index.py"""
    def set_exp_lane_clust(self, instrument, chemistry, paired, read_length):
        if instrument == 'miseq':
            if chemistry == 'MiSeq':
                if read_length >= 75 and read_length <= 300:  
                    self.exp_lane_clust = 18000000
                else:                               
                    self.exp_lane_clust = 10000000
        elif instrument == 'hiseq':
            #Rapid run flowcell
            if chemistry in ['HiSeq Rapid Flow Cell v1','HiSeq Rapid Flow Cell v2', "TruSeq Rapid Flow Cell v2", "TruSeq Rapid Flow Cell v1"] :
                self.exp_lane_clust = 114000000
            #v3
            elif chemistry == 'HiSeq Flow Cell v3':
               self.exp_lane_clust = 143000000
            #v4
            elif chemistry == 'HiSeq Flow Cell v4':
                self.exp_lane_clust = 188000000
        elif instrument == 'HiSeqX':
            #HiSeqX runs are always paired!
            if paired:
                #X v2.5 (common)
                if chemistry == 'HiSeqX v2.5':
                    self.exp_lane_clust = 320000000
                #X v2.0 (rare)
                elif chemistry == 'HiSeqX v2.0':
                    self.exp_lane_clust = 305000000
        if not self.exp_lane_clust:
            sys.exit("Can't set Clusters per lane. Detected setup is classed as valid but has no thresholds set in bcl_thresholds.py")