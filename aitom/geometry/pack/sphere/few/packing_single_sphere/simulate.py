"""
If you want to see the output image(location, loss, etc.) of the simulating process
please uncomment the line 4, line 134-139.
"""
from  . import pdb2ball_single as P2B
from . import random_select as RS
from . import packing as PK
# from . import drawing as DR
import pprint
import sys

packing_op = {#'target': 'pdb1',
              'random_protein_number': 4,
              'PDB_ori_path': '../IOfile/pdbfile/',
              'iteration': 5001,
              'step': 1,
              'show_img': 1,
              'show_log': 1,
              'boundary_shpere': None}


def packing_with_target(packing_op):
    """
    :param
        target_protein: the name of the target macromolecule
        random_protein_number: the number of random neighbors
        iteration: the number of iteration time
        PDB_ori_path: the path to all pdb files
        step: the moving step(parameter to chotrol how long a macromolecules will move) in each iteration
        show_img: draw image or not
        show_log: print log or not
    :return:
        the optimal packing result and other info
        packing_result = {
            'general_info': {
                'target': name of the target macromolecules
                'random_protein_number'
                'iteration'
                'step'
                'box_size'}
            'boundary_shpere': a dictionary format the same as the output in pdb2ball_single {
                'pdb_id': {'pdb_id': ****, 'atom_number': ****, 'center': ****, 'radius': ****}
                'pdb_id': {'pdb_id': ****, 'atom_number': ****, 'center': ****, 'radius': ****}
                ...}
            'optimal_result': {
                'pdb_id': a list of all macromolecules' pdb_id
                'box_size': a number, the size of the simulation field
                # the following information is the same as the output of do_packing()
                'sum' : a number, final value of the loss
                'grad' : a number, final valus of the grad of the loss
                'x' : list, final location of all macromolecules in the simulation field
                'y' : list, final location of all macromolecules in the simulation field
                'z' : list, final location of all macromolecules in the simulation field
                'sum_list' : list, the sumlist of all the macromolecules, is used to draw the img of loss
                    in each iteration}}
    """
    # convert pdb file into single ball and get the center and radius of this ball.
    # boundary_shpere = P2B.pdb2ball_single(PDB_ori_path=packing_op['PDB_ori_path'], show_log=packing_op['show_log'])

    # set target protein
    if packing_op['show_log'] != 0:
        print('target protein is', packing_op['target'], '\n\n')
    protein_name = [packing_op['target']]
    print("Protein : {}".format(protein_name))
#    print("Keys: {}".format(packing_op['boundary_shpere']['pdb1'].keys()))
    radii_list = [packing_op['boundary_shpere'][protein_name[0]]['radius']]
    print("List ",radii_list)
    # select random proteins
    random_protein = RS.get_random_protein(packing_op['boundary_shpere'],
                                           protein_number=packing_op['random_protein_number'],
                                           show_log=packing_op['show_log'])

    # get important info
    info = RS.get_radius_and_id(random_protein, radii_list=radii_list, protein_name=protein_name,
                                show_log=packing_op['show_log'])
    radius_list = info['radius_list']
    protein = info['protein_key']

    # set box
    box_size = PK.get_box_size(radius_list, show_log=packing_op['show_log'])  # obtain box size

    # random run multiple times and return the optimal result
    dict_out = {}
    sum_list = []

    # try n times and get the optimal solution
    for i in range(5):
        if packing_op['show_log'] != 0:
            print('Round', i + 1)

        # initialization
        location = PK.initialization(radius_list, box_size, show_log=packing_op['show_log'])
        save_location = [tuple(location[0]), tuple(location[1]), tuple(location[2])]
        # print('init 1',location)

        # packing
        dict = PK.do_packing(radius_list, location, iteration=packing_op['iteration'], step=packing_op['step'],
                             show_log=packing_op['show_log'])
        save_location = [list(save_location[0]), list(save_location[1]), list(save_location[2])]
        dict['initialization'] = save_location
        dict_out[i] = dict
        # print('init x', dict['initialization'][0])
        # print('init y', dict['initialization'][1])
        # print('init z', dict['initialization'][2])
        # print('final x',dict['x'])
        # print('final y',dict['y'])
        # print('final z',dict['z'])

        # save result
        sum_list.append(dict['sum'])
        if packing_op['show_log'] != 0:
            print('sum:\t', dict['sum'], '\tgrad:\t', dict['grad'], '\n\n')

    # choose a best result
    index = sum_list.index(min(sum_list))
    min_dict = dict_out[index]
    min_dict['pdb_id'] = protein
    min_dict['box_size'] = box_size
    general_info = {'target': packing_op['target'],
                    'random_protein_number': packing_op['random_protein_number'],
                    'iteration': packing_op['iteration'],
                    'step': packing_op['step'],
                    'box_size': box_size}

