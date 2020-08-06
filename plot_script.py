import matplotlib.pyplot as plt
from netCDF4 import Dataset
import os, fnmatch

import numpy as np
RAW_PATH= 'C:\\Users\\baars\\Desktop\\earlient_converter\\test_data\\' #path where the converted file are
Data_path = 'C:\\Users\\baars\\Desktop\\earlient_converter\\eliza_test_data\\out\\'
names = []
dict_back =  {}
dict_hei = {}
dict_ext = {}
dict_rat = {}
dict_dep = {}
dict_vol = {}





for name in fnmatch.filter(os.listdir(path=RAW_PATH), '*.nc'):
    names.append(name)
    backscatter = []
    extinction = []
    volume = []
    lidar_ratio = []
    depol = []
    lidar_ratio = []
    list_ext = []
    list_dep = []
    height = []

    file = Dataset(RAW_PATH + name)
    #height = file.variables["altitude"][:]

# next code is appending .nc variables to lists, also checking if some of vars exost as extinction, etc
    for i in range(file.dimensions["altitude"].size):

        backscatter.append(float(file.variables["backscatter"][0,0,i]))
        height.append(float(file.variables["altitude"][i]))
#        lidar_ratio.append(float(file.variables[""]))
        if "extinction" in file.variables:
            extinction.append(float(file.variables["extinction"][0, 0, i]))
            lidar_ratio.append(float(file.variables["extinction"][0,0,i])/float(file.variables["backscatter"][0, 0, i]))
        if "particledepolarization" in file.variables:
            depol.append(float(file.variables["particledepolarization"][0, 0, i]))
        if "volumedepolarization" in file.variables:
            volume.append(float(file.variables["volumedepolarization"][0, 0, i]))


    # create dictionaries for plotting
    dict_2 = {name.split("_")[-1] : tuple(backscatter)}
    dict_back.update(dict_2)

    dict_4 = {name.split("_")[-1]: tuple(height)}
    dict_hei.update(dict_4)

    dict_1 = {name.split("_")[-1]: tuple(extinction)}
    dict_ext.update(dict_1)

    dict_5 = {name.split("_")[-1]: tuple(lidar_ratio)}
    dict_rat.update(dict_5)

    dict_3 = {name.split("_")[-1]: tuple(depol)}
    dict_dep.update(dict_3)

    dict_6 = {name.split("_")[-1]: tuple(volume)}
    dict_vol.update(dict_6)






# plotting routine from dictionaries

fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
fig.suptitle('Horizontally stacked subplots')


ax1.set_title("Backscatter, 1/(m*sr)")

ax1.plot(dict_back.get("b532.nc"), dict_hei.get("b532.nc"),label="b532", color='red', linestyle='--', linewidth='2')
ax1.plot(dict_back.get("b1064.nc"), dict_hei.get("b1064.nc"), label="b1064",linestyle=':', linewidth='2')
ax1.plot(dict_back.get("b355.nc"), dict_hei.get("b355.nc"), label="b355", linestyle='--', linewidth='2')
ax1.plot(dict_back.get("e355.nc"), dict_hei.get("e355.nc"), label="e355", linestyle=':', linewidth='1')
ax1.plot(dict_back.get("e532.nc"), dict_hei.get("e532.nc"),  label="e532", color='blue',linestyle=':', linewidth='1')
ax1.set_xlim(left=0)
#ax1.set_xticks(rotation=45)
ax1.legend()



ax2.set_title("Extinction, 1/m")

ax2.plot(dict_ext.get("e355.nc"), dict_hei.get("e355.nc"), label="e355")
ax2.plot(dict_ext.get("e532.nc"), dict_hei.get("e532.nc"), label="e532" )
ax2.set_xlim(left=0)
ax2.legend()




for i in dict_dep:
    if len(dict_dep.get(i)) != 0 and all(dict_dep.get(i))!="nan":
        ax3.plot(dict_dep.get(i), dict_hei.get(i), label="particledepol" + "_" +  i)
        ax3.plot(dict_vol.get(i), dict_hei.get(i), label="volumedepol" +"_" + i)
        ax3.set_title("Particle/Volume depolarization")
        #ax3.set_xlim(0,0.5)
ax3.legend()

for i in dict_rat:
    if len(dict_rat.get(i)) != 0 and all(dict_rat.get(i))!="nan":
        ax4.plot(dict_rat.get(i), dict_hei.get(i), label=i)
        ax4.set_title("Lidar Ratio")
        ax4.set_xlim(0,250)
        #ax4.set_xticks(rotation=45)
ax4.legend()

fig = plt.gcf()
#plt.gca().set_xlim(left=0)
fig.autofmt_xdate(rotation=45)
fig.set_size_inches((15, 11), forward=False)
fig.savefig(Data_path + name +'.png', dpi=500)

plt.close()


