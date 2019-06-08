#=============================================================================================================================================
# File:	 	learn_psdd_wrapper_v2.py
# Author: 	Anton Fuxjaeger 		(anton.fuxjaeger@ed.ac.uk)
# Data  :	29/05/2019
# Tested: 	Yes (Python 3.7 with Scala-LearnPsdd clone on (27/05/2019)) - for query updated source is needed
#
# Information: 	The following file contains a python wrapper for the STARAI-UCLA Psdd learner found at https://github.com/YitaoLiang/Scala-LearnPsdd
#				To be specific, the different functionalities of the repo are wrapped by individual methods in this file 
#				Additionally ther is a method 'learnpsdd' provided which handles a whole experiment w/o constraints, vtreelearning and psddlearning
#				The code also provides file handling for the whole experiment, as well as visualization
#
# Usage:		To use this file, please specify the user variables, in the first few lines, basically pointing the code to you local source dir
#				The sdd_lib is necessary for compiling constraints into sdd format
#				enjoy
#				
#=============================================================================================================================================
import os, platform, shutil

#DEPENDENCIES and USER variables:

# - PYTHON 3.+
#
# - Scala-PlearnPsdd 	(STARAI-UCLA software)  -   Link: https://github.com/YitaoLiang/Scala-LearnPsdd
# 													The root location of the source directory should be specified (relative to home, or abs) in the following variable
LEARNPSDD_ROOT_DIR_USER = './code/msc/src/Scala-LearnPsdd/'
RECOMPILE_PSDD_SOURCE = True
# -------------------------------------------------------------------------------------------------------------------------
#
# - GRAPHVIZ   			(graphing software)     -   Please specify if finstalled:
#
GRAPHVIZ_INSTALLED = True
# -------------------------------------------------------------------------------------------------------------------------
#
# - SDDLIB BINARY       (STAR-UCLA software)    -   Link: http://reasoning.cs.ucla.edu/sdd/
#
SDD_LIB_DIR_USER = './code/msc/src/wmisdd/bin/'
#
#============================================================================================================================
#============================ SCRIPT METHODS (need to be at the top of the file =============================================
#============================================================================================================================

def write(message, level = 'info'):
	out_string = '[{}]'.format(level.upper())
	message_start_idx = 20
	out_string += ' ' * (message_start_idx - len(out_string))
	out_string += '- {}'.format(message)
	if level == 'error':
		print(out_string)
		raise Exception(out_string)
	elif level == 'cmd-start':
		out_string = '\n{}\n'.format(out_string)
		out_string += '-'* 40 + ' CMD OUTPUT ' + '-'*40
	elif level == 'cmd-end':
		out_string = '=' * 40 + ' CMD OUTPUT END ' + '=' * 40 + '\n' + out_string + '\n'

	print(out_string)

def _check_if_file_exists(file_path, raiseException = True):
	if os.path.isfile(file_path):
		return True
	elif raiseException:
		write('Trying to use file that does not exist: {}'.format(file_path), 'error')
	else:
		return False

def _check_if_dir_exists(dir_path, raiseException = True):
	if os.path.isdir(dir_path):
		return True
	elif raiseException:
		write('Trying to use directory that does not exist: {}'.format(dir_path), 'error')
	else:
		return False

def _recompile_source(compile_dir):
	current_dir = os.path.abspath('.')
	os.chdir(compile_dir)
	write('recompiling source at: {}'.format(compile_dir), 'cmd-start')
	os.system('sbt assembly')
	write('finished compiling', 'cmd-end')
	os.chdir(current_dir)

def _add_learn_psdd_lib_to_path(learnpsdd_lib):
	# os.environ['LD_LIBRARY_PATH'] = ''
	if 'LD_LIBRARY_PATH' not in os.environ:
		os.environ['LD_LIBRARY_PATH'] = learnpsdd_lib# + os.pathsep + SDD_LIB_DIR
		write('variable LD_LIBRARY_PATH created and set to: {}'.format(os.environ['LD_LIBRARY_PATH']), 'init')
	
	if not learnpsdd_lib in os.environ['LD_LIBRARY_PATH']:
		os.environ['LD_LIBRARY_PATH'] += os.pathsep + learnpsdd_lib
		write('variable LD_LIBRARY_PATH updated to: {}'.format(os.environ['LD_LIBRARY_PATH']), 'init')
	
	# if not SDD_LIB_DIR in os.environ['LD_LIBRARY_PATH']:
	# 	os.environ['LD_LIBRARY_PATH'] += os.pathsep + SDD_LIB_DIR
	# 	write('variable LD_LIBRARY_PATH updated to: {}'.format(os.environ['LD_LIBRARY_PATH']))

	if not learnpsdd_lib in os.environ['PATH']:
		os.environ['PATH'] += str(os.pathsep + learnpsdd_lib)
		write('variable PATH updated to: {}'.format(os.environ['PATH']), 'init')

