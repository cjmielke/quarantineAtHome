import os
import sys

def prepGPF(cwd):
	'''Extracted from MGLtools - this recreates key script steps and runs library with newer interpreter .....'''

	# none of this worked ..... but all we really need to do is run the whole project on numpy==1.8
	#numpy = 'mgltools_x86_64Linux2_1.5.6/lib/python2.5/site-packages/numpy/__init__.py'
	#numpy = 'mgltools_x86_64Linux2_1.5.6/lib/python2.5/site-packages/numpy/'
	#numpy = imp.load_source('numpy', os.path.join(os.getcwd(), numpy))

	ligand_filename = os.path.join(cwd, 'ligand.pdbqt')
	receptor_filename = os.path.join(cwd, 'receptor.pdbqt')
	gpf_filename = os.path.join(cwd, 'template.gpf')
	output_gpf_filename = os.path.join(cwd, 'autogrid.gpf')
	print output_gpf_filename

	#from AutoDockTools.GridParameters import GridParameter4FileMaker
	from mglmin.AutoDockTools.GridParameters import GridParameter4FileMaker

	center_on_ligand = False
	size_box_to_include_ligand = True
	npts_increment = 0
	ligand_types_defined = False
	verbose = 1

	gpfm = GridParameter4FileMaker(size_box_to_include_ligand=size_box_to_include_ligand, verbose=verbose)

	gpfm.read_reference(gpf_filename)
	gpfm.set_ligand(ligand_filename)
	gpfm.set_receptor(receptor_filename)


	# gpfm.set_grid_parameters(spacing=1.0)
	if center_on_ligand is True:
		gpfm.gpo['gridcenterAuto']['value'] = 0
		cenx, ceny, cenz = gpfm.ligand.getCenter()
		gpfm.gpo['gridcenter']['value'] = "%.3f %.3f %.3f" % (cenx, ceny, cenz)
	if npts_increment:
		orig_npts = gpfm.gpo['npts']['value']  # [40,40,40]
		if verbose: print "before increment npts=", orig_npts
		for ind in range(3):
			gpfm.gpo['npts']['value'][ind] += npts_increment
		if verbose: print "after increment npts =", gpfm.gpo['npts']['value']
	gpfm.write_gpf(output_gpf_filename)


