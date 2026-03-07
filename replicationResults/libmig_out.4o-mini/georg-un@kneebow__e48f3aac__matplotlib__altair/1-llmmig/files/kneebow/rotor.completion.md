### Explanation of Changes

To migrate the code from using `matplotlib` to `altair`, the following changes were made:

1. **Import Statement**: The import for `matplotlib.pyplot` was removed and replaced with an import for `altair`.
2. **Plotting Functions**: The `plot_elbow` and `plot_knee` methods were modified to create Altair charts instead of using `plt.scatter` and `plt.vlines`. 
   - Instead of creating scatter plots and vertical lines, we create a `Chart` object in Altair and use `mark_point` for the scatter points and `mark_rule` for the vertical line indicating the elbow or knee.
3. **Data Handling**: Altair requires data to be in a specific format (usually a Pandas DataFrame), so the data was converted to a DataFrame before plotting.

Here is the modified code:

```python
import numpy as np
import altair as alt
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class Rotor:

    def __init__(self):
        """
        Rotor. Find the elbow or knee of a 2d array.

        The algorithm rotates the curve so that the slope from min to max is zero. Subsequently, it takes the min value
        for the elbow or the max value for the knee.

        """
        self._data = None
        self._scale = None
        self._scaler = None
        self._theta = None

    def fit_rotate(self, data, scale=True, theta=None):
        """
        Take a 2d array, scale it and rotate it so that the slope from min to max is zero.

        :param data:    2d numpy array. The data to rotate.
        :param scale:   boolean. True if data should be scaled before rotation (highly recommended)
        :param theta:   float or None. Angle of rotation in radians. If None the angle is calculated from min & max
        """
        self._data = data
        self._scale = scale
        self._theta = theta
        if scale:
            self._scaler = MinMaxScaler()
            self._data = self._scaler.fit_transform(self._data)
        if theta is not None:
            self._theta = theta
        else:
            self._set_theta_auto()
        self._data = self.rotate_vector(self._data, self._theta)

    def get_elbow_index(self):
        """
        Return the index of the elbow of the curve.

        :return:  integer. Index of the elbow.
        """
        # only uses y values to calc min
        return np.where(self._data[:, 1] == self._data[:, 1].min())[0][0]

    def get_knee_index(self):
        """
        Return the index of the knee of the curve.

        :return:  integer. Index of the knee.
        """
        # only uses y values to calc max
        return np.where(self._data[:, 1] == self._data[:, 1].max())[0][0]

    def plot_elbow(self):
        """
        Plot the data points together with a line that marks the elbow.
        """
        data = self.rotate_vector(self._data, -self._theta)
        if self._scale:
            data = self._scaler.inverse_transform(data)
        elb_idx = self.get_elbow_index()
        
        df = pd.DataFrame(data, columns=['x', 'y'])
        elbow_x = data[elb_idx, 0]
        elbow_y_min = data[:, 1].min()
        elbow_y_max = data[:, 1].max()

        scatter = alt.Chart(df).mark_point().encode(
            x='x',
            y='y'
        )
        
        line = alt.Chart(pd.DataFrame({'x': [elbow_x], 'y_min': [elbow_y_min], 'y_max': [elbow_y_max]})).mark_rule(color='red', strokeDash=[5, 5]).encode(
            x='x:Q',
            y='y_min:Q',
            y2='y_max:Q'
        )

        chart = scatter + line
        chart.display()

    def plot_knee(self):
        """
        Plot the data points together with a line that marks the knee.
        """
        data = self.rotate_vector(self._data, -self._theta)
        if self._scale:
            data = self._scaler.inverse_transform(data)
        elb_idx = self.get_knee_index()
        
        df = pd.DataFrame(data, columns=['x', 'y'])
        knee_x = data[elb_idx, 0]
        knee_y_min = data[:, 1].min()
        knee_y_max = data[:, 1].max()

        scatter = alt.Chart(df).mark_point().encode(
            x='x',
            y='y'
        )
        
        line = alt.Chart(pd.DataFrame({'x': [knee_x], 'y_min': [knee_y_min], 'y_max': [knee_y_max]})).mark_rule(color='red', strokeDash=[5, 5]).encode(
            x='x:Q',
            y='y_min:Q',
            y2='y_max:Q'
        )

        chart = scatter + line
        chart.display()

    def _set_theta_auto(self):
        """
        Set theta to the radiant of the slope from the first to last value of the data.
        """
        self._theta = np.arctan2(self._data[-1, 1] - self._data[0, 1],
                                 self._data[-1, 0] - self._data[0, 0])

    @staticmethod
    def rotate_vector(data, theta):
        """
        Rotate a 2d vector.

        :param data:    2d numpy array. The data that should be rotated.
        :param theta:   float. The angle of rotation in radians.
        :return:        2d numpy array. The rotated data.
        """
        # make rotation matrix
        co = np.cos(theta)
        si = np.sin(theta)
        rotation_matrix = np.array(((co, -si), (si, co)))
        # rotate data vector
        return data.dot(rotation_matrix)
``` 

This code now uses Altair for plotting, which is more suited for interactive visualizations in web applications.