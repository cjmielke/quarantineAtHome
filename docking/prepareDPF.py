
import string
import os.path
from MolKit import Read
from AutoDockTools.DockingParameters import DockingParameters, DockingParameter4FileMaker, genetic_algorithm_list, \
                genetic_algorithm_local_search_list4, local_search_list4,\
                simulated_annealing_list4
                


 

def usage():
    print "Usage: prepare_dpf4.py -l pdbqt_file -r pdbqt_file"
    print "    -l ligand_filename"
    print "    -r receptor_filename"
    print
    print "Optional parameters:"
    print "    [-o output dpf_filename]"
    print "    [-i template dpf_filename]"
    print "    [-x flexres_filename]"
    print "    [-p parameter_name=new_value]"
    print "    [-k list of parameters to write]"
    print "    [-e write epdb dpf ]"
    print "    [-v] verbose output"
    print "    [-L] use local search parameters"
    print "    [-S] use simulated annealing search parameters"
    print "    [-s] seed population using ligand's present conformation"
    print
    print "Prepare a docking parameter file (DPF) for AutoDock4."
    print
    print "   The DPF will by default be <ligand>_<receptor>.dpf. This"
    print "may be overridden using the -o flag."


def prepDPF(cwd):

    receptor_filename = os.path.join(cwd, 'receptor.pdbqt')
    ligand_filename = os.path.join(cwd, 'ligand.pdbqt')
    dpf_filename = os.path.join(cwd, 'autodock.dpf')
    template_filename = os.path.join(cwd, 'template.dpf')

    flexres_filename = None
    parameters = []
    parameter_list = genetic_algorithm_local_search_list4
    pop_seed = False
    verbose = None
    epdb_output = False


    #9/2011: fixing local_search bugs:
    # specifically: 
    # 1. quaternion0 0 0 0 0  
    # 2. dihe0 0 0 0 0 0 <one per rotatable bond>
    # 3. about == tran0 
    # 4. remove tstep  qstep and dstep
    # 5. remove ls_search_freq
    local_search = parameter_list==local_search_list4
    dm = DockingParameter4FileMaker(verbose=verbose)

    if template_filename is not None:  #setup values by reading dpf
        dm.dpo.read(template_filename)

    dm.set_ligand(ligand_filename)
    dm.set_receptor(receptor_filename)

    #dm.set_docking_parameters( ga_num_evals=1750000,ga_pop_size=150, ga_run=20, rmstol=2.0)
    kw = {}    
    for p in parameters:
        key,newvalue = string.split(p, '=')
        #detect string reps of lists: eg "[1.,1.,1.]"
        if newvalue[0]=='[':
            nv = []
            for item in newvalue[1:-1].split(','):
                nv.append(float(item))
            #print "nv=", nv
            newvalue = nv
        if key=='epdb_flag':
            print "setting epdb_flag to", newvalue
            kw['epdb_flag'] = 1
        elif key=='set_psw1':
            print "setting psw1_flag to", newvalue
            kw['set_psw1'] = 1
            kw['set_sw1'] = 0
        elif key=='set_sw1':
            print "setting set_sw1 to", newvalue
            kw['set_sw1'] = 1
            kw['set_psw1'] = 0
        elif key=='include_1_4_interactions_flag':
            kw['include_1_4_interactions'] = 1
        elif 'flag' in key:
            if newvalue in ['1','0']:
                newvalue = int(newvalue)
            if newvalue =='False':
                newvalue = False
            if newvalue =='True':
                newvalue = True
        elif local_search and 'about' in key:
            kw['about'] = newvalue
            kw['tran0'] = newvalue     
        else:         
            kw[key] = newvalue
        apply(dm.set_docking_parameters, (), kw)
        if key not in parameter_list:
            #special hack for output_pop_file
            if key=='output_pop_file':
                parameter_list.insert(parameter_list.index('set_ga'), key)
            else:
                parameter_list.append(key) 
    dm.write_dpf(dpf_filename, parameter_list, pop_seed)
    

