from oceanborn import Plotter
import os

#instantiation of plotter instance sets the matplotlib params globally
ocean_plt=Plotter()

#genfig generates a fig and ax instance similar to plt.subplots with the same args and kwargs
fig, ax = ocean_plt.genfig()

#fig and ax can either be accessed directly or with the class properties
ocean_plt.ax.plot([0,1,1,0,0], [0,0,1,1,0])

#If saved via the method savefig, there exists a possiblity of saving a dict as json
#and a str as txt file if the properties save_dict and save_txt are not empty
ocean_plt.save_dict={'x': 'test'}
ocean_plt.save_txt='0,1\n0,2'

#If saving_dir is set, this dir will be used for saving, otherwise it's save at cwd
ocean_plt.saving_dir = os.getcwd()

#The method savfig takes the figure name as argument, if empty, the figure will have a default name!
ocean_plt.savefig('Test')

#There are shades of grey provided in the class
print(f'Greys: {", ".join(ocean_plt.greys)}')

#There are colors for vlines and hlines provided
print(f'Vline color: {ocean_plt.vline_color}, Hline color: {ocean_plt.hline_color}')

#Enjoy OCEANborn
