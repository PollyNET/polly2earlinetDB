# SCC Convertor for PollyNET Products
![License: CC-BY-NC-SA](https://img.shields.io/badge/license-CC--BY--NC--SA-blue)![Build](https://github.com/PollyNET/polly2scc/workflows/Build/badge.svg?branch=master)

At June 24, 2019, the new EARLINET database was released and new data format for the netCDF files was applied. Therefore, in order to be compatible with this update, we (PollyNET group) need to change the output results from Picasso (PollyNET automatic processing program) to be adapted to this change.

## Requirements

- python 3.5
- [`Anaconda3`][1] (Python 3.x version)

## Installation

### python virtual environment and install python dependencies

If you have installed [`Anaconda3`][1], you can easily setup the python environment for running the program. Otherwise, you can go [here][2] for some details of the installation.

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

**build the repository**

```bash
pip install git+https://github.com/PollyNET/polly2scc.git
```

## Usage

After the steps mentioned above, the command line tool **polly2scc** should be ready in your system **PATH**. You can see the instructions of the command with using `polly2scc -h`

```text
usage: polly2scc [-h] [-p POLLY_TYPE] [-l LOCATION] [-t FILE_TYPE] [-c CATEGORY]
              [-f FILENAME] [-d OUTPUT_DIR]
              [--range_e RANGE_LIM_E RANGE_LIM_E]
              [--range_b RANGE_LIM_B RANGE_LIM_B] [--camp_info CAMP_INFO]
              [--force]
              {list} ...

convert the polly profiles from labview program to EARLINET format

positional arguments:
  {list}                list supported campaign and instruments.
    list                list supported campaign and instruments.

optional arguments:
  -h, --help            show this help message and exit
  -p POLLY_TYPE, --polly_type POLLY_TYPE
                        setup the instrument type
  -l LOCATION, --location LOCATION
                        setup the campaign location
  -t FILE_TYPE, --file_type FILE_TYPE
                        setup the type of the profile (labview | picasso)
  -c CATEGORY, --category CATEGORY
                        setup the category of the profile (user_defined_category)
                        flag_masks: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
                        flag_meanings: cirrus climatol dicycles etna forfires
                        photosmog rurban sahadust stratos satellite_overpasses
  -f FILENAME, --filename FILENAME
                        setup the filename of the polly profile
  -d OUTPUT_DIR, --output_dir OUTPUT_DIR
                        setup the directory for the converted files
  --range_e RANGE_LIM_E RANGE_LIM_E
                        setup the height range for the converted e-files.
                        (e.g., --range_e 200 16000)
  --range_b RANGE_LIM_B RANGE_LIM_B
                        setup the height range for the converted b-files.
                        (e.g., --range_b 200 16000)
  --camp_info CAMP_INFO
                        setup the campaign info file [*.toml].
                        If not set, the program will search the config folder for a suitable one.
  --force               whether to overwrite the nc files if they exists
```

**Display the supported polly types**

```bash
polly2scc list --instrument
```

**Display the supported campaigns**

```bash
polly2scc list --campaign
polly2scc list --all   # show all campaigns together with the systems
```

**Convert one file**

```bash
polly2scc -p pollyxt_lacros -l punta_arenas -t labview -c 2 -f /User/zhenping/desktop/file1.txt -d /Users/zhenping/Destkop/test --force
```

|output file namings|example|description|
|:----------:|:-----:|:----------|
|{date:yyyymmdd\_HH:MM}\_{smooth:03d}\_{station ID}\_{PollyType}\_b355.nc|20190723\_1900\_075\_lei\_arielle\_b355.nc|results associated with backscatter, vol/par depolarization ratio at 355 nm|
|{date:yyyymmdd\_HH:MM}\_{smooth:03d}\_{station ID}\_{PollyType}\_b532.nc|20190723\_1900\_075\_lei\_arielle\_b532.nc|results associated with backscatter, vol/par depolarization ratio at 532 nm|
|{date:yyyymmdd\_HH:MM}\_{smooth:03d}\_{station ID}\_{PollyType}\_b1064.nc|20190723\_1900\_075\_lei\_arielle\_b1064.nc|results associated with backscatter coefficient at 1064 nm|
|{date:yyyymmdd\_HH:MM}\_{smooth:03d}\_{station ID}\_{PollyType}\_e355.nc|20190723\_1900\_075\_lei\_arielle\_e355.nc|results associated with backscatter and extinction coefficients at 355 nm|
|{date:yyyymmdd\_HH:MM}\_{smooth:03d}\_{station ID}\_{PollyType}\_e532.nc|20190723\_1900\_075\_lei\_arielle\_e532.nc|results associated with backscatter and extinction coefficients at 532 nm|

**convert files with using wildcards**

```bash
polly2scc -p pollyxt_lacros -l punta_arenas -t labview -c 2 -f /User/zhenping/desktop/file*.txt -d /Users/zhenping/Destkop/test --force
```

## Q&A

If you have any questions, please go to the [`issues`][4] session to check whether there was an answer. If not, please contact [me](#contact) or draft a new issue there.

## Acknowledgement

Special thanks to the persistent help from [Holger Baars][5] to test uploading the converted files to the new EARLINET database, which helps a lot for the debugging. In addition, I thank [Martin Radenz](radenz@tropos.de) to solve the file encoding issue.

> The repository is dependent on the [lidar_molecular][3], developed by **Iannis Binietoglou**. Thanks for sharing your great work.

## License

MIT License

Feel free to distribute it!!! :beer::beer::beer:

## Contact

Zhenping Yin 
<zhenping@tropos.de>

[1]: https://www.anaconda.com/distribution/
[2]: https://github.com/ZPYin/Pollynet_Processing_Chain/blob/master/doc/anaconda_installation.md
[3]: https://bitbucket.org/iannis_b/lidar_molecular/
[4]: https://github.com/ZPYin/polly_2_earlinet_convertor/issues
[5]: https://www.tropos.de/institut/ueber-uns/mitarbeitende/holger-baars