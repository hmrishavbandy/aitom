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
    #os.system('touch file_unique.mrc')
    root='./tmp_here/'
    out_fn=os.path.abspath(root+'{}-{}-{}.mrc'.format(op['pdb_id'],op['spacing'],op['resolution']))

    assert os.path.isfile(op['pdb_file'])
    cmd = [str(op['situs_pdb2vol_program']), op['pdb_file'], out_fn]
    #print("Inputs",cmd)
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

#    proc.wait()
    import mrcfile
    #print("Path here",out_fn)
    op['map'] = mrcfile.open(os.path.abspath(out_fn), mode='r+', permissive=True).data.astype('float')#TIF.read_mrc_data(out_fn).astype('float')

    os.remove(os.path.abspath(out_fn))

    print('pdb_id', op['pdb_id'], 'map size:', op['map'].shape, 'mean:', op['map'].mean(), 'std:', op['map'].std())
    return op


def convert_interactive(op):
    """interactively convert pdb file to a volume file using Situs's pdb2vol"""
    # raise           # currently this function does not work

    import tempfile
    import os
    import subprocess
    import Queue

    [fh, out_fn] = tempfile.mkstemp(suffix='.mrc')
    os.close(fh)

    cmd = [str(op['situs_pdb2vol_program']), op['pdb_file'], out_fn]
    print(cmd)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False,
                            universal_newlines=True)

    def enqueue_output(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def getOutput(outQueue):
        outStr = ''
        try:
            # Adds output from the Queue until it is empty
            while True:
                outStr += outQueue.get_nowait()

        except Queue.Empty:
            return outStr

    outQueue = Queue.Queue()
    errQueue = Queue.Queue()

    from threading import Thread

    outThread = Thread(target=enqueue_output, args=(proc.stdout, outQueue))
    errThread = Thread(target=enqueue_output, args=(proc.stderr, errQueue))

    outThread.daemon = True
    errThread.daemon = True

    outThread.start()
    errThread.start()

    '''
    found_key_sentence = False
    while True:
        line = proc.stdout.readline()
        print line

        if line == '':  break
        if line.find('Do you want to exclude the water atoms?') >= 0:       found_key_sentence = True

    assert  found_key_sentence
    '''

    import time
    while True:
        someInput = raw_input("Input: ")
        proc.stdin.write(someInput + '\n')

        errors = getOutput(errQueue)
        output = getOutput(outQueue)

        print('output:' + output)
        print('errors:' + errors)

        someInput = raw_input("Input: ")
        proc.stdin.write(someInput + '\n')

    os.remove(out_fn)

    print('return')
    return op

