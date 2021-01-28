"""
This script converts pdb files to density maps
"""
import sys

sys.path.append("/mnt/ssd2/docker/ubuntu-sshd/home/v_hmrishav_bandyopadhyay/aitom/")

op = {'situs_pdb2vol_program': '../Situs_3.1/bin/pdb2vol',
      'spacing_s': [10.0],
      'resolution_s': [10.0],
      'pdb_dir': '../IOfile/pdbfile',
      'out_file': '../IOfile/map_single/situs_maps.pickle',
      'savepath': '../IOfile/map_single/'
      }


def pdb2map(op):
    # convert to density maps
    import aitom.structure.pdb.situs_pdb2vol__batch as TSPS
    import aitom.image.vol.util as TIVU
    #print("op",op)
    ms = TSPS.batch_processing(op)
    #print("fd")
    # use resize_center_batch_dict() to change maps into same size
    #print(ms[list(ms.keys())[0]][30.0][30.0].keys() )
    
    ms = {_: ms[_][30.0][30.0]['map'] for _ in ms}
    #ms = {_: ms[_][10.0][10.0] for _ in ms}

    import numpy as np
    for n in ms:
        print(n, np.shape(ms[n]))
    #print("MS ",ms)
    #ms = TIVU.resize_center_batch_dict(vs=ms, cval=0.0)
    print('#resize#')
    for n in ms:
        print(n, np.shape(ms[n]))

    return ms


def pdb2map_save(op):
    ms = pdb2map(op)
    from . import iomap as IM
    for n in ms:
        v = ms[n]
        IM.map2mrc(v, op['savepath'] + '{}.mrc'.format(n))

    data = {}
    i = 0
    for n in ms:
        data[i] = {n: ms[n]}
        i = i + 1
    import numpy as np
    np.save(op['savepath'] + 'data.npy', data)


if __name__ == '__main__':
    pdb2map_save(op)
