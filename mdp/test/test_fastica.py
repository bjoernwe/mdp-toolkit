from builtins import str
import mdp
from ._tools import *
uniform = mdp.numx_rand.random

def pytest_generate_tests(metafunc):
    _fastica_test_factory(metafunc)

def _fastica_test_factory(metafunc):
    # generate FastICANode testcases
    fica_parm = {'approach': ['symm', 'defl'],
                 'g': ['pow3', 'tanh', 'gaus', 'skew'],
                 'fine_g': [None, 'pow3', 'tanh', 'gaus', 'skew'],
                 'sample_size': [1, 0.99999],
                 'mu': [1, 0.999999],
                 'coarse_limit': [None, 0.01],
                 }

    for parms in mdp.utils.orthogonal_permutations(fica_parm):
        # skew nonlinearity works only with skewed input data
        if parms['g'] != 'skew' and parms['fine_g'] == 'skew':
            continue
        if parms['g'] == 'skew' and parms['fine_g'] != 'skew':
            continue
        # skip testing coarse_limit if g's are the same --
        # it should not be in effect
        if parms['coarse_limit'] is not None \
          and parms['g'] == parms['fine_g']:
          continue
        funcargs = dict(parms=parms)
        theid = fastICA_id(parms)
        metafunc.addcall(funcargs, id=theid)

def fastICA_id(parms):
    app =     'AP:'+parms['approach']
    nl =      'NL:'+parms['g']
    fine_nl = 'FT:'+str(parms['fine_g'])
    coarse_l = 'CL:'+str(parms['coarse_limit'])
    if parms['sample_size'] == 1:
        compact = 'SA:01 '
    else:
        compact = 'SA:<1 '
    if parms['mu'] == 1:
        compact += 'S:01'
    else:
        compact += 'S:<1'
    desc = ' '.join([app, nl, fine_nl, compact, coarse_l])
    return desc


def test_FastICA(parms):
    if parms['g'] == 'skew':
        rand_func = mdp.numx_rand.exponential
    else:
        rand_func = uniform

    # try three times just to clear failures due to randomness
    for exc in (Exception, Exception, ()):
        try:
            ica = mdp.nodes.FastICANode(limit=10**(-decimal),**parms)
            ica2 = ica.copy()
            verify_ICANode(ica, rand_func=rand_func, vars=2)
            verify_ICANodeMatrices(ica2, rand_func=rand_func, vars=2)
        except exc:
            pass
