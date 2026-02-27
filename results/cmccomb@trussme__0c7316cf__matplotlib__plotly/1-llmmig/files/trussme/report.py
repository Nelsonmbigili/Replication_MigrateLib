import json
import io
import re

import plotly.graph_objects as go
import numpy
import pandas
import scipy

import trussme.visualize

from trussme.truss import Truss, Goals


def _fig_to_svg(fig: go.Figure) -> str:
    """
    Converts a Plotly figure to an SVG string.

    Parameters
    ----------
    fig: go.Figure
        The Plotly figure to convert

    Returns
    -------
    str
        The SVG string representation of the figure
    """
    # Use Plotly's write_image method to save the figure as an SVG
    imgdata = io.StringIO()
    fig.write_image(imgdata, format="svg")
    imgdata.seek(0)  # rewind the data

    svg = imgdata.getvalue()
    svg = re.sub("<dc:date>(.*?)</dc:date>", "<dc:date></dc:date>", svg)
    svg = re.sub("url\\(#(.*?)\\)", "url(#truss)", svg)
    svg = re.sub('<clipPath id="(.*?)">', '<clipPath id="truss">', svg)

    return svg


def report_to_str(truss: Truss, goals: Goals, with_figures: bool = True) -> str:
    """
    Generates a report on the truss

    Parameters
    ----------
    truss: Truss
        The truss to be reported on
    goals: Goals
        The goals against which to evaluate the truss
    with_figures: bool, default=True
        Whether to include figures in the report

    Returns
    -------
    str
        A full report on the truss
    """
    truss.analyze()

    report_string = __generate_summary(truss, goals) + "\n"
    report_string += __generate_instantiation_information(truss, with_figures) + "\n"
    report_string += __generate_stress_analysis(truss, goals, with_figures) + "\n"

    return report_string


def print_report(truss: Truss, goals: Goals) -> None:
    """
    Prints a report on the truss

    Parameters
    ----------
    truss: Truss
        The truss to be reported on
    goals: Goals
        The goals against which to evaluate the truss

    Returns
    -------
    None
    """
    print(report_to_str(truss, goals, with_figures=False))


def report_to_md(
    file_name: str, truss: Truss, goals: Goals, with_figures: bool = True
) -> None:
    """
    Writes a report in Markdown format

    Parameters
    ----------
    file_name: str
        The name of the file
    truss: Truss
        The truss to be reported on
    goals: Goals
        The goals against which to evaluate the truss
    with_figures: bool, default=True
        Whether to include figures in the report

    Returns
    -------
    None
    """
    with open(file_name, "w") as f:
        f.write(report_to_str(truss, goals, with_figures=with_figures))


def __generate_instantiation_information(truss, with_figures: bool = True) -> str:
    """
    Generate a summary of the instantiation information.

    Parameters
    ----------
    truss: Truss
        The truss to be reported on
    with_figures: bool, default=True
        Whether to include figures in the report

    Returns
    -------
    str
        A report of the instantiation information
    """
    instantiation = "# INSTANTIATION INFORMATION\n"

    if with_figures:
        # Assume trussme.visualize.plot_truss now returns a Plotly figure
        instantiation += _fig_to_svg(trussme.visualize.plot_truss(truss)) + "\n"

    # Print joint information
    instantiation += "## JOINTS\n"
    data = []
    rows = []
    for j in truss.joints:
        rows.append("Joint_" + "{0:02d}".format(j.idx))
        data.append(
            [
                str(j.coordinates[0]),
                str(j.coordinates[1]),
                str(j.coordinates[2]),
                str(j.translation_restricted[0]),
                str(j.translation_restricted[1]),
                str(j.translation_restricted[2]),
            ]
        )

    instantiation += pandas.DataFrame(
        data,
        index=rows,
        columns=["X", "Y", "Z", "X Support?", "Y Support?", "Z Support?"],
    ).to_markdown()

    # Print member information
    instantiation += "\n## MEMBERS\n"
    data = []
    rows = []
    for m in truss.members:
        rows.append("Member_" + "{0:02d}".format(m.idx))
        data.append(
            [
                str(m.begin_joint.idx),
                str(m.end_joint.idx),
                m.material_name,
                m.shape.name(),
                json.dumps(m.shape._params)
                .replace('"', "")
                .replace(": ", "=")
                .replace("{", "")
                .replace("}", ""),
                m.mass,
            ]
        )

    instantiation += pandas.DataFrame(
        data,
        index=rows,
        columns=[
            "Beginning Joint",
            "Ending Joint",
            "Material",
            "Shape",
            "Parameters (m)",
            "Mass (kg)",
        ],
    ).to_markdown()

    # Print material list
    instantiation += "\n## MATERIALS\n"
    data = []
    rows = []
    for mat in truss.materials:
        rows.append(mat["name"])
        data.append(
            [
                str(mat["density"]),
                str(mat["elastic_modulus"] / pow(10, 9)),
                str(mat["yield_strength"] / pow(10, 6)),
            ]
        )

    instantiation += pandas.DataFrame(
        data,
        index=rows,
        columns=[
            "Density (kg/m3)",
            "Elastic Modulus (GPa)",
            "Yield Strength (MPa)",
        ],
    ).to_markdown()

    return instantiation


