import math
from itertools import chain
from multiprocessing import cpu_count, Pool

#  Multiprocessing parameters
NB_CORES = cpu_count() - 1


def parallelize(function, arguments_list, batch_mode=False, parallel=True):
    if parallel:
        if batch_mode:
            return parallelize_batch(function, arguments_list)
        else:
            with Pool(NB_CORES) as p:
                return p.map(function, arguments_list)
    else:
        return [function(arguments) for arguments in arguments_list]


def create_batch_function(function):
    def batch_function(a_list):
        return [function(a) for a in a_list]
    return batch_function


def parallelize_batch(function, argument_list):
    nb_argument = len(argument_list)
    batch_size = math.ceil(nb_argument / NB_CORES)
    with Pool(NB_CORES) as p:
        result_list = p.map(function, batch(argument_list, batch_size=batch_size))
        if None in result_list:
            return None
        else:
            return list(chain.from_iterable(result_list))


def batch_nb_cores(iterable):
    batch_size = math.ceil(len(iterable) / NB_CORES)
    return batch(iterable, batch_size)


def batch(iterable, batch_size):
    l = len(iterable)
    for ndx in range(0, l, batch_size):
        yield iterable[ndx:min(ndx + batch_size, l)]
