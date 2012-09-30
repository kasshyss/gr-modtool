""" Automatically create XML bindings for GRC from block code """

import os
import re
import sys
import glob
import xml.dom.minidom as minidom
from optparse import OptionGroup

from util_functions import remove_pattern_from_file, is_number
from modtool_base import ModTool
from cmakefile_editor import CMakeFileEditor

### Remove module ###########################################################
class ModToolMakeXML(ModTool):
    """ Make XML file for GRC block bindings """
    name = 'makexml'
    aliases = ('mx',)
    def __init__(self):
        ModTool.__init__(self)

    def setup_parser(self):
        " Initialise the option parser for 'gr_modtool.py makexml' "
        parser = ModTool.setup_parser(self)
        parser.usage = '%prog makexml [options]. \n Call %prog without any options to run it interactively.'
        ogroup = OptionGroup(parser, "Make XML module options")
        ogroup.add_option("-p", "--pattern", type="string", default=None,
                help="Filter possible choices for blocks to be parsed.")
        ogroup.add_option("-y", "--yes", action="store_true", default=False,
                help="Answer all questions with 'yes'. This can overwrite existing files!")
        parser.add_option_group(ogroup)
        return parser

    def setup(self):
        ModTool.setup(self)
        options = self.options
        if options.pattern is not None:
            self._info['pattern'] = options.pattern
        elif options.block_name is not None:
            self._info['pattern'] = options.block_name
        elif len(self.args) >= 2:
            self._info['pattern'] = self.args[1]
        else:
            self._info['pattern'] = raw_input('Which blocks do you want to parse? (Regex): ')
        if len(self._info['pattern']) == 0:
            self._info['pattern'] = '.'
        self._info['yes'] = options.yes

    def run(self):
        """ Go, go, go! """
        # 1) Go through lib/
        if not self._skip_subdirs['lib']:
            files = self._search_files('lib', '*.cc')
            for f in files:
                block_data = self._parse_cc_h(f)
                # Check if overwriting
                # Check if exists in CMakeLists.txt
        # 2) Go through python/


    def _search_files(self, path, path_glob):
        """ Search for files matching pattern in the given path. """
        files = glob.glob("%s/%s"% (path, path_glob))
        files_filt = []
        print "Searching for matching files in %s/:" % path
        for f in files:
            if re.search(self._info['pattern'], os.path.basename(f)) is not None:
                files_filt.append(f)
        if len(files_filt) == 0:
            print "None found."
        return files_filt


    def _parse_cc_h(self, filename):
        """ Go through a .cc and .h-file defining a block and info """
        def _type_translate(p_type, default_v):
            TRANS = {'float': 'real', 'double': 'real', 'gr_complex': 'complex'}
            if p_type in TRANS.keys():
                return TRANS[p_type]
            if default_v[0:2] == '0x' and p_type == 'int':
                return 'hex'
            return p_type

        blockname = os.path.splitext(os.path.basename(filename))[0]
        header_fname = blockname + '.h'
        blockname = blockname.replace(self._info['modname']+'_', '', 1)
        parser = ParserCCBlock(filename, header_fname, blockname)
        block_data = {}

        params = parser.read_params()
        iosig = parser.read_io_signature()

        # Adapt for GRC
        if is_number(iosig['in']['max_ports']) and int(iosig['in']['max_ports'].isdigit()) == -1:
            iosig['in']['max_ports'] = '$num_inputs'
            params.append({'name': 'Num inputs', 'key': 'num_inputs', 'type': 'int', 'default': 2})
        if iosig['out']['max_ports'].isdigit() and int(iosig['out']['max_ports'].isdigit()) == -1:
            iosig['out']['max_ports'] = '$num_outputs'
            params.append({'name': 'Num outputs', 'key': 'num_outputs', 'type': 'int', 'default': 2})




        # Figure out:
        # name, key from blockname
        # import statement
        # params (default value, type)
        # # sinks, # sources (types)





