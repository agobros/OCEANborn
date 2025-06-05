import os, matplotlib, json, shutil, subprocess, copy
import matplotlib.pyplot as plt 
from cycler import cycler
import matplotlib.cm as cm
from importlib import resources
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from numpy.typing import NDArray
import numpy as np


class Plotter():
    def __init__(self):



        self.font_name = 'Arial'
        self.lw = 1 #linewidth in points

        self.ms = 2.5 #markersize
        self.markers = ['o','v','^','<','>','*','h','D']
        
        self.label_size = 10
        self.fs = 8 #fontsize

        self.get_colors()

        #https://www.nature.com/nature/for-authors/final-submission 
        self.figsize = [3.50394/89*75, 3.50394/89*75]
        self.dpi = 450

        self.legend_params = {
            'labelspacing': 0.2,
            'frameon': False,
            'handlelength': 1.5
        }

        self.use_latex = self.is_latex_installed() #Check if latex is installed and updates params

        self.saving_dir = os.path.join(os.getcwd(), 'figures') #saving directory for figures
        self.save_dict = {} #Will be saved as json in saving folder, if not empty
        self.save_txt = '' #Will be saved as json in saving folder, if not empty

        self.print_infos = True #Bool if infos about saved figures should be printed

    def __str__(self) -> str:
        ret = 'The OCEANborn plotter sets matplotlib.rcparams.'
        ret += '\nIn addition self.savefig(fn: str = "") saves your figure as pdf, svg and png.'
        ret += '\nIf self.save_dict and/or self.save_txt is not empty, these files are also saved in the corresponding folder.'
        return ret

    @property
    def fig(self) -> Figure:
        return plt.gcf()
    
    @property
    def ax(self) -> Axes:
        return plt.gca()
    
    @property
    def use_latex(self) -> bool:
        return self._use_latex
    
    @use_latex.setter
    def use_latex(self, new_val: bool) -> None:
        if isinstance(new_val, bool):
            self._use_latex = new_val
        else:
            raise TypeError(f'Provide a bool for use_latex and not {new_val}!')
        self.update_plt_params()

    def get_colors(self) -> None:        
        self.colors={
                    "cycler": [
                        "#4169E1",
                        "#66CC66",
                        "#fc6600",
                        "#CC0033",
                        "#be29ec",
                        "#ff00a9",
                        "#006600"
                    ],
                    "vline": "#E7D27C",
                    "hline": "#CC9999",
                    "greys": [
                        "#F5F5F5",
                        "#DCDCDC",
                        "#D3D3D3", 
                        "#C0C0C0", 
                        "#A9A9A9", 
                        "#808080", 
                        "#696969", 
                        "#778899", 
                        "#708090", 
                        "#2F4F4F", 
                        "#343434", 
                        "#36454F", 
                        "#353839", 
                        "#000000"]
                    }

        self.color_palette = self.colors['cycler'] #For cycler
        #http://medialab.github.io/iwanthue/
        self.vline_color = self.colors['vline']
        self.hline_color = self.colors['hline']
        self.greys = self.colors['greys']
        self.custom_cycler = (cycler(color=self.color_palette))
        return
    
    def genfig(self, *args, **kwargs) -> tuple:
        fig, ax = plt.subplots(*args, **kwargs)
        return fig, ax

    def savefig(self, fn:str = '') -> None:

        if fn == '':
            counter = 0
            fn = f'new_plot_{counter}'
            if os.path.exists(os.path.join(self.saving_dir, fn)):
                counter += 1
                fn = f'new_plot_{counter}'

        fn = fn.replace('.', '_') #Check for .

        loc_fn = copy.deepcopy(fn)
        name_len_issues = False
        while True:
            final_dir = os.path.join(self.saving_dir, loc_fn)
            try:
                os.makedirs(final_dir, exist_ok=True)
            except FileNotFoundError:
                name_len_issues = True
                if len(loc_fn) > 3:
                    loc_fn = loc_fn[:len(loc_fn)-1]
                else:
                    raise MemoryError(f'Was not able to save the figure as \n{os.path.join(self.saving_dir, fn)} \n(probably due to length restrictions in the name)')
            else:
                if name_len_issues:
                    with open(os.path.join(final_dir, 'info.txt'), 'w') as txt_file:
                        txt_file.write(f'Was not able to save under:\n{os.path.join(self.saving_dir, fn)}\nNew name:\n{final_dir}')
                break

        fn = os.path.join(final_dir, loc_fn)
        if name_len_issues:
            fn = os.path.join(final_dir[:-1],'0')


        if self.save_txt != '':
            with open(fn+'.txt', 'w') as txt_file:
                txt_file.write(self.save_txt)

        if len(self.save_dict.keys()) > 0:
            with open(fn+'.json', 'w') as json_file:
                json.dump(self.save_dict, json_file, indent=4)

        plt.savefig(fn+'.pdf')
        plt.savefig(fn+'.svg')
        plt.savefig(fn+'.png')

        if self.print_infos:
            print(f'Figures saved as: {fn}')

        self.reset()

        pass

    def reset(self):
        '''
        Called after saving a figure
        '''
        plt.close()
        self.save_dict = {}
        self.save_txt = ''

    def update_plt_params(self):

        matplotlib.rcParams.update(matplotlib.rcParamsDefault)

        if not self.is_latex_installed() and self.use_latex:
            print(f'There was no LATEX distribution detected and the suage of LATEX was prevented!')
            self._use_latex = False
        
        if self.use_latex:
            matplotlib.use("Pgf")

            matplotlib.rcParams.update({
            "pgf.texsystem": "pdflatex",
            'text.usetex': True,
            'pgf.rcfonts': True,
            'text.latex.preamble': r"""\usepackage{lmodern, amsmath, amssymb, sfmath, siunitx}
            \sisetup{detect-all}""",    
            "pgf.preamble": r"""
            \usepackage[utf8]{inputenc}
            \usepackage{amsmath, amssymb, lmodern, sfmath, siunitx}  % Use Latin Modern for better symbol support
            \sisetup{detect-all}
            """  # Latin Modern and other math packages
            })
        
        else:
            matplotlib.use("Agg")

        matplotlib.rcParams.update({
            'axes.prop_cycle': self.custom_cycler,
            'font.family': 'sans-serif',
            'font.sans-serif': self.font_name,
            'font.weight': 'normal',
            'font.size': self.fs,
            'mathtext.default': 'regular',
            'mathtext.fontset': 'custom',
            'mathtext.rm': 'sans',
            'xtick.top': True,
            'xtick.minor.visible': True,
            'xtick.direction': 'in',
            'ytick.right': True,
            'ytick.minor.visible': True,
            'ytick.direction': 'in',
            'legend.frameon': self.legend_params['frameon'],
            'legend.labelspacing':  self.legend_params['labelspacing'],
            'legend.handlelength': self.legend_params['handlelength'],
            'legend.fontsize': self.fs,
            'savefig.bbox': 'tight',
            'lines.markersize': self.ms,
            'lines.linewidth': self.lw,
            'errorbar.capsize': 1,
            'figure.figsize': self.figsize,
            'figure.dpi': self.dpi
        })

    @staticmethod
    def is_latex_installed() -> bool:
        latex_path = shutil.which("pdflatex")
        if latex_path is None:
            return False
        try:
            result = subprocess.run(["pdflatex", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
