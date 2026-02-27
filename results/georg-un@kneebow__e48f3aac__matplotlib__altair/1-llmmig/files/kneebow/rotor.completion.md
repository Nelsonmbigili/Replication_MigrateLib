### Explanation of Changes
To migrate the code from `matplotlib` to `altair`, the following changes were made:
1. **Import Statement**: Removed the `matplotlib.pyplot` import and added the `altair` import.
2. **Plotting Functions**:
   - Replaced `plt.scatter` with `alt.Chart` for scatter plots.
   - Replaced `plt.vlines` with an `alt.Chart` rule layer to draw vertical lines.
   - Combined the scatter plot and vertical line into a single `altair` chart using layering.
3. **Data Handling**: Since `altair` works with Pandas DataFrames, converted the `numpy` arrays to DataFrames before plotting.
4. **No Changes to Logic**: The rest of the logic, including the rotation and scaling, remains unchanged.

### Modified Code
```python
import numpy as np
import pandas as pd
import altair as alt
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

        # Convert data to a DataFrame for Altair
        df = pd.DataFrame(data, columns=['x', 'y'])

        # Create scatter plot
        scatter = alt.Chart(df).mark_circle(size=60).encode(
            x='x',
            y='y'
        )

        # Add vertical line for the elbow
        elbow_line = alt.Chart(pd.DataFrame({
            'x': [df.iloc[elb_idx]['x']],
            'y_min': [df['y'].min()],
            'y_max': [df['y'].max()]
        })).mark_rule(color='red', strokeDash=[5, 5]).encode(
            x='x',
            y='y_min',
            y2='y_max'
        )

        # Combine scatter plot and vertical line
        chart = scatter + elbow_line
        chart.show()

    def plot_knee(self):
        """
        Plot the data points together with a line that marks the knee.
        """
        data = self.rotate_vector(self._data, -self._theta)
        if self._scale:
            data = self._scaler.inverse_transform(data)
        knee_idx = self.get_knee_index()

        # Convert data to a DataFrame for Altair
        df = pd.DataFrame(data, columns=['x', 'y'])

        # Create scatter plot
        scatter = alt.Chart(df).mark_circle(size=60).encode(
            x='x',
            y='y'
        )

        # Add vertical line for the knee
        knee_line = alt.Chart(pd.DataFrame({
            'x': [df.iloc[knee_idx]['x']],
            'y_min': [df['y'].min()],
            'y_max': [df['y'].max()]
        })).mark_rule(color='red', strokeDash=[5, 5]).encode(
            x='x',
            y='y_min',
            y2='y_max'
        )

        # Combine scatter plot and vertical line
        chart = scatter + knee_line
        chart.show()

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

### Key Notes
- The `altair` library requires data to be in a tabular format (e.g., Pandas DataFrame), so the `numpy` arrays were converted to DataFrames before plotting.
- The `alt.Chart` object was used to create scatter plots and vertical lines, and these were combined using the `+` operator.
- The `chart.show()` method is used to display the plot in a browser or notebook environment.