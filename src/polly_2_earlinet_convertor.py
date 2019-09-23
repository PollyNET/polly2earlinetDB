import os
import sys
import toml
import logging
import glob
import numpy as np
import datetime
import re
import argparse
from netCDF4 import Dataset
from scipy.interpolate import interp1d

LOG_MODE = 'DEBUG'
LOGFILE = 'log'
CONVERT_KEY_FILE = 'labview_key_2_earlinet_key_spec.toml'
METADATA_FILE = 'metadata.toml'
CAMPAIGN_LIST_FILE = 'campaign_list.toml'
NETCDF_FORMAT = "NETCDF4"
PROJECTDIR = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))
)

# initialize the logger
logFile = os.path.join(PROJECTDIR, LOGFILE)
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
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logModeDict[LOG_MODE])

formatterFh = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - ' +
                                '%(funcName)s - %(lineno)d - %(message)s')
formatterCh = logging.Formatter(
    '%(message)s')
fh.setFormatter(formatterFh)
ch.setFormatter(formatterCh)

logger.addHandler(fh)
logger.addHandler(ch)


class polly_earlinet_convertor(object):
    """
    Description
    -----------
    convert the polly data into EARLINET format
    Exemplified file can be found under the folder of "include/".

    Method
    ------
    read_data_file: read polly results into data container of 'variables',
                    'dimensions' and 'global_attr'

    search_data_files: search the polly data files through wildcards

    write_to_earlinet_nc: write data container into EARLINET nc files

    History
    -------
    2019-09-09. First edition by Zhenping
    """

    def __init__(self, pollyType='', location='', fileType='labview',
                 category=2, output_dir='', *, camp_info_file='', force=False):
        '''
        Initialize the class variables

        parameters
        ----------
        pollyType: str
            polly type. e.g., pollyxt_tropos
        location: str
            location of the campaign.
        fileType: str
            polly file type. (labview | picasso)
        category: int
            category of the results.
        output_dir: str
            directory for saving the converted files

        Keywords
        --------
        camp_info_file: str
            campaign info file to provide the global attributes.
        force: boolean
            flag to control whether to overwirte the netCDF files.
        '''

        # initialize the class variables
        self.pollyType = pollyType
        self.location = location
        self.fileType = fileType
        self.category = category
        self.projectDir = PROJECTDIR
        self.outputDir = output_dir
        self.force = force

        # setup the campaign config file
        self.camp_info_file = os.path.join(self.projectDir,
                                           'config',
                                           camp_info_file)

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
            location_list.append(self.campaign_dict[camp_label]['location'])
        self.location_list = list(set(location_list))

    def load_metadata(self, filename):
        '''
        load the metadata for output nc files.
        '''
        if (not os.path.exists(filename)) or (not os.path.isfile(filename)):
            logger.error('metadata file does not exist!\n{file}'.
                         format(filename))
            raise FileNotFoundError

        with open(filename, 'r', encoding='utf-8') as fh:
            metaData = toml.loads(fh.read())

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

        with open(camp_list_file, 'r', encoding='utf-8') as fh:
            camp_dict = toml.loads(fh.read())

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
        convert_key_filepath = os.path.join(self.projectDir,
                                            'config',
                                            CONVERT_KEY_FILE)

        if (not os.path.exists(convert_key_filepath)) or \
           (not os.path.isfile(convert_key_filepath)):
            logger.error('CONVERT_KEY_FILE does not exist!\n{file}'.format(
                file=convert_key_filepath))
            raise FileNotFoundError

        # load conversion key
        try:
            with open(convert_key_filepath, 'r', encoding='utf-8') as fh:
                conversion_key = toml.loads(fh.read())
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

        with open(camp_info_file, 'r', encoding='uft-8') as fh:
            camp_info = toml.loads(fh.read())

        return camp_info

    def read_data_file(self, filename):
        '''
        read the data from the polly data file (labview or picasso style)
        '''
        if self.fileType.lower() == 'labview':
            dims, data, global_attr = self.__read_labview_results(filename)
        elif self.fileType.lower() == 'picasso':
            dims, data, global_attr = self.__read_picasso_results(filename)
        else:
            logger.error('Wrong input of fileType: {fileType}'.format(
                fileType=self.fileType))

        return dims, data, global_attr

    def search_data_files(self, filename, filepath=None):
        '''
        Search the polly data files. Wildcards are supported.
        '''
        if not filepath:
            filepath = os.getcwd()

        # search the files
        logger.info('Start to search polly data files...')
        fileList = glob.glob(os.path.join(filepath, filename))
        logger.info('number of files: {nFiles:d}'.
                    format(nFiles=len(fileList)))

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
            return ''

        # search campaign info file
        campaign_dict = self.campaign_dict
        campaign_file_list = []
        for item in self.campaign_dict:
            flagLocation = self.campaign_dict[item]['location'].lower() == \
                           location.lower()
            flagSystem = self.campaign_dict[item]['system'].lower() == \
                pollyType.lower()
            flagTime = (starttime > self.campaign_dict[item]['starttime']) and\
                       (starttime <= self.campaign_dict[item]['endtime'])
            if flagLocation and flagSystem and flagTime:
                campaign_file_list.append(os.path.join(self.projectDir,
                                                       'config',
                                                       item + '.toml'))

        if len(campaign_file_list) > 1:
            logger.error('Duplicated campaign info files were found.\n{file}'.
                         format(file=campaign_file_list))

        if not campaign_file_list:
            logger.warning('No campaign info file was found.')
            return ''
        else:
            logger.info('{file} will be loaded for campaign configs.'.
                        format(file=campaign_file_list[0]))

        return campaign_file_list[0]

    def __read_labview_results(self, filename):
        '''
        read labview results into the data pool, which will then be exported
        to earlinet data format.

        If the file does no exist or the file was retrieved with Klett method,
        return None
        '''
        if (not os.path.exists(filename)) or (not os.path.isfile(filename)):
            logger.warning('{file} does not exist!\nFinish!'.
                           format(file=filename))
            return None, None, None

        logger.info('Start reading {filename}'.format(filename=filename))

        # read labview info file
        infoFilename = filename[0:-4] + '-info.txt'
        labviewInfo = self.__read_labview_info(infoFilename)

        if not labviewInfo:
            # if failed in retrieving the labview info
            return None, None, None

        # # jump over Klett profiles
        # if labviewInfo['retrieving_method'] == 1:
        #     logger.warning(
        #     'File was retrieved with Klett method.\n{file}\nJump over!!!'.
        #     format(file=filename))
        #     return None, None, None

        # search the campaign info file
        if (not os.path.exists(self.camp_info_file)) or \
           (not os.path.isfile(self.camp_info_file)):
            logger.warning('Campaign info file does not exist. Please check ' +
                           'the {file}'.format(file=self.camp_info_file) +
                           '.\nNow turn to auto-searching.')

            # auto-search for campaign info file
            self.camp_info_file = self.search_camp_info_file(
                                    self.pollyType,
                                    self.location, labviewInfo['starttime'])

            if (not os.path.exists(self.camp_info_file)) or \
               (not os.path.isfile(self.camp_info_file)):
                logger.warning('Failed in searching the campaign info file. ' +
                               'Your instrument or campaign is not ' +
                               'supported by the campaign list.')
                return None, None, None

        # load the campaign info
        with open(self.camp_info_file, 'r', encoding='utf-8') as fh:
            camp_info = toml.loads(fh.read())

        if not (camp_info['processor_name']):
            # set processor_name automatically if not set in the camp_info file
            camp_info['processor_name'] = labviewInfo['software_version']

            if not (labviewInfo['software_version']):
                logger.warn('No software_version in your info file.\n' +
                            'Please check your labview version. Or set the ' +
                            'process_name in the campaign info file.')
                return None, None, None

        self.camp_info = camp_info

        # read labview data file
        labviewData = self.__read_labview_data(filename)

        # cut off the bins with influences from smoothing
        smoothWin = labviewInfo['smoothWindow']
        labviewDataCut = labviewData[int(smoothWin/2):-int(smoothWin/2), :]

        # convert the data matrix into dict with unit conversion
        labviewDataDict = {
            'height': labviewDataCut[:, 0] * 1e3,
            'bsc_355': labviewDataCut[:, 1] * 1e-6,
            'bsc_std_355': labviewDataCut[:, 2] * 1e-6,
            'bsc_532': labviewDataCut[:, 3] * 1e-6,
            'bsc_std_532': labviewDataCut[:, 4] * 1e-6,
            'bsc_1064': labviewDataCut[:, 5] * 1e-6,
            'bsc_std_1064': labviewDataCut[:, 6] * 1e-6,
            'ext_355': labviewDataCut[:, 7] * 1e-6,
            'ext_std_355': labviewDataCut[:, 8] * 1e-6,
            'ext_532': labviewDataCut[:, 9] * 1e-6,
            'ext_std_532': labviewDataCut[:, 10] * 1e-6,
            'lr_355': labviewDataCut[:, 11],
            'lr_std_355': labviewDataCut[:, 12],
            'lr_532': labviewDataCut[:, 13],
            'lr_std_532': labviewDataCut[:, 14],
            'EAE_355_532': labviewDataCut[:, 15],
            'EAE_std_355_532': labviewDataCut[:, 16],
            'BAE_355_532': labviewDataCut[:, 17],
            'BAE_std_355_532': labviewDataCut[:, 18],
            'BAE_532_1064': labviewDataCut[:, 19],
            'BAE_std_532_1064': labviewDataCut[:, 20],
            'height_vdr_532': labviewDataCut[:, 21] * 1e3,
            'vdr_532': labviewDataCut[:, 22],
            'vdr_std_532': labviewDataCut[:, 23],
            'height_pdr_532': labviewDataCut[:, 24] * 1e3,
            'pdr_532': labviewDataCut[:, 25],
            'pdr_std_532': labviewDataCut[:, 26],
            'height_sounding': labviewDataCut[:, 27] * 1e3,
            'temperature': labviewDataCut[:, 28],
            'pressure': labviewDataCut[:, 29],
            'height_vdr_355': labviewDataCut[:, 30] * 1e3,
            'vdr_355': labviewDataCut[:, 31],
            'vdr_std_355': labviewDataCut[:, 32],
            'height_pdr_355': labviewDataCut[:, 33] * 1e3,
            'pdr_355': labviewDataCut[:, 34],
            'pdr_std_355': labviewDataCut[:, 35],
            # the unit in labview file is wrong
            'bsc_mol_355': labviewDataCut[:, 66] * 1e-3,
            'bsc_mol_532': labviewDataCut[:, 67] * 1e-3,
            'bsc_mol_1064': labviewDataCut[:, 68] * 1e-3
        }

        # interpolate the data into the same grid
        fh_vdr_532 = interp1d(
            labviewDataDict['height_vdr_532'],
            labviewDataDict['vdr_532'],
            kind='linear',
            fill_value='extrapolate')
        fh_vdr_std_532 = interp1d(
            labviewDataDict['height_vdr_532'],
            labviewDataDict['vdr_std_532'],
            kind='linear',
            fill_value='extrapolate')
        fh_pdr_532 = interp1d(
            labviewDataDict['height_pdr_532'],
            labviewDataDict['pdr_532'],
            kind='linear',
            fill_value='extrapolate')
        fh_pdr_std_532 = interp1d(
            labviewDataDict['height_pdr_532'],
            labviewDataDict['pdr_std_532'],
            kind='linear',
            fill_value='extrapolate')
        fh_vdr_355 = interp1d(
            labviewDataDict['height_vdr_355'],
            labviewDataDict['vdr_355'],
            kind='linear',
            fill_value='extrapolate')
        fh_vdr_std_355 = interp1d(
            labviewDataDict['height_vdr_355'],
            labviewDataDict['vdr_std_355'],
            kind='linear',
            fill_value='extrapolate')
        fh_pdr_355 = interp1d(
            labviewDataDict['height_pdr_355'],
            labviewDataDict['pdr_355'],
            kind='linear',
            fill_value='extrapolate')
        fh_pdr_std_355 = interp1d(
            labviewDataDict['height_pdr_355'],
            labviewDataDict['pdr_std_355'],
            kind='linear',
            fill_value='extrapolate')

        labviewDataDict['vdr_532'] = fh_vdr_532(labviewDataDict['height'])
        labviewDataDict['vdr_std_532'] = fh_vdr_std_532(
            labviewDataDict['height'])
        labviewDataDict['pdr_532'] = fh_pdr_532(labviewDataDict['height'])
        labviewDataDict['pdr_std_532'] = fh_pdr_std_532(
            labviewDataDict['height'])
        labviewDataDict['vdr_355'] = fh_vdr_355(labviewDataDict['height'])
        labviewDataDict['vdr_std_355'] = fh_vdr_std_355(
            labviewDataDict['height'])
        labviewDataDict['pdr_355'] = fh_pdr_355(labviewDataDict['height'])
        labviewDataDict['pdr_std_355'] = fh_pdr_std_355(
            labviewDataDict['height'])

        # calculate the backscatter-ratio at the reference height
        refMask355 = (labviewDataDict['height'] >=
                      labviewInfo['backscatter_calibration_range_355'][0]) & \
                     (labviewDataDict['height'] <=
                      labviewInfo['backscatter_calibration_range_355'][1])
        refBscMol355 = np.nanmean(labviewDataDict['bsc_mol_355'][refMask355])
        refBscRatio355 = labviewInfo['backscatter_calibration_value_355'] / \
            refBscMol355 + 1
        refMask532 = (labviewDataDict['height'] >=
                      labviewInfo['backscatter_calibration_range_532'][0]) & \
                     (labviewDataDict['height'] <=
                      labviewInfo['backscatter_calibration_range_532'][1])
        refBscMol532 = np.nanmean(labviewDataDict['bsc_mol_532'][refMask532])
        refBscRatio532 = labviewInfo['backscatter_calibration_value_532'] / \
            refBscMol532 + 1
        refMask1064 = (labviewDataDict['height'] >=
                       labviewInfo['backscatter_calibration_range_1064'][0]) &\
                      (labviewDataDict['height'] <=
                       labviewInfo['backscatter_calibration_range_1064'][1])
        refBscMol1064 = np.nanmean(
            labviewDataDict['bsc_mol_1064'][refMask1064])
        refBscRatio1064 = labviewInfo['backscatter_calibration_value_1064'] / \
            refBscMol1064 + 1

        # convert the labview data into the data container
        dimensions = {
            'altitude': len(labviewDataDict['height']),
            'time': 1,
            'wavelength': 1,
            'nv': 2   # number of values (2 for reference height)
        }

        data = {
            'altitude': labviewDataDict['height'],
            'time': labviewInfo['starttime'].timestamp(),
            'time_bounds': np.array([tObj.timestamp()
                                     for tObj in labviewInfo['time_bounds']]),
            'vertical_resolution': labviewInfo['vertical_resolution'] *
            np.ones(labviewDataDict['height'].shape,
                    dtype=np.double),
            'cloud_mask': -127 * np.ones(labviewDataDict['height'].shape,
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
            'ext_355': labviewDataDict['ext_355'],
            'ext_std_355': labviewDataDict['ext_std_355'],
            'ext_532': labviewDataDict['ext_532'],
            'ext_std_532': labviewDataDict['ext_std_532'],
            'bsc_355': labviewDataDict['bsc_355'],
            'bsc_std_355': labviewDataDict['bsc_std_355'],
            'bsc_532': labviewDataDict['bsc_532'],
            'bsc_std_532': labviewDataDict['bsc_std_532'],
            'bsc_1064': labviewDataDict['bsc_1064'],
            'bsc_std_1064': labviewDataDict['bsc_std_1064'],
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
            'zenith_angle': labviewInfo['zenith_angle'],
            }

        # setup global attributes
        global_attrs = camp_info

        return dimensions, data, global_attrs

    def __read_labview_data(self, filename):
        '''
        read the labview retrieving data
        '''
        dataMatrix = np.loadtxt(filename, skiprows=1, dtype=float,
                                encoding='cp1252')
        return dataMatrix

    def __read_labview_info(self, filename):
        '''
        read the labview info file, which contains the retrieving information
        '''

        labviewInfo = self.labview_info_parser(filename)

        if not labviewInfo:
            # if failed in retrieving the info
            return None

        # convert the datetime
        labviewInfo['starttime'] = datetime.datetime.strptime(
            labviewInfo['starttime'], '%y%m%d %H%M')
        labviewInfo['endtime'] = datetime.datetime.strptime(
            labviewInfo['endtime'], '%y%m%d %H%M')

        # concatenate reference height
        labviewInfo['reference_height_355'] = np.array(
            [labviewInfo['reference_height_bottom_355'],
             labviewInfo['reference_height_top_355']])
        labviewInfo['reference_height_532'] = np.array(
            [labviewInfo['reference_height_bottom_532'],
             labviewInfo['reference_height_top_532']])
        labviewInfo['reference_height_1064'] = np.array(
            [labviewInfo['reference_height_bottom_1064'],
             labviewInfo['reference_height_top_1064']])

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
                'software_version': labviewInfo['software_version'],
                'starttime': labviewInfo['starttime'],
                'endtime': labviewInfo['endtime'],
                'sounding_type': labviewInfo['sounding_type'],
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
            logger.warning('Labview info file does not exist.\n{infoFile}'.
                           format(infoFile=filename))
            return None

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
                    r'(?<=bis \(UTC\): )\d+.\d+',
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
                    float,
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
                    float,
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
                    float,
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
        with open(filename, 'r', encoding='cp1252') as fh:
            content = fh.read()

        for key, regex in decoders.items():
            val = find_in_string(key, regex, content)
            data.update({key: val})

        # souding_type is still a float number, convert it to integer
        data['sounding_type'] = int(data['sounding_type'])

        # determine the range_resolution (old version labview don't provide it)
        if abs(data['range_resolution'] - 0) <= 1e-9:
            logger.warn('range_resolution is 0 m. Check whether you are ' +
                        'old version labview program. We will change the ' +
                        'range_resolution to 30 m for the converison.')
            data['range_resolution'] = 30

        return data

    def __read_picasso_results(self):
        data = []
        return data

    def write_to_earlinet_nc(self, variables, dimensions, global_attri):
        '''
        write the variables, dimensions and global_attri to EARLINET files.
        Examples can be found in 'include'
        '''

        force = self.force

        if (not variables) or (not dimensions) or (not global_attri):
            return

        # determine whether the output directory exists or not
        if not os.path.exists(self.outputDir):
            logger.warning('Output directory for saving the results does' +
                           'not exist.\n{path}'.format(path=self.outputDir))
            # prompt up the request for creating the output directory
            res = input("Create the folder forcefully? (yes|no): ")
            if res.lower() == 'yes':
                os.mkdir(self.outputDir)

        # write to b355
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b355|e355}.nc
        file_b355 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_b355.nc'.
            format(date=datetime.datetime.
                   utcfromtimestamp(variables['time']).
                   strftime('%Y%m%d_%H%M'),
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
            'error_particledepolarization':
                variables['pdr_std_355'],
            'error_retrieval_method':
                variables['error_retrieval_method'],
            'error_volumedepolarization':
                variables['vdr_std_355'],
            'latitude':
                variables['latitude'],
            'longitude':
                variables['longitude'],
            'particledepolarization':
                variables['pdr_355'],
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
                variables['vdr_355'],
            'wavelength':
                355,
            'zenith_angle':
                variables['zenith_angle']
        }
        dim_b355 = dimensions
        global_attri_b355 = global_attri
        logger.info('Writing data to {file}'.format(file=file_b355))
        self.__write_2_earlinet_nc(file_b355, var_b355, dim_b355,
                                   global_attri_b355, force)

        # write to e355
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b355|e355}.nc
        file_e355 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_e355.nc'.
            format(date=datetime.datetime.
                   utcfromtimestamp(variables['time']).
                   strftime('%Y%m%d_%H%M'),
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
                variables['ext_355'],
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
                                   global_attri_e355, force)

        # write to b532
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b532|e532}.nc
        file_b532 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_b532.nc'.
            format(date=datetime.datetime.
                   utcfromtimestamp(variables['time']).
                   strftime('%Y%m%d_%H%M'),
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
                                   global_attri_b532, force)

        # write to e532
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b532|e532}.nc
        file_e532 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_e532.nc'.
            format(date=datetime.datetime.
                   utcfromtimestamp(variables['time']).
                   strftime('%Y%m%d_%H%M'),
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
                variables['ext_532'],
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
                                   global_attri_e532, force)

        # write to b1064
        # Up till now, I didn't find naming conventions for the nc files.
        # according to the emails, the filename can be handled by the webpage
        # Therefore, I just give it an arbitrary style with
        #
        # yyyymmdd_HHMM_{station_ID}_{instrument}_{b1064}.nc
        file_b1064 = os.path.join(
            self.outputDir,
            '{date}_{station_ID}_{instrument}_b1064.nc'.
            format(date=datetime.datetime.
                   utcfromtimestamp(variables['time']).
                   strftime('%Y%m%d_%H%M'),
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
                                   global_attri_b1064, force)

    def __write_2_earlinet_nc(self, filename, variables, dimensions,
                              global_attri, force):
        '''
        write to EARLINET nc file. Example can be found in 'include'
        '''

        # whether overwrite the file if it exists
        if (os.path.exists(filename)) and \
           (os.path.isfile(filename)) and (not force):
            logger.warning('{file} exists. Jump over!'.format(file=filename))
            return

        elif (os.path.exists(filename)) and \
             (os.path.isfile(filename)) and force:
            logger.warning('{file} exists. Overwrite it!'.
                           format(file=filename))

        if not variables:
            # no available data
            return

        dataset = Dataset(filename, 'w', format=NETCDF_FORMAT, zlib=True)

        # create dimensions
        for dim_key in self.metadata['dimensions']:
            dataset.createDimension(dim_key, dimensions[dim_key])

        # create and write variables, write variable attributes
        npTypeDict = {
            'byte': np.byte,
            'int': np.intc,
            'float': np.single,
            'double': np.double
        }
        for var_key in variables:
            # create variable
            if ('_FillValue' in self.metadata[var_key]):
                # with fill_values
                dataset.createVariable(
                    var_key,
                    npTypeDict[self.metadata[var_key]['dtype']],
                    tuple(self.metadata[var_key]['dims']),
                    fill_value=self.metadata[var_key]['_FillValue']
                )
            else:
                # without fill_values
                dataset.createVariable(
                    var_key,
                    npTypeDict[self.metadata[var_key]['dtype']],
                    tuple(self.metadata[var_key]['dims'])
                    )

            # write variables
            dataset.variables[var_key][:] = variables[var_key]

            # write attributes
            for var_attr in self.metadata[var_key]:
                if (not var_attr == 'dtype') and \
                   (not var_attr == 'dims') and \
                   (not var_attr == '_FillValue'):
                    setattr(
                        dataset.variables[var_key],
                        var_attr,
                        self.metadata[var_key][var_attr]
                        )

        # create global attributes
        for attr_key in self.camp_info:
            setattr(dataset, attr_key, self.camp_info[attr_key])

        # write system, measurement_start_datetime and
        # measurement_stop_datetime to global attributes
        camp_info_file_base = os.path.basename(self.camp_info_file)
        camp_info_filename = os.path.splitext(camp_info_file_base)[0]
        system_label = self.campaign_dict[camp_info_filename]['system']
        starttime = datetime.datetime.fromtimestamp(
                        variables['time_bounds'][0]
                    )
        endtime = datetime.datetime.fromtimestamp(
                        variables['time_bounds'][1]
                    )
        setattr(dataset, 'system', system_label)
        setattr(dataset, 'measurement_start_datetime',
                starttime.strftime('%Y-%m-%dT%H:%M:%SZ'))
        setattr(dataset, 'measurement_stop_datetime',
                endtime.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # write location to global attributes
        city = system_label = \
            self.campaign_dict[camp_info_filename]['location']
        country = system_label = \
            self.campaign_dict[camp_info_filename]['country']
        loc_string = "{city}, {country}".format(city=city, country=country)
        setattr(dataset, 'location', loc_string)

        # write history to global attributes
        historyStr = "{process_time}: {program_name}".format(
                     process_time=starttime.strftime('%Y-%m-%dT%H:%M:%SZ'),
                     program_name=self.camp_info['processor_name']
                  )
        setattr(dataset, 'history', historyStr)

        dataset.close()


class ArgumentParser(argparse.ArgumentParser):
    """
    Override the error message for argparse.

    reference
    ---------
    https://stackoverflow.com/questions/5943249/python-argparse-and-controlling-overriding-the-exit-status-code/5943381
    """

    def _get_action_from_name(self, name):
        """Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is
        passed as it's first arg...
        """
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        exc = sys.exc_info()[1]
        if exc:
            exc.argument = self._get_action_from_name(exc.argument_name)
            raise exc
        super(ArgumentParser, self).error(message)


def show_list(flagShowCampaign=False,
              flagShowInstrument=False,
              flagShowAll=False):
    '''
    print the campaign and instrument list
    '''

    # initialize the instance
    p2eConvertor = polly_earlinet_convertor()
    camp_dict = p2eConvertor.campaign_dict

    # print the full list
    if flagShowAll:
        for indx, camp_info_key in enumerate(camp_dict):
            logger.info(
                '{indx}: {starttime}-{endtime} {location} {instrument}'.
                format(
                    indx=indx + 1,
                    starttime=camp_dict[camp_info_key]['starttime'].
                    strftime('%Y-%m-%d'),
                    endtime=camp_dict[camp_info_key]['endtime'].
                    strftime('%Y-%m-%d'),
                    location=camp_dict[camp_info_key]['location'],
                    instrument=camp_dict[camp_info_key]['system']
                        ))

    # print the campaign list
    if flagShowCampaign:
        for indx, location in enumerate(p2eConvertor.location_list):
            logger.info('{indx}: {location}'.
                        format(indx=indx + 1, location=location))

    # print the instrument list
    if flagShowInstrument:
        for indx, instrument in enumerate(p2eConvertor.instrument_list):
            logger.info('{indx}: {instrument}'.
                        format(indx=indx + 1, instrument=instrument))


def p2e_go(polly_type, location, file_type, category, filename, output_dir,
           camp_info, force):
    '''
    convert the polly files according to the input information

    parameters
    ----------
    polly_type: str
    the name of the running instrument. see the full list in `doc\pollyType.md`

    location: str
    the location for the measurements. The naming should be included in
    `config\campaign_list.toml`.

    file_type: str
    the type of the results that you need to convert. (`labview` or `picasso`)

    category: integer
    the category of your measurements.               
    1: cirrus; 2:climatol; 4:dicycles; 8:etna; 16:forfires;
    32:photosmog; 64:rurban; 128:sahadust; 256:stratos;
    512:satellite_overpasses

    filename: str
    the path of your results. (wildcards are supported.)

    output_dir: str
    the directory for saving the converted netCDF files.

    camp_info: str
    filename of the campaigin configuration file.
    (only the filename is necessary)

    force: boolean
    flag to control whether to override the previous results. (default: false)
    '''

    p2e_convertor = polly_earlinet_convertor(polly_type, location,
                                             fileType=file_type,
                                             category=category,
                                             output_dir=output_dir,
                                             camp_info_file=camp_info,
                                             force=force)

    # search files
    filePath = os.path.dirname(filename)
    file = os.path.basename(filename)
    fileLists = p2e_convertor.search_data_files(file, filepath=filePath)

    # convert all the files
    for task in fileLists:
        dims, data, global_attrs = p2e_convertor.read_data_file(task)
        p2e_convertor.write_to_earlinet_nc(data, dims, global_attrs)


def main():

    # Define the command line arguments.
    description = 'convert the polly profiles from labview program to ' + \
                  'EARLINET format'
    parser = ArgumentParser(prog='p2e_go', description=description)

    # Setup the arguments
    parser.add_argument("-p", "--polly_type",
                        help="setup the instrument type",
                        dest='polly_type',
                        default='pollyxt_tjk')
    parser.add_argument("-l", "--location",
                        help="setup the campaign location",
                        dest='location',
                        default='dushanbe')
    helpMsg = "setup the type of the profile (labview | picasso)"
    parser.add_argument("-t", "--file_type",
                        help=helpMsg,
                        dest='file_type',
                        default='labview')
    helpMsg = "setup the category of the profile\n" + \
              "flag_masks: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512\n" + \
              "flag_meanings: cirrus climatol dicycles etna forfires " + \
              "photosmog rurban sahadust stratos satellite_overpasses"
    parser.add_argument("-c", "--category",
                        help=helpMsg,
                        dest='category',
                        default='2',
                        type=int)
    parser.add_argument("-f", "--filename",
                        help='setup the filename of the polly profile',
                        dest='filename',
                        default='')
    parser.add_argument("-d", "--output_dir",
                        help='setup the directory for the converted files',
                        dest='output_dir',
                        default='')
    helpMsg = 'setup the campaign info file [*.toml].\n' + \
              'If not set, the program will search the config folder for ' + \
              'a suitable one.'
    parser.add_argument("--camp_info",
                        help=helpMsg,
                        dest='camp_info',
                        default='')
    parser.add_argument("--force",
                        help='whether to overwrite the nc files ' +
                             'if they exists',
                        dest='force',
                        action='store_true')

    # sub argument
    helpMsg = "list supported campaign and instruments."
    subparsers = parser.add_subparsers(dest='list', help=helpMsg)

    list_parser = subparsers.add_parser("list", help=helpMsg)

    list_parser.add_argument("--campaign",
                             help="show the supported campaign list",
                             dest='flagShowCampaign',
                             action='store_true')
    list_parser.add_argument("--instrument",
                             help="show the supported instrument list",
                             dest='flagShowInstrument',
                             action='store_true')
    list_parser.add_argument("--all",
                             help="show the full campaign list",
                             dest='flagShowAll',
                             action='store_true')
    # if no input arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        # error info can be obtained by using e.argument_name and e.message
        logger.error('Error in parsing the input arguments. Please check ' +
                     'your inputs.\n{message}'.format(message=e.message))
        raise ValueError

    if args.list:
        show_list(
                  args.flagShowCampaign,
                  args.flagShowInstrument,
                  args.flagShowAll
                  )
    else:
        # run the command
        p2e_go(args.polly_type, args.location, args.file_type,
               args.category, args.filename, args.output_dir,
               args.camp_info, args.force)


# When running through terminal
if __name__ == '__main__':
    main()
