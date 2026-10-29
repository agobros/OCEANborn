import os
import json
import shutil
import subprocess
import hashlib
import math
import warnings
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Optional, Union
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import is_color_like
from cycler import cycler
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class Plotter:
    _LIVE_STYLE_ATTRIBUTES = {
        "font_name",
        "font_family",
        "lw",
        "ms",
        "label_size",
        "fs",
        "dpi",
    }

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if (
            name in self._LIVE_STYLE_ATTRIBUTES
            and self.__dict__.get("_style_ready", False)
        ):
            self._apply_matplotlib_settings()

    def __init__(
        self,
        use_latex: bool = False,
        save_formats: Union[str, Sequence[str]] = ("png",),
    ):

        self._style_ready = False
        self.save_formats = save_formats
        self._fig: Optional[Figure] = None
        self._context_figures: Optional[set[int]] = None

        # Basic properties
        self.font_name = 'Arial'
        self.font_family = 'sans-serif'
        self.lw = 1.2
        self.ms = 2.4
        self.label_size = 9
        self.fs = 8

        # Matplotlib colors
        self._init_colors()

        # A6 landscape (148 x 105 mm), in inches.
        self.figsize = (148 / 25.4, 105 / 25.4)
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
        self.use_latex = use_latex
        self._style_ready = True

    def __str__(self) -> str:
        return (
            'The OCEANborn plotter sets matplotlib.rcparams.\n'
            'self.savefig(fn="") saves your figure in save_formats (PNG by default).\n'
            'If save_dict and/or save_txt are set, they are saved alongside.'
        )

    # --------------------------------------------------------------------------
    # CONTEXT MANAGER SUPPORT
    # --------------------------------------------------------------------------

    def __enter__(self):
        """Create a clean figure while preserving figures opened beforehand."""
        if self._context_figures is not None:
            raise RuntimeError("A Plotter context manager cannot be re-entered")
        self.reset()
        self._context_figures = set(plt.get_fignums())
        self._fig = plt.figure()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close figures created in the context without suppressing exceptions."""
        try:
            for figure_number in plt.get_fignums():
                if figure_number not in self._context_figures:
                    plt.close(figure_number)
        finally:
            self.reset()
            self._context_figures = None
        return False   # Do not suppress exceptions

    # --------------------------------------------------------------------------

    @property
    def fig(self) -> Figure:
        if self._fig is None or not plt.fignum_exists(self._fig.number):
            self._fig = plt.gcf()
        return self._fig

    @property
    def ax(self) -> Axes:
        return self.fig.gca()

    @property
    def figsize(self) -> tuple[float, float]:
        return self._figsize

    @figsize.setter
    def figsize(self, size: Sequence[float]):
        if isinstance(size, str) or not isinstance(size, Sequence) or len(size) != 2:
            raise TypeError("figsize must be a sequence of two positive numbers")
        if any(
            isinstance(dimension, bool)
            or not isinstance(dimension, (int, float))
            or not math.isfinite(dimension)
            or dimension <= 0
            for dimension in size
        ):
            raise ValueError("figsize dimensions must be finite positive numbers")
        self._figsize = (float(size[0]), float(size[1]))
        if self.__dict__.get("_style_ready", False):
            self._apply_matplotlib_settings()

    @property
    def legend_params(self) -> Mapping[str, Union[bool, float]]:
        return MappingProxyType(self._legend_params)

    @legend_params.setter
    def legend_params(self, params: Mapping[str, Union[bool, float]]):
        if not isinstance(params, Mapping):
            raise TypeError("legend_params must be a mapping")
        expected = {"labelspacing", "frameon", "handlelength"}
        if set(params) != expected:
            raise ValueError(f"legend_params must contain exactly {sorted(expected)}")
        if not isinstance(params["frameon"], bool):
            raise TypeError("legend_params['frameon'] must be bool")
        for key in ("labelspacing", "handlelength"):
            value = params[key]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise ValueError(f"legend_params[{key!r}] must be a finite non-negative number")
        self._legend_params = dict(params)
        if self.__dict__.get("_style_ready", False):
            self._apply_matplotlib_settings()

    @property
    def greys(self) -> list[str]:
        return self.colors["greys"]

    @property
    def vline_color(self) -> str:
        return self.colors["vline"]

    @property
    def hline_color(self) -> str:
        return self.colors["hline"]

    @property
    def color_palette(self) -> list[str]:
        return list(self.colors["cycler"])

    @property
    def cycler(self) -> list[str]:
        return list(self.colors["cycler"])

    @color_palette.setter
    def color_palette(self, colors: Sequence[str]):
        if isinstance(colors, str) or not isinstance(colors, Sequence):
            raise TypeError("color_palette must be a sequence of color values")
        if not colors:
            raise ValueError("color_palette must contain at least one color")
        if not all(isinstance(color, str) and is_color_like(color) for color in colors):
            raise ValueError("color_palette entries must be valid Matplotlib colors")
        self.colors["cycler"] = list(colors)
        self.custom_cycler = cycler(color=self.colors["cycler"])
        if hasattr(self, "_use_latex"):
            self._apply_matplotlib_settings()

    @property
    def save_formats(self) -> tuple[str, ...]:
        return self._save_formats

    @save_formats.setter
    def save_formats(self, formats: Union[str, Sequence[str]]):
        if isinstance(formats, str):
            formats = (formats,)
        elif not isinstance(formats, Sequence):
            raise TypeError("save_formats must be a format name or a sequence of names")

        normalized = []
        for value in formats:
            if not isinstance(value, str):
                raise TypeError("each save format must be a string")
            extension = value.strip().lstrip(".").lower()
            if not extension or any(char in extension for char in '\\/:*?"<>|'):
                raise ValueError(f"save_formats contains an invalid format: {value!r}")
            normalized.append(extension)

        if not normalized:
            raise ValueError("save_formats must contain at least one format")
        self._save_formats = tuple(dict.fromkeys(normalized))

    @property
    def use_latex(self) -> bool:
        return self._use_latex

    @use_latex.setter
    def use_latex(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError(f'use_latex must be bool, not {type(value)}')
        if value and not self.is_latex_installed():
            warnings.warn(
                "LaTeX was requested but pdflatex is unavailable; using Matplotlib mathtext.",
                RuntimeWarning,
                stacklevel=2,
            )
            value = False
        self._use_latex = value
        self._apply_matplotlib_settings()

    # --------------------------------------------------------------------------

    def _init_colors(self):
        self.colors = {
            "cycler": [
                "#0077BB", "#EE7733", "#009988", "#CC3311",
                "#AA4499", "#33BBEE", "#882255", "#228833"
            ],
            "vline": "#E7D27C",
            "hline": "#CC9999",
            "greys": [
                "#F5F5F5", "#DCDCDC", "#D3D3D3", "#C0C0C0", "#A9A9A9",
                "#808080", "#696969", "#778899", "#708090", "#2F4F4F",
                "#343434", "#36454F", "#353839", "#000000"
            ],
        }
        self.markers = (
            "o", "s", "^", "v", "D", "*", "p", "X", "+", "x",
            "<", ">", "1", "2", "3", "4", "|", "_",
        )
        self.custom_cycler = cycler(color=self.colors["cycler"])

    # --------------------------------------------------------------------------

    def genfig(self, *args, **kwargs):
        """Convenience wrapper for plt.subplots()."""
        self._fig, ax = plt.subplots(*args, **kwargs)
        return self._fig, ax

    # --------------------------------------------------------------------------

    def savefig(self, fn: str = ''):
        if (
            (self._fig is None or not plt.fignum_exists(self._fig.number))
            and not plt.get_fignums()
        ):
            raise RuntimeError(
                "No figure is available to save; create one with genfig() or pyplot first."
            )
        fig = self.fig

        # Add figure ID if present
        if self.fig_id:
            fig.text(
                1., 0., self.fig_id,
                ha='right', va='bottom',
                fontsize=self.id_fontsize,
                transform=fig.transFigure
            )

        # Determine filename
        if not fn:
            fn_base = "new_plot"
            counter = 0
            extensions = [ext.lstrip(".") for ext in self.save_formats]
            if self.save_txt:
                extensions.append("txt")
            if self.save_dict:
                extensions.append("json")
            while any(
                os.path.exists(
                    os.path.join(self.saving_dir, f"{fn_base}_{counter}.{ext}")
                )
                for ext in extensions
            ):
                counter += 1
            fn = f"{fn_base}_{counter}"

        fn = os.path.basename(os.path.normpath(fn))
        stem, extension = os.path.splitext(fn)
        if extension.lstrip(".").lower() in {*self.save_formats, "json", "txt"}:
            fn = stem
        if not fn:
            raise ValueError("Figure name must not be empty")
        if len(fn) > 60:
            digest = hashlib.sha256(fn.encode("utf-8")).hexdigest()[:12]
            fn = f"{fn[:47]}_{digest}"

        os.makedirs(self.saving_dir, exist_ok=True)
        base = os.path.join(self.saving_dir, fn)

        try:
            if self.save_txt:
                with open(base + ".txt", "w", encoding="utf-8") as f:
                    f.write(self.save_txt)

            if self.save_dict:
                with open(base + ".json", "w", encoding="utf-8") as f:
                    json.dump(self.save_dict, f, indent=4)

            for ext in self.save_formats:
                fig.savefig(f"{base}.{ext.lstrip('.')}")
        finally:
            self.reset()

        if self.print_infos:
            print(f"Figures saved as: {base}")
            print(f"Saved formats: {', '.join(ext.lstrip('.') for ext in self.save_formats)}")

    # --------------------------------------------------------------------------

    def reset(self):
        """Close this plotter's figure and clear optional sidecar data."""
        if self._fig is not None:
            plt.close(self._fig)
            self._fig = None
        self.save_dict = {}
        self.save_txt = ""

    # --------------------------------------------------------------------------

    def _apply_matplotlib_settings(self):
        """Apply all Matplotlib rcParams."""
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
            'font.family': self.font_family,
            'font.size': self.fs,
            'axes.labelsize': self.label_size,
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
        font_list = 'font.serif' if self.font_family == 'serif' else 'font.sans-serif'
        matplotlib.rcParams[font_list] = [self.font_name]

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
        except OSError:
            return False
        

class NaturePlotter(Plotter):
    """
    A Plotter subclass styled according to Nature Publishing Group guidelines.
    """
    def __init__(self, use_latex: bool = False):
        super().__init__(use_latex=use_latex)

        # Nature figure sizes:
        # Single-column width ~89 mm
        self.figsize = (3.5, 3.5)   # in inches (~89mm)
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
    def __init__(self, use_latex: bool = False, two_column: bool = False):
        super().__init__(use_latex=use_latex)

        # IEEE dimensions
        if two_column:
            self.figsize = (7.16, 3.0)  # full-width figure
        else:
            self.figsize = (3.5, 3.0)   # single-column figure

        self.dpi = 600

        # IEEE prefers Times or Times-like font (when LaTeX is used)
        self.font_family = 'serif'
        self.font_name = 'Times New Roman'
        self.fs = 8
        self.lw = 1.2
        self.ms = 3

        self._apply_matplotlib_settings()
        return