import pytest, os
from oceanborn import Plotter
import matplotlib.pyplot as plt
import numpy as np

def test_plotter_initialization():
    p = Plotter()
    assert p is not None

def test_id():
    p = Plotter()
    p.fig_id = 'Test ID'
    p.saving_dir = os.path.join('.', 'tests')
    try:
        for idx, marker in enumerate(p.markers):
            x = np.array((range(-10,10)))*10 # type: ignore
            y = [-4*idx+np.sin(i)+np.exp(np.abs(i)*1e-2) for i in x]
            label = f'Marker {idx}'
            plt.plot(x, y,f'--{marker}',label=label)
        plt.legend(loc=7)
        plt.xlim((-100,250))

        plt.xlabel(r'Test xlabel $\si{\micro M/s}$ $\mathrm{\mu\Delta <}$')
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
        plt.legend(loc=7)
        plt.xlim((-100,250))

        plt.xlabel(r'Test xlabel $\mathrm{\mu\Delta <}$')
        plt.ylabel('Test ylabel')


        plt.savefig(os.path.join('.','tests','test_colors.png'), dpi=450)
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
        plt.xlabel(r'Test xlabel $\mathrm{\mu\Delta <}$')
        plt.ylabel('Test ylabel')

        plt.savefig(os.path.join('.','tests','test_greys.png'), dpi=450)
        plt.close()
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_vh_line():
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

        plt.savefig(os.path.join('.','tests','test_vh_lines.png'), dpi=450)
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
        plt.savefig(os.path.join('.','tests','test_sizes.png'), dpi=450)
        plt.close()
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_markers():
    p = Plotter()
    try:
        for idx, marker in enumerate(p.markers):
            x = np.array((range(-10,10)))*10 # type: ignore
            y = [-4*idx+np.sin(i)+np.exp(np.abs(i)*1e-2) for i in x]
            label = f'Marker {idx}'
            plt.plot(x, y,f'--{marker}',label=label)
        plt.legend(loc=7)
        plt.xlim((-100,250))

        plt.xlabel(r'Test xlabel $\si{\micro M/s}$ $\mathrm{\mu\Delta <}$')
        plt.ylabel('Test ylabel')
        
        plt.savefig(os.path.join('.','tests','test_markers.png'), dpi=450)
        plt.close()
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_save_fig():
    p = Plotter()
    p.saving_dir = os.path.join('.', 'tests')
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

        ax.set_xlabel(r'Test xlabel $\mathrm{\mu\Delta <}$')
        ax.set_ylabel('Test ylabel')

        p.savefig(os.path.join('test_self_save_fig'))
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")
    

def test_no_latex():
    p = Plotter()
    p.saving_dir = os.path.join('.', 'tests')
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

        ax.set_xlabel(r'Test xlabel $\mathrm{\mu\Delta <}$')
        ax.set_ylabel('Test ylabel')

        p.savefig(os.path.join('test_no_latex'))
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")

def test_long_name():
    p = Plotter()
    p.saving_dir = os.path.join('.', 'tests')
    try:
        fig, ax = p.genfig()
        ax.plot([0,1], [0,1])
        p.savefig("_".join([str(i) for i in range(1000)]))
    except Exception as e:
        pytest.fail(f"Plot method raised an exception: {e}")
