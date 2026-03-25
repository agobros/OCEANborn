import os
import json
import shutil
import subprocess
import copy
import matplotlib
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class Plotter:
    def __init__(self, use_latex: bool = True):

        # Basic properties
        self.font_name = 'Arial'
        self.lw = 1
        self.ms = 2.5
        self.label_size = 10
        self.fs = 8

        # Matplotlib colors
        self._init_colors()

        # Nature journal typical figure size
        self.figsize = [3.50394 / 89 * 75, 3.50394 / 89 * 75]
        self.dpi = 450

        self.legend_params = {
            'labelspacing': 0.25,
            'frameon': False,
            'handlelength': 1.5,
        }

        self.saving_dir = os.path.join(os.getcwd(), 'figures')
        self.save_dict = {}
        self.save_txt = ''
        self.fig_id = ''
        self.id_fontsize = 5
        self.print_infos = True

        # LaTeX availability check
        self.use_latex = use_latex and self.is_latex_installed()

    def __str__(self) -> str:
        return (
            'The OCEANborn plotter sets matplotlib.rcparams.\n'
            'self.savefig(fn="") saves your figure as PDF, SVG, PNG.\n'
            'If save_dict and/or save_txt are set, they are saved alongside.'
        )

    # --------------------------------------------------------------------------
    # CONTEXT MANAGER SUPPORT
    # --------------------------------------------------------------------------

    def __enter__(self):
        """Prepare a clean plotting environment."""
        plt.close('all')
        self.reset()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Cleanup after exiting the context block."""
        plt.close('all')
        self.reset()
        return False   # Do not suppress exceptions

    # --------------------------------------------------------------------------

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
    def use_latex(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f'use_latex must be bool, not {type(value)}')
        self._use_latex = value
        self._apply_matplotlib_settings()

    # --------------------------------------------------------------------------

    def _init_colors(self):
        self.colors = {
            "cycler": [
                "#4169E1", "#66CC66", "#fc6600", "#CC0033",
                "#be29ec", "#ff00a9", "#006600"
            ],
            "vline": "#E7D27C",
            "hline": "#CC9999",
            "greys": [
                "#F5F5F5", "#DCDCDC", "#D3D3D3", "#C0C0C0", "#A9A9A9",
                "#808080", "#696969", "#778899", "#708090", "#2F4F4F",
                "#343434", "#36454F", "#353839", "#000000"
            ],
        }

        self.custom_cycler = cycler(color=self.colors["cycler"])

    # --------------------------------------------------------------------------

    def genfig(self, *args, **kwargs):
        """Convenience wrapper for plt.subplots()."""
        return plt.subplots(*args, **kwargs)

    # --------------------------------------------------------------------------

    def savefig(self, fn: str = ''):
        # Add figure ID if present
        if self.fig_id:
            self.fig.text(
                1., 0., self.fig_id,
                ha='right', va='bottom',
                fontsize=self.id_fontsize,
                transform=self.fig.transFigure
            )

        # Determine filename
        if not fn:
            fn_base = "new_plot"
            counter = 0
            while os.path.exists(os.path.join(self.saving_dir, f"{fn_base}_{counter}")):
                counter += 1
            fn = f"{fn_base}_{counter}"

        fn = fn.replace(".", "_")

        # Create folder for figure
        final_dir = os.path.join(self.saving_dir, fn)
        os.makedirs(final_dir, exist_ok=True)

        base = os.path.join(final_dir, fn)

        # Save additional text/json
        if self.save_txt:
            with open(base + ".txt", "w") as f:
                f.write(self.save_txt)

        if self.save_dict:
            with open(base + ".json", "w") as f:
                json.dump(self.save_dict, f, indent=4)

        # Save the figure formats
        for ext in ("pdf", "svg", "png"):
            plt.savefig(f"{base}.{ext}")

        if self.print_infos:
            print(f"Figures saved as: {base}")

        self.reset()

    # --------------------------------------------------------------------------

    def reset(self):
        """Internal reset after saving or context exit."""
        plt.close()
        self.save_dict = {}
        self.save_txt = ""

    # --------------------------------------------------------------------------

    def _apply_matplotlib_settings(self):
        """Apply all Matplotlib rcParams."""
        matplotlib.rcParams.update(matplotlib.rcParamsDefault)

        if self.use_latex:
            matplotlib.rcParams.update({
                "pgf.texsystem": "pdflatex",
                "text.usetex": True,
                "pgf.rcfonts": True,
                "text.latex.preamble": r"\usepackage{lmodern, amsmath, amssymb, sfmath, siunitx}",
            })
        else:
            matplotlib.rcParams["text.usetex"] = False

        matplotlib.rcParams.update({
            'axes.prop_cycle': self.custom_cycler,
            'font.family': 'sans-serif',
            'font.sans-serif': self.font_name,
            'font.size': self.fs,
            'lines.markersize': self.ms,
            'lines.linewidth': self.lw,
            'legend.frameon': self.legend_params['frameon'],
            'legend.labelspacing': self.legend_params['labelspacing'],
            'legend.handlelength': self.legend_params['handlelength'],
            'figure.figsize': self.figsize,
            'figure.dpi': self.dpi,
            'xtick.direction': 'in',
            'ytick.direction': 'in',
            'xtick.top': True,
            'ytick.right': True,
            'xtick.minor.visible': True,
            'ytick.minor.visible': True,
            'savefig.bbox': 'tight',
        })

    # --------------------------------------------------------------------------

    @staticmethod
    def is_latex_installed() -> bool:
        """Check if pdflatex is available."""
        latex = shutil.which("pdflatex")
        if not latex:
            return False
        try:
            result = subprocess.run(
                ["pdflatex", "--version"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False
        

class NaturePlotter(Plotter):
    """
    A Plotter subclass styled according to Nature Publishing Group guidelines.
    """
    def __init__(self, use_latex: bool = True):
        super().__init__(use_latex=use_latex)

        # Nature figure sizes:
        # Single-column width ~89 mm
        self.figsize = [3.5, 3.5]   # in inches (~89mm)
        self.dpi = 600

        # Nature style choices
        self.font_name = 'Arial'
        self.fs = 7
        self.lw = 1
        self.ms = 3

        self._apply_matplotlib_settings()
        return

class IEEEPlotter(Plotter):
    """
    A Plotter subclass styled for IEEE Transactions publications.
    """
    def __init__(self, use_latex: bool = True, two_column: bool = False):
        super().__init__(use_latex=use_latex)

        # IEEE dimensions
        if two_column:
            self.figsize = [7.16, 3.0]  # full-width figure
        else:
            self.figsize = [3.5, 3.0]   # single-column figure

        self.dpi = 600

        # IEEE prefers Times or Times-like font (when LaTeX is used)
        self.font_name = 'Times New Roman'
        self.fs = 8
        self.lw = 1.2
        self.ms = 3

        self._apply_matplotlib_settings()
        return