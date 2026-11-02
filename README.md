# OCEANborn

OCEANborn provides consistent Matplotlib styling and figure-saving helpers for
publication-ready plots.

## Install

OCEANborn requires Python 3.11 or newer.

Create and activate a virtual environment on Windows:

```console
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

In Command Prompt, activate it with `.venv\Scripts\activate.bat` instead. To
install only the package without test dependencies, use:

```console
python -m pip install .
```

## Publish to PyPI

The GitHub Actions workflow at `.github/workflows/publish.yml` tests and builds
the wheel and source distribution, then publishes them when a GitHub Release is
published. Configure a PyPI trusted publisher for project `oceanborn` with:

- Owner: `agobros`
- Repository: `OCEANborn`
- Workflow filename: `publish.yml`
- GitHub environment: `pypi`

Create and publish a GitHub Release for the version declared in `pyproject.toml`
to start the workflow. It runs the tests and builds the distributions before
the separate publishing job receives them. No PyPI API token is needed.

## Quick start

```python
from oceanborn import Plotter

plotter = Plotter(use_latex=False)
fig, ax = plotter.genfig()
ax.plot([0, 1, 2], [0, 1, 4], label="Series")
ax.legend()
plotter.savefig("example")
```

Figures are saved directly in `plotter.saving_dir` (by default, `figures/`).
The output formats default to PNG and can be set with a single format name or
a sequence, for example `Plotter(save_formats=("png", "pdf"))`. To save
additional JSON or text beside the plot, set `plotter.save_dict` or
`plotter.save_txt` before calling `savefig`. Named saves overwrite matching
files; omitting the name chooses an unused `new_plot_N` name.

`savefig()` prefers a figure created by `plotter.genfig()` and otherwise saves
the current pyplot figure. It closes the saved figure afterward. The context
manager starts with a fresh current figure and closes figures created inside
the block while preserving figures that were already open.

`Plotter` applies its Matplotlib style globally. LaTeX is disabled by default;
set `use_latex=True` to request it when you have a working LaTeX installation.
If `pdflatex` is absent, OCEANborn warns and uses Matplotlib mathtext. Errors
during LaTeX rendering (for example, missing TeX packages) propagate to the
caller.
`NaturePlotter` and `IEEEPlotter` are available from the package root for
journal-oriented defaults. Assigning style attributes such as `fs`, `lw`,
`figsize`, `font_name`, or `font_family` immediately updates Matplotlib's
global settings. `figsize` and `legend_params` are immutable when read; assign
the full tuple or mapping to change them.

## Colors and markers

The default categorical color cycle is:

| Order | Color | Hex |
|---:|---|---|
| 1 | Blue | `#1f78b4` |
| 2 | Green | `#1b9e26` |
| 3 | Orange-red | `#d93f02` |
| 4 | Purple | `#ae42ec` |
| 5 | Magenta | `#e7298a` |
| 6 | Ochre | `#e6ab02` |
| 7 | Brown | `#b4670f` |
| 8 | Dark green | `#1A683D` |

Reference lines use dark purple (`#542788`) for vertical lines and dark brown
(`#6B4423`) for horizontal lines. The palette is for categorical series, not
continuous data, and color alone should not be the only way important data is
encoded. Use `plotter.color_palette` to inspect or replace the cycle,
`plotter.greys` for neutral shades, and `plotter.markers` for the suggested
marker cycle.
