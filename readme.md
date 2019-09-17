# EARLINET Data Format Convertor for PollyNET Products

## Description

At June 24, 2019, the new EARLINET database was released and new data format for the netCDF files was applied. Therefore, in order to be compatible with this update, we (PollyNET group) need to change the output results from Picasso (PollyNET automatic processing program) to be adapted to this change.

## Requirements

- python 3.5
- [`Anaconda3`](https://www.anaconda.com/distribution/)
- **Windows 10** or **Ubuntu**

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

If you have installed [`Anaconda3`](https://www.anaconda.com/distribution/), you can easily setup the python environment for running the program. Otherwise, you can go [here](https://github.com/ZPYin/Pollynet_Processing_Chain/blob/master/doc/anaconda_installation.md) for some details of the installation.

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

After the steps mentioned above, the command line tool **p2e_go** (polly_to_earlinet convertor) should be ready in your system **PATH**. You can see the instructions of the command with using `p2e_go -h`

```text
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
p2e_go list --all   # show all campaigns together with the systems
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

If you have any questions, please go to the [`issues`](https://github.com/ZPYin/polly_2_earlinet_convertor/issues) session to check whether there was an answer. If not, please contact [me](#contact) or draft a new issue there.

## Acknowledgement

Special thanks to the persistent help from [Holger Baars](baars@tropos.de) to test uploading the converted files to the new EARLINET database, which helps a lot for the debugging. In addition, I thank [Martin Radenz](radenz@tropos.de) to solve the file encoding issue.

## License

MIT License

Feel free to distribute it!!! :beer::beer::beer:

## Contact

Zhenping Yin 
<zhenping@tropos.de>