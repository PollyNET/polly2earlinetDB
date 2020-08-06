import numpy as np
import os, fnmatch

import datetime
import math
from netCDF4 import Dataset
import shutil

name = 0
dict_pro = {}
dict_cloud = {}
RAW_PATH = 'C:\\Users\\baars\\Desktop\\earlient_converter\\eliza_test_data\\new_test_data\\'          # path where you want to store files: profiles, cloudinfo, etc
Data_path = 'C:\\Users\\baars\\Desktop\\earlient_converter\\eliza_test_data\\out\\' # path for the converted files
first_date = datetime.datetime(1970, 1, 1)
names = []
value_no_cloud = 15000

# Create directories to separate different files profiles, cloudinfo, etc
dirName = 'cloud'
try:
    # Create target Directory
    os.mkdir(RAW_PATH + dirName)
    print("Directory " , dirName ,  " Created ")
except FileExistsError:
    print("Directory " , dirName ,  " already exists")

# Create directory
dirName = 'height'
try:
    # Create target Directory
    os.mkdir(RAW_PATH + dirName)
    print("Directory " , dirName ,  " Created ")
except FileExistsError:
    print("Directory " , dirName ,  " already exists")

# Create directory
dirName = 'profiles'
try:
    # Create target Directory
    os.mkdir(RAW_PATH + dirName)
    print("Directory " , dirName ,  " Created ")
except FileExistsError:
    print("Directory " , dirName ,  " already exists")

dirName = 'plots'
try:
    # Create target Directory
    os.mkdir(RAW_PATH + dirName)
    print("Directory " , dirName ,  " Created ")
except FileExistsError:
    print("Directory " , dirName ,  " already exists")
#for file in os.listdir(RAW_PATH + "profiles/"):
 #   try:
  #      s = Dataset(RAW_PATH + "profiles/" + file)
   # except:
    #    continue
    #if "aerBsc_raman_1064" in s.variables or "aerBsc_raman_355" in s.variables or "aerBsc_raman_532" in s.variables :
     #   g = np.array(s.variables["aerBsc_raman_1064"])
      #  print(g)
       # print(np.all([g,np.nan]))
        #if s.variables['aerBsc_raman_532'][:]

        #shutil.copy(RAW_PATH + "profiles/" + file, Data_path  + "data_w_back/")

# copy files from raw-path dir for separation
for file in fnmatch.filter(os.listdir(path=RAW_PATH), '*_cloudinfo.nc'):
    shutil.copy(RAW_PATH + file, RAW_PATH + "cloud\\")
for file in fnmatch.filter(os.listdir(path=RAW_PATH), '*_profiles.nc'):
    if "NR" not in file and "OC"  not in file:
        shutil.copy(RAW_PATH + file, RAW_PATH + "profiles\\")


#creating dictionaries for further comparison between profiles  and cloudinfo files
for name in os.listdir(RAW_PATH + 'profiles\\'):
    #print(name)

    list_names_prof = ["Year", "Month", "Day", "Day_Week", "Location", "a", "b", "c", "Start_time", "End_time", "ext"]


    lst = name.split(sep="_")
    lst2 = name.split(sep="_")[:6]
    for j in range(len(lst)):
        dict1 = {list_names_prof[j]: lst[j]}
        dict_pro.update(dict1)
    for name1 in os.listdir(RAW_PATH + 'cloud\\'):
        d = name1.split(sep="_")[:6]
        #print(d, lst2)
        cloud = name1.split(sep="_")
        if lst2 == d:

            list_names_cloud = ["Year", "Month", "Day", "Day_Week", "Location", "a", "b", "c", "ext"]


            for i in range(len(cloud)):
                dict2 = {list_names_cloud[i]: cloud[i]}
                dict_cloud.update(dict2)

            time_since = datetime.datetime(int(dict_cloud.get("Year")), int(dict_cloud.get("Month")),
                                       int(dict_cloud.get("Day"))) - first_date
            seconds = int(time_since.total_seconds())


            r = Dataset(RAW_PATH + "cloud\\" + name1)
            d = Dataset(RAW_PATH + "profiles\\" + name)
            #print(dict_pro)
            #print(dict_cloud)
           # print("MATCH!", name1)
            low_base = []
            st_time = r.variables['time'][0]
            hour_start = int((st_time - seconds) / 3600)
            min_start = int((st_time - seconds - hour_start * 3600) / 60)
            sec_start = int(st_time - seconds -  hour_start * 3600 - min_start * 60)

            #low base searching
            for i in range(r.dimensions["time"].size):
                #print(int((r.variables["time"][i] - seconds)/3600), int(dict_pro.get("Start_time")[:2]))
                if int((r.variables["time"][i] - seconds)/3600) == int(dict_pro.get("Start_time")[:2]):

                    if math.isnan(r.variables["cloud_base_height"][i][0]):
                        continue
                    else:
                        low_base.append(int(r.variables["cloud_base_height"][i][0]))
            #print(name.split(sep='cloudinfo')[0])

            for i in low_base:
                if i < 1000:
                    low_base.remove(i)
            #print(low_base)

            if len(low_base) == 0:


                break
                #outF.write(str(d.dimensions["height"].size))
                #outF.write("\n")
            else:                     # saving low base values for different text files for bash script
                #print(min(low_base))
                outF = open(
                    Data_path + "height\\ " + name1.split(sep='cloudinfo')[0] + str(dict_pro.get("Start_time")) + "_" + str(
                        dict_pro.get("End_time")) + "_" + "profiles" + ".nc", "w")
                outF.write(str(min(low_base)))
                outF.write("\n")
                outF.close()

