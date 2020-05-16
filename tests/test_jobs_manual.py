import unittest
import numpy as np 
import os, sys
import torch
import shutil, time
import copy

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, path)

from haven import haven_utils as hu
from haven import haven_results as hr
from haven import haven_chk as hc
from haven import haven_jobs as hjb
from haven import haven_orkestrator as ho
from haven import haven_jupyter as hj


if __name__ == '__main__':
    # return
    exp_list = [{'model':{'name':'mlp', 'n_layers':30}, 
                'dataset':'mnist', 'batch_size':1}]
    savedir_base = '/home/toolkit/home_mnt/data/experiments'
    job_config = {
        'image': 'registry.console.elementai.com/mila.mattie_sandbox.fewshotgan/fewshot-gan',
        'data': ['mila.mattie_sandbox.fewshotgan.home:/home/toolkit/home_mnt'],
        'options': {
            'resources': {
                'gpu-mem': 16,
                'cuda-version': '10.1'
            }
        },
        'resources': {
            'cpu': 8,
            'mem': 12,
            'gpu': 2
        },
        'interactive': False,
    }

    # run
    run_command = ('python3.6 example.py -ei <exp_id> -sb %s' %  (savedir_base))
    hjb.run_exp_list_jobs(exp_list, 
                        savedir_base=savedir_base, 
                        workdir=os.path.dirname(os.path.realpath(__file__)),
                        run_command=run_command,
                        job_config=job_config,
                        force_run=False,
                        wait_seconds=0,
                        account_id='mila.mattie_sandbox.fewshotgan',
                        token=None
                        )

    assert(os.path.exists(os.path.join(savedir_base, hu.hash_dict(exp_list[0]), 'job_dict.json')))
    jm = hjb.JobManager(exp_list=exp_list, savedir_base=savedir_base)
    jm_summary_list = jm.get_summary()
    rm = hr.ResultManager(exp_list=exp_list, savedir_base=savedir_base)
    rm_summary_list = rm.get_job_summary()
    assert(rm_summary_list['table'].equals(jm_summary_list['table']))

    jm.kill_jobs()
    assert('CANCELLED' in jm.get_summary()['status'][0])