"""Audit the supplied Figure 4 and Figure 5 tables without deriving new results.

This script checks whether the workbooks contain formulas, whether Figure 4
relative contributions sum to one within each region/period, and whether the
Figure 5 waterfall contributions reconcile the reported period endpoints.
It intentionally does not reconstruct the missing normalization coefficient.
"""

from __future__ import annotations

from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[2]
FIG4 = ROOT / "data" / "review_required" / "figure4" / "Figure4_relative_contributions.xlsx"
FIG5 = ROOT / "data" / "review_required" / "figure5" / "Figure5_absolute_contributions.xlsx"


def formula_count(path: Path) -> int:
    workbook = openpyxl.load_workbook(path, data_only=False, read_only=True)
    try:
        return sum(
            1
            for sheet in workbook.worksheets
            for row in sheet.iter_rows()
            for cell in row
            if isinstance(cell.value, str) and cell.value.startswith("=")
        )
    finally:
        workbook.close()


def audit_figure4() -> None:
    workbook = openpyxl.load_workbook(FIG4, data_only=True, read_only=True)
    try:
        print(f"Figure 4 workbook formulas: {formula_count(FIG4)}")
        for sheet in workbook.worksheets:
            rows = list(sheet.iter_rows(min_row=2, values_only=True))
            before = sum(float(row[1] or 0) for row in rows)
            after = sum(float(row[3] or 0) for row in rows)
            print(
                f"Figure 4 {sheet.title}: "
                f"2001-2013 sum={before:.12f}; 2013-2020 sum={after:.12f}"
            )
    finally:
        workbook.close()


def audit_figure5() -> None:
    workbook = openpyxl.load_workbook(FIG5, data_only=True, read_only=True)
    try:
        print(f"Figure 5 workbook formulas: {formula_count(FIG5)}")
        for sheet in workbook.worksheets:
            rows = [(row[0], float(row[1])) for row in sheet.iter_rows(values_only=True)]
            anchor_indices = [index for index, (label, _) in enumerate(rows) if isinstance(label, int)]
            for start_index, end_index in zip(anchor_indices, anchor_indices[1:]):
                start_year, start_value = rows[start_index]
                end_year, end_value = rows[end_index]
                contribution_sum = sum(value for _, value in rows[start_index + 1 : end_index])
                residual = start_value + contribution_sum - end_value
                print(
                    f"Figure 5 {sheet.title} {start_year}-{end_year}: "
                    f"start={start_value:.1f}; contributions={contribution_sum:+.1f}; "
                    f"end={end_value:.1f}; residual={residual:+.1f}"
                )
    finally:
        workbook.close()


if __name__ == "__main__":
    audit_figure4()
    audit_figure5()