#============================================================================================================================
#======================================  INIT (executed when module is loaded ===============================================
#============================================================================================================================

LEARNPSDD_ROOT_DIR = os.path.abspath(os.path.join(os.environ['HOME'],LEARNPSDD_ROOT_DIR_USER))
write('LEARNPSDD_ROOT_DIR \t{}'.format(LEARNPSDD_ROOT_DIR),'init')
_check_if_dir_exists(LEARNPSDD_ROOT_DIR)
if RECOMPILE_PSDD_SOURCE:
	_recompile_source(LEARNPSDD_ROOT_DIR)
LEARNPSDD_CMD = os.path.abspath(os.path.join(LEARNPSDD_ROOT_DIR,'./target/scala-2.11/psdd.jar'))
LEARNPSDD_LIB = os.path.abspath(os.path.join(LEARNPSDD_ROOT_DIR, './lib/')) + '/'
_check_if_file_exists(LEARNPSDD_CMD)
_check_if_dir_exists(LEARNPSDD_LIB)
_add_learn_psdd_lib_to_path(LEARNPSDD_LIB)

SDDLIB_BIN = os.path.abspath(os.path.join(os.environ['HOME'],SDD_LIB_DIR_USER))
write('SDDLIB_BIN \t{}'.format(SDDLIB_BIN),'init')
_check_if_dir_exists(SDDLIB_BIN)
if 'Linux' in platform.system():
	SDDLIB_CMD = os.path.abspath(os.path.join(SDDLIB_BIN, 'sdd-linux'))
else:
	SDDLIB_CMD = os.path.abspath(os.path.join(SDDLIB_BIN, 'sdd-darwin'))
	write('the program only works fully on linux based systems, so some aspects might not work for you\n --> Assuming OSX', 'warning')
write('SDDLIB_CMD \t{}'.format(SDDLIB_CMD),'init')
_check_if_file_exists(SDDLIB_CMD)

#============================================================================================================================
#============================================ AUXILIARY FUNCTIONS ====================================================
#============================================================================================================================

def convert_dot_to_pdf(file_path, do_this = True):
	if not do_this or not _check_if_file_exists(file_path + '.dot', raiseException = False) or not GRAPHVIZ_INSTALLED:
		return

	cmd_str = 'dot -Tpdf {}.dot -o {}.pdf'.format(file_path,file_path)
	os.system(cmd_str)
	write('Converted file to pdf (graphical depictoin). Location: {}'.format(file_path + '.pdf'))

def _list_to_cs_string(list_to_convert):
	outstr = ''
	for i in list_to_convert:
		outstr += '{},'.format(i)
	outstr = outstr[:-1]
	return outstr

def _get_psdd_file_names_and_check(psdd_out_dir):

	vtree_path = os.path.join(psdd_out_dir, './model.vtree')
	write('output vtree file: {}'.format(vtree_path), 'files')
	_check_if_file_exists(vtree_path)

	psdd_file = os.path.join(psdd_out_dir, './model.psdd')
	write('output psdd file: {}'.format(psdd_file), 'files')
	_check_if_file_exists(psdd_file)

	psdds = list([psdd_file])

	weights = list([1])

	return vtree_path, psdds, weights
#============================================================================================================================
#============================================================================================================================
#============================================================================================================================

