#!/usr/bin/env python

import glob,os
import sys, getopt
import gzip
from fastq_reader import Fastq_Reader

# PAIRED READ FILES ARE ASSUMED TO BE SORTED
def kmer_bins(b,A,pfx,outfile):
	current_id = None
	pair = []
	bins = []
	for a in range(len(A)):
		# use this for readid/1, readid/2 pairs
		#read_id = A[a].split()[0]
		# use this for readid 1, readid 2 pairs
		read_id = A[a][:A[a].index(' ')+2]
		if read_id != current_id:
			if (len(bins) > 0) and (read_id[:-1] != current_id[:-1]):
				for rp in pair:
					outfile.write(rp)
					outfile.write(pfx+','.join([str(x) for x in bins]) + ']\n')
				pair = []
				bins = []
			current_id = read_id
			pair.append(A[a])
		bins.append(b[a])

help_message = 'usage example: python hash_fastq_reads.py -r 1 -i /project/home/original_reads/ -o /project/home/hashed_reads/'
if __name__ == "__main__":
	try:
		opts, args = getopt.getopt(sys.argv[1:],'hr:i:o:',["filerank=","inputdir=","outputdir="])
	except:
		print help_message
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h','--help'):
			print help_message
			sys.exit()
		elif opt in ('-r','--filerank'):
			fr = int(arg) - 1
		elif opt in ('-i','--inputdir'):
			inputdir = arg
			if inputdir[-1] != '/':
				inputdir += '/'
		elif opt in ('-o','--outputdir'):
			outputdir = arg
			if outputdir[-1] != '/':
				outputdir += '/'
	FP = glob.glob(os.path.join(inputdir,'*.fastq.*'))
	file_prefix = FP[fr]
	file_split = file_prefix[-3:]
	file_prefix = file_prefix[file_prefix.rfind('/')+1:file_prefix.index('.fastq')]
	hashobject = Fastq_Reader(inputdir,outputdir)
	f = open(hashobject.input_path+file_prefix+'.fastq'+file_split,'r')
	g = gzip.open(hashobject.output_path+file_prefix+'.hashq'+file_split+'.gz','wb')
	hashobject.hpfx = hashobject.hpfx + str(hashobject.kmer_size)+','
	A = []
	while A != None:
		try:
			A,B = hashobject.generator_to_bins(hashobject.read_generator(f,max_reads=25000,verbose_ids=True),rc=True)
			for b in range(len(B)):
				kmer_bins(B[b],A,hashobject.hpfx,g)
		except Exception,err:
			print str(err)
	f.close()
	g.close()