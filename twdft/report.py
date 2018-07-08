import collections

from typing import List, Tuple


class Report:
    """
    A column-based report outputing data from the system.
    Composed of a ReportHeader and ReportBody, which in turn
    contains multiple ReturnLine objects.
    """
    def __init__(self, data: List[Tuple], titles: List) -> None:
        self.titles = titles
        self.data = data
        self.header = ReportHeader(titles)
        self.body = ReportBody(self.data)
        self._create_presentation()

    def _create_presentation(self):
        self.presentation = []
        self.presentation.append(str(self.header))
        for line in self.body.data:
            self.presentation.append(str(line))


class ReportCell:
    "A ReportLine is comprised of a list of ReportCell objects."
    def __init__(self, text: str) -> None:
        pass


class ReportHeader:
    "The top line of a Report."""
    def __init__(self, headers: List) -> None:
        self.headers = headers

    def __str__(self):
        return " | ".join(self.headers)


class ReportBody:
    "The body of a Report, containing ReportLine objects."
    def __init__(self, data: List[Tuple]) -> None:
        self.data = data


class ReportLine:
    """
    Formats a tuple to create a line suitable for including in a Report.
    """
    def __init__(self, report: Report, data: Tuple) -> None:
        self.report = report
        self.data = data

