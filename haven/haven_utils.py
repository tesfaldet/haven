import contextlib
import copy
import hashlib
import itertools
import json
import os
import pickle
import shlex
import subprocess
import threading
import time
from datetime import datetime

import numpy as np
import pylab as plt
import torch
from PIL import Image


def cartesian_exp_group(exp_config):
    """Cartesian experiment config.

    It converts the exp_config into a list of experiment configuration by doing
    the cartesian product of the different configuration. It is equivalent to
    do a grid search.

    Parameters
    ----------
    exp_config : str
        Dictionary with the experiment Configuration

    Returns
    -------
    exp_list: str
        A list of experiments, each defines a single set of hyper-parameters
    """
    exp_config_copy = copy.deepcopy(exp_config)

    # Make sure each value is a list
    for k, v in exp_config_copy.items():
        if not isinstance(exp_config_copy[k], list):
            exp_config_copy[k] = [v]

    # Create the cartesian product
    exp_list_raw = (dict(zip(exp_config_copy.keys(), values))
                    for values in itertools.product(*exp_config_copy.values()))

    # Convert into a list
    exp_list = []
    for exp_dict in exp_list_raw:
        exp_list += [exp_dict]

    return exp_list


def hash_dict(exp_dict):
    """Create a hash for an experiment.

    Parameters
    ----------
    exp_dict : dict
        An experiment, which is a single set of hyper-parameters

    Returns
    -------
    hash_id: str
        A unique id defining the experiment
    """
    dict2hash = ""
    if not isinstance(exp_dict, dict):
        raise ValueError('exp_dict is not a dict')

    for k in sorted(exp_dict.keys()):
        if isinstance(exp_dict[k], dict):
            v = hash_dict(exp_dict[k])
        else:
            v = exp_dict[k]

        dict2hash += os.path.join(str(k), str(v))

    hash_id = hashlib.md5(dict2hash.encode()).hexdigest()

    return hash_id


def hash_str(str):
    """Hashes a string using md5.

    Parameters
    ----------
    str
        a string

    Returns
    -------
    str
        md5 hash for the input string
    """
    return hashlib.md5(str.encode()).hexdigest()


def save_json(fname, data, makedirs=True):
    """Save data into a json file.

    Parameters
    ----------
    fname : str
        Name of the json file
    data : [type]
        Data to save into the json file
    makedirs : bool, optional
        If enabled creates the folder for saving the file, by default True
    """
    if makedirs:
        os.makedirs(os.path.dirname(fname), exist_ok=True)
    with open(fname, "w") as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)


def load_mat(fname):
    """Load a matlab file.

    Parameters
    ----------
    fname : str
        File name

    Returns
    -------
    dict
        Dictionary with the loaded data
    """
    import scipy.io as io
    return io.loadmat(fname)


def load_json(fname, decode=None):  # TODO: decode???
    """Load a json file.

    Parameters
    ----------
    fname : str
        Name of the file
    decode : [type], optional
        [description], by default None

    Returns
    -------
    [type]
        Content of the file
    """
    with open(fname, "r") as json_file:
        d = json.load(json_file)

    return d