def learn_vtree(train_data_path, vtree_out_path, 
		out_learnvtree_tmp_dir = '.learnVtree_tmp/', vtree_method = 'miBlossom', convert_to_pdf = True, keep_generated_files = False):
	
	'''
	-d, --trainData <file>   
	-v, --vtreeMethod leftLinear-rand|leftLinea-ord|pairwiseWeights|balanced-rand|rightLinear-ord|rightLinear-rand|balanced-ord|miBlossom|miGreedyBU|miMetis
						   default: miBlossom
		 * leftLinear-rand: left linear vtree a random order
		 * leftLinea-ord: left linear vtree using variable order
		 * pairwiseWeights: balanced vtree by top down selection of the split that minimizes the mutual information between the two parts, using exhaustive search.
		 * balanced-rand: balanced vtree using a random order
		 * rightLinear-ord: right linear vtree using variable order
		 * rightLinear-rand: right linear vtree using a random order
		 * balanced-ord: balanced vtree using variable order
		 * miBlossom: balanced vtree by bottom up matching of the pairs that maximizes the average mutual information in a pair, using blossomV.
		 * miGreedyBU: balanced vtree by bottom up matching of the pairs that maximizes the average mutual information in a pair, using greedy selection.
		 * miMetis: balanced vtree by top down selection of the split that minimizes the mutual information between the two parts, using metis.
	-o, --out <path>         
	-e, --entropyOrder       choose prime variables to have lower entropy
	'''
	_check_if_file_exists(train_data_path)

	out_learnvtree_tmp_dir = os.path.abspath(out_learnvtree_tmp_dir)
	if _check_if_dir_exists(out_learnvtree_tmp_dir, raiseException = False):
		shutil.rmtree(out_learnvtree_tmp_dir)
	os.mkdir(out_learnvtree_tmp_dir)

	vtree_tmp_output_file = os.path.abspath(os.path.join(out_learnvtree_tmp_dir, '{}.vtree'.format(vtree_method)))

	cmd_str = 'java -jar {} learnVtree '.format(LEARNPSDD_CMD) + \
		  ' --trainData {}'.format(train_data_path) + \
		  ' --vtreeMethod {}'.format(vtree_method) + \
		  ' --out {}'.format(vtree_tmp_output_file.replace('.vtree',''))

	write(cmd_str,'cmd-start')
	os.system(cmd_str)

	_check_if_file_exists(vtree_tmp_output_file)
	
	shutil.copyfile(vtree_tmp_output_file, vtree_out_path)
	if _check_if_file_exists(vtree_tmp_output_file + '.dot', raiseException = False):
		convert_dot_to_pdf(vtree_tmp_output_file, convert_to_pdf)
		shutil.copyfile(vtree_tmp_output_file + '.pdf', vtree_out_path + '.pdf')

	if not keep_generated_files and _check_if_file_exists(vtree_out_path):
		shutil.rmtree(out_learnvtree_tmp_dir)
	
	write('Finished leraning Vtree from data. File location: {}'.format(vtree_out_path), 'cmd-end')

def compile_cnf_to_sdd(cnf_path, sdd_path, vtree_out_path, \
	vtree_in_path = None, initial_vtree_type = 'random', vtree_search_freq = 5, post_compilation_vtree_search = False, \
	convert_to_pdf = True, minimize_sdd_cardinality = False):

	'''
	If vtree_in_path == None, invoke vtree search every vtree_search_freq clauses

	NOTE: minimizing the cardinality of the sdd messes up the knowledge base... i think this method is not working properly, so best leave it False

	libsdd version 2.0, January 08, 2018
	sdd (-c FILE | -d FILE | -s FILE) [-v FILE | -t TYPE] [-WVRS FILE] [-r MODE] [-mhqp]
	  -c FILE         set input CNF file
	  -d FILE         set input DNF file
	  -v FILE         set input VTREE file
	  -s FILE         set input SDD file
	  -W FILE         set output VTREE file
	  -V FILE         set output VTREE (dot) file
	  -R FILE         set output SDD file
	  -S FILE         set output SDD (dot) file
	  -m              minimize the cardinality of compiled sdd
	  -t TYPE         set initial vtree type (left/right/vertical/balanced/random)
	  -r K            if K>0: invoke vtree search every K clauses
						if K=0: disable vtree search
						by default (no -r option), dynamic vtree search is enabled
	  -q              perform post-compilation vtree search
	  -h              print this help and exit
	  -p              verbose output
	  '''

	_check_if_file_exists(cnf_path)
	_check_if_file_exists(vtree_out_path)

	generate_vtree = vtree_in_path == None

	if not generate_vtree:
		_check_if_file_exists(vtree_in_path)

	cmd_str = '{} '.format(SDDLIB_CMD) + \
		  ' -c {}'.format(cnf_path)
	
	if generate_vtree:
		cmd_str += ' -t {}'.format(initial_vtree_type)
	else:
		cmd_str += ' -v {}'.format(vtree_in_path)

	cmd_str += ' -W {}'.format(vtree_out_path)
	cmd_str += ' -V {}.dot'.format(vtree_out_path)
	cmd_str += ' -R {}'.format(sdd_path)
	cmd_str += ' -S {}.dot'.format(sdd_path)
	if minimize_sdd_cardinality:
		cmd_str += ' -m'

	if generate_vtree:
		cmd_str += ' -r {}'.format(vtree_search_freq)
	else:
		cmd_str += ' -r 0'

	if post_compilation_vtree_search:
		cmd_str += ' -q'

	write(cmd_str,'cmd-start')
	os.system(cmd_str)

	write('Finished compiling CNF to SDD. File location: {}'.format(sdd_path), 'cmd-end')
	_check_if_file_exists(vtree_out_path) and _check_if_file_exists(sdd_path)

	if generate_vtree:
		convert_dot_to_pdf(vtree_out_path,convert_to_pdf)
	convert_dot_to_pdf(sdd_path,convert_to_pdf)

