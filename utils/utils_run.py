import logging

#  Run parameters
random_seed = 42
nb_bootstrap_samples = 1000

#  Some customized exceptions to catch run that crashed
class CustomizedValueError(ValueError):
    pass
