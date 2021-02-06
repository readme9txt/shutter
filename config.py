import configparser
import os

# 加载配置文件
ini_file = 'configs.ini'
conf = configparser.ConfigParser()
if not os.path.exists(ini_file):
    conf.add_section('config')
    conf.set('config', 'output_dir', './')
    conf.write(open(ini_file, 'w'))
conf.read(ini_file)


class Config:
    output_dir = conf.get('config', 'output_dir')

    @staticmethod
    def set_output_dir(path):
        conf.set('config', 'output_dir', path)
        conf.write(open(ini_file, 'w'))
        Config.output_dir = path


if not os.path.exists(Config.output_dir):
    Config.output_dir = './'