def compile_sdd_to_psdd(train_data_path, vtree_path, sdd_path, psdd_path, 
			valid_data_path = None, test_data_path = None, smoothing = 'l-1'):

	'''
	  -d, --trainData <file>   
	  -b, --validData <file>   
	  -t, --testData <file>    
	  -v, --vtree <file>       
	  -s, --sdd <file>         
	  -o, --out <path>         
	  -m, --smooth <smoothingType>
							   default: l-1
			 * mc-m-<m>: m-estimator, weighted with model count
			 * mc-<m>: model count as pseudo count, weighted with m
			 * l-<m>: laplace smoothing, weighted with m
			 * m-<m>: m-estimator smoothing
			 * mc-l-<m>: laplace smoothing, weighted with model count and m
			 * no: No smoothing
	  --help                   prints this usage text
	'''
	_check_if_file_exists(train_data_path)
	_check_if_file_exists(vtree_path)
	_check_if_file_exists(sdd_path)

	cmd_str = 'java -jar {} sdd2psdd '.format(LEARNPSDD_CMD) + \
		  ' -d {}'.format(train_data_path) + \
		  ' -v {}'.format(vtree_path) + \
		  ' -s {}'.format(sdd_path) + \
		  ' -o {}'.format(psdd_path) + \
		  ' -m {}'.format(smoothing)

	if valid_data_path != None and _check_if_file_exists(valid_data_path, raiseException = False):
		cmd_str += ' -b {}'.format(valid_data_path)
	if test_data_path != None and _check_if_file_exists(test_data_path, raiseException = False):
		cmd_str += ' -t {}'.format(test_data_path)

	write(cmd_str,'cmd-start')
	os.system(cmd_str)

	_check_if_file_exists(psdd_path)
	write('Finished compiling SDD to PSDD. File location: {}'.format(psdd_path), 'cmd-end')

