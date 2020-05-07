import sys
import os
import unittest
import shutil

projectDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmpDir = os.path.join(projectDir, 'data', 'tmp')
sys.path.append(os.path.join(projectDir, 'src'))

from polly_2_earlinet_convertor import *


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print('Start to test polly_2_earlinet_convertor...')
        if not os.path.exists(tmpDir):
            os.mkdir(tmpDir)

    @classmethod
    def tearDownClass(self):
        if os.path.exists(tmpDir):
            shutil.rmtree(tmpDir)

        print('Finish testing polly_2_earlinet_convertor!')

    def setUp(self):
        print("execute setUp")

    def tearDown(self):
        print("execute tearDown")

    def test_find_in_string(self):
        print('---> Test on find_in_string')

        inStr = 'Reference value: 1.000000e-02 [Mm^{-1}*Sr^{-1}]; Reference' +\
                ' search range:   500.00 - 14000.00 [m]; Smoothing window: ' +\
                '4.575000e+02 [m]; Angstroem exponent: 0.90'

        value = find_in_string((
                    r'(?<=Reference search range:......... - )\d+.\d+',
                    float,
                    0
                ), inStr)

        print(value)
        self.assertEqual(value, 14000)

    def test_show_list(self):
        print('---> Test show_list')

        p2eConvertor = polly_earlinet_convertor()
        camp_dict = p2eConvertor.campaign_dict

        self.assertGreater(len(camp_dict), 0)

    def test_search_data_files(self):
        print('---> Test on search_data_file')

        p2eConvertor = polly_earlinet_convertor('arielle', 'leipzig')
        p2eConvertor.fileType = 'labview'

        # test search labview files
        labviewFiles = p2eConvertor.search_data_files(
            'le_*smooth.txt', filepath=os.path.join(projectDir, 'data')
        )
        self.assertEqual(len(labviewFiles), 1)
        self.assertEqual(
            os.path.basename(labviewFiles[0]),
            'le_arielle-20190723_2100-0058-49smooth.txt')

        # test search picasso files
        picassoFiles = p2eConvertor.search_data_files(
            '*TROPOS*profiles.nc', filepath=os.path.join(projectDir, 'data')
        )
        self.assertEqual(len(picassoFiles), 1)
        self.assertEqual(
            os.path.basename(picassoFiles[0]),
            '2020_05_06_Wed_TROPOS_00_00_01_0000_0059_profiles.nc'
        )

    def test_convert_labview_file(self):
        print('---> Test on convert labview file')

        p2eConvertor = polly_earlinet_convertor(
            'arielle', 'leipzig',
            fileType='labview', category=1,
            output_dir=os.path.join(projectDir, 'data', 'tmp'),
            force=True)

        fileLists = p2eConvertor.search_data_files(
            'le_*smooth.txt', filepath=os.path.join(projectDir, 'data')
        )

        for task in fileLists:
            dims, data, global_attris = p2eConvertor.read_data_file(task)

            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='b355')
            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='e355')
            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='b532')
            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='e532')
            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='b1064')

        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20190723_2100_0366_lei_arielle_b355.nc')))
        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20190723_2100_0366_lei_arielle_e355.nc')))
        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20190723_2100_0366_lei_arielle_b532.nc')))
        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20190723_2100_0366_lei_arielle_e532.nc')))
        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20190723_2100_0366_lei_arielle_b1064.nc')))

    def test_convert_picasso_file(self):
        print('---> Test on convert picasso file')

        p2eConvertor = polly_earlinet_convertor(
            'PollyXT_TROPOS', 'leipzig',
            fileType='picasso', category=1,
            output_dir=os.path.join(projectDir, 'data', 'tmp'),
            force=True)

        fileLists = p2eConvertor.search_data_files(
            '*TROPOS*profiles.nc', filepath=os.path.join(projectDir, 'data')
        )

        for task in fileLists:
            dims, data, global_attris = p2eConvertor.read_data_file(task)

            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='b355')
            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='e355')
            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='b532')
            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='e532')
            p2eConvertor.write_to_earlinet_nc(
                data, dims, global_attris,
                range_lim=[0, 15000], prodType='b1064')

        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20200506_0029_0458_lei_pollyxt_tropos_b355.nc')))
        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20200506_0029_0458_lei_pollyxt_tropos_e355.nc')))
        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20200506_0029_0458_lei_pollyxt_tropos_b532.nc')))
        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20200506_0029_0458_lei_pollyxt_tropos_e532.nc')))
        self.assertTrue(os.path.exists(
            os.path.join(
                tmpDir, '20200506_0029_0458_lei_pollyxt_tropos_b1064.nc')))

    def test_list_avail_prodType(self):
        print('---> Test on list_avail_prodType')

        p2eConvertor = polly_earlinet_convertor(
            'PollyXT_TROPOS', 'leipzig',
            fileType='picasso', category=1,
            output_dir=os.path.join(projectDir, 'data', 'tmp'),
            force=True)

        fileLists = p2eConvertor.search_data_files(
            '*TROPOS*profiles.nc', filepath=os.path.join(projectDir, 'data')
        )

        dims, data, global_attris = p2eConvertor.read_data_file(fileLists[0])
        availProds = p2eConvertor.list_avail_prodType(data)

        self.assertListEqual(
            availProds,
            ['b355', 'e355', 'b532', 'e532', 'b1064'])


def main():

    suite = unittest.TestSuite()

    tests = [
        Test('test_find_in_string')
        ]   # setup the test list
    suite.addTests(tests)

    # print the test report as html file
    # with open('HTMLReport.html', 'w') as f:
    #     runner = HTMLTestRunner(stream=f,
    #                             title='MathFunc Test Report',
    #                             description='generated by HTMLTestRunner.',
    #                             verbosity=2
    #                             )
    #     runner.run(suite)

    # print the test report to the console
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == '__main__':
    main()
