# EARLINET Data Format Convertor for PollyNET Products

## Description

At June 24, 2019, the new EARLINET database was released and new data format for the netCDF files was applied. Therefore, in order to be compatible with this update, we (PollyNET group) need to change the output results from Picasso (PollyNET automatic processing program) to be adapted to this change.

## Requirements

- python 3.5
- [`Anaconda`](https://www.anaconda.com/distribution/)

## Download

You can download the code by using git

```bash
git clone https://github.com/ZPYin/polly_2_earlinet_convertor.git
```

or 

click the download [link](https://github.com/ZPYin/polly_2_earlinet_convertor/archive/master.zip)

## Installation

go to the package folder

```bash
cd polly_2_earlinet_convertor
```

### python virtual environment and install python dependencies

If you have installed [`Anaconda`](https://www.anaconda.com/distribution/), you can easily setup the python environment for running the program. Otherwise, you can go [here](https://github.com/ZPYin/Pollynet_Processing_Chain/blob/master/doc/anaconda_installation.md) for some details.

**create a new virtual environment.**

```bash
conda create -n polly_earlinet
```

**activate the virtual environment**
```bash
activate polly_earlinet # windows
source activate polly_earlinet # linux
```

**install python3.5**
```bash
conda install python=3.5
```

**install python dependencies**
```bash
pip install -r requirements.txt
```

### Compile the python codes

compile the source code with using python setuptools

```bash
python setup.py install
```

## Usage

After the steps mentioned above, the command line tool p2e_go (polly_to_earlinet convertor) should be ready in your system **PATH**. You can see the instructions of the command with using `p2e_go -h`

```bash

```

**Display the supported polly types**

```bash
p2e_go list --instrument
```

**Display the supported campaigns**

```bash
p2e_go list --campaign
```

**Convert one file**

```bash
p2e_go 
```

## Acknowledgement

Thanks to **Iannis Binietoglou** with the repository of [`SCC access`](https://bitbucket.org/iannis_b/scc-access/src/default/) and **Ina Mattis** with the repository of [`inqbus.lidar`](https://github.com/Inqbus/inqbus.lidar). 

## License

MIT License

Feel free to distribute it!!! :beer::beer::beer:

## Contact

Zhenping Yin 
<zhenping@tropos.de>