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
import pandas as pd
import altair as alt


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
        """Prepare data for plotting using Altair"""

        # Prepare data for Altair
        data = []
        for i, pkg in enumerate(self.packages):
            data.append({
                "Task": pkg.label,
                "Start": pkg.start,
                "End": pkg.end,
                "Duration": self.durations[i],
                "Color": pkg.color,
                "YPos": self.yPos[i]
            })

        df = pd.DataFrame(data)

        # Create the Gantt chart
        bars = alt.Chart(df).mark_bar().encode(
            x=alt.X("Start:Q", title=self.xlabel),
            x2="End:Q",
            y=alt.Y("Task:N", sort=self.labels, title=""),
            color=alt.Color("Color:N", scale=None, legend=None)
        )

        # Add milestones if they exist
        if self.milestones:
            milestone_data = []
            for key, values in self.milestones.items():
                for value in values:
                    milestone_data.append({
                        "Task": key,
                        "Milestone": value,
                        "YPos": self.yPos[self.labels.index(key)]
                    })

            milestone_df = pd.DataFrame(milestone_data)

            milestones = alt.Chart(milestone_df).mark_point(
                shape="diamond", size=120, color="yellow", stroke="black"
            ).encode(
                x="Milestone:Q",
                y=alt.Y("Task:N", sort=self.labels, title="")
            )

            chart = bars + milestones
        else:
            chart = bars

        # Add title and configure chart
        chart = chart.properties(
            title=self.title,
            width=800,
            height=400
        ).configure_axis(
            grid=True
        )

        self.chart = chart

    def show(self):
        """Show the plot"""
        self.chart.show()

    def save(self, saveFile="img/GANTT.html"):
        """Save the plot to a file. It defaults to `img/GANTT.html`.

        :arg str saveFile: file to save to
        """
        self.chart.save(saveFile)


if __name__ == "__main__":
    g = Gantt("sample.json")
    g.render()
    g.show()
    # g.save('img/GANTT.html')
