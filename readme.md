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
conda activate polly_earlinet # linux
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
usage: p2e_go [-h] [-p POLLY_TYPE] [-l LOCATION] [-t FILE_TYPE] [-c CATEGORY]
              [-f FILENAME] [-d OUTPUT_DIR] [--camp_info CAMP_INFO] [--force]
              {list} ...

convert the polly profiles from labview program to EARLINET format

positional arguments:
  {list}                list supported campaign and instruments.

optional arguments:
  -h, --help            show this help message and exit
  -p POLLY_TYPE, --polly_type POLLY_TYPE
                        setup the instrument type
  -l LOCATION, --location LOCATION
                        setup the campaign location
  -t FILE_TYPE, --file_type FILE_TYPE
                        setup the type of the profile (labview | picasso)
  -c CATEGORY, --category CATEGORY
                        setup the category of the profile flag_masks: 1, 2, 4,
                        8, 16, 32, 64, 128, 256, 512 flag_meanings: cirrus
                        climatol dicycles etna forfires photosmog rurban
                        sahadust stratos satellite_overpasses
  -f FILENAME, --filename FILENAME
                        setup the filename of the polly profile
  -d OUTPUT_DIR, --output_dir OUTPUT_DIR
                        setup the directory for the converted files
  --camp_info CAMP_INFO
                        setup the campaign info file [*.toml]. If not set, the
                        program will search the config folder for a suitable
                        one.
  --force               whether to overwrite the nc files if they exists
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
p2e_go -p pollyxt_lacros -l punta_arenas -f labview -c 2 -f /User/zhenping/desktop/file1.txt -d /Users/zhenping/Destkop/test --force
```

**convert files with using wildcards**

```bash
p2e_go -p pollyxt_lacros -l punta_arenas -f labview -c 2 -f /User/zhenping/desktop/file*.txt -d /Users/zhenping/Destkop/test --force
```

## Q&A

### How to add a new campaign in the configs?

A: Firstly, you should know some details of the configurations used for the convertor. If you open the `config` folder, you will find bunch of `toml` files used for the projects. But only two kinds associated with the campaign info, as below

```text
# campaign list
campaign_list.toml

# configurations for single campaign
{location}_campaign_info{tag}.toml
```

Therefore, to do that, you need firstly write down the fundamental information of the campaign, like below

```text
# for one instrument available along the measurement history
[Dushanbe_campaign_info]
location = "Dushanbe"
country = "Tajikistan"
starttime = "2019-06-15 00:00:00"
endtime = "2029-01-01 00:00:00"
system = "PollyXT_TJK" 

# for multiple instruments
[Dushanbe_campaign_info_2]
location = "Dushanbe"
country = "Tajikistan"
starttime = "2019-06-15 00:00:00"
endtime = "2029-01-01 00:00:00"
system = "PollyXT_TJK" 

[Dushanbe_campaign_info_1]
location = "Dushanbe"
country = "Tajikistan"
starttime = "2015-03-17 00:00:00"
endtime = "2016-09-30 00:00:00"
system = "PollyXT_TROPOS" 
```
After the entry point was setup in the campaign list file, you need to create the campaign metadata file with the same keyword in the campaign list, e.g., `Dushanbe_campaign_info_1.toml` and `Dushanbe_campaign_info_2.toml`. To simplify this, you can copy and manipulate items in other campaign list file. 

Note: If you used the python setuptools and using the executable command, you need to recompile it. Because the configuration files also needs to be updated for the script. To do like, you can follow the instructions below,

```bash
# delete the previous executable scripts
pip uninstall polly_2_earlinet_convertor

# reinstall it with using new configuration files
python setup.py install
```

## Acknowledgement

Thanks to **Iannis Binietoglou** with the repository of [`SCC access`](https://bitbucket.org/iannis_b/scc-access/src/default/) and **Ina Mattis** with the repository of [`inqbus.lidar`](https://github.com/Inqbus/inqbus.lidar). 

## License

MIT License

Feel free to distribute it!!! :beer::beer::beer:

## Contact

Zhenping Yin 
<zhenping@tropos.de>