def learn_psdd_from_data(train_data_path, vtree_path, out_psdd_file, \
		out_learnpsdd_tmp_dir = './.out_learnpsdd_tmp_dir/', psdd_input_path = None, valid_data_path = None, 
		test_data_path = None, smoothing = 'l-1', clone_k = 3, split_k = 1, completion = 'maxDepth-3', scorer = 'dll/ds',
		maxIt = 'max', save_freq = 'best-3', keep_generated_files = False, convert_to_pdf = True):
	
	'''
	  -p, --psdd <file>        If no psdd is provided, the learning starts from a mixture of marginals.
	  -v, --vtree <file>
	  -d, --trainData <file>   
	  -b, --validData <file>   
	  -t, --testData <file>
	  -o, --out <path>         The folder for output

	  -m, --smooth <smoothingType>
							   default: l-1
			 * mc-m-<m>: m-estimator, weighted with model count
			 * mc-<m>: model count as pseudo count, weighted with m
			 * l-<m>: laplace smoothing, weighted with m
			 * m-<m>: m-estimator smoothing
			 * mc-l-<m>: laplace smoothing, weighted with model count and m
			 * no: No smoothing

					 * l-<m>: laplace smoothing, weighted with m
			 * m-<m>: m-estimator smoothing
			 * mc-l-<m>: laplace smoothing, weighted with model count and m
			 * no: No smoothing

	  -h, --opTypes <opType>,<opType>,...
							   default: clone-3,split-1
			options: clone-<k>,split-<k>
			In split-k, k is the number of splits.
			In clone-k, k is the maximum number of parents to redirect to the clone.

	  -c, --completion <completionType>
							   default: maxDepth-3
			 * complete
			 * min
			 * maxDepth-<k>
			 * maxEdges-<k>

	  -s, --scorer <scorer>    default: dll/ds
			 * dll
			 * dll/ds

	  -e, --maxIt <maxIt>      For search, this is the maximum number of operations to be applied on the psdd.
			For bottom-up and top-down, at every level at most f*#vtreeNodesAtThisLevel operations will be applied.
			default: maxInt

	  -f, --freq <freq>        method for saving psdds
			default: best-1
			 * all-<k>
			 * best-<k>
			best-k to only keep the best psdd on disk, all-k keeps all of the. A save attempt is made every k iterations

	  -q, --debugLevel <level>
							   debug level

	  --help                   prints this usage text
	'''
	_check_if_file_exists(train_data_path)
	_check_if_file_exists(vtree_path)

	out_learnpsdd_tmp_dir = os.path.abspath(out_learnpsdd_tmp_dir)
	if _check_if_dir_exists(out_learnpsdd_tmp_dir, raiseException = False):
		shutil.rmtree(out_learnpsdd_tmp_dir)
	os.mkdir(out_learnpsdd_tmp_dir)

	cmd_str = 'java -jar {} learnPsdd search '.format(LEARNPSDD_CMD) + \
		  ' --trainData {}'.format(train_data_path) + \
		  ' --vtree {}'.format(vtree_path) + \
		  ' --out {}'.format(out_learnpsdd_tmp_dir)

	if valid_data_path != None and _check_if_file_exists(valid_data_path, raiseException = False):
		cmd_str += ' --validData {}'.format(valid_data_path)
	if test_data_path != None and _check_if_file_exists(test_data_path, raiseException = False):
		cmd_str += ' --testData {}'.format(test_data_path)
	if psdd_input_path != None and _check_if_file_exists(psdd_input_path, raiseException = False):
		cmd_str += ' -p {}'.format(psdd_input_path)

	cmd_str += ' --smooth {}'.format(smoothing) + \
			   ' --opTypes clone-{},split-{}'.format(clone_k, split_k) + \
			   ' --completion {}'.format(completion) + \
			   ' --scorer {}'.format(scorer) + \
			   ' --freq {}'.format(save_freq)
	if not maxIt == 'max':
		cmd_str += ' --maxIt {}'.format(maxIt)
 
	write(cmd_str,'cmd-start')
	os.system(cmd_str)

	final_psdd_file = os.path.join(out_learnpsdd_tmp_dir,'./models/final.psdd')
	write('Finished PSDD learnin. File location: {}'.format(final_psdd_file), 'cmd-end')
	_check_if_file_exists(final_psdd_file)
	
	shutil.copyfile(final_psdd_file, out_psdd_file)

	final_psdd_dot_file = os.path.join(out_learnpsdd_tmp_dir,'./models/final.dot')
	if not _check_if_file_exists(final_psdd_dot_file, raiseException = False):
		write('final psdd dot file counld not be found at location: {}'.format(final_psdd_dot_file),'warning')
	else:
		convert_dot_to_pdf(final_psdd_dot_file.replace('.dot',''), convert_to_pdf)
		shutil.copyfile(final_psdd_dot_file.replace('.dot', '.pdf'), out_psdd_file + '.pdf')

	if not keep_generated_files:
		shutil.rmtree(out_learnpsdd_tmp_dir)

def query_psdd_from_dir(train_data_path, query_data_path, out_learnpsdd_tmp_dir,\
		valid_data_path = None, out_file = None):
	vtree_path, psdd_files, componentweights = _get_psdd_file_names_and_check(out_learnpsdd_tmp_dir)
	query_psdd(train_data_path, vtree_path, query_data_path, psdd_files, componentweights, valid_data_path, out_file)

def query_psdd(train_data_path, vtree_path, query_data_path, psdd_files, componentweights,\
		valid_data_path = None, out_file = None):
	
	'''
		  -d, --trainData <file>   
		  -b, --validData <file>   
		  -q, --queryFile <file>   
		  -v, --vtree <file>       
		  -o, --out <path>         
		  -a, --componentweights <double>,<double>,...
		                           
		  -p, --psdds <file>,<file>,...
		                           
		  --help                   prints this usage text

	'''
	_check_if_file_exists(train_data_path)
	_check_if_file_exists(vtree_path)
	_check_if_file_exists(query_data_path)
	for i in psdd_files:
		_check_if_file_exists(i)

	if out_file == None:
		out_file = query_data_path + '.anwser'

	cmd_str = 'java -jar {} query '.format(LEARNPSDD_CMD) + \
		  ' --trainData {}'.format(train_data_path) + \
		  ' --vtree {}'.format(vtree_path) + \
		  ' --out {}'.format(out_file) + \
		  ' --queryFile {}'.format(query_data_path) + \
		  ' --psdds {}'.format(_list_to_cs_string(psdd_files)) + \
		  ' --componentweights {}'.format(_list_to_cs_string(componentweights))

	if valid_data_path != None and _check_if_file_exists(valid_data_path, raiseException = False):
		cmd_str += ' --validData {}'.format(valid_data_path)

	write(cmd_str,'cmd-start')
	os.system(cmd_str)

	write('Finished PSDD Query for query file: {}'.format(query_data_path), 'cmd-end')
	_check_if_file_exists(out_file)

