import pytest, os
import matplotlib
matplotlib.use("Agg")

from oceanborn import IEEEPlotter, Plotter
import matplotlib.pyplot as plt
import numpy as np

def unit_xlabel(use_latex):
    if use_latex:
        return r'Test xlabel $\si{\micro\metre\per\second}$'
    return 'Test xlabel µM/s'

def test_unit_xlabel_uses_siunitx_when_latex_is_enabled():
    assert r"\si{\micro\metre\per\second}" in unit_xlabel(True)
    assert unit_xlabel(False) == "Test xlabel µM/s"

def test_public_plotter_helpers():
    p = Plotter(use_latex=False)
    assert len(p.color_palette) == 8
    assert len(p.greys) > 0
    assert p.vline_color.startswith("#")
    assert p.hline_color.startswith("#")
    assert len(p.markers) > 0

def test_plotter_string_describes_usage_and_current_settings():
    p = Plotter(use_latex=False, save_formats=("png", "pdf"))
    description = str(p)

    assert "Quick start:" in description
    assert "p.genfig(*args, **kwargs)" in description
    assert "p.savefig(name)" in description
    assert "png, pdf" in description
    assert "DPI: 450" in description
    assert "LaTeX is disabled" in description
    assert "p.color_palette" in description

def test_default_figure_size_is_a6_landscape():
    p = Plotter(use_latex=False)
    assert p.figsize == pytest.approx((148 / 25.4, 105 / 25.4))

def test_default_style_dimensions():
    p = Plotter(use_latex=False)
    assert p.label_size == 9
    assert p.lw == 1.2
    assert p.ms == 3
    assert p.id_fontsize == 5

def test_color_palette_updates_rcparams():
    p = Plotter(use_latex=False)
    p.color_palette = ["#123456", "#abcdef"]
    assert p.color_palette == ["#123456", "#abcdef"]
    assert list(plt.rcParams["axes.prop_cycle"].by_key()["color"]) == p.color_palette

def test_style_attributes_update_rcparams():
    p = Plotter(use_latex=False)
    p.lw = 2.25
    p.label_size = 12
    p.font_name = "DejaVu Sans"
    p.figsize = (4, 3)
    p.legend_params = {
        "labelspacing": 0.5,
        "frameon": True,
        "handlelength": 2,
    }

    assert plt.rcParams["lines.linewidth"] == 2.25
    assert plt.rcParams["axes.labelsize"] == 12
    assert plt.rcParams["font.sans-serif"][0] == "DejaVu Sans"
    assert list(plt.rcParams["figure.figsize"]) == [4, 3]
    assert plt.rcParams["legend.frameon"] is True
    assert p.figsize == (4, 3)
    with pytest.raises(TypeError):
        p.figsize[0] = 5
    with pytest.raises(TypeError):
        p.legend_params["frameon"] = False

def test_ieee_plotter_uses_serif_font():
    p = IEEEPlotter(use_latex=False)

    assert p.font_family == "serif"
    assert plt.rcParams["font.family"] == ["serif"]
    assert plt.rcParams["font.serif"][0] == "Times New Roman"

def test_color_palette_getter_returns_copy():
    p = Plotter(use_latex=False)
    palette = p.color_palette
    palette[0] = "#000000"

    assert p.color_palette[0] != "#000000"

def test_color_palette_rejects_invalid_colors():
    p = Plotter(use_latex=False)
    with pytest.raises(ValueError, match="valid Matplotlib colors"):
        p.color_palette = ["not-a-color"]

def test_saving_generated_figure_preserves_other_figures(tmp_path):
    p = Plotter(use_latex=False)
    p.saving_dir = str(tmp_path)
    unrelated_fig = plt.figure()
    fig, ax = p.genfig()
    ax.plot([0, 1], [0, 1])

    p.savefig("generated")

    assert plt.fignum_exists(unrelated_fig.number)
    assert not plt.fignum_exists(fig.number)

def test_savefig_writes_directly_to_saving_dir(tmp_path):
    p = Plotter(use_latex=False)
    p.saving_dir = str(tmp_path)
    p.print_infos = False
    fig, ax = p.genfig()
    ax.plot([0, 1], [1, 0])
    p.save_dict = {"test": "passed"}
    p.save_txt = "saved"

    p.savefig("direct-output")

    assert (tmp_path / "direct-output.png").is_file()
    assert (tmp_path / "direct-output.json").is_file()
    assert (tmp_path / "direct-output.txt").is_file()
    assert not (tmp_path / "direct-output").exists()
    plt.close(fig)

