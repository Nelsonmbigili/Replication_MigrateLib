### Explanation of Changes
To migrate the code from `matplotlib` to `plotly`, the following changes were made:
1. Replaced `matplotlib.pyplot` (`plt`) with `plotly.graph_objects` (`go`) for plotting.
2. Used `go.Scatter` to create scatter plots and `go.Figure` to manage the plot.
3. Replaced `plt.vlines` with `go.Scatter` to draw vertical lines by specifying the x-coordinate as a constant and varying the y-coordinates.
4. Removed the need for `plt.show()` since `plotly` automatically renders the plot in an interactive format.

The rest of the code remains unchanged, as the migration only affects the plotting functionality.

---

### Modified Code
```python
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go


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

        # Create scatter plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data[:, 0], y=data[:, 1], mode='markers', name='Data Points'))

        # Add vertical line for the elbow
        fig.add_trace(go.Scatter(
            x=[data[elb_idx, 0], data[elb_idx, 0]],
            y=[data[:, 1].min(), data[:, 1].max()],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Elbow'
        ))

        # Show the plot
        fig.show()

    def plot_knee(self):
        """
        Plot the data points together with a line that marks the knee.
        """
        data = self.rotate_vector(self._data, -self._theta)
        if self._scale:
            data = self._scaler.inverse_transform(data)
        elb_idx = self.get_knee_index()

        # Create scatter plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data[:, 0], y=data[:, 1], mode='markers', name='Data Points'))

        # Add vertical line for the knee
        fig.add_trace(go.Scatter(
            x=[data[elb_idx, 0], data[elb_idx, 0]],
            y=[data[:, 1].min(), data[:, 1].max()],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Knee'
        ))

        # Show the plot
        fig.show()

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