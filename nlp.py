import os
import re
# from nltk.parse import stanford 
# stanza.install_corenlp()
from nltk.stem import WordNetLemmatizer
# from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.parse.stanford import StanfordParser
from nltk.tree import *
from six.moves import urllib
import zipfile
import sys
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# These few lines are important
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Download zip file from https://nlp.stanford.edu/software/stanford-parser-full-2018-10-17.zip and extract in stanford-parser-full-2015-04-20 folder in higher directory
os.environ['CLASSPATH'] = os.path.join(BASE_DIR, 'stanford-parser-full-2018-10-17')
os.environ['STANFORD_MODELS'] = os.path.join(BASE_DIR,
                                             'stanford-parser-full-2018-10-17/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')

# checks if jar file of stanford parser is present or not
def is_parser_jar_file_present():
    stanford_parser_zip_file_path = os.environ.get('CLASSPATH') + ".jar"
    return os.path.exists(stanford_parser_zip_file_path)

def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.perf_counter()
        return
    duration = time.perf_counter() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = min(int(count*block_size*100/total_size),100)
    sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

# downloads stanford parser
def download_parser_jar_file():
    stanford_parser_zip_file_path = os.environ.get('CLASSPATH') + ".jar"
    url = "https://nlp.stanford.edu/software/stanford-parser-full-2018-10-17.zip"
    urllib.request.urlretrieve(url, stanford_parser_zip_file_path, reporthook)

# extracts stanford parser
def extract_parser_jar_file():
    stanford_parser_zip_file_path = os.environ.get('CLASSPATH') + ".jar"
    try:
        with zipfile.ZipFile(stanford_parser_zip_file_path) as z:
            z.extractall(path=BASE_DIR)
    except Exception:
        os.remove(stanford_parser_zip_file_path)
        download_parser_jar_file()
        extract_parser_jar_file()

# extracts models of stanford parser
def extract_models_jar_file():
    stanford_models_zip_file_path = os.path.join(os.environ.get('CLASSPATH'), 'stanford-parser-3.9.2-models.jar')
    stanford_models_dir = os.environ.get('CLASSPATH')
    with zipfile.ZipFile(stanford_models_zip_file_path) as z:
        z.extractall(path=stanford_models_dir)

# checks jar file and downloads if not present 
def download_required_packages():
    if not os.path.exists(os.environ.get('CLASSPATH')):
        if is_parser_jar_file_present():
           pass
        else:
            download_parser_jar_file()
        extract_parser_jar_file()

    if not os.path.exists(os.environ.get('STANFORD_MODELS')):
        extract_models_jar_file()

# stop words that are not to be included in ISL
stop_words = set(["am","are","is","was","were","be","being","been","have","has","had",
					"does","did","could","should","would","can","shall","will","may",
					"might","must","let", 'for', 'of', 'an', 'the', 'having', 'to', 'and', 'or'])

def convert_to_sentence_list(text):
	sentences = []
	
	for sentence in sent_tokenize(text):
		sentences.append(sentence)
	return sentences

# converts to words array for each sentence. ex=[ ["This","is","a","test","sentence"]];
def convert_to_word_list(sentences):
	temp_list=[]
	words = []
	for sentence in sentences:
		for word in sentence.split():
			temp_list.append(word)
		words.append(temp_list.copy())
		temp_list.clear()
	return words

# removes stop words
def filter_words(words):
	temp_list=[]
	final_words=[]
	# removing stop words from word_list
	for word in words:
		temp_list.clear()
		for w in word:
			if w not in stop_words:
				temp_list.append(w)
		final_words.append(temp_list.copy());
	
	return final_words

# removes punctutation 
def remove_punct(words):
	# removes punctutation from words
	for i in words:
		for j in i:
			if re.sub(r'[^\w\s]', '', j) == '':
				try:
					i.remove(j)
				except ValueError:
					pass
	return words

# lemmatizes words
def lemmatize(words):
	wnl = WordNetLemmatizer()
	for i in range(len(words)):
		for j in range(len(words[i])):
			words[i][j] = wnl.lemmatize(words[i][j])
	return words
			
