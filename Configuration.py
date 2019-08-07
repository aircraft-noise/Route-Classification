import os
import yaml

def read_config(cfg_env_var = 'MONA_CFG'):
    #print(os.getenv(cfg_env_var))
    with open(os.getenv(cfg_env_var), 'r') as cfg_file_fd:
        return yaml.safe_load(cfg_file_fd)

configuration = read_config()

print('datafile_basedir: {}'.format(configuration['classify']['datafile_basedir']))