def learn_ensembly_psdd_from_data(train_data_path, vtree_path, out_psdd_file, \
		 out_learnpsdd_tmp_dir = './.out_ensemblylearnpsdd_tmp_dir/',psdd_input_path = None, num_compent_learners = 5,valid_data_path = None, \
		 test_data_path = None, smoothing = 'l-1', structureChangeIt = 3, parameterLearningIt = 1, scorer = 'dll/ds', maxIt = 'max', \
		 save_freq = 'best-3'):
	
	'''
	  -p, --psdd <file>        If no psdd is provided, the learning starts from a mixture of marginals.

	  -v, --vtree <file>       
	  -d, --trainData <file>   
	  -b, --validData <file>   
	  -t, --testData <file>    
	  -o, --out <path>         The folder for output

	  -c, --numComponentLearners <numComponentLearners>
							   The number of component learners to form the ensemble

	  -m, --smooth <smoothingType>
							   default: l-1
			 * mc-m-<m>: m-estimator, weighted with model count
			 * mc-<m>: model count as pseudo count, weighted with m
			 * l-<m>: laplace smoothing, weighted with m
			 * m-<m>: m-estimator smoothing
			 * mc-l-<m>: laplace smoothing, weighted with model count and m
			 * no: No smoothing

	  -s, --scorer <scorer>    default: dll/ds
			 * dll
			 * dll/ds

	  -e, --maxIt <maxIt>      this is the maximum number of ensemble learning iterations.

	  --structureChangeIt <structureChangeIt>
							   this is the number of structure changes before a new round of parameter learning .

	  --parameterLearningIt <parameterLearningIt>
							   this is the number of iterators for parameter learning before the structure of psdds changes again.

	  --help                   prints this usage text
	'''

	_check_if_file_exists(train_data_path)
	_check_if_file_exists(vtree_path)

	out_learnpsdd_tmp_dir = os.path.abspath(out_learnpsdd_tmp_dir)
	if _check_if_dir_exists(out_learnpsdd_tmp_dir, raiseException = False):
		shutil.rmtree(out_learnpsdd_tmp_dir)
	os.mkdir(out_learnpsdd_tmp_dir)


	cmd_str = 'java -jar {} learnEnsemblePsdd softEM '.format(LEARNPSDD_CMD) + \
		  ' --trainData {}'.format(train_data_path) + \
		  ' --vtree {}'.format(vtree_path) + \
		  ' --out {}'.format(out_learnpsdd_tmp_dir) + \
		  ' --numComponentLearners {}'.format(num_compent_learners)

	if valid_data_path != None and _check_if_file_exists(valid_data_path, raiseException = False):
		cmd_str += ' --validData {}'.format(valid_data_path)
	if test_data_path != None and _check_if_file_exists(test_data_path, raiseException = False):
		cmd_str += ' --testData {}'.format(test_data_path)
	if psdd_input_path != None and _check_if_file_exists(psdd_input_path, raiseException = False):
		cmd_str += ' -p {}'.format(psdd_input_path)

	cmd_str += ' --smooth {}'.format(smoothing) + \
			   ' --structureChangeIt {}'.format(structureChangeIt) + \
			   ' --parameterLearningIt {}'.format(parameterLearningIt) + \
			   ' --scorer {}'.format(scorer)

	if not maxIt == 'max':
		cmd_str += ' --maxIt {}'.format(maxIt)
			   # ' --freq {}'.format(save_freq)

	write(cmd_str,'cmd-start')
	os.system(cmd_str)

	# NOT IMPLEMENTED BECAUSE METHOD IS NOT WORKING AND OUTPUT COULD NOT BE COMPUTED
	
	# final_psdd_file = os.path.join(out_learnpsdd_tmp_dir,'./models/final.psdd')
	# write('Finished PSDD learnin. File location: {}'.format(final_psdd_file), 'cmd-end')
	# _check_if_file_exists(final_psdd_file)
	
	# shutil.copyfile(final_psdd_file, out_psdd_file)

	# final_psdd_dot_file = os.path.join(out_learnpsdd_tmp_dir,'./models/final.dot')
	# if not _check_if_file_exists(final_psdd_dot_file, raiseException = False):
	# 	write('final psdd dot file counld not be found at location: {}'.format(final_psdd_dot_file),'warning')
	# else:
	# 	convert_dot_to_pdf(final_psdd_dot_file.replace('.dot',''), convert_to_pdf)
	# 	shutil.copyfile(final_psdd_dot_file.replace('dot', '.pdf'), out_psdd_file + '.pdf')

	# if not keep_generated_files:
	# 	shutil.rmtree(out_learnpsdd_tmp_dir)