def label_parse_subtrees(parent_tree):
    tree_traversal_flag = {}

    for sub_tree in parent_tree.subtrees():
        tree_traversal_flag[sub_tree.treeposition()] = 0
    return tree_traversal_flag

# handles if noun is in the tree
def handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    # if clause is Noun clause and not traversed then insert them in new tree first
    if tree_traversal_flag[sub_tree.treeposition()] == 0 and tree_traversal_flag[sub_tree.parent().treeposition()] == 0:
        tree_traversal_flag[sub_tree.treeposition()] = 1
        modified_parse_tree.insert(i, sub_tree)
        i = i + 1
    return i, modified_parse_tree

# handles if verb/proposition is in the tree followed by nouns
def handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    # if clause is Verb clause or Proportion clause recursively check for Noun clause
    for child_sub_tree in sub_tree.subtrees():
        if child_sub_tree.label() == "NP" or child_sub_tree.label() == 'PRP':
            if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                tree_traversal_flag[child_sub_tree.treeposition()] = 1
                modified_parse_tree.insert(i, child_sub_tree)
                i = i + 1
    return i, modified_parse_tree

# modifies the tree according to POS
def modify_tree_structure(parent_tree):
    # Mark all subtrees position as 0
    tree_traversal_flag = label_parse_subtrees(parent_tree)
    # Initialize new parse tree
    modified_parse_tree = Tree('ROOT', [])
    i = 0
    for sub_tree in parent_tree.subtrees():
        if sub_tree.label() == "NP":
            i, modified_parse_tree = handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)
        if sub_tree.label() == "VP" or sub_tree.label() == "PRP":
            i, modified_parse_tree = handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)

    # recursively check for omitted clauses to be inserted in tree
    for sub_tree in parent_tree.subtrees():
        for child_sub_tree in sub_tree.subtrees():
            if len(child_sub_tree.leaves()) == 1:  #check if subtree leads to some word
                if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                    tree_traversal_flag[child_sub_tree.treeposition()] = 1
                    modified_parse_tree.insert(i, child_sub_tree)
                    i = i + 1

    return modified_parse_tree

# converts the text in parse trees
def reorder_eng_to_isl(input_string):
	download_required_packages()
	# check if all the words entered are alphabets.
	count=0
	for word in input_string:
		if(len(word)==1):
			count+=1

	if(count==len(input_string)):
		return input_string
	
	parser = StanfordParser()
	# Generates all possible parse trees sort by probability for the sentence
	possible_parse_tree_list = [tree for tree in parser.parse(input_string)]
	# print("i am testing this",possible_parse_tree_list)
	# Get most probable parse tree
	parse_tree = possible_parse_tree_list[0]
	print(parse_tree)
	# Convert into tree data structure
	parent_tree = ParentedTree.convert(parse_tree)
	
	modified_parse_tree = modify_tree_structure(parent_tree)
	
	parsed_sent = modified_parse_tree.leaves()
	return parsed_sent

# checks if sigml file exists of the word if not use letters for the words
def final_output(input):
	valid_words=open("words.txt",'r').read();
	valid_words=valid_words.split('\n')
	fin_words=[]
	for word in input:
		if word == None:
			continue
		word=word.lower()
		if(word not in valid_words):
			for letter in word:
				# final_string+=" "+letter
				fin_words.append(letter);
		else:
			fin_words.append(word);

	return fin_words

# converts the final list of words in a final list with letters seperated if needed
def convert_to_final(words):
	output = []
	for word in words:
		output.append(final_output(word))
	return output

# takes input from the user
def translate(text):
	clean_text= text.strip().replace("\n","").replace("\t","")

	return convert(clean_text)

def convert(some_text):
	sentences = convert_to_sentence_list(some_text)
	words = convert_to_word_list(sentences)

	# reorders the words in input
	for i, word in enumerate(words):
		words[i]=reorder_eng_to_isl(word)

	# removes punctuation and lemmatizes words
	# words = remove_punct(words)
	words = filter_words(words)
	words = lemmatize(words)
	output = convert_to_final(words)
	output = remove_punct(output)
	# remove_punct(final_output_in_sent)
	print(output)
	return output
	