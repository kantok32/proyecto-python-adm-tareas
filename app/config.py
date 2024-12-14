import configparser

def load_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    if 'network' not in config:
        config['network'] = {'ipAddress': '127.0.0.1'}
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    return config