# ====================================================================================================================
# ========================================   Higher level methods    =================================================
# ====================================================================================================================

def learn_psdd(psdd_out_dir, train_data_path, 
		valid_data_path = None, test_data_path = None, replace_existing = False, vtree_method = 'miBlossom', \
		num_compent_learners = 1, constraints_cnf_file = None, keep_generated_files = True, convert_to_pdf = True):
	# For ease of use, I have create one function that takes care of almost all subpart when it comes to psdd learning
	# It learnes a vtree from data, compiles constraints to sdd/psdd if present, and learnes a psdd with the vtree and constaints (if present)
	# Arguments:
	#	psdd_out_dir           a directory will be created with this name
	#   train_data_path       pretty self expanitory i think - Validation/test data are optional
	#
	# Options:
	#	constraints_cnf_file  constraints that should be enfoced in the psdd structure before learning starts,
	#						  	this can be handed to the method by cnf (DEMACS) file see example at the bottom of file
	#	num_compent_learners  curretnly only '1' supported, as the emsnebly learning scala code fails
	#	vtree_method		  method used for learning the vtree from data, please refer to learn_vtree method for more details
	#   convert_to_pdf        specify if generated dot files should be converted to pdf, Graphviz has to be installed
	#	keep_generated_files  keep the files generated by the individual learners, otherwise they are deleted
	#	repace_existsing      replaces the existing dir, if present 
	
	#Set up experiment directory
	experiment_path = os.path.abspath(psdd_out_dir)
	write('experiment dir path: {}'.format(experiment_path),'files')
	if _check_if_dir_exists(experiment_path, raiseException = False):
		if not replace_existing:
			write('Experiment dir already exists, please delete this or specify to do so in the arguments. (or give a different name)', 'error')
		else:
			shutil.rmtree(experiment_path)
	os.mkdir(experiment_path)

	#Set up learner directories
	out_learnpsdd_tmp_dir = os.path.join(experiment_path, './learnpsdd_tmp_dir/')
	os.mkdir(out_learnpsdd_tmp_dir)
	write('psdd learner dir: {}'.format(out_learnpsdd_tmp_dir), 'files')

	out_learnvtree_tmp_dir = os.path.join(experiment_path, './learnvtree_tmp_dir/')
	os.mkdir(out_learnvtree_tmp_dir)
	write('vtere learner dir: {}'.format(out_learnvtree_tmp_dir), 'files')

	#Set up resulting vtree/psdd file at the root of the psdd_out_dir
	out_vtree_file = os.path.join(experiment_path, './model.vtree')
	write('output vtree file: {}'.format(out_vtree_file), 'files')
	out_psdd_file = os.path.join(experiment_path, './model.psdd')
	write('output psdd file: {}'.format(out_psdd_file), 'files')

	#Learn vtree from data 
	learn_vtree(train_data_path, out_vtree_file, out_learnvtree_tmp_dir = out_learnvtree_tmp_dir,\
						 vtree_method = vtree_method, convert_to_pdf = convert_to_pdf, keep_generated_files = keep_generated_files)

	#Compile constraints to sdd/psdd if present
	if constraints_cnf_file != None:
		_check_if_file_exists(constraints_cnf_file, raiseException = True)

		contraints_tmp_dir = os.path.join(experiment_path, './constraints_tmp_dir/')
		os.mkdir(contraints_tmp_dir)

		constraints_sdd_file = os.path.join(contraints_tmp_dir, './constraints_as.sdd')
		compile_cnf_to_sdd(constraints_cnf_file, constraints_sdd_file, out_vtree_file, \
							vtree_in_path = out_vtree_file, post_compilation_vtree_search = False, convert_to_pdf = convert_to_pdf)
		
		constraints_psdd_file = os.path.join(contraints_tmp_dir, './constraints_as.psdd')
		compile_sdd_to_psdd(train_data_path, out_vtree_file, constraints_sdd_file, constraints_psdd_file, \
							valid_data_path = valid_data_path, test_data_path = test_data_path)
	else:
		constraints_psdd_file = None

	#Learn Psdd with all data avaliable 
	if num_compent_learners < 1:
		write('The number of psdd_compents (for ensembly learning) has to be > 0', 'error')
	elif num_compent_learners == 1:
		learn_psdd_from_data(train_data_path, out_vtree_file, out_psdd_file, out_learnpsdd_tmp_dir = out_learnpsdd_tmp_dir, valid_data_path = valid_data_path, \
			test_data_path = test_data_path, psdd_input_path = constraints_psdd_file, keep_generated_files = keep_generated_files, convert_to_pdf = convert_to_pdf)
	else:
		raise Exception('Ensemply learning is not working')
		learn_ensembly_psdd_from_data(train_data_path, out_vtree_file, out_psdd_file, out_learnpsdd_tmp_dir,psdd_input_path = constraints_psdd_file,\
			 num_compent_learners = num_compent_learners, valid_data_path = valid_data_path, test_data_path = test_data_path)

	#Remove tmp files
	if not keep_generated_files and constraints_cnf_file != None:
		if _check_if_dir_exists(contraints_tmp_dir, raiseException = False):
			shutil.rmtree(contraints_tmp_dir)

	write('learn_psdd method finished.','final')