def test_savefig_preserves_dots_in_figure_name(tmp_path):
    p = Plotter(use_latex=False)
    p.saving_dir = str(tmp_path)
    p.print_infos = False

    p.genfig()
    p.savefig("experiment.v1")
    p.genfig()
    p.savefig("explicit-format.png")

    assert (tmp_path / "experiment.v1.png").is_file()
    assert (tmp_path / "explicit-format.png").is_file()

def test_savefig_without_a_figure_raises(monkeypatch):
    p = Plotter(use_latex=False)
    monkeypatch.setattr(plt, "get_fignums", lambda: [])
    monkeypatch.setattr(
        plt,
        "gcf",
        lambda: pytest.fail("savefig must not create a blank figure"),
    )

    with pytest.raises(RuntimeError, match="No figure is available to save"):
        p.savefig("empty")

def test_default_save_format_is_png():
    p = Plotter(use_latex=False)
    assert p.save_formats == ("png",)

def test_save_formats_accept_string_or_sequence():
    assert Plotter(use_latex=False, save_formats="PDF").save_formats == ("pdf",)
    assert Plotter(
        use_latex=False,
        save_formats=[".PNG", "pdf", "png"],
    ).save_formats == ("png", "pdf")

@pytest.mark.parametrize("formats", [(), [], ""])
def test_save_formats_reject_empty_input(formats):
    with pytest.raises(ValueError, match="save_formats"):
        Plotter(use_latex=False, save_formats=formats)

def test_save_formats_reject_non_string_entries():
    with pytest.raises(TypeError, match="each save format"):
        Plotter(use_latex=False, save_formats=("png", 3))

def test_unnamed_saves_choose_unused_names(tmp_path):
    p = Plotter(use_latex=False)
    p.saving_dir = str(tmp_path)
    p.print_infos = False

    p.genfig()
    p.savefig()
    p.genfig()
    p.savefig()

    assert (tmp_path / "new_plot_0.png").is_file()
    assert (tmp_path / "new_plot_1.png").is_file()

def test_context_manager_closes_new_figures_only():
    p = Plotter(use_latex=False)
    existing_fig = plt.figure()

    with p:
        plt.plot([0, 1], [1, 0])
        context_fig = p.fig

    assert plt.fignum_exists(existing_fig.number)
    assert not plt.fignum_exists(context_fig.number)

def test_plotter_initialization():
    p = Plotter()
    assert p is not None

def test_id():
    p = Plotter(use_latex=True)
    p.fig_id = 'Test ID'
    p.saving_dir = os.path.dirname(__file__)
    try:
        for idx, marker in enumerate(p.markers):
            x = np.array((range(-10,10)))*10 # type: ignore
            y = [-4*idx+np.sin(i)+np.exp(np.abs(i)*1e-2) for i in x]
            label = f'Marker {idx}'
            plt.plot(x, y,f'--{marker}',label=label)
        plt.legend(loc=7)
        plt.xlim((-100,250))

        plt.xlabel(unit_xlabel(p.use_latex))
        plt.ylabel('Test ylabel')

        p.savefig('Test_ID')
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")


