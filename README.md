<!-- <table>
    <thead>
        <tr>
            <th style="text-align:center;"><img src="docs/images/haven_logo.png" width="40%" alt="Image"></th>
        </tr>
    </thead>
    <tbody>
    </tbody>
</table> -->
# Haven 

A library for defining hyperparameters, launching and managing many experiments, and visualizing their results. If you have access to the orkestrator, you can run and manage thousands of experiments in parallel.

### Install
```
$ pip install --upgrade git+https://github.com/ElementAI/haven
```

<!-- /home/issam/Research_Ground/haven/ -->

### Examples

The following are example projects built using this library.

- [Minimal](https://github.com/ElementAI/haven/tree/master/examples/minimal)
- [Classification](https://github.com/ElementAI/haven/tree/master/examples/classification)
- [Active Learning](https://github.com/ElementAI/haven/tree/master/examples/active_learning)
- [Object Counting](https://github.com/ElementAI/haven/tree/master/examples/object_counting)


### Usage

A minimal codebase can include the following 4 files. They are hyper-linked to a template source code.

- [`exp_configs.py`](https://github.com/ElementAI/haven/tree/master/examples/minimal/exp_configs.py) contains experiment groups for MNIST.
- [`trainval.py`](https://github.com/ElementAI/haven/tree/master/examples/minimal/trainval.py) contains the main training and validation loop for an experiment.
- [`datasets.py`](https://github.com/ElementAI/haven/tree/master/examples/minimal/datasets.py) contains the code for acquiring a Pytorch dataset.
- [`models.py`](https://github.com/ElementAI/haven/tree/master/examples/minimal/models.py) contains the code for acquiring a Pytorch model.

#### 1. Run the Experiments

To run the `mnist` experiment group, follow the two steps below.

##### 2.1 Run trainval.py in Command Line

The following command launches the mnist experiments and saves their results under `../results/`.

```
python trainval.py -e mnist -sb ../results -r 1
```

##### 2.2 Using the orkestrator

The following script uses the orkestrator to run all the experiments in parallel. Note that you will be able to view their status and logs using the visualization script in Section 4. To request access to the orkestrator please visit the [orkestrator website](https://www.elementai.com/products/ork).

```python
# launch jobs
elif args.run_jobs:
        # launch jobs
        from haven import haven_jobs as hjb
        run_command = ('python trainval.py -ei <exp_id> -sb %s -d %s -nw 1' %  (args.savedir_base, args.datadir_base))
        job_config = {'volume': <volume>,
                    'image': <docker image>,
                    'bid': '1',
                    'restartable': '1',
                    'gpu': '4',
                    'mem': '30',
                    'cpu': '2'}
        workdir = os.path.dirname(os.path.realpath(__file__))

        hjb.run_exp_list_jobs(exp_list, 
                            savedir_base=args.savedir_base, 
                            workdir=workdir,
                            run_command=run_command,
                            job_config=job_config)
```

#### 3. Visualize the Results

The following two steps will setup the visualization environment.

##### 3.1 Launch Jupyter

Run the following in command line to install a Jupyter server
```bash
jupyter nbextension enable --py widgetsnbextension --sys-prefix
jupyter notebook
```

or if you are working using an open-ssh server, run the following instead,

```
jupyter notebook --ip 0.0.0.0 --port 9123 \
      --notebook-dir="/home/$USER" --NotebookApp.token="password"
```

##### 3.2 Run Jupyter script

Run the following script from a Jupyter cell to launch a dashboard.


```python
from haven import haven_jupyter as hj
from haven import haven_results as hr
from haven import haven_utils as hu

# path to where the experiments got saved
savedir_base = <insert_savedir_base>
exp_list = None

# exp_list = hu.load_py(<exp_config_name>).EXP_GROUPS[<exp_group>]
# get experiments
rm = hr.ResultManager(exp_list=exp_list, 
                      savedir_base=savedir_base, 
                      verbose=0
                     )
# launch dashboard
hj.get_dashboard(rm, vars(), wide_display=True)
```

This script outputs the following dashboard.

![](examples/4_results.png)


### Contributing

We love contributions!
