#!/usr/bin/env python
# pylint: disable=R0902, R0903, C0103
"""
Gantt.py is a simple class to render Gantt charts, as commonly used in
"""

import os
import json
import platform
from operator import sub

import numpy as np
import plotly.graph_objects as go


class Package:
    """Encapsulation of a work package

    A work package is instantiated from a dictionary. It **has to have**
    a label, astart and an end. Optionally it may contain milestones
    and a color

    :arg str pkg: dictionary w/ package data name
    """

    def __init__(self, pkg):

        DEFCOLOR = "#32AEE0"

        self.label = pkg["label"]
        self.start = pkg["start"]
        self.end = pkg["end"]

        if self.start < 0 or self.end < 0:
            raise ValueError("Package cannot begin at t < 0")
        if self.start > self.end:
            raise ValueError("Cannot end before started")

        try:
            self.milestones = pkg["milestones"]
        except KeyError:
            pass

        try:
            self.color = pkg["color"]
        except KeyError:
            self.color = DEFCOLOR

        try:
            self.legend = pkg["legend"]
        except KeyError:
            self.legend = None


class Gantt:
    """Gantt
    Class to render a simple Gantt chart, with optional milestones
    """

    def __init__(self, dataFile):
        """Instantiation

        Create a new Gantt using the data in the file provided
        or the sample data that came along with the script

        :arg str dataFile: file holding Gantt data
        """
        self.dataFile = dataFile

        # some lists needed
        self.packages = []
        self.labels = []

        self._loadData()
        self._procData()

    def _loadData(self):
        """Load data from a JSON file that has to have the keys:
        packages & title. Packages is an array of objects with
        a label, start and end property and optional milesstones
        and color specs.
        """

        # load data
        with open(self.dataFile) as fh:
            data = json.load(fh)

        # must-haves
        self.title = data["title"]

        for pkg in data["packages"]:
            self.packages.append(Package(pkg))

        self.labels = [pkg["label"] for pkg in data["packages"]]

        # optionals
        self.milestones = {}
        for pkg in self.packages:
            try:
                self.milestones[pkg.label] = pkg.milestones
            except AttributeError:
                pass

        try:
            self.xlabel = data["xlabel"]
        except KeyError:
            self.xlabel = ""
        try:
            self.xticks = data["xticks"]
        except KeyError:
            self.xticks = ""

    def _procData(self):
        """Process data to have all values needed for plotting"""
        # parameters for bars
        self.nPackages = len(self.labels)
        self.start = [None] * self.nPackages
        self.end = [None] * self.nPackages

        for pkg in self.packages:
            idx = self.labels.index(pkg.label)
            self.start[idx] = pkg.start
            self.end[idx] = pkg.end

        self.durations = list(map(sub, self.end, self.start))
        self.yPos = np.arange(self.nPackages, 0, -1)

    def render(self):
        """Prepare data for plotting"""

        # Create the figure
        fig = go.Figure()

        # Add horizontal bars for each package
        for idx, pkg in enumerate(self.packages):
            fig.add_trace(
                go.Bar(
                    x=[self.durations[idx]],
                    y=[self.labels[idx]],
                    base=self.start[idx],
                    orientation="h",
                    marker=dict(color=pkg.color),
                    name=pkg.legend if pkg.legend else pkg.label,
                )
            )

        # Add milestones as scatter points
        if self.milestones:
            x = []
            y = []
            for key in self.milestones.keys():
                for value in self.milestones[key]:
                    y += [self.labels.index(key) + 1]
                    x += [value]

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=[self.labels[i - 1] for i in y],
                    mode="markers",
                    marker=dict(symbol="diamond", size=10, color="yellow", line=dict(color="black", width=1)),
                    name="Milestones",
                )
            )

        # Format the layout
        fig.update_layout(
            title=self.title,
            xaxis=dict(title=self.xlabel, tickvals=self.xticks, ticktext=list(map(str, self.xticks)) if self.xticks else None),
            yaxis=dict(title="", tickvals=self.yPos, ticktext=self.labels),
            barmode="stack",
            showlegend=True,
        )

        self.fig = fig

    def show(self):
        """Show the plot"""
        self.fig.show()

    def save(self, saveFile="img/GANTT.png"):
        """Save the plot to a file. It defaults to `img/GANTT.png`.

        :arg str saveFile: file to save to
        """
        self.fig.write_image(saveFile)


if __name__ == "__main__":
    g = Gantt("sample.json")
    g.render()
    g.show()
    # g.save('img/GANTT.png')