def test_colors():
    p = Plotter()
    try:
        for color_idx in range(len(p.color_palette)):
            x = np.array((range(-1000,1000)))/10 # type: ignore
            y = [-4*color_idx+np.sin(i)+np.exp(np.abs(i)*1e-2) for i in x]
            plt.plot(x, y ,label=f'Color {color_idx}')
        plt.axvline(0, color=p.colors["vline"], label="Vertical line")
        plt.axhline(0, color=p.colors["hline"], label="Horizontal line")
        plt.legend(loc=7)
        plt.xlim((-100,250))

        plt.xlabel('Test xlabel')
        plt.ylabel('Test ylabel')


        plt.savefig(os.path.join(os.path.dirname(__file__), 'test_colors.png'), dpi=450)
        plt.close()
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_greys():
    p = Plotter()
    try:
        for idx, color in enumerate(p.greys):
            x = np.array((range(-1000,1000)))/10 # type: ignore
            y = [-4*idx+np.sin(i)+np.exp(np.abs(i)*1e-2) for i in x]
            plt.plot(x, y ,label=f'Grey {idx}', color=color)
        plt.legend(loc=7)
        plt.xlim((-100,250))
        plt.xlabel('Test xlabel')
        plt.ylabel('Test ylabel')

        plt.savefig(os.path.join(os.path.dirname(__file__), 'test_greys.png'), dpi=450)
        plt.close()
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_vh_line(tmp_path):
    p = Plotter()
    try:

        plt.axvline(0, -1e3, 1e3 ,label=f'Vline color', color=p.vline_color)
        plt.axhline(0, 0, 1 ,label=f'Hline color', color=p.hline_color)

        for color_idx in range(len(p.color_palette)):
            x = np.array((range(-1000,1000)))/10 # type: ignore
            y = [-4*color_idx+np.sin(i)+np.exp(np.abs(i)*1e-2) for i in x]
            plt.plot(x, y ,label=f'__nolegend__')

        plt.legend(loc=7)
        plt.xlabel(r'Test v and h line')
        plt.ylabel('Test ylabel')

        plt.xlim((-100,250))
        plt.ylim((-25,5))

        plt.savefig(tmp_path / 'test_vh_lines.png', dpi=450)
        plt.close()
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_sizes():
    p = Plotter()
    try:



        plt.plot([-1,1],[-1,1])
        num_points = 10
        plt.plot(np.linspace(-1,1,num_points), np.linspace(1,-1,num_points), 'o')
        plt.plot(np.linspace(0,0,num_points), np.linspace(1,-1,num_points), '--o')
        plt.plot(np.linspace(-1,1,num_points), np.linspace(0,0,num_points), '.')

        plt.xlabel('Test xlabel')
        plt.ylabel('Test ylabel')
        plt.savefig(os.path.join(os.path.dirname(__file__), 'test_sizes.png'), dpi=450)
        plt.close()
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_markers():
    p = Plotter(use_latex=True)
    try:
        for idx, marker in enumerate(p.markers):
            x = np.array((range(-10,10)))*10 # type: ignore
            y = [-4*idx+np.sin(i)+np.exp(np.abs(i)*1e-2) for i in x]
            label = f'Marker {idx}'
            plt.plot(x, y,f'--{marker}',label=label)
        plt.legend(loc=7)
        plt.xlim((-100,250))

        plt.xlabel(unit_xlabel(p.use_latex))
        plt.ylabel('Test ylabel')
        
        plt.savefig(os.path.join(os.path.dirname(__file__), 'test_markers.png'), dpi=450)
        plt.close()
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_save_fig(tmp_path):
    p = Plotter()
    p.saving_dir = str(tmp_path)
    try:
        fig, ax = p.genfig()
        for color_idx in range(len(p.color_palette)):
            x = np.array((range(-1000,1000)))/10 # type: ignore
            y = [-4*color_idx+np.sin(i)+np.exp(np.abs(i)*1e-2) for i in x]
            ax.plot(x, y ,label=f'Color {color_idx}')
        ax.legend(loc=7)
        ax.set_xlim((-100,250))

        p.save_dict = {'test': 'passed'}
        p.save_txt = 'Test passed'

        ax.set_xlabel('Test xlabel')
        ax.set_ylabel('Test ylabel')

        p.savefig(os.path.join('test_self_save_fig'))
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")
    

def test_no_latex():
    p = Plotter()
    p.saving_dir = os.path.dirname(__file__)
    p.use_latex = False
    try:
        fig, ax = p.genfig()
        for color_idx in range(len(p.color_palette)):
            x = np.array((range(-1000,1000)))/10 # type: ignore
            y = [-4*color_idx+np.sin(i)+np.exp(np.abs(i)*1e-2) for i in x]
            ax.plot(x, y ,label=f'Color {color_idx}')
        ax.legend(loc=7)
        ax.set_xlim((-100,250))

        p.save_dict = {'test': 'passed'}
        p.save_txt = 'Test passed'

        ax.set_xlabel('Test xlabel')
        ax.set_ylabel('Test ylabel')

        p.savefig(os.path.join('test_no_latex'))
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_long_name(tmp_path):
    p = Plotter()
    p.saving_dir = str(tmp_path)
    try:
        fig, ax = p.genfig()
        ax.plot([0,1], [0,1])
        p.savefig("_".join([str(i) for i in range(1000)]))
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")