def __generate_stress_analysis(truss, goals, with_figures: bool = True) -> str:
    """
    Generate a summary of the stress analysis information.

    Parameters
    ----------
    truss: Truss
        The truss to be reported on
    goals: Goals
        The goals against which to evaluate the truss
    with_figures: bool, default=True
        Whether to include figures in the report

    Returns
    -------
    str
        A report of the stress analysis information
    """
    analysis = "# STRESS ANALYSIS INFORMATION\n"

    # Print information about loads
    analysis += "## LOADING\n"
    data = []
    rows = []
    for j in truss.joints:
        rows.append("Joint_" + "{0:02d}".format(j.idx))
        data.append(
            [
                str(j.loads[0] / pow(10, 3)),
                format(
                    (
                        j.loads[1]
                        - sum([m.mass / 2.0 * scipy.constants.g for m in j.members])
                    )
                    / pow(10, 3),
                    ".2f",
                ),
                str(j.loads[2] / pow(10, 3)),
            ]
        )

    analysis += pandas.DataFrame(
        data, index=rows, columns=["X Load", "Y Load", "Z Load"]
    ).to_markdown()

    # Print information about reactions
    analysis += "\n## REACTIONS\n"
    data = []
    rows = []
    for j in truss.joints:
        rows.append("Joint_" + "{0:02d}".format(j.idx))
        data.append(
            [
                format(j.reactions[0] / pow(10, 3), ".2f")
                if j.translation_restricted[0] != 0.0
                else "N/A",
                format(j.reactions[1] / pow(10, 3), ".2f")
                if j.translation_restricted[1] != 0.0
                else "N/A",
                format(j.reactions[2] / pow(10, 3), ".2f")
                if j.translation_restricted[2] != 0.0
                else "N/A",
            ]
        )

    analysis += pandas.DataFrame(
        data,
        index=rows,
        columns=["X Reaction (kN)", "Y Reaction (kN)", "Z Reaction (kN)"],
    ).to_markdown()

    # Print information about members
    analysis += "\n## FORCES AND STRESSES\n"

    if with_figures:
        # Assume trussme.visualize.plot_truss now returns a Plotly figure
        analysis += (
            _fig_to_svg(trussme.visualize.plot_truss(truss, starting_shape="force"))
            + "\n"
        )

    data = []
    rows = []
    for m in truss.members:
        rows.append("Member_" + "{0:02d}".format(m.idx))
        data.append(
            [
                m.area,
                format(m.moment_of_inertia, ".2e"),
                format(m.force / pow(10, 3), ".2f"),
                m.fos_yielding,
                "Yes" if m.fos_yielding > goals.minimum_fos_yielding else "No",
                m.fos_buckling if m.fos_buckling > 0 else "N/A",
                "Yes"
                if m.fos_buckling > goals.minimum_fos_buckling or m.fos_buckling < 0
                else "No",
            ]
        )

    analysis += pandas.DataFrame(
        data,
        index=rows,
        columns=[
            "Area (m^2)",
            "Moment of Inertia (m^4)",
            "Axial force(kN)",
            "FOS yielding",
            "OK yielding?",
            "FOS buckling",
            "OK buckling?",
        ],
    ).to_markdown()

    # Print information about members
    analysis += "\n## DEFLECTIONS\n"

    if with_figures:
        analysis += (
            _fig_to_svg(
                trussme.visualize.plot_truss(
                    truss, starting_shape="k", deflected_shape="m"
                )
            )
            + "\n"
        )

    data = []
    rows = []
    for j in truss.joints:
        rows.append("Joint_" + "{0:02d}".format(j.idx))
        data.append(
            [
                format(j.deflections[0] * pow(10, 3), ".5f")
                if j.translation_restricted[0] == 0.0
                else "N/A",
                format(j.deflections[1] * pow(10, 3), ".5f")
                if j.translation_restricted[1] == 0.0
                else "N/A",
                format(j.deflections[2] * pow(10, 3), ".5f")
                if j.translation_restricted[2] == 0.0
                else "N/A",
                "Yes"
                if numpy.linalg.norm(j.deflections) < goals.maximum_deflection
                else "No",
            ]
        )

    analysis += pandas.DataFrame(
        data,
        index=rows,
        columns=[
            "X Deflection(mm)",
            "Y Deflection (mm)",
            "Z Deflection (mm)",
            "OK Deflection?",
        ],
    ).to_markdown()

    return analysis
