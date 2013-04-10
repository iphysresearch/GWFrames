#! /usr/bin/env python

"""
Extrapolate a bunch of waveforms.

"""


DefaultTemplate = """#! /usr/bin/env python
## Automatically generated by {ScriptName}

# Set up the paths
D = {}
D['InputDirectory'] = '{TopLevelInputDir}/{Subdirectory}'
D['OutputDirectory'] = '{TopLevelOutputDir}/{Subdirectory}'
D['DataFile'] = '{DataFile}'

# Find ChMass from metadata.txt
import re
ChMass = 0.0
try :
    with open('{TopLevelInputDir}/{Subdirectory}/metadata.txt', 'r') as file :
        for line in file :
            m = re.match(r'\s*relaxed-mass[12]\s*=\s*([0-9.]*)', line)
            if(m) : ChMass += float(m.group(1))
    D['ChMass'] = ChMass
except :
    print("WARNING: Could not find metadata.txt in '{TopLevelInputDir}/{Subdirectory}'")

# Now run the actual extrapolation
import GWFrames.Extrapolation
try :
    GWFrames.Extrapolation.Extrapolate(**D)
except Exception as e : # Pass exceptions to shell as failures
    from sys import exit
    print e
    exit(1)
"""



if __name__ == "__main__" :
    import os
    import sys
    import argparse
    import sqlite3
    from datetime import datetime
    from GWFrames.Extrapolation import *
    from GWFrames.Extrapolation import _safe_format
    
    # Set up and run the parser
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('--dry_run', action='store_true',
                        help='do not actually run extrapolations; just show directories that would be run')
    parser.add_argument('--generate_database', default='',
                        help='create the named sqlite3 database to track which extrapolations need to be done')
    parser.add_argument('--use_database', default='',
                        help='use the named sqlite3 database to track which extrapolations need to be done')
    parser.add_argument('--run_unstarted', action='store_true',
                        help='find directories with data that have not yet been started')
    parser.add_argument('--rerun_new_data', action='store_true',
                        help='find directories with data that is newer than the last completed extrapolation')
    parser.add_argument('--rerun_unfinished', action='store_true',
                        help='find directories where the extrapolation was started, but did not finish')
    parser.add_argument('--rerun_errored', action='store_true',
                        help='find directories where the extrapolation was started, but failed')
    parser.add_argument('--rerun_all', action='store_true',
                        help='find all possible directories with sufficient data')
    parser.add_argument('--start_with', default=0,
                        help='offset the place we start on, just to avoid possible collisions')
    parser.add_argument('--template_file', default='',
                        help='file name containing the template extrapolation script (default shown with the following option)')
    parser.add_argument('--show_default_template', action='store_true',
                        help='simply print out the default extrapolation script template')
    parser.add_argument('--input_dir', default='FiniteRadiusData',
                        help='directory in which the possible data may be found (default: FiniteRadiusData)')
    parser.add_argument('--output_dir', default='ExtrapolatedData',
                        help='directory in which the resulting extrapolations will be (default: ExtrapolatedData)')
    args = vars(parser.parse_args(sys.argv[1:]))
    
    # If we are asked for the default template, just print it out and quit
    if(args['show_default_template']) :
        print(DefaultTemplate)
        import sys
        sys.exit(0)
    
    # Make sure we have the full path to both directories
    TopLevelInputDir = os.path.abspath(args['input_dir'])
    TopLevelOutputDir = os.path.abspath(args['output_dir'])
    if(TopLevelInputDir.endswith('/')) : TopLevelInputDir = TopLevelInputDir[:-1]
    if(TopLevelOutputDir.endswith('/')) : TopLevelOutputDir = TopLevelOutputDir[:-1]
    
    # Get the template
    if(args['template_file']) :
        try :
            with open(args['template_file'], 'r') as myfile :
                Template = myfile.read()
        except IOError :
            print("Could not find file '{0}' specified in input arguments".format(args['template_file']))
            raise
    else :
        Template = DefaultTemplate
    Template = _safe_format(Template, ScriptName = sys.argv[0], TopLevelInputDir=TopLevelInputDir, TopLevelOutputDir=TopLevelOutputDir)
    
    # If no options were added, default to just run_unstarted, but
    # other options can be specified which overrule this.
    if(not args['run_unstarted'] and not args['rerun_new_data'] and not args['rerun_unfinished'] and not args['rerun_errored'] and not args['rerun_all']) :
        args['run_unstarted'] = True
    
    # Just a little helper function
    def _uniq(seq) :
        checked = []
        for e in seq :
            if e not in checked :
                checked.append(e)
        return checked
    
    # Determine the runs we will try
    Runs = []
    SubdirectoriesAndDataFiles = FindPossibleExtrapolationsToRun(TopLevelInputDir)
    if(args['rerun_all']) :
        Runs = SubdirectoriesAndDataFiles
    else :
        if(args['run_unstarted']) :
            Runs.extend(UnstartedExtrapolations(TopLevelOutputDir, SubdirectoriesAndDataFiles))
        if(args['rerun_new_data']) :
            Runs.extend(NewerDataThanExtrapolation(TopLevelOutputDir, SubdirectoriesAndDataFiles))
        if(args['rerun_unfinished']) :
            Runs.extend(StartedButUnfinishedExtrapolations(TopLevelOutputDir, SubdirectoriesAndDataFiles))
        if(args['rerun_errored']) :
            Runs.extend(ErroredExtrapolations(TopLevelOutputDir, SubdirectoriesAndDataFiles))
    Runs = _uniq(Runs)
    Runs = Runs[int(args['start_with']):] + Runs[:int(args['start_with'])]
    
    # If requested, generate a database, and use that to do the runs
    if(args['generate_database']) :
        conn = sqlite3.connect(args['generate_database'], timeout=60)
        conn.isolation_level = 'EXCLUSIVE'
        conn.execute('BEGIN EXCLUSIVE')
        c = conn.cursor()
        c.execute("""CREATE TABLE extrapolations
             (subdirectory text, datafile text, started text, finished text, error integer)""")
        for Subdirectory,DataFile in Runs :
            c.execute("INSERT INTO extrapolations VALUES ('{0}','{1}','','',0)".format(Subdirectory, DataFile))
        conn.commit()
        conn.close()
    else :
        # Now run the extrapolation
        print("Running the following {0} runs:\n{1}".format(len(Runs),Runs))
        print ""
        for Subdirectory,DataFile in Runs :
            if(args['use_database']) :
                conn = sqlite3.connect(args['use_database'], timeout=60)
                conn.isolation_level = 'EXCLUSIVE'
                conn.execute('BEGIN EXCLUSIVE')
                c = conn.cursor()
                record = [r for r in c.execute("""SELECT started, finished, error FROM extrapolations WHERE subdirectory='{0}' AND datafile='{1}'""".format(
                            Subdirectory, DataFile))]
                if(record[0][0]) :
                    # This has already been run
                    print("{0}/{1} has already run".format(Subdirectory, DataFile))
                    conn.close()
                else :
                    print("Extrapolating {0}/{1}".format(Subdirectory, DataFile))
                    c.execute("""UPDATE extrapolations SET started='{0}' WHERE subdirectory='{1}' AND datafile='{2}'""".format(
                            str(datetime.now()), Subdirectory, DataFile))
                    conn.commit()
                    conn.close()
                    if(args['dry_run']) :
                        print("Actually, this is just a dry run...  that's changing the database...")
                        ReturnValue = 17
                    else :
                        ReturnValue = RunExtrapolation(TopLevelInputDir, TopLevelOutputDir, Subdirectory, DataFile, Template)
                    conn = sqlite3.connect(args['use_database'], timeout=60)
                    conn.isolation_level = 'EXCLUSIVE'
                    conn.execute('BEGIN EXCLUSIVE')
                    c = conn.cursor()
                    c.execute("""UPDATE extrapolations SET finished='{0}',error='{1}' WHERE subdirectory='{2}' AND datafile='{3}'""".format(
                            str(datetime.now()), ReturnValue, Subdirectory, DataFile))
                    conn.commit()
                    conn.close()
            else :
                print("Extrapolating {0}/{1}".format(Subdirectory, DataFile))
                if(args['dry_run']) :
                    print("Actually, this was just a dry run...")
                else :
                    RunExtrapolation(TopLevelInputDir, TopLevelOutputDir, Subdirectory, DataFile, Template)
