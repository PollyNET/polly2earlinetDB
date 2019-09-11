import os
import toml
import logging
import glob
import numpy as np
import datetime
from scipy.interpolate import interp1d

LOG_MODE = 'INFO'
LOGFILE = 'log'
CONVERT_KEY_FILE = 'labview_key_2_earlinet_key_spec.toml'
METADATA_FILE = 'metadata.toml'
CAMPAIGN_LIST_FILE = 'campaign_list.toml'

# initialize the logger
projectDir = os.path.dirname(os.path.realpath(__file__))
logFile = os.path.join(projectDir, 'log', LOGFILE)
logModeDict = {
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'DEBUG': logging.DEBUG,
                'ERROR': logging.ERROR
              }
logger = logging.getLogger(__name__)
logger.setLevel(logModeDict[logMode])

fh = logging.FileHandler(logFile)
fh.setLevel(logModeDict[logMode])
ch = logging.StreamHandler()
ch.setLevel(logModeDict[logMode])

formatterFh = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s')
formatterCh = logging.Formatter('%(name)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s')
fh.setFormatter(formatterFh)
ch.setFormatter(formatterCh)

logger.addHandler(fh)

class polly_earlinet_convertor(object):
    """ 
    Description
    -----------
    convert the polly data into EARLINET format
    Exemplified file can be found under the folder of "include/".

    Parameters
    ----------
    filename: string

    fileType: string
        'labview' or 'picasso'

    configFile: string
    
    Keywords
    --------
    logFile: string

    logMode: string
        'INFO', 'WARNING', 'ERROR' or 'DEBUG'

    History
    -------
    2019-09-09. First edition by Zhenping
    """

    def __init__(self, pollyType, location, fileType='labview', category=2, '*', configFolder=''):
    '''
    Initialize the class variables
    '''
        # initialize the class variables
        self.pollyType = pollyType
        self.location = location
        self.fileType = fileType
        self.category = category
        self.projectDir = os.path.dirname(os.path.realpath(__file__))

        # setup the configuration folder. (Default: 'config/')
        if not os.path.exists(configFolder):
            logger.warning("'configFolder' of {configFolder} does not exist.\nSet it to be {projectConfigFolder}".format(configFolder=configFolder, projectConfigFolder=os.path.join(self.projectDir, 'config')))
            self.configFolder = os.path.join(self.projectDir, 'config')

        # load conversion key
        self.conversion_key = self.load_convert_key_config()

        # load campaign list
        self.campaign_dict = self.load_campaign_list()
        
        # get instrument list
        instrument_list = []
        for camp_label in self.campaign_dict:
            instrument_list.append(self.campaign_dict[camp_label]['system'])
        self.instrument_list = list(set(instrument_list))

        # get location list
        location_list = []
        for camp_label in self.campaign_dict:
            location_list.append(self.campaign_dict[camp_label][location])
        self.location_list = list(set(location_list))

    

    def load_campaign_list(self):
    '''
    load the campaign information list into a dict
    '''

    camp_list_file = os.path.join(self.projectDir, 'config', CAMPAIGN_LIST_FILE)

    # check the campaign list file
    if (not os.path.exists(camp_list_file)) or (not os.path.isfile(camp_list_file)):
        logger.error('campaign list file does not exist!\n{file}'.format(file=camp_list_file))
        raise FileNotFoundError

    camp_dict = toml.loads(camp_list_file)

    # convert the timestamp to datetime object
    for camp_label in camp_list:
        camp_dict[camp_label]['starttime'] = datetime.datetime.strptime(camp_dict[camp_label]['starttime'], '%Y-%m-%d %H:%M:%S')
        camp_dict[camp_label]['endtime'] = datetime.datetime.strptime(camp_dict[camp_label]['endtime'], '%Y-%m-%d %H:%M:%S')

    return camp_dict



    def load_convert_key_config(self):
    '''
    load the convert key for mapping the labview configurations to EARLINET standard configurations.
    '''
        convert_key_filepath = os.path.join(self.projectDir, CONVERT_KEY_FILE)
        
        if (not os.path.exists(convert_key_filepath)) or (not os.path.isfile(convert_key_filepath)):
            logger.error('CONVERT_KEY_FILE does not exist!\n{file}'.format(file=convert_key_filepath))
            raise FileNotFoundError

        # load conversion key
        try:
            conversion_key = toml.loads(convert_key_filepath)
        except Exception as e:
            logger.error('Failure in reading CONVERT_KEY_FILE\n{file}'.format(file=convert_key_filepath))
            raise IOError

        return conversion_key


    def load_camp_info(self, camp_info_file=None):
    '''
    load the campain information
    '''

    if (not os.path.exists(camp_info_file)) or (not os.path.isfile(camp_info_file)):
        logger.error('campaign configuration file does not exist!\n{file}'.format(file=camp_info_file))


    def read_data_file(self, filename):
    '''
    read the data from the polly data file (labview or picasso style)
    '''
    if self.fileType.lower() == 'labview':
        pollyData = self.__read_labview_results(filename)
    elif self.fileType.lower() == 'picasso':
        pollyData = self.__read_picasso_results(filename)
    else:
        logger.error('Wrong input of fileType: {fileType}'.format(fileType=self.fileType))

    return pollyData


    def search_data_files(self, filename, filepath=None):
    '''
    Search the polly data files. Wildcards are supported.
    '''
    if not filepath:
        filepath = os.getcwd()

    # search the files
    logger.info('Start to search polly data files...')
    fileList = glob.glob(os.path.join(filepath, filename))
    logger.info('number of files: {nFiles:%d}'.format(nFiles=self.nFiles))

    return fileList



    def __read_labview_results(self, filename):
    '''
    read labview results into the data pool, which will then be exported to earlinet data format.

    If the file does no exist or the file was retrieved with Klett method, return None
    '''
        if (not os.path.exists(filename)) or (not os.path.isfile(filename)):
            logger.warning('Input filename does not exist! \nFinish!')
            return None, None, None
        
        logger.info('Start reading {filename}'.format(filename=filename))

        # read labview info file
        infoFilename = filename[0:-4] + '-info.txt'
        labviewInfo = self.__read_labview_info(infoFilename)

        # jump over Klett profiles
        if labviewInfo['retrieving_method'] == 1:
            logger.warning('File was retrieved with Klett method.\n{file}\nJump over!!!'.format(file=filename))
            return None, None, None
        
        # search the campaign info file
        camp_info_file = self.search_

        # read labview data file
        labviewData = self.__read_labview_data(fielname)

        # cut off the bins with influences from smoothing
        smoothWin = labviewInfo['smoothWindow']
        labviewDataCut = labviewData[int(smoothWin/2):-int(smoothWin/2), :]

        # convert the data matrix into dict with unit conversion
        labviewDataDict = {
            'height': labviewDataCut[0. :] * 1e3,
            'bsc_355': labviewDataCut[1, :] * 1e-6,
            'bsc_std_355': labviewDataCut[2, :] * 1e-6,
            'bsc_532': labviewDataCut[3, :] * 1e-6,
            'bsc_std_532': labviewDataCut[4, :] * 1e-6,
            'bsc_1064': labviewDataCut[5, :] * 1e-6,
            'bsc_std_1064': labviewDataCut[6, :] * 1e-6,
            'ext_355': labviewDataCut[7, :] * 1e-6,
            'ext_std_355': labviewDataCut[8, :] * 1e-6,
            'ext_532': labviewDataCut[9, :] * 1e-6,
            'ext_std_532': labviewDataCut[10, :] * 1e-6,
            'lr_355': labviewDataCut[11, :],
            'lr_std_355': labviewDataCut[12, :],
            'lr_532': labviewDataCut[13, :],
            'lr_std_532': labviewDataCut[14, :],
            'EAE_355_532': labviewDataCut[15, :],
            'EAE_std_355_532': labviewDataCut[16, :],
            'BAE_355_532': labviewDataCut[17, :],
            'BAE_std_355_532': labviewDataCut[18, :],
            'BAE_532_1064': labviewDataCut[19, :],
            'BAE_std_532_1064': labviewDataCut[20, :],
            'height_vdr_532': labviewDataCut[21, :],
            'vdr_532': labviewDataCut[22, :],
            'vdr_std_532': labviewDataCut[23, :],
            'height_pdr_532': labviewDataCut[24, :],
            'pdr_532': labviewDataCut[25, :],
            'pdr_std_532': labviewDataCut[26, :],
            'height_sounding': labviewDataCut[27, :],
            'temperature': labviewDataCut[28, :],
            'pressure': labviewDataCut[29, :],
            'height_vdr_355': labviewDataCut[30, :],
            'vdr_355': labviewDataCut[31, :],
            'vdr_std_355': labviewDataCut[32, :],
            'height_pdr_355': labviewDataCut[33, :],
            'pdr_355': labviewDataCut[34, :],
            'pdr_std_355': labviewDataCut[35, :], 
            'bsc_mol_355': labviewDataCut[66, :] * 1e-3,   # the unit in labview file is wrong
            'bsc_mol_532': labviewDataCut[67, :] * 1e-3,
            'bsc_mol_1064': labviewDataCut[68, :] * 1e-3
        }

        # interpolate the data into the same grid
        fh_vdr_532 = interp1d(labviewDataCut['height_vdr_532'], labviewDataCut['vdr_532'], kind='linear')
        fh_vdr_std_532 = interp1d(labviewDataCut['height_vdr_532'], labviewDataCut['vdr_std_532'], kind='linear')
        fh_pdr_532 = interp1d(labviewDataCut['height_pdr_532'], labviewDataCut['pdr_532'], kind='linear')
        fh_pdr_std_532 = interp1d(labviewDataCut['height_pdr_std_532'], labviewDataCut['pdr_std_532'], kind='linear')
        fh_vdr_355 = interp1d(labviewDataCut['height_vdr_355'], labviewDataCut['vdr_355'], kind='linear')
        fh_vdr_std_355 = interp1d(labviewDataCut['height_vdr_355'], labviewDataCut['vdr_std_355'], kind='linear')
        fh_pdr_355 = interp1d(labviewDataCut['height_pdr_355'], labviewDataCut['pdr_355'], kind='linear')
        fh_pdr_std_355 = interp1d(labviewDataCut['height_pdr_std_355'], labviewDataCut['pdr_std_355'], kind='linear')

        labviewDataCut['vdr_532'] = fh_vdr_532(labviewDataCut['height'])
        labviewDataCut['vdr_std_532'] = fh_vdr_std_532(labviewDataCut['height'])
        labviewDataCut['pdr_532'] = fh_pdr_532(labviewDataCut['height'])
        labviewDataCut['pdr_std_532'] = fh_pdr_std_532(labviewDataCut['height'])
        labviewDataCut['vdr_355'] = fh_vdr_355(labviewDataCut['height'])
        labviewDataCut['vdr_std_355'] = fh_vdr_std_355(labviewDataCut['height'])
        labviewDataCut['pdr_355'] = fh_pdr_355(labviewDataCut['height'])
        labviewDataCut['pdr_std_355'] = fh_pdr_std_355(labviewDataCut['height'])

        # convert the labview data into the data container
        dimensions = {
            'altitude': len(labviewDataCut['height']),
            'time': 1,
            'wavelength': 1,
            'nv': 2   # number of values (2 for reference height)
            }
        data = {
            'altitude': labviewDataCut['height'],
            'time': labviewInfo['starttime'].timestamp(),
            'time_bounds': np.array([tObj.timestamp() for tObj in labviewInfo['time_bounds']]),
            'vertical_resolution': labviewInfo['dz'],
            'cloud_mask': -127 * np.ones(labviewDataCut['height'].shape, dtype=np.byte),
            'cirrus_contamination': 0,   # 0: not_available; 1: no_cirrus; 2: cirrus_detected
            'cirrus_contamination_source': 0,   # 0: not_available; 1: user_provided; 2: automatic_calculated
            'error_retrieval_method': 1,   # 0: monte_carlo; 1: error_propagation
            'extinction_evaluation_algorithm': 1,   # 0: Ansmann; 1: via_backscatter_ratio
            'ext_355': labviewDataCut['ext_355'],
            'ext_std_355': labviewDataCut['ext_std_355'],
            'ext_532': labviewDataCut['ext_532'],
            'ext_std_532': labviewDataCut['ext_std_532'],
            'ext_1064': labviewDataCut['ext_1064'],
            'ext_std_1064': labviewDataCut['ext_std_1064'],
            'user_defined_category': self.category,
            'cirrus_contamination_source': 0,
            'atmospheric_molecular_calculation_source': labviewInfo['sounding_type'],
            'latitude': 
            }
        global_attrs = {}

        return dimensions, data, global_attrs



    def __read_labview_data(self, filename):
    '''
    read the labview retrieving data
    '''
        dataMatrix = np.loadtxt(filename, skiprows=1, dtype=float)


    def __read_labview_info(self, filename):
    '''
    read the labview info file, which contains the retrieving information
    '''
        labviewInfo = self.labview_info_parser(filename)
        
        # convert the datetime
        labviewInfo['starttime'] = datetime.datetime.strptime(labviewInfo['starttime'], '%y%m%d %H%M')
        labviewInfo['endtime'] = datetime.datetime.strptime(labviewInfo['endtime'], '%y%m%d %H%M')

        # concatenate reference height
        labviewInfo['reference_height_355'] = np.concatenate((labviewInfo['reference_height_bottom_355'], labviewInfo['reference_height_top_355']), axis=0)
        labviewInfo['reference_height_532'] = np.concatenate((labviewInfo['reference_height_bottom_532'], labviewInfo['reference_height_top_532']), axis=0)
        labviewInfo['reference_height_1064'] = np.concatenate((labviewInfo['reference_height_bottom_1064'], labviewInfo['reference_height_top_1064']), axis=0)

        # convert the retrieving method
        retMethodDict = dict(zip(self.conversion_key['lk_retrieving_method'], self.conversion_key['ek_retrieving_method']))
        labviewInfo['retrieving_method'] = retMethodDict[labviewInfo['retrieving_method']]
        
        # convert the sounding type
        soundingSearchList = self.conversion_key['ek_meteor_source']
        labviewInfo['sounding_type'] = soundingSearchList[labviewInfo['sounding_type']]

        data = {
                'atmospheric_molecular_calculation_source': labviewInfo['sounding_type'],   # 0: US_standard_atmosphere; 1: radiosonding; 2: ecmwf; 3: icon-iglo-12-23; 4: gdas
                'backscatter_calibration_range_355': labviewInfo['reference_height_355'],
                'backscatter_calibration_range_532': labviewInfo['reference_height_532'],
                'backscatter_calibration_range_1064': labviewInfo['reference_height_1064'],
                'backscatter_calibration_range_search_algorithm': 0,
                'backscatter_calibration_value_355': labviewInfo['reference_value_355'],
                'backscatter_calibration_value_532': labviewInfo['reference_value_532'],
                'backscatter_calibration_value_1064': labviewInfo['reference_value_1064'],
                'backscatter_evaluation_method': labviewInfo['retrieving_method'],   # 0: Raman; 1: elastic_backscatter
                'smoothWindow': labviewInfo['smooth_ext_355'],
                'retrieving_method': labviewInfo['retrieving_method'],
                'extinction_assumed_wavelength_dependence': labviewInfo['AE'],   # Ångstroem exponent
                'extinction_evaluation_algorithm': 1,   # 0: weighted_linear_fit; 1: non-weighted_linear_fit
                'shots': 1,   # number of accumulated laser shots
                'time': labviewInfo['starttime'],   # seconds since 1970-01-01 00:00:00
                'time_bounds': [labviewInfo['starttime'], labviewInfo['endtime']],   # time_bounds
                'user_defined_category': self.category,   # 1: cirrus; 2: climatol; 4: dicycles; 8: etna; 16: forfires; 32: photosmog; 64: rurban; 128: sahadust; 256: stratos; 512: satellite_overpass
                'vertical_resolution': labviewInfo['dz'],   # [m]
                'zenith_angle': np.rad2deg(np.arccos(labviewInfo['dz']/labviewInfo['range_resolution']))
                }

        return data



    def labview_info_parser(self, filename):
    '''
    parsing the information from the labview info file
    '''
        
        if (not os.path.exists(filename)) or (not os.path.isfile(filename)):
            logger.error('Labview info file does not exist.\n{infoFile}'.format(infoFile=filename))
            raise ValueError
        
        # decoder structure
        # key:  regex, conversion function fill value
        decoders = {
            'starttime': (r'(?<=Messung von \(UTC\):)\d+.\d+', str, '000000 0000'),
            'endtime': (r'(?<=bis \(UTC\))\d+.\d+', str, '000000 0000'),
            'reference_height_bottom_355': (r'(?<=refheigt355\(m\) from : )\d+', float, 0),
            'reference_height_top_355': (r'(?<=refheight355 \(m\) to: )\d+', float, 0),
            'reference_value_355': (r'(?<=refwert355 \(km\^-1 sr\^-1\): )\d+\.\d+[eE]-?\d+', str, 0),
            'reference_height_bottom_532': (r'(?<=refheigt532\(m\) from : )\d+', float, 0),
            'reference_height_top_532': (r'(?<=refheight532 \(m\) to: )\d+', float, 0),
            'reference_value_532': (r'(?<=refwert532 \(km\^-1 sr\^-1\): )\d+\.\d+[eE]-?\d+', str, 0),
            'reference_height_bottom_1064': (r'(?<=refheigt1064\(m\) from : )\d+', float, 0),
            'reference_height_top_1064': (r'(?<=refheight1064 \(m\) to: )\d+', float, 0),
            'reference_value_1064': (r'(?<=refwert1064 \(km\^-1 sr\^-1\): )\d+\.\d+[eE]-?\d+', str, 0),
            'smooth_ext_355': (r'(?<=smoothingalpha355: )\d+', int, 0),
            'smooth_bsc_355': (r'(?<=smootingbeta355: )\d+', int, 0),
            'smooth_ext_532': (r'(?<=smoothingalpha532: )\d+', int, 0),
            'smooth_bsc_532': (r'(?<=smootingbeta532: )\d+', int, 0),
            'smooth_ext_1064': (r'(?<=smoothingalpha1064: )\d+', int, 0),
            'smooth_bsc_1064': (r'(?<=smootingbeta1064: )\d+', int, 0),
            'dz': (r'(?<=dz: )\d+\.?\d+', float, 0),
            'retrieving_method': (r'(?<=\nMethod:)\w+', str, 'Raman'),
            'AE': (r'(?<=Angström for Raman Extinction: )\d+\.?\d+', float, 0),
            'sounding_type': (r'(?<=Sounding Type: )\d\.?\d+', float, 0),
            'flag_deadtime_correction': (r'(?<=Death time correction: )\w+', str, 'no'),
            'flag_use_particle_ext_for_raman_bsc': (r'(?<=Use particle ext for raman Bsc: )\w+', str, 'no'),
            'range_resolution': (r'(?<=Range resolution: )\d+\.?\d+', float, 0),
            'software_version': (r'(?<=Software version: )\w+\.?\w+', str, ''),
        }

        def find_in_string(key, dec, str):
            res = re.search(dec[0], str)
            if res != None:
                val = dec[1](res.group())
            else:
                val = dec[2]
            return val

        # intialize the data
        data = {}

        # read the labview info file
        with open(filename, 'r') as fh:
            content = fh.read()

        l = content.decode('ascii').strip()
        for key, regex in decoders.items():
            val = find_in_string(key, regex, l)
            data.update({key:val})

        return data



    def __read_picasso_results(self):
        data = []
        return data



    def write_to_earlinet_nc(self, variables, dimensions, global_attri):



# Command line interface
# convert_polly_2_earlinet -p pollyxt_lacros -l dushanbe -t labview -c 2 -f xxx.txt [-c xxx.toml --force true]
# convert_polly_2_earlinet --list_campaign
# convert_polly_2_earlinet -h|--help