def read_text(fname):
    """Loads the content of a text file.

    Parameters
    ----------
    fname : str
        File name

    Returns
    -------
    list
        Content of the file. List containing the lines of the file
    """
    with open(fname, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # lines = [line.decode('utf-8').strip() for line in f.readlines()]  # TODO: Delete?
    return lines


def load_pkl(fname):
    """Load the content of a pkl file.

    Parameters
    ----------
    fname : str
        File name

    Returns
    -------
    [type]
        Content of the file
    """
    with open(fname, "rb") as f:
        return pickle.load(f)


def save_pkl(fname, data, with_rename=True, makedirs=True):
    """Save data in pkl format.

    Parameters
    ----------
    fname : str
        File name
    data : [type]
        Data to save in the file
    with_rename : bool, optional
        [description], by default True
    makedirs : bool, optional
        If enabled creates the folder for saving the file, by default True
    """
    # Create folder
    if makedirs:
        os.makedirs(os.path.dirname(fname), exist_ok=True)

    # Save file
    if with_rename:
        fname_tmp = fname + "_tmp.pth"
        with open(fname_tmp, "wb") as f:
            pickle.dump(data, f)
        if os.path.exists(fname):
            os.remove(fname)
        os.rename(fname_tmp, fname)
    else:
        with open(fname, "wb") as f:
            pickle.dump(data, f)


def save_image(fname, img, size=None, makedirs=True):
    """Save an image into a file.

    Parameters
    ----------
    fname : str
        Name of the file
    img : [type]
        Image data. #TODO We asume it is.....?????? \in [0, 1]? Numpy? PIL? RGB?
    makedirs : bool, optional
        If enabled creates the folder for saving the file, by default True
    """
    dirname = os.path.dirname(fname)
    if makedirs and dirname != '':
        os.makedirs(dirname, exist_ok=True)

    if img.dtype == 'uint8':
        img_pil = Image.fromarray(img)
        img_pil.save(fname)
    else:
        arr = f2l(t2n(img)).squeeze()
        # print(arr.shape)
        if size is not None:  
            arr = Image.fromarray(arr)
            arr = arr.resize(size)
            arr = np.array(arr)

        img = Image.fromarray(np.uint8(arr * 255))
        img.save(fname)


def load_txt(fname):
    """Load the content of a txt file.

    Parameters
    ----------
    fname : str
        File name

    Returns
    -------
    list
        Content of the file. List containing the lines of the file
    """
    with open(fname, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines


def torch_load(fname, map_location=None):
    """Load the content of a torch file.

    Parameters
    ----------
    fname : str
        File name
    map_location : [type], optional
        Maping the loaded model to a specific device (i.e., CPU or GPU), this
        is needed if trained in CPU and loaded in GPU and viceversa, by default
        None

    Returns
    -------
    [type]
        Loaded torch model
    """
    obj = torch.load(fname, map_location=map_location)

    return obj


def torch_save(fname, obj):
    """Save data in torch format.

    Parameters
    ----------
    fname : str
        File name
    obj : [type]
        Data to save
    """
    # Create folder
    os.makedirs(os.path.dirname(fname), exist_ok=True)  # TODO: add makedirs parameter?

    # Define names of temporal files
    fname_tmp = fname + ".tmp"  # TODO: Make the safe flag?

    torch.save(obj, fname_tmp)
    if os.path.exists(fname):
        os.remove(fname)
    os.rename(fname_tmp, fname)


class Parallel:
    """Class for run a function in parallel."""
    def __init__(self):
        """Constructor"""
        self.threadList = []
        self.count = 0

    def add(self, func,  *args):
        """Add a function to run as a process.

        Parameters
        ----------
        func : function
            Pointer to the function to parallelize
        args : list
            Arguments of the funtion to parallelize
        """
        self.threadList += [
            threading.Thread(target=func, name="thread-%d" % self.count,
                             args=args)]
        self.count += 1

    def run(self):
        """Run the added functions in parallel"""
        for thread in self.threadList:
            thread.daemon = True
            print("  > Starting thread %s" % thread.name)
            thread.start()

    def close(self):
        """Finish: wait for all the functions to finish"""
        for thread in self.threadList:
            print("  > Joining thread %s" % thread.name)
            thread.join()


def subprocess_call(cmd_string):
    """Run a terminal process.

    Parameters
    ----------
    cmd_string : str
        Command to execute in the terminal

    Returns
    -------
    [type]
        Error code or 0 if no error happened
    """
    return subprocess.check_output(
        shlex.split(cmd_string), shell=False).decode("utf-8")


def copy_code(src_path, dst_path, verbose=1):
    """Copy the code.
    
    Typically, when you run an experiment, first you copy the code used to the
    experiment folder. This function copies the code using rsync terminal
    command.

    Parameters
    ----------
    src_path : str
        Source code directory
    dst_path : str
        Destination code directory
    verbose : int, optional
        Verbosity level. If 0 does not print stuff, by default 1

    Raises
    ------
    ValueError
        [description]
    """
    time.sleep(.5)  # TODO: Why? Why?

    if verbose:
        print("  > Copying code from %s to %s" % (src_path, dst_path))

    # Create destination folder
    os.makedirs(dst_path, exist_ok=True)

    # Define the command for copying the code using rsync
    rsync_code = "rsync -av -r -q  --delete-before --exclude='.git/' " \
                 " --exclude='*.pyc' --exclude='__pycache__/' %s %s" % (
                     src_path, dst_path)

    # Run the command in the terminal
    try:
        subprocess_call(rsync_code)
    except subprocess.CalledProcessError as e:
        raise ValueError("Ping stdout output:\n", e.output)

    time.sleep(.5)  # TODO: Why?


def zipdir(src_dirname, out_fname, include_list=None):
    """Compress a folder using ZIP.

    Parameters
    ----------
    src_dirname : str
        Directory to compress
    out_fname : str
        File name of the compressed file
    include_list : list, optional
        List of files to include. If None, include all files in the folder, by
        default None
    """
    import zipfile  # TODO: Move to the beggining of the file
    # TODO: Do we need makedirs?
    # Create the zip file
    zipf = zipfile.ZipFile(out_fname, 'w', zipfile.ZIP_DEFLATED)

    # ziph is zipfile handle
    for root, dirs, files in os.walk(src_dirname):
        for file in files:
            # Descard files if needed
            if include_list is not None and file not in include_list:
                continue
            
            abs_path = os.path.join(root, file)
            rel_path = fname_parent(abs_path)  # TODO: fname_parent not defined
            print(rel_path)
            zipf.write(abs_path, rel_path)

    zipf.close()


def zip_score_list(exp_list, savedir_base, out_fname, include_list=None):
    """Compress a list of experiments in zip.

    Parameters
    ----------
    exp_list : list
        List of experiments to zip
    savedir_base : str
        Directory where the experiments from the list are saved
    out_fname : str
        File name for the zip file
    include_list : list, optional
        List of files to include. If None, include all files in the folder, by
        default None
    """
    for exp_dict in exp_list:  # TODO: This will zip only the last experiments, zipdir will overwritwe the previous file
        # Get the experiment id
        exp_id = hash_dict(exp_dict)
        # Zip folder
        zipdir(os.path.join(savedir_base, exp_id),
               out_fname, include_list=include_list)


def time_to_montreal():
    """Get time in Montreal zone.

    Returns
    -------
    str
        Current date at the selected timezone in string format
    """
    # Get time
    ts = time.time()

    import pytz
    tz = pytz.timezone('America/Montreal')
    dt = datetime.fromtimestamp(ts, tz)

    return dt.strftime("%I:%M %p (%b %d)")


def time2mins(time_taken):
    """Convert time into minutes.

    Parameters
    ----------
    time_taken : float
        Time in seconds

    Returns
    -------
    float
        Minutes
    """
    return time_taken / 60.


def n2t(x, dtype="float"):  # TODO: dtype is not used!!
    """Array or Numpy array to Pytorch tensor.

    Parameters
    ----------
    x : array or Numpy array
        Data to transform
    dtype : [type]
        [description]

    Returns
    -------
    Pytorch tensor
        x converted to pytorch tensor format
    """
    if isinstance(x, (int, np.int64, float)):
        x = np.array([x])

    if isinstance(x, np.ndarray):
        x = torch.from_numpy(x)
    return x


def t2n(x):
    """Pytorch tensor to Numpy array.

    Parameters
    ----------
    x : Pytorch tensor
        A Pytorch tensor to transform

    Returns
    -------
    Numpy array
        x transformed to numpy array
    """
    try:
        x = x.detach().cpu().numpy()
    except:
        x = x

    return x


def l2f(X):
    """Move the channels from the last dimension to the first dimension.

    Parameters
    ----------
    X : Numpy array
        Tensor with the channel dimension at the last dimension

    Returns
    -------
    Numpy array
        X transformed with the channel dimension at the first dimension
    """
    if X.ndim == 3 and (X.shape[0] == 3 or X.shape[0] == 1):
        return X
    if X.ndim == 4 and (X.shape[1] == 3 or X.shape[1] == 1):
        return X

    if X.ndim == 4 and (X.shape[1] < X.shape[3]):
        return X

    # Move the channel dimension from the last position to the first one
    if X.ndim == 3:
        return np.transpose(X, (2, 0, 1))
    if X.ndim == 4:
        return np.transpose(X, (0, 3, 1, 2))

    return X


def f2l(X):
    """Move the channels from the first dimension to the last dimension.

`   Parameters
    ----------
    X : Numpy array
        Tensor with the channel dimension at the first dimension

    Returns
    -------
    Numpy array
        X transformed with the channel dimension at the last dimension
    """
    if X.ndim == 3 and (X.shape[2] == 3 or X.shape[2] == 1):
        return X
    if X.ndim == 4 and (X.shape[3] == 3 or X.shape[3] == 1):
        return X

    # Move the channel dimension from the first position to the last one
    if X.ndim == 3:
        return np.transpose(X, (1, 2, 0))
    if X.ndim == 4:
        return np.transpose(X, (0, 2, 3, 1))

    return X


def n2p(image):  #TODO: Create p2n function and use it in get_image()
    """Numpy image to PIL image.

    Parameters
    ----------
    image : Numpy array
        Input image in numpy format

    Returns
    -------
    PIL image
        Input image converted into PIL format
    """
    image = f2l(image.squeeze())
    if image.max() <= 1:
        image = image * 255
    return Image.fromarray(image.astype('uint8'))


def _denorm(image, mu, var, bgr2rgb=False):
    """Denormalize an image.

    Parameters
    ----------
    image : [type]
        Image to denormalize
    mu : [type]
        Mean used to normalize the image
    var : [type]
        Variance used to normalize the image
    bgr2rgb : bool, optional
        Whether to also convert from bgr 2 rgb, by default False

    Returns
    -------
    [type]
        Denormalized image
    """
    if image.ndim == 3:
        result = image * var[:, None, None] + mu[:, None, None]  # TODO: Is it variance or std?
        if bgr2rgb:
            result = result[::-1]
    else:
        result = image * var[None, :, None, None] + mu[None, :, None, None]
        if bgr2rgb:
            result = result[:, ::-1]
    return result


def denormalize(img, mode=0):  # TODO: Remove the default value or set to a valid number, complete documentation
    """Denormalize an image.

    Parameters
    ----------
    img : [type]
        Input image to denormalize
    mode : int or str, optional
        Predefined denormalizations, by default 0
        If 1 or 'rgb'... 
        If 2 or 'brg'...,
        If 3 or 'basic'...
        Else do nothing

    Returns
    -------
    [type]
        Denormalized image
    """
    # _img = t2n(img)
    # _img = _img.copy()
    image = t2n(img).copy().astype("float")

    if mode in [1, "rgb"]:
        mu = np.array([0.485, 0.456, 0.406])
        var = np.array([0.229, 0.224, 0.225])
        image = _denorm(image, mu, var)

    elif mode in [2, "bgr"]:
        mu = np.array([102.9801, 115.9465, 122.7717])
        var = np.array([1, 1, 1])
        image = _denorm(image, mu, var, bgr2rgb=True).clip(0, 255).round()

    elif mode in [3, "basic"]:
        mu = np.array([0.5, 0.5, 0.5])
        var = np.array([0.5, 0.5, 0.5])
        image = _denorm(image, mu, var)

    # TODO: Add a case for 0 or None and else raise an error exception.

    return image


def get_image(imgs, mask=None, label=False, enlarge=0, gray=False, denorm=0,
              bbox_yxyx=None, annList=None, pretty=False, pointList=None,
              **options):  # TODO: Issam, can you document this?
    """[summary]

    Parameters
    ----------
    imgs : [type]
        [description]
    mask : [type], optional
        [description], by default None
    label : bool, optional
        [description], by default False
    enlarge : int, optional
        [description], by default 0
    gray : bool, optional
        [description], by default False
    denorm : int, optional
        [description], by default 0
    bbox_yxyx : [type], optional
        [description], by default None
    annList : [type], optional
        [description], by default None
    pretty : bool, optional
        [description], by default False
    pointList : [type], optional
        [description], by default None

    Returns
    -------
    [type]
        [description]
    """
    # TODO: Comment these transformations and make sure they are correct. Difficult to follow.
    imgs = denormalize(imgs, mode=denorm)
    if isinstance(imgs, Image.Image):
        imgs = np.array(imgs)
    if isinstance(mask, Image.Image):
        mask = np.array(mask)

    imgs = t2n(imgs).copy()
    imgs = l2f(imgs)

    if pointList is not None and len(pointList):
        h, w = pointList[0]["h"], pointList[0]["w"]
        mask_points = np.zeros((h, w))
        for p in pointList:
            y, x = p["y"], p["x"]
            mask_points[int(h*y), int(w*x)] = 1
        imgs = maskOnImage(imgs, mask_points, enlarge=1)

    if pretty or annList is not None:
        imgs = pretty_vis(imgs, annList, **options)
        imgs = l2f(imgs)

    if mask is not None and mask.sum() != 0:
        imgs = maskOnImage(imgs, mask, enlarge)

    if bbox_yxyx is not None:
        _, _, h, w = imgs.shape
        mask = bbox_yxyx_2_mask(bbox_yxyx, h, w)
        imgs = maskOnImage(imgs, mask, enlarge=1)

    # LABEL
    elif (not gray) and (label or imgs.ndim == 2 or
                         (imgs.ndim == 3 and imgs.shape[0] != 3) or
                         (imgs.ndim == 4 and imgs.shape[1] != 3)):

        imgs = label2Image(imgs)

        if enlarge:
            imgs = zoom(imgs, 11)

    # Make sure it is 4-dimensional
    if imgs.ndim == 3:
        imgs = imgs[np.newaxis]

    return imgs


def show_image(fname):  # TODO: Why the input is a filename instead of an image?
    """Load and image from hard disk and plot it.

    Parameters
    ----------
    fname : str
        Name of an image to load and show
    """
    ncols = 1  # TODO: Magic numbers
    nrows = 1
    height = 12
    width = 12
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols,
                            figsize=(ncols*width, nrows*height))
    if not hasattr(axs, 'size'):  #TODO: What is this?
        axs = [[axs]]

    for i in range(ncols):
        img = plt.imread(fname)
        axs[0][i].imshow(img)
        axs[0][i].set_axis_off()
        axs[0][i].set_title('%s' % (fname))

    plt.axis('off')
    plt.tight_layout()

    plt.show()


def shrink2roi(img, roi):
    """[summary]

    Parameters
    ----------
    img : [type]
        [description]
    roi : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    ind = np.where(roi != 0)

    y_min = min(ind[0])
    y_max = max(ind[0])

    x_min = min(ind[1])
    x_max = max(ind[1])

    return img[y_min:y_max, x_min:x_max]


@contextlib.contextmanager
def random_seed(seed):
    """[summary]

    Parameters
    ----------
    seed : [type]
        [description]
    """
    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)


def is_subset(d1, d2, strict=False):
    """[summary]

    Parameters
    ----------
    d1 : [type]
        [description]
    d2 : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    flag = True
    for k in d1:
        v1, v2 = d1.get(k), d2.get(k)

        # if both are values
        if not isinstance(v2, dict) and not isinstance(v1, dict):
            if v1 != v2:
                flag = False

        # if both are dicts
        elif isinstance(v2, dict) and isinstance(v1, dict):
            flag = is_subset(v1, v2)

        # if d1 is dict and not d2
        elif isinstance(v1, dict) and not isinstance(v2, dict):
            flag = False

        # if d1 is not and d2 is dict
        elif not isinstance(v1, dict) and isinstance(v2, dict):
            flag = False

        if flag is False:
            break

    return flag


def as_double_list(v):
    """[summary]

    Parameters
    ----------
    v : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    if not isinstance(v, list) and not isinstance(v, np.ndarray):
        v = [v]

    if not isinstance(v[0], list) and not isinstance(v[0], np.ndarray):
        v = [v]

    return v

def check_duplicates(list_of_dicts):
    # ensure no duplicates in exp_list
    hash_list = set()
    for data_dict in list_of_dicts:
        dict_id = hash_dict(data_dict)
        if dict_id in hash_list:
            raise ValueError('duplicate experiments detected...')
        else:
            hash_list.add(dict_id)

def load_py(fname):
    """[summary]

    Parameters
    ----------
    fname : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    import sys
    from importlib import reload
    from importlib import import_module

    if not os.path.exists(fname):
        raise ValueError('%s not found...' % fname)

    sys.path.append(os.path.dirname(fname))

    name = os.path.split(fname)[-1].replace('.py','')
    module = import_module(name) 
    reload(module)
    sys.path.pop()

    return module