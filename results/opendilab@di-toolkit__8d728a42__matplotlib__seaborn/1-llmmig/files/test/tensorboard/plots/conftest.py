import seaborn as sns
import pytest


@pytest.fixture(scope='module', autouse=True)
def clear_previous_plot():
    sns.plt.cla()

