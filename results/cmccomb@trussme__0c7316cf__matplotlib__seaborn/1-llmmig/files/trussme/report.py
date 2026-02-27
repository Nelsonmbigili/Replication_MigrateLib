import json
import io
import re

import seaborn as sns  # Replaced matplotlib.pyplot with seaborn
import numpy
import pandas
import scipy

import trussme.visualize

from trussme.truss import Truss, Goals


def _fig_to_svg(fig) -> str:
    imgdata = io.StringIO()
    fig.savefig(imgdata, format="svg")
    imgdata.seek(0)  # rewind the data

    svg = imgdata.getvalue()
    svg = re.sub("<dc:date>(.*?)</dc:date>", "<dc:date></dc:date>", svg)
    svg = re.sub("url\(#(.*?)\)", "url(#truss)", svg)
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


def __generate_summary(truss, goals) -> str:
    """
    Generate a summary of the analysis.

    Parameters
    ----------
    truss: Truss
        The truss to be summarized
    goals: Goals
        The goals against which to evaluate the truss

    Returns
    -------
    str
        A string containing the summary
    """
    summary = "# SUMMARY OF ANALYSIS\n"
    summary += (
        "- The truss has a mass of "
        + format(truss.mass, ".2f")
        + " kg, and a total factor of safety of "
        + format(truss.fos, ".2f")
        + ".\n"
    )
    summary += "- The limit state is " + truss.limit_state + ".\n"

    success_string = []
    failure_string = []

    if goals.minimum_fos_buckling < truss.fos_buckling:
        success_string.append("buckling FOS")
    else:
        failure_string.append("buckling FOS")

    if goals.minimum_fos_yielding < truss.fos_yielding:
        success_string.append("yielding FOS")
    else:
        failure_string.append("yielding FOS")

    if goals.maximum_mass > truss.mass:
        success_string.append("mass")
    else:
        failure_string.append("mass")

    if goals.maximum_deflection > truss.deflection:
        success_string.append("deflection")
    else:
        failure_string.append("deflection")

    if len(success_string) != 0:
        if len(success_string) == 1:
            summary += (
                " The design goal for " + str(success_string[0]) + " was satisfied.\n"
            )
        elif len(success_string) == 2:
            summary += (
                "- The design goals for "
                + str(success_string[0])
                + " and "
                + str(success_string[1])
                + " were satisfied.\n"
            )
        else:
            summary += "- The design goals for "
            for st in success_string[0:-1]:
                summary += st + ", "
            summary += "and " + str(success_string[-1]) + " were satisfied.\n"

    if len(failure_string) != 0:
        if len(failure_string) == 1:
            summary += (
                "- The design goal for "
                + str(failure_string[0])
                + " was not satisfied.\n"
            )
        elif len(failure_string) == 2:
            summary += (
                "- The design goals for "
                + str(failure_string[0])
                + " and "
                + str(failure_string[1])
                + " were not satisfied.\n"
            )
        else:
            summary += "- The design goals for "
            for st in failure_string[0:-1]:
                summary += st + ","
            summary += "and " + str(failure_string[-1]) + " were not satisfied.\n"

    data = []
    rows = [
        "Minimum FOS for Buckling",
        "Minimum FOS for Yielding",
        "Maximum Mass",
        "Maximum Deflection",
    ]
    data.append(
        [
            goals.minimum_fos_buckling,
            truss.fos_buckling,
            "Yes" if truss.fos_buckling > goals.minimum_fos_buckling else "No",
        ]
    )
    data.append(
        [
            goals.minimum_fos_yielding,
            truss.fos_yielding,
            "Yes" if truss.fos_yielding > goals.minimum_fos_yielding else "No",
        ]
    )
    data.append(
        [
            goals.maximum_mass,
            truss.mass,
            "Yes" if truss.mass < goals.maximum_mass else "No",
        ]
    )
    data.append(
        [
            goals.maximum_deflection,
            truss.deflection,
            "Yes" if truss.deflection < goals.maximum_deflection else "No",
        ]
    )

    summary += (
        "\n"
        + pandas.DataFrame(
            data,
            index=rows,
            columns=["Target", "Actual", "Ok?"],
        ).to_markdown()
    )

    return summary
