import os, matplotlib
import matplotlib.pyplot as plt 
from cycler import cycler
import matplotlib.cm as cm


import json
import importlib.resources as pkg_resources
from oceanborn import _lib

with pkg_resources.open_text(_lib, "secret.json") as f:
    data = json.load(f)

print(data)

class Plotter():
    def __init__(self):
        self.font_name = 'Arial'
        self.linewidth = 0.5
        self.label_size = 10

        self.small_linewidth = 0.3
        self.font_size = 9

        self.color_palette = ['#4169E1', #royal blue4169E1
        "#66CC66", #green
        '#fc6600', #orange 
        '#CC0033', #red
        '#be29ec', #purple
        '#ff00a9', #pink
        '#006600'] #dark green

        #http://medialab.github.io/iwanthue/
        self.vline_color = '#E7D27C'
        self.vline_color_rgb = [231, 210, 124]
        self.vline_color_rgb = [i/255 for i in self.vline_color_rgb]

        self.hline_color = '#CC9999'
        self.hline_color_rgb = [204, 153, 153]
        self.hline_color_rgb = [i/255 for i in self.hline_color_rgb]

        self.grey = '#C0C0C0'
        self.custom_cycler = (cycler(color=self.color_palette))

        matplotlib.use("pgf")
        #print(matplotlib.rcParams.keys())
        
        # A4 dimensions in inches (1 inch = 25.4 mm)
        a4_width = 210 / 25.4
        a4_height = 297 / 25.4

        # Quarter A4 dimensions
        quarter_a4_width = a4_width / 3 #/2 seems too big
        quarter_a4_height = a4_height / 3

        self.figsize=(quarter_a4_height,quarter_a4_width)
        self.update_plt_params()
    
    def save_fig(self, saving_folder: str = '', fn:str = '', txt_str: str = ''):
        
        if saving_folder == '':
            saving_folder = os.path.join(os.getcwd(), 'Plots')
        if fn == '':
            fn = 'new_plot'

        final_dir = os.path.join(saving_folder, fn)
        try:
            os.makedirs(final_dir, exist_ok=True)

        except FileNotFoundError:
            counter = 0
            final_dir = os.path.join(saving_folder, f'counter_{counter}')
            while os.path.exists(fn):
                counter += 1
                final_dir = os.path.join(saving_folder, f'counter_{counter}')

            os.makedirs(final_dir, exist_ok=True)
            with open(os.path.join(final_dir, 'info.txt'), 'w') as txt_file:
                txt_file.write(f'Was not able to save under:\n{os.path.join(saving_folder, fn)}')

        fn = os.path.join(final_dir, fn.replace('.', '_'))
        try:
            plt.savefig(fn+'.pdf')
            plt.savefig(fn+'.svg')
            plt.savefig(fn+'.png', dpi=450)
        except RuntimeError:
            self.disable_latex()
            plt.savefig(fn+'.pdf')
            plt.savefig(fn+'.svg')
            plt.savefig(fn+'.png', dpi=450)
        except FileNotFoundError:
            counter = 0
            fn = os.path.join(final_dir, f'counter_{counter}')
            while os.path.exists(fn):
                counter += 1
                fn = os.path.join(final_dir, f'counter_{counter}')

            plt.savefig(fn+'.pdf')
            plt.savefig(fn+'.svg')
            plt.savefig(fn+'.png', dpi=450)

        if txt_str != '':
            with open(fn+'.txt', 'w') as txt_file:
                txt_file.write(txt_str)

        pass

    def update_plt_params(self):
        matplotlib.use("Pgf")
        matplotlib.rcParams.update({
            'axes.prop_cycle': self.custom_cycler,
            #"pgf.texsystem": "pdflatex",
            'font.family': 'sans-serif',
            'font.sans-serif': self.font_name,
            'font.weight': 'normal',
            'font.size': self.font_size,
            'text.usetex': True,
            #'pgf.rcfonts': True,
            'mathtext.default': 'regular',
            'mathtext.fontset': 'custom',
            'mathtext.rm': 'sans',
            #'text.latex.preamble': r"""\usepackage{lmodern, amsmath, amssymb, sfmath, siunitx}
            #\sisetup{detect-all}""",    
            #"pgf.preamble": r"""
            #\usepackage[utf8]{inputenc}
            #\usepackage{amsmath, amssymb, lmodern, sfmath, siunitx}  % Use Latin Modern for better symbol support
            #\sisetup{detect-all}
            #""",  # Latin Modern and other math packages
            'xtick.top': True,
            'xtick.minor.visible': True,
            'xtick.direction': 'in',
            'ytick.right': True,
            'ytick.minor.visible': True,
            'ytick.direction': 'in',
            'legend.frameon': False,
            'legend.labelspacing':  0.1,
            'legend.fontsize': self.font_size,
            'savefig.bbox': 'tight',
            'lines.markersize': 3,
            'lines.linewidth': self.linewidth,
            'errorbar.capsize': 1,
            'figure.figsize': self.figsize
        })

    def disable_latex(self):


        matplotlib.rcParams.update(matplotlib.rcParamsDefault)
        matplotlib.use("Agg")
        
        matplotlib.rcParams.update({
            'axes.prop_cycle': self.custom_cycler,
            'font.family': 'sans-serif',
            'font.sans-serif': self.font_name,
            'font.weight': 'normal',
            'font.size': self.font_size,
            'text.usetex': False,
            'mathtext.default': 'regular',
            'xtick.top': True,
            'xtick.minor.visible': True,
            'xtick.direction': 'in',
            'ytick.right': True,
            'ytick.minor.visible': True,
            'ytick.direction': 'in',
            'legend.frameon': False,
            'legend.labelspacing': 0.3,
            'savefig.bbox': 'tight',
            'lines.markersize': 3,
            'lines.linewidth': 1.2,
            'errorbar.capsize': 1
        })
        print(f'Diabled Latex')
        pass