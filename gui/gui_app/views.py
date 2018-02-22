# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from collections import OrderedDict
import os
from django.template import loader
import sys
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from .forms import NameForm
import subprocess
from django.conf import settings as se
import string
import time

#adding table-extractor project path to system path so that python can search for the files in the paths specified.
sys.path.append(se.FILES_DIR)
sys.path.append(se.FILES_DIR+"/domain_explorer")
sys.path.append(se.FILES_DIR+"/table_extractor")

from table_extractor import settings, mapping_rules

# Create your views here.
def exploreDomain(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = NameForm(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data as required
			res_name = request.POST.get('resource_name', '')
			lang = request.POST.get('lang', '')
			res_type = request.POST.get('res_type', '')
			output_format = request.POST.get('output_format', '')
			print(res_name,lang,res_type,output_format)

			try:
				import pyDomainExplorer
				import settings


				file_path = os.path.join(se.FILES_DIR, 'pyDomainExplorer.py')
				# spawn a new process that makes a call to the pyDomainExplorer.py with required params, which creates/updates the
				# domain_settings.py for the given resource.
				proc = subprocess.Popen(['python', file_path, '-c', lang, 
					'-f', output_format, '-'+str(res_type), str(res_name)], stdout=subprocess.PIPE)
				#wait for the process to terminate
				proc.wait()
				pipe_output = proc.stdout.read()  #redirect the input into python variable
				print(pipe_output)
				#proc.kill()  #kill the spawned process

			#handle different errors
			except (ValueError):
				raise
			except (OSError):
				print('Error spawning process!')
				raise

			#get resource details and mappings of the resource from domain_settings.py
			header_dict, mappings = read_parameters_research()
			#get the mappings from actual dictionary
			dict_mappings = load_mappings()

			return render(request, 'gui_app/exploreDomain.html', {'form': form, 
				'header_dict': header_dict, 'mappings':mappings, 'dict_mappings':dict_mappings})

	# if a GET (or any other method) we'll create a blank form
	else:
		form = NameForm

	return render(request, 'gui_app/exploreDomain.html', {'form': form})

def extractTriples(request):
	
	try:

		file_path = os.path.join(se.FILES_DIR, 'pyTableExtractor.py')
		# spawn a new process that makes a call to the pyTableExtractor.py, which extracts the triples
		# and store them in an appropriate .ttl file
		proc = subprocess.Popen(['python', file_path ], stdout=subprocess.PIPE)
		#Wait for the process to terminate
		proc.wait()
		pipe_output = proc.stdout.read()  #redirect the input into python variable
		print(pipe_output)
		#proc.kill()  #kill the spawned process

	#handle different errors
	except (ValueError):
		raise
	except (OSError):
		print('Error spawning process!')
		raise

	context = {
		'success_msg': 'Triples formed successfuly', 'form': NameForm
	}

	return render(request, 'gui_app/exploreDomain.html' ,context)

def read_parameters_research():
    """
    Read parameters defined in header of settings file
    :return: set all parameters of research
    """
    
    head={}
    if os.path.exists("../domain_explorer/domain_settings.py"):
    	from domain_explorer import domain_settings

    	for name, val in domain_settings.__dict__.items():
			# read domain
			if name == settings.DOMAIN_TITLE:
				head[settings.DOMAIN_TITLE] = val
			# read language
			elif name == settings.CHAPTER:
				head[settings.CHAPTER] = val
			# read research type (-s -t or -w)
			elif name == settings.RESEARCH_TYPE:
				head[settings.RESEARCH_TYPE] = val
			# read name of resource's file
			elif name == settings.RESOURCE_FILE:
				head[settings.RESOURCE_FILE] = val
			# read output format value
			elif name == settings.OUTPUT_FORMAT_TYPE:
				head[settings.OUTPUT_FORMAT_TYPE] = val

    	#get mappings of the section/headers found inside the tables of the resource
    	mappings = read_mapping_rules()
    	#print(mappings)
    	return head, mappings
    else:
    	print("File not found. You should run pyDomainExplorer.")
    	#return empty dicts
    	return {},{}

def read_mapping_rules():
	"""
	Read mapping rules found during domain exploration
	:return: mapping rules
	"""
	
	if os.path.exists("../domain_explorer/domain_settings.py"):
		# Import is there for being sure that the file exists.
		from domain_explorer import domain_settings
		new_mapping_rules = OrderedDict()
		# search for right dictionary
		for name, val in domain_settings.__dict__.iteritems():
			if settings.SECTION_NAME in name:
				name_section = name.replace(settings.SECTION_NAME, "")
				new_mapping_rules[name_section] = OrderedDict()
				new_mapping_rules[name_section].update(val)
				#print(val)
	return new_mapping_rules

def load_mappings():
	"""
	Read actual mapping rules of the chapter selected
	:return: mapping rules already defined
	"""
	chapter = "en"
	actual_mapping_rules = OrderedDict()
	# read dictionary that is of the right language
	for name, val in mapping_rules.__dict__.iteritems():
		if chapter.upper() in name[-2:]:
			actual_mapping_rules = dict(val)
	return actual_mapping_rules