#    return {'optimal_result':min_dict,'general_info':dict_out}
    packing_result = {'general_info': general_info,
                      'boundary_shpere': packing_op['boundary_shpere'],
                      'optimal_result': min_dict}
    return packing_result

    # delete sum_list and print the optimal 
"""
import tomominer.structure.pdb.situs_pdb2vol as SP
"""


def convert(op):
    """
    functions to convert pdb structures to density maps
    convert pdb file to a volume file using Situs's pdb2vol
    """
    import tempfile
    import os
    import subprocess
    import aitom.io.file as TIF

    [fh, out_fn] = tempfile.mkstemp(prefix='tmp-%s-%d-%d-' % (op['pdb_id'], op['spacing'], op['resolution']),
                                    suffix='.mrc')

    os.close(fh)

    assert os.path.isfile(op['pdb_file'])
    cmd = str("./"+op['situs_pdb2vol_program'])+" "+op['pdb_file']+" "+out_fn
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
                            universal_newlines=True)
    proc.stdin.write("1\n")
    proc.stdin.write("2\n")
    proc.stdin.write("{}\n".format(op['spacing']))
    proc.stdin.write("{}\n".format(op['resolution']))
    proc.stdin.write("1\n")
    proc.stdin.write("1\n")
    proc.stdin.write("1\n")


    # print(proc.stdin, 2,file=sys.stderr)  # Do you want to mass-weight the atoms ?    1: No   2: Yes
    # print(proc.stdin, 1,file=sys.stderr)  # Do you want to select atoms based on a B-factor threshold?            1: No       2: Yes
    # print(proc.stdin, op['spacing'],file=sys.stderr)  # Please enter the desired voxel spacing for the output map (in Angstrom):
    # print(proc.stdin, -op[
    #     'resolution'],file=sys.stderr)  # Kernel width. Please enter (in Angstrom):     (as pos. value) kernel half-max radius or (as
    # # neg. value) target resolution (2 sigma)
    # print(proc.stdin, 1,file=sys.stderr)  # Please select the type of smoothing kernel:       1: Gaussian, exp(-1.5 r^2 / sigma^2)
    # #       2: Triangular, max(0, 1 - 0.5 |r| / r-half)     3: Semi-Epanechnikov, max(0, 1 - 0.5 |r|^1.5 /
    # #       r-half^1.5)      4: Epanechnikov, max(0, 1 - 0.5 r^2 / r-half^2)         5: Hard Sphere, max(0,
    # #       1 - 0.5 r^60 / r-half^60)
    # print(proc.stdin, 1,file=sys.stderr)  # Do you want to correct for lattice interpolation smoothing effects?       1: Yes (
    # # slightly lowers the kernel width to maintain target resolution)     2: No
    # print(proc.stdin, 1,file=sys.stderr)  # Finally, please enter the desired kernel amplitude (scaling factor):

    # proc.wait()

    op['map'] = TIF.read_mrc_data(out_fn).astype('float')
    if packing_op['show_log'] != 0:
        print('The following is the optimal solution:')
        sum_list = min_dict.pop('sum_list')
        dic_print = pprint.PrettyPrinter(indent=4)
        dic_print.pprint(min_dict)
        # add back sum_list
        min_dict['sum_list'] = sum_list

    # show image
    # if packing_op['show_img'] != 0:
    #    DR.show_center_img(min_dict['initialization'][0], min_dict['initialization'][1], min_dict['initialization'][2])
    #    DR.show_center_img(min_dict['x'], min_dict['y'], min_dict['z'])
    #    DR.show_sum_img(min_dict['sum_list'], len(radius_list), protein_name)
    #    DR.get_packing_and_plot_ball(min_dict, boundary_shpere)

    # save general information
    general_info = {'target': packing_op['target'],
                    'random_protein_number': packing_op['random_protein_number'],
                    'iteration': packing_op['iteration'],
                    'step': packing_op['step'],
                    'box_size': box_size}

    # save return information
    packing_result = {'general_info': general_info,
                      'boundary_shpere': packing_op['boundary_shpere'],
                      'optimal_result': min_dict}

    return packing_result


if __name__ == '__main__':
    # convert pdb file into single ball and get the center and radius of this ball.
    packing_op['boundary_shpere'] = P2B.pdb2ball_single(PDB_ori_path='../IOfile/pdbfile/', show_log=0)
    try:
        packing_with_target(sys.argv[1])
    except:
        packing_with_target(packing_op)