# ============================================================================================================================
# ============================================================================================================================
# ============================================================================================================================

if __name__ == '__main__':
	experiment_dir_path = os.path.abspath(os.path.join(os.environ['HOME'],'./code/msc/output/experiments/ex_7_mnist_24_4'))
	# test_data_path = os.path.join(experiment_dir_path, 'encoded_data/mnist-encoded-test.data')
	valid_data_path = os.path.join(experiment_dir_path, './encoded_data/mnist-encoded-valid.data')
	train_data_path = os.path.join(experiment_dir_path, './encoded_data/mnist-encoded-train.data')
	query_data_path = os.path.join(experiment_dir_path, './encoded_data/query.data')

	#Test without constraints
	# experiment_name = 'psdd_search_miBlossom'
	# psdd_out_dir = os.path.join(experiment_dir_path,'./{}/'.format(experiment_name))
	# learn_psdd(psdd_out_dir, train_data_path, valid_data_path = valid_data_path, replace_existing = True, \
	# 	vtree_method = 'miBlossom', keep_generated_files = True)

	# experiment_name = 'psdd_search_miMetis'
	# psdd_out_dir = os.path.join(experiment_dir_path,'./{}/'.format(experiment_name))
	# learn_psdd(psdd_out_dir, train_data_path, valid_data_path = valid_data_path, replace_existing = True, \
	# 	vtree_method = 'miMetis', keep_generated_files = True)


	# #Test with constraints
	# experiment_name = 'psdd_search_constraints'
	# psdd_out_dir = os.path.join(experiment_dir_path,'./{}/'.format(experiment_name))
	# test_contraints = os.path.join(experiment_dir_path, './test_contraints.cnf')
	# learn_psdd(psdd_out_dir, train_data_path, constraints_cnf_file = test_contraints, valid_data_path = valid_data_path,\
	# 			replace_existing = True, vtree_method = 'miBlossom')


	#Test query
	out_learnpsdd_tmp_dir = os.path.abspath(os.path.join(experiment_dir_path, './psdd_search_student_compute/'))
	query_psdd_from_dir(train_data_path, query_data_path, out_learnpsdd_tmp_dir)


'''
query file example: 2 queries
Pr(not '1' and not '2') where '1' and '2' indicat the variables
Pr(not '10' and '20') where '10' and '20' indicat the variables

query.data file content:

-1,-2
-10,20

'''



'''
cnf file example: 8 Variables, 7 Clauses
	the kb sepcifies that variables {1,2,3,4} are onehot encoded

example.cnf file content:

c this the Abstacted SMT Formalu in CNF (DEMACS)
p cnf 8 7
1 2 3 4 0
-1 -2 0
-1 -3 0
-1 -4 0
-2 -3 0
-2 -4 0
-3 -4 0

'''


