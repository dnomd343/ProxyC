#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml


def loadEnvOptions(envFile: str) -> dict:
    try:
        yamlFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), envFile)
        yamlContent = open(yamlFile, 'r', encoding = 'utf-8').read()  # read raw yaml content
        envOptions = yaml.load(yamlContent, Loader = yaml.FullLoader)  # decode yaml configure
    except:  # something error in env configure
        return {}
    options = {
        'Version': envOptions['version'] if 'version' in envOptions else None,
        'LogLevel': envOptions['loglevel'] if 'loglevel' in envOptions else None,
        'WorkDir': envOptions['dir'] if 'dir' in envOptions else None,
        'DnsServer': envOptions['dns'] if 'dns' in envOptions else None,
    }
    if 'api' in envOptions:
        options.update({
            'ApiPort': envOptions['api']['port'] if 'port' in envOptions['api'] else None,
            'ApiPath': envOptions['api']['path'] if 'path' in envOptions['api'] else None,
            'ApiToken': envOptions['api']['token'] if 'token' in envOptions['api'] else None,
        })
    return {k: v for k, v in options.items() if v is not None}  # remove empty value
