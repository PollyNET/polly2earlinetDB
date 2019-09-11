import os
import toml
import logging
import glob
import numpy as np
import datetime
import re
from netCDF4 import Dataset
from scipy.interpolate import interp1d

LOG_MODE = 'INFO'
LOGFILE = 'log'
CONVERT_KEY_FILE = 'labview_key_2_earlinet_key_spec.toml'
METADATA_FILE = 'metadata.toml'
CAMPAIGN_LIST_FILE = 'campaign_list.toml'
NETCDF_FORMAT = "NETCDF4"

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
logger.setLevel(logModeDict[LOG_MODE])

fh = logging.FileHandler(logFile)
fh.setLevel(logModeDict[LOG_MODE])
ch = logging.StreamHandler()
ch.setLevel(logModeDict[LOG_MODE])

formatterFh = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - ' +
                                '%(funcName)s - %(lineno)d - %(message)s')
formatterCh = logging.Formatter(
    '%(name)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s')
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

    def __init__(self, pollyType, location, fileType='labview',
                 category=2, *, output_dir='', camp_info_file=''):
        '''
        Initialize the class variables
        '''
        # initialize the class variables
        self.pollyType = pollyType
        self.location = location
        self.fileType = fileType
        self.category = category
        self.projectDir = os.path.dirname(os.path.realpath(__file__))
        self.outputDir = output_dir

        # setup the campaign config file
        self.camp_info_file = os.path.join(self.projectDir,
                                           'config',
                                           camp_info_file)

        # determine whether the output directory exists or not
        if not os.path.exists(self.outputDir):
            logger.warning('Output directory for saving the results does' +
                           'not exist.\n{path}'.format(path=self.outputDir))
            # prompt up the request for creating the output directory
            res = input("Create the folder forcefully? (yes|no): ")
            if res.lower() == 'yes':
                os.mkdir(self.outputDir)

        # load conversion key
        self.conversion_key = self.load_convert_key_config()

        # load campaign list
        self.campaign_dict = self.load_campaign_list()

        # load metadata for the nc variables
        metadataFile = os.path.join(self.projectDir, 'config', METADATA_FILE)
        self.metadata = self.load_metadata(metadataFile)

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

    def load_metadata(self, filename):
        '''
        load the metadata for output nc files.
        '''
        if (not os.path.exists(filename)) or (not os.path.isfile(filename)):
            logger.error('metadata file does not exist!\n{file}'.
                         format(filename))
            raise FileNotFoundError

        metaData = toml.loads(filename)

        return metaData

    def load_campaign_list(self):
        '''
        load the campaign information list into a dict
        '''

        camp_list_file = os.path.join(
            self.projectDir, 'config', CAMPAIGN_LIST_FILE)

        # check the campaign list file
        if (not os.path.exists(camp_list_file)) or \
           (not os.path.isfile(camp_list_file)):
            logger.error('campaign list file does not exist!\n{file}'.format(
                file=camp_list_file))
            raise FileNotFoundError

        camp_dict = toml.loads(camp_list_file)

        # convert the timestamp to datetime object
        for camp_label in camp_dict:
            camp_dict[camp_label]['starttime'] = datetime.datetime.strptime(
                camp_dict[camp_label]['starttime'], '%Y-%m-%d %H:%M:%S')
            camp_dict[camp_label]['endtime'] = datetime.datetime.strptime(
                camp_dict[camp_label]['endtime'], '%Y-%m-%d %H:%M:%S')

        return camp_dict

    def load_convert_key_config(self):
        '''
        load the convert key for mapping the labview configurations to
        EARLINET standard configurations.
        '''
        convert_key_filepath = os.path.join(self.projectDir, CONVERT_KEY_FILE)

        if (not os.path.exists(convert_key_filepath)) or \
           (not os.path.isfile(convert_key_filepath)):
            logger.error('CONVERT_KEY_FILE does not exist!\n{file}'.format(
                file=convert_key_filepath))
            raise FileNotFoundError

        # load conversion key
        try:
            conversion_key = toml.loads(convert_key_filepath)
        except Exception as e:
            logger.error('Failure in reading CONVERT_KEY_FILE\n{file}'.format(
                file=convert_key_filepath))
            raise IOError

        return conversion_key

    def load_camp_info(self, camp_info_file=None):
        '''
        load the campain information
        '''

        if (not os.path.exists(camp_info_file)) or \
           (not os.path.isfile(camp_info_file)):
            logger.error('campaign configuration file does not exist!\n{file}'.
                         format(file=camp_info_file))
            raise FileNotFoundError

        camp_info = toml.loads(camp_info_file)

        return camp_info

    def read_data_file(self, filename):
        '''
        read the data from the polly data file (labview or picasso style)
        '''
        if self.fileType.lower() == 'labview':
            pollyData = self.__read_labview_results(filename)
        elif self.fileType.lower() == 'picasso':
            pollyData = self.__read_picasso_results(filename)
        else:
            logger.error('Wrong input of fileType: {fileType}'.format(
                fileType=self.fileType))

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

    def search_camp_info_file(self, pollyType, location, starttime):
        '''
        search the required campaign info file.

        If no file was found, return None
        '''
        instrument_list = [item.lower() for item in self.instrument_list]
        location_list = [item.lower() for item in self.location_list]

        if (not (pollyType.lower() in instrument_list)) or \
           (not (location.lower() in location_list)):
            return None

        # search campaign info file
        campaign_dict = self.campaign_dict
        campaign_file_list = []
        for item in self.campaign_dict:
            flagLocation = [self.campaign_dict[item]['location'].lower() ==
                            location.lower()]
            flagSystem = [self.campaign_dict[item]['system'].lower() ==
                          pollyType.lower()]
            flagTime = [(starttime < self.campaign_dict[item]['starttime']) and
                        (starttime >= self.campaign_dict[item]['endtime'])]
            if flagLocation and flagSystem and flagTime:
                campaign_file_list.append(os.path.join(self.projectDir,
                                                       'config',
                                                       item + '.toml'))

        if len(campaign_file_list) > 1:
            logger.error('Duplicated campaign info files were found.\n{file}'.
                         format(file=campaign_file_list))

        if not campaign_file_list:
            logger.warning('No campaign info file was found.')

        return campaign_file_list[0]

    def __read_labview_results(self, filename):
        '''
        read labview results into the data pool, which will then be exported
        to earlinet data format.

        If the file does no exist or the file was retrieved with Klett method,
        return None
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
            logger.warning(
                'File was retrieved with Klett method.\n{file}\nJump over!!!'.
                format(file=filename))
            return None, None, None

        # search the campaign info file
        if (not os.path.exists(self.camp_info_file)) or \
           (not os.path.isfile(self.camp_info_file)):
            logger.warning('Campaign info file does not exist. ' +
                           'Please check the {file}.\nNow turn to ' +
                           'auto-searching.'.format(file=self.camp_info_file))

            # auto-search for campaign info file
            self.camp_info_file = self.search_camp_info_file(
                                    self.pollyType,
                                    self.location, labviewInfo['starttime'])

            if (not os.path.exists(self.camp_info_file)) or \
               (not os.path.isfile(self.camp_info_file)):
                logger.error('Failed in searching the campaign info file. ' +
                             'Your file is not supported by the ' +
                             'campaign list.')
                raise FileNotFoundError

        # load the campaign info
        camp_info = toml.loads(self.camp_info_file)
        self.camp_info = camp_info

        # read labview data file
        labviewData = self.__read_labview_data(filename)

        # cut off the bins with influences from smoothing
        smoothWin = labviewInfo['smoothWindow']
        labviewDataCut = labviewData[int(smoothWin/2):-int(smoothWin/2), :]

        # convert the data matrix into dict with unit conversion
        labviewDataDict = {
            'height': labviewDataCut[0.:] * 1e3,
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
            # the unit in labview file is wrong
            'bsc_mol_355': labviewDataCut[66, :] * 1e-3,
            'bsc_mol_532': labviewDataCut[67, :] * 1e-3,
            'bsc_mol_1064': labviewDataCut[68, :] * 1e-3
        }

        # interpolate the data into the same grid
        fh_vdr_532 = interp1d(
            labviewDataCut['height_vdr_532'],
            labviewDataCut['vdr_532'],
            kind='linear')
        fh_vdr_std_532 = interp1d(
            labviewDataCut['height_vdr_532'],
            labviewDataCut['vdr_std_532'],
            kind='linear')
        fh_pdr_532 = interp1d(
            labviewDataCut['height_pdr_532'],
            labviewDataCut['pdr_532'],
            kind='linear')
        fh_pdr_std_532 = interp1d(
            labviewDataCut['height_pdr_std_532'],
            labviewDataCut['pdr_std_532'],
            kind='linear')
        fh_vdr_355 = interp1d(
            labviewDataCut['height_vdr_355'],
            labviewDataCut['vdr_355'],
            kind='linear')
        fh_vdr_std_355 = interp1d(
            labviewDataCut['height_vdr_355'],
            labviewDataCut['vdr_std_355'],
            kind='linear')
        fh_pdr_355 = interp1d(
            labviewDataCut['height_pdr_355'],
            labviewDataCut['pdr_355'],
            kind='linear')
        fh_pdr_std_355 = interp1d(
            labviewDataCut['height_pdr_std_355'],
            labviewDataCut['pdr_std_355'],
            kind='linear')

        labviewDataCut['vdr_532'] = fh_vdr_532(labviewDataCut['height'])
        labviewDataCut['vdr_std_532'] = fh_vdr_std_532(
            labviewDataCut['height'])
        labviewDataCut['pdr_532'] = fh_pdr_532(labviewDataCut['height'])
        labviewDataCut['pdr_std_532'] = fh_pdr_std_532(
            labviewDataCut['height'])
        labviewDataCut['vdr_355'] = fh_vdr_355(labviewDataCut['height'])
        labviewDataCut['vdr_std_355'] = fh_vdr_std_355(
            labviewDataCut['height'])
        labviewDataCut['pdr_355'] = fh_pdr_355(labviewDataCut['height'])
        labviewDataCut['pdr_std_355'] = fh_pdr_std_355(
            labviewDataCut['height'])

        # calculate the backscatter-ratio at the reference height
        refMask355 = (labviewDataCut['height'] >=
                      labviewInfo['backscatter_calibration_range_355'][0]) & \
                     (labviewDataCut['height'] <=
                      labviewInfo['backscatter_calibration_range_355'][1])
        refBscMol355 = np.nanmean(labviewDataCut['bsc_mol_355'][refMask355])
        refBscRatio355 = labviewInfo['backscatter_calibration_value_355'] / \
            refBscMol355 + 1
        refMask532 = (labviewDataCut['height'] >=
                      labviewInfo['backscatter_calibration_range_532'][0]) & \
                     (labviewDataCut['height'] <=
                      labviewInfo['backscatter_calibration_range_532'][1])
        refBscMol532 = np.nanmean(labviewDataCut['bsc_mol_532'][refMask532])
        refBscRatio532 = labviewInfo['backscatter_calibration_value_532'] / \
            refBscMol532 + 1
        refMask1064 = (labviewDataCut['height'] >=
                       labviewInfo['backscatter_calibration_range_1064'][0]) &\
                      (labviewDataCut['height'] <=
                       labviewInfo['backscatter_calibration_range_1064'][1])
        refBscMol1064 = np.nanmean(labviewDataCut['bsc_mol_1064'][refMask355])
        refBscRatio1064 = labviewInfo['backscatter_calibration_value_1064'] / \
            refBscMol1064 + 1

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
            'time_bounds': np.array([tObj.timestamp()
                                     for tObj in labviewInfo['time_bounds']]),
            'vertical_resolution': labviewInfo['dz'] * np.ones(
                             labviewDataCut['height'].shape, dtype=np.double),
            'cloud_mask': -127 * np.ones(labviewDataCut['height'].shape,
                                         dtype=np.byte),
            'cirrus_contamination': 0,   # 0: not_available;
                                         # 1: no_cirrus;
                                         # 2: cirrus_detected
            'cirrus_contamination_source': 0,   # 0: not_available;
                                                # 1: user_provided;
                                                # 2: automatic_calculated
            'error_retrieval_method': 1,   # 0: monte_carlo;
                                           # 1: error_propagation
            'extinction_evaluation_algorithm': 1,   # 0: Ansmann;
                                                    # 1: via_backscatter_ratio
            'backscatter_evaluation_method':
                labviewInfo['backscatter_evaluation_method'],
            'raman_backscatter_algorithm':
                labviewInfo['raman_backscatter_algorithm'],
            'extinction_assumed_wavelength_dependence':
                labviewInfo['extinction_assumed_wavelength_dependence'],
            'backscatter_calibration_range_355':
                labviewInfo['backscatter_calibration_range_355'],
            'backscatter_calibration_range_532':
                labviewInfo['backscatter_calibration_range_532'],
            'backscatter_calibration_range_1064':
                labviewInfo['backscatter_calibration_range_1064'],
            'backscatter_calibration_value_355':
                refBscRatio355,
            'backscatter_calibration_value_532':
                refBscRatio532,
            'backscatter_calibration_value_1064':
                refBscRatio1064,
            # the backscatter calibration search range
            # was not supported by labview. Therefore, set it to be constants.
            'backscatter_calibration_search_range_355':
                [0, 20000],
            'backscatter_calibration_search_range_532':
                [0, 20000],
            'backscatter_calibration_search_range_1064':
                [0, 20000],
            'ext_355': labviewDataCut['ext_355'],
            'ext_std_355': labviewDataCut['ext_std_355'],
            'ext_532': labviewDataCut['ext_532'],
            'ext_std_532': labviewDataCut['ext_std_532'],
            'bsc_355': labviewDataCut['bsc_355'],
            'bsc_std_355': labviewDataCut['bsc_std_355'],
            'bsc_532': labviewDataCut['bsc_532'],
            'bsc_std_532': labviewDataCut['bsc_std_532'],
            'bsc_1064': labviewDataCut['bsc_1064'],
            'bsc_std_1064': labviewDataCut['bsc_std_1064'],
            'vdr_355': labviewDataDict['vdr_355'],
            'vdr_std_355': labviewDataDict['vdr_std_355'],
            'vdr_532': labviewDataDict['vdr_532'],
            'vdr_std_532': labviewDataDict['vdr_std_532'],
            'pdr_355': labviewDataDict['pdr_355'],
            'pdr_std_355': labviewDataDict['pdr_std_355'],
            'pdr_532': labviewDataDict['pdr_532'],
            'pdr_std_532': labviewDataDict['pdr_std_532'],
            'user_defined_category': self.category,
            'cirrus_contamination_source': 0,
            'atmospheric_molecular_calculation_source':
            labviewInfo['sounding_type'],
            'latitude': camp_info['station_latitude'],
            'longitude': camp_info['station_longitude'],
            'shots': labviewInfo['shots'],
            'station_altitude': camp_info['station_altitude'],
            'zenith_angle': labviewInfo['zeinth_angle'],
            }

        global_attrs = camp_info

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
        labviewInfo['starttime'] = datetime.datetime.strptime(
            labviewInfo['starttime'], '%y%m%d %H%M')
        labviewInfo['endtime'] = datetime.datetime.strptime(
            labviewInfo['endtime'], '%y%m%d %H%M')

        # concatenate reference height
        labviewInfo['reference_height_355'] = np.concatenate(
            (labviewInfo['reference_height_bottom_355'],
             labviewInfo['reference_height_top_355']), axis=0)
        labviewInfo['reference_height_532'] = np.concatenate(
            (labviewInfo['reference_height_bottom_532'],
             labviewInfo['reference_height_top_532']), axis=0)
        labviewInfo['reference_height_1064'] = np.concatenate(
            (labviewInfo['reference_height_bottom_1064'],
             labviewInfo['reference_height_top_1064']), axis=0)

        # convert the retrieving method
        retMethodDict = dict(zip(
            self.conversion_key['lk_retrieving_method'],
            self.conversion_key['ek_retrieving_method']))
        labviewInfo['retrieving_method'] = \
            retMethodDict[labviewInfo['retrieving_method']]

        # convert the flag_use_particle_ext_for_raman_bsc
        ramanMethodDict = dict(zip(
            self.conversion_key['lk_raman_backscatter_algorithm'],
            self.conversion_key['ek_raman_backscatter_algorithm']
        ))
        labviewInfo['raman_backscatter_algorithm'] = \
            ramanMethodDict[labviewInfo['flag_use_particle_ext_for_raman_bsc']]

        # convert the sounding type
        soundingSearchList = self.conversion_key['ek_meteor_source']
        labviewInfo['sounding_type'] = \
            soundingSearchList[labviewInfo['sounding_type']]

        data = {
                'atmospheric_molecular_calculation_source':
                labviewInfo['sounding_type'],   # 0: US_standard_atmosphere;
                                                # 1: radiosonding;
                                                # 2: ecmwf;
                                                # 3: icon-iglo-12-23;
                                                # 4: gdas
                'backscatter_calibration_range_355': \
                labviewInfo['reference_height_355'],
                'backscatter_calibration_range_532': \
                labviewInfo['reference_height_532'],
                'backscatter_calibration_range_1064': \
                labviewInfo['reference_height_1064'],
                'backscatter_calibration_range_search_algorithm': 0,
                'backscatter_calibration_value_355': \
                labviewInfo['reference_value_355'],
                'backscatter_calibration_value_532': \
                labviewInfo['reference_value_532'],
                'backscatter_calibration_value_1064': \
                labviewInfo['reference_value_1064'],
                # 0: Raman; 1: elastic_backscatter
                'backscatter_evaluation_method': \
                labviewInfo['retrieving_method'],
                'smoothWindow': labviewInfo['smooth_ext_355'],
                'retrieving_method': labviewInfo['retrieving_method'],
                # Ångstroem exponent
                'extinction_assumed_wavelength_dependence': labviewInfo['AE'],
                # 0: weighted_linear_fit; 1: non-weighted_linear_fit
                'extinction_evaluation_algorithm': 1,
                'shots': 1,   # number of accumulated laser shots
                # seconds since 1970-01-01 00:00:00
                'time': labviewInfo['starttime'],
                # time_bounds
                'time_bounds': \
                [labviewInfo['starttime'], labviewInfo['endtime']],
                # 1: cirrus; 2: climatol; 4: dicycles; 8: etna; 16: forfires;
                # 32: photosmog; 64: rurban; 128: sahadust; 256: stratos;
                # 512: satellite_overpass
                'user_defined_category': self.category,
                'vertical_resolution': labviewInfo['dz'],   # [m]
                'zenith_angle': \
                np.rad2deg(np.arccos(labviewInfo['dz'] /
                           labviewInfo['range_resolution'])),
                'raman_backscatter_algorithm':
                labviewInfo['raman_backscatter_algorithm']
            }

        return data

    def labview_info_parser(self, filename):
        '''
        parsing the information from the labview info file
        '''

        if (not os.path.exists(filename)) or (not os.path.isfile(filename)):
            logger.error('Labview info file does not exist.\n{infoFile}'.
                         format(infoFile=filename))
            raise ValueError

        # decoder structure
        # key:  regex, conversion function fill value
        decoders = {
            'starttime':
                (
                        r'(?<=Messung von \(UTC\):)\d+.\d+',
                        str,
                        '000000 0000'
                ),
            'endtime':
                (
                    r'(?<=bis \(UTC\))\d+.\d+',
                    str,
                    '000000 0000'
                ),
            'reference_height_bottom_355':
                (
                    r'(?<=refheigt355\(m\) from : )\d+',
                    float,
                    0
                ),
            'reference_height_top_355':
                (
                    r'(?<=refheight355 \(m\) to: )\d+',
                    float,
                    0
                ),
            'reference_value_355':
                (
                    r'(?<=refwert355 \(km\^-1 sr\^-1\): )\d+\.\d+[eE]-?\d+',
                    str,
                    0
                ),
            'reference_height_bottom_532':
                (
                    r'(?<=refheigt532\(m\) from : )\d+',
                    float,
                    0
                ),
            'reference_height_top_532':
                (
                    r'(?<=refheight532 \(m\) to: )\d+',
                    float,
                    0
                ),
            'reference_value_532':
                (
                    r'(?<=refwert532 \(km\^-1 sr\^-1\): )\d+\.\d+[eE]-?\d+',
                    str,
                    0
                ),
            'reference_height_bottom_1064':
                (
                    r'(?<=refheigt1064\(m\) from : )\d+',
                    float,
                    0
                ),
            'reference_height_top_1064':
                (
                    r'(?<=refheight1064 \(m\) to: )\d+',
                    float,
                    0
                ),
            'reference_value_1064':
                (
                    r'(?<=refwert1064 \(km\^-1 sr\^-1\): )\d+\.\d+[eE]-?\d+',
                    str,
                    0
                ),
            'smooth_ext_355':
                (
                    r'(?<=smoothingalpha355: )\d+',
                    int,
                    0
                ),
            'smooth_bsc_355':
                (
                    r'(?<=smootingbeta355: )\d+',
                    int,
                    0
                ),
            'smooth_ext_532':
                (
                    r'(?<=smoothingalpha532: )\d+',
                    int,
                    0
                ),
            'smooth_bsc_532':
                (
                    r'(?<=smootingbeta532: )\d+',
                    int,
                    0
                ),
            'smooth_ext_1064':
                (
                    r'(?<=smoothingalpha1064: )\d+',
                    int,
                    0
                ),
            'smooth_bsc_1064':
                (
                    r'(?<=smootingbeta1064: )\d+',
                    int,
                    0
                ),
            'dz':
                (
                    r'(?<=dz: )\d+\.?\d+',
                    float,
                    0
                ),
            'retrieving_method':
                (
                    r'(?<=\nMethod:)\w+',
                    str,
                    'Raman'
                ),
            'AE':
                (
                    r'(?<=Angström for Raman Extinction: )\d+\.?\d+',
                    float,
                    0
                ),
            'sounding_type':
                (
                    r'(?<=Sounding Type: )\d\.?\d+',
                    float,
                    0
                ),
            'flag_deadtime_correction':
                (
                    r'(?<=Death time correction: )\w+',
                    str,
                    'no'
                ),
            'flag_use_particle_ext_for_raman_bsc':
                (
                    r'(?<=Use particle ext for raman Bsc: )\w+',
                    str,
                    'no'
                ),
            'range_resolution':
                (
                    r'(?<=Range resolution: )\d+\.?\d+',
                    float,
                    0
                ),
            'software_version':
                (
                    r'(?<=Software version: )\w+\.?\w+',
                    str,
                    ''
                ),
        }

        def find_in_string(key, dec, str):
            res = re.search(dec[0], str)
            if res is not None:
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
            data.update({key: val})

        return data

    def __read_picasso_results(self):
        data = []
        return data

    def write_to_earlinet_nc(self, variables, dimensions, global_attri):
        '''
        write the variables, dimensions and global_attri to EARLINET files.
        Examples can be found in 'include'
        '''

        # write to b355
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b355|e355}.nc
        file_b355 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_b355.nc'.
            format(date=datetime.datetime.strftime('%Y%m%d_%H%M'),
                   station_ID=self.camp_info['station_ID'].lower(),
                   instrument=self.pollyType.lower()))
        var_b355 = {
            'altitude':
                variables['altitude'],
            'atmospheric_molecular_calculation_source':
                variables['atmospheric_molecular_calculation_source'],
            'backscatter':
                variables['bsc_355'],
            'backscatter_calibration_range':
                variables['backscatter_calibration_range_355'],
            'backscatter_calibration_range_search_algorithm':
                0,
            'backscatter_calibration_search_range':
                variables['backscatter_calibration_search_range_355'],
            'backscatter_calibration_value':
                variables['backscatter_calibration_value_355'],
            'backscatter_evaluation_method':
                variables['backscatter_evaluation_method'],
            'cirrus_contamination':
                variables['cirrus_contamination'],
            'cirrus_contamination_source':
                variables['cirrus_contamination_source'],
            'cloud_mask':
                variables['cloud_mask'],
            'earlinet_product_type':
                2,
            'elastic_backscatter_algorithm':
                1,
            'error_backscatter':
                variables['bsc_std_355'],
            'error_retrieval_method':
                variables['error_retrieval_method'],
            'latitude':
                variables['latitude'],
            'longitude':
                variables['longitude'],
            'raman_backscatter_algorithm':
                variables['raman_backscatter_algorithm'],
            'shots':
                variables['shots'],
            'station_altitude':
                variables['station_altitude'],
            'time':
                variables['time'],
            'time_bounds':
                variables['time_bounds'],
            'user_defined_category':
                variables['user_defined_category'],
            'vertical_resolution':
                variables['vertical_resolution'],
            'wavelength':
                355,
            'zenith_angle':
                variables['zenith_angle']
        }
        dim_b355 = dimensions
        global_attri_b355 = global_attri
        logger.info('Writing data to {file}'.format(file=file_b355))
        self.__write_2_earlinet_nc(file_b355, var_b355, dim_b355,
                                   global_attri_b355)

        # write to e355
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b355|e355}.nc
        file_e355 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_e355.nc'.
            format(date=datetime.datetime.strftime('%Y%m%d_%H%M'),
                   station_ID=self.camp_info['station_ID'].lower(),
                   instrument=self.pollyType.lower()))
        var_e355 = {
            'altitude':
                variables['altitude'],
            'atmospheric_molecular_calculation_source':
                variables['atmospheric_molecular_calculation_source'],
            'backscatter':
                variables['bsc_355'],
            'backscatter_calibration_range':
                variables['backscatter_calibration_range_355'],
            'backscatter_calibration_range_search_algorithm':
                0,
            'backscatter_calibration_search_range':
                variables['backscatter_calibration_search_range_355'],
            'backscatter_calibration_value':
                variables['backscatter_calibration_value_355'],
            'backscatter_evaluation_method':
                variables['backscatter_evaluation_method'],
            'cirrus_contamination':
                variables['cirrus_contamination'],
            'cirrus_contamination_source':
                variables['cirrus_contamination_source'],
            'cloud_mask':
                variables['cloud_mask'],
            'earlinet_product_type':
                2,
            'elastic_backscatter_algorithm':
                1,
            'error_backscatter':
                variables['bsc_std_355'],
            'error_extinction':
                variables['ext_std_355'],
            'error_retrieval_method':
                variables['error_retrieval_method'],
            'extinction':
                variables['extinction'],
            'extinction_assumed_wavelength_dependence':
                variables['extinction_assumed_wavelength_dependence'],
            'extinction_evaluation_algorithm':
                variables['extinction_evaluation_algorithm'],
            'latitude':
                variables['latitude'],
            'longitude':
                variables['longitude'],
            'raman_backscatter_algorithm':
                variables['raman_backscatter_algorithm'],
            'shots':
                variables['shots'],
            'station_altitude':
                variables['station_altitude'],
            'time':
                variables['time'],
            'time_bounds':
                variables['time_bounds'],
            'user_defined_category':
                variables['user_defined_category'],
            'vertical_resolution':
                variables['vertical_resolution'],
            'wavelength':
                355,
            'zenith_angle':
                variables['zenith_angle']
        }
        dim_e355 = dimensions
        global_attri_e355 = global_attri
        logger.info('Writing data to {file}'.format(file=file_e355))
        self.__write_2_earlinet_nc(file_e355, var_e355, dim_e355,
                                   global_attri_e355)

        # write to b532
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b532|e532}.nc
        file_b532 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_b532.nc'.
            format(date=datetime.datetime.strftime('%Y%m%d_%H%M'),
                   station_ID=self.camp_info['station_ID'].lower(),
                   instrument=self.pollyType.lower()))
        var_b532 = {
            'altitude':
                variables['altitude'],
            'atmospheric_molecular_calculation_source':
                variables['atmospheric_molecular_calculation_source'],
            'backscatter':
                variables['bsc_532'],
            'backscatter_calibration_range':
                variables['backscatter_calibration_range_532'],
            'backscatter_calibration_range_search_algorithm':
                0,
            'backscatter_calibration_search_range':
                variables['backscatter_calibration_search_range_532'],
            'backscatter_calibration_value':
                variables['backscatter_calibration_value_532'],
            'backscatter_evaluation_method':
                variables['backscatter_evaluation_method'],
            'cirrus_contamination':
                variables['cirrus_contamination'],
            'cirrus_contamination_source':
                variables['cirrus_contamination_source'],
            'cloud_mask':
                variables['cloud_mask'],
            'earlinet_product_type':
                2,
            'elastic_backscatter_algorithm':
                1,
            'error_backscatter':
                variables['bsc_std_532'],
            'error_particledepolarization':
                variables['pdr_std_532'],
            'error_retrieval_method':
                variables['error_retrieval_method'],
            'error_volumedepolarization':
                variables['vdr_std_532'],
            'latitude':
                variables['latitude'],
            'longitude':
                variables['longitude'],
            'particledepolarization':
                variables['pdr_532'],
            'raman_backscatter_algorithm':
                variables['raman_backscatter_algorithm'],
            'shots':
                variables['shots'],
            'station_altitude':
                variables['station_altitude'],
            'time':
                variables['time'],
            'time_bounds':
                variables['time_bounds'],
            'user_defined_category':
                variables['user_defined_category'],
            'vertical_resolution':
                variables['vertical_resolution'],
            'volumedepolarization':
                variables['vdr_532'],
            'wavelength':
                532,
            'zenith_angle':
                variables['zenith_angle']
        }
        dim_b532 = dimensions
        global_attri_b532 = global_attri
        logger.info('Writing data to {file}'.format(file=file_b532))
        self.__write_2_earlinet_nc(file_b532, var_b532, dim_b532,
                                   global_attri_b532)

        # write to e532
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b532|e532}.nc
        file_e532 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_e532.nc'.
            format(date=datetime.datetime.strftime('%Y%m%d_%H%M'),
                   station_ID=self.camp_info['station_ID'].lower(),
                   instrument=self.pollyType.lower()))
        var_e532 = {
            'altitude':
                variables['altitude'],
            'atmospheric_molecular_calculation_source':
                variables['atmospheric_molecular_calculation_source'],
            'backscatter':
                variables['bsc_532'],
            'backscatter_calibration_range':
                variables['backscatter_calibration_range_532'],
            'backscatter_calibration_range_search_algorithm':
                0,
            'backscatter_calibration_search_range':
                variables['backscatter_calibration_search_range_532'],
            'backscatter_calibration_value':
                variables['backscatter_calibration_value_532'],
            'backscatter_evaluation_method':
                variables['backscatter_evaluation_method'],
            'cirrus_contamination':
                variables['cirrus_contamination'],
            'cirrus_contamination_source':
                variables['cirrus_contamination_source'],
            'cloud_mask':
                variables['cloud_mask'],
            'earlinet_product_type':
                2,
            'elastic_backscatter_algorithm':
                1,
            'error_backscatter':
                variables['bsc_std_532'],
            'error_extinction':
                variables['ext_std_532'],
            'error_retrieval_method':
                variables['error_retrieval_method'],
            'extinction':
                variables['extinction'],
            'extinction_assumed_wavelength_dependence':
                variables['extinction_assumed_wavelength_dependence'],
            'extinction_evaluation_algorithm':
                variables['extinction_evaluation_algorithm'],
            'latitude':
                variables['latitude'],
            'longitude':
                variables['longitude'],
            'raman_backscatter_algorithm':
                variables['raman_backscatter_algorithm'],
            'shots':
                variables['shots'],
            'station_altitude':
                variables['station_altitude'],
            'time':
                variables['time'],
            'time_bounds':
                variables['time_bounds'],
            'user_defined_category':
                variables['user_defined_category'],
            'vertical_resolution':
                variables['vertical_resolution'],
            'wavelength':
                532,
            'zenith_angle':
                variables['zenith_angle']
        }
        dim_e532 = dimensions
        global_attri_e532 = global_attri
        logger.info('Writing data to {file}'.format(file=file_e532))
        self.__write_2_earlinet_nc(file_e532, var_e532, dim_e532,
                                   global_attri_e532)

        # write to b1064
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b1064}.nc
        file_b1064 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_b1064.nc'.
            format(date=datetime.datetime.strftime('%Y%m%d_%H%M'),
                   station_ID=self.camp_info['station_ID'].lower(),
                   instrument=self.pollyType.lower()))
        var_b1064 = {
            'altitude':
                variables['altitude'],
            'atmospheric_molecular_calculation_source':
                variables['atmospheric_molecular_calculation_source'],
            'backscatter':
                variables['bsc_1064'],
            'backscatter_calibration_range':
                variables['backscatter_calibration_range_1064'],
            'backscatter_calibration_range_search_algorithm':
                0,
            'backscatter_calibration_search_range':
                variables['backscatter_calibration_search_range_1064'],
            'backscatter_calibration_value':
                variables['backscatter_calibration_value_1064'],
            'backscatter_evaluation_method':
                variables['backscatter_evaluation_method'],
            'cirrus_contamination':
                variables['cirrus_contamination'],
            'cirrus_contamination_source':
                variables['cirrus_contamination_source'],
            'cloud_mask':
                variables['cloud_mask'],
            'earlinet_product_type':
                2,
            'elastic_backscatter_algorithm':
                1,
            'error_backscatter':
                variables['bsc_std_1064'],
            'error_retrieval_method':
                variables['error_retrieval_method'],
            'latitude':
                variables['latitude'],
            'longitude':
                variables['longitude'],
            'raman_backscatter_algorithm':
                variables['raman_backscatter_algorithm'],
            'shots':
                variables['shots'],
            'station_altitude':
                variables['station_altitude'],
            'time':
                variables['time'],
            'time_bounds':
                variables['time_bounds'],
            'user_defined_category':
                variables['user_defined_category'],
            'vertical_resolution':
                variables['vertical_resolution'],
            'wavelength':
                1064,
            'zenith_angle':
                variables['zenith_angle']
        }
        dim_b1064 = dimensions
        global_attri_b1064 = global_attri
        logger.info('Writing data to {file}'.format(file=file_b1064))
        self.__write_2_earlinet_nc(file_b1064, var_b1064, dim_b1064,
                                   global_attri_b1064)

    def __write_2_earlinet_nc(self, filename, variables, dimensions,
                              global_attri):
        '''
        write to EARLINET nc file. Example can be found in 'include'
        '''
        dataset = Dataset(filename, 'w', format=NETCDF_FORMAT)

        # create dimensions
        for dim_key in self.metadata['dimensions']:
            dataset.createDimension(dim_key, dimensions[dim_key])

        # create variables
        npTypeDict = {
            'byte': np.byte,
            'int': np.intc,
            'float': np.single,
            'double': np.double
        }
        for var_key in variables:
            dataset.createVariable(var_key,
                                   npTypeDict[self.metadata[var_key]['dtype']],
                                   set(self.metadata[var_key]['dims']))

        # write variables
        for var_key in variables:
            dataset.variables[var_key][:] = variables[var_key]

        # create variable attributes
        for var_key in variables:
            for var_attr in self.metadata[var_key]:
                setattr(dataset.variables[var_key],
                        var_attr,
                        self.metadata[var_key][var_attr])

        # create global attributes
        for attr_key in self.camp_info:
            setattr(dataset, attr_key, self.camp_info[attr_key])

        dataset.close()

        # Command line interface
        # convert_polly_2_earlinet -p pollyxt_lacros -l dushanbe -t labview
        # -c 2 -f xxx.txt -d output_dir [-c xxx.toml --force true]
        # convert_polly_2_earlinet --list_campaign
        #   convert_polly_2_earlinet -h | --help
