import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path



INPUT_DIR = Path("merged")
SNAPSHOT_TIME = 120.0
BASELINE_SOLVER = "cpsat-ip"
NEW_SOLVER = "cpsat-ip-heuristics"


METRIC = "bound"

GAP_RELATIVE = True

OUTPUT_FILE = f"plots/scatter_{METRIC}_{BASELINE_SOLVER}_vs_{NEW_SOLVER}.png"


def _load_snapshot_from_csv(
    csv_path: str | Path,
    solver_col: str = "solver",
    time_col: str = "time",
    objective_col: str = "objective",
    lower_bound_col: str = "bound",
    snapshot_time: float = 60.0,
) -> pd.DataFrame:
    """
    Liest eine Instanz-CSV ein und extrahiert pro Solver den letzten bekannten Stand
    bis einschließlich snapshot_time.

    Die Instanz wird aus dem Dateinamen genommen, da keine 'instance'-Spalte existiert.
    """
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)

    required_cols = {solver_col, time_col, objective_col, lower_bound_col}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"{csv_path} fehlt Spalten: {sorted(missing)}")

    df = df.copy()
    df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
    df[objective_col] = pd.to_numeric(df[objective_col], errors="coerce")
    df[lower_bound_col] = pd.to_numeric(df[lower_bound_col], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df[df[time_col] <= snapshot_time].copy()

    if df.empty:
        return pd.DataFrame(columns=["instance", "solver", "time", "objective", "bound"])

    df = df.sort_values([solver_col, time_col])
    idx = df.groupby(solver_col)[time_col].idxmax()
    snap = df.loc[idx, [solver_col, time_col, objective_col, lower_bound_col]].copy()

    snap.rename(
        columns={
            solver_col: "solver",
            time_col: "time",
            objective_col: "objective",
            lower_bound_col: "bound",
        },
        inplace=True,
    )
    snap["instance"] = csv_path.stem
    return snap[["instance", "solver", "time", "objective", "bound"]]


def build_snapshot_dataframe(
    csv_files,
    snapshot_time: float = 60.0,
) -> pd.DataFrame:
    parts = [
        _load_snapshot_from_csv(csv_file, snapshot_time=snapshot_time)
        for csv_file in csv_files
    ]
    if not parts:
        raise ValueError("Keine CSV-Dateien gefunden.")
    data = pd.concat(parts, ignore_index=True)
    if data.empty:
        raise ValueError(f"Kein Solver hat bis {snapshot_time}s einen Eintrag.")
    return data


def add_gap_column(
    data: pd.DataFrame,
    objective_col: str = "objective",
    lower_bound_col: str = "bound",
    gap_col: str = "gap",
    relative: bool = True,
) -> pd.DataFrame:
    df = data.copy()
    obj = pd.to_numeric(df[objective_col], errors="coerce")
    lb = pd.to_numeric(df[lower_bound_col], errors="coerce")

    if relative:
        denom = obj.abs()
        gap = (obj - lb) / denom
        gap = gap.where(denom != 0, np.nan)
    else:
        gap = obj - lb

    df[gap_col] = gap.replace([np.inf, -np.inf], np.nan)
    return df


def plot_performance_scatter(
    ax,
    baseline: pd.Series,
    new_values: pd.Series,
    lower_is_better: bool = True,
    title: str = "",
    **kwargs,
):
    """
    Scatter-Vergleich baseline vs new_values.
    """
    if not isinstance(baseline, pd.Series) or not isinstance(new_values, pd.Series):
        raise ValueError("Both baseline and new_values should be pandas Series.")
    if baseline.size != new_values.size:
        raise ValueError("Both Series should have the same length.")

    scatter_kwargs = {
        "color": kwargs.get("color", "blue"),
        "marker": kwargs.get("marker", "x"),
        "label": kwargs.get("label", "Data Points"),
    }

    line_kwargs = {
        "color": kwargs.get("line_color", "k"),
        "linestyle": kwargs.get("line_style", "--"),
        "label": kwargs.get("line_label", "No Change"),
    }

    fill_improve_kwargs = {
        "color": kwargs.get("improve_color", "green"),
        "alpha": kwargs.get("improve_alpha", 0.3),
        "label": kwargs.get("improve_label", "Improved Performance"),
    }

    fill_decline_kwargs = {
        "color": kwargs.get("decline_color", "red"),
        "alpha": kwargs.get("decline_alpha", 0.3),
        "label": kwargs.get("decline_label", "Declined Performance"),
    }

    baseline = baseline.replace([np.inf, -np.inf], np.nan)
    new_values = new_values.replace([np.inf, -np.inf], np.nan)

    max_val = max(baseline.max(skipna=True), new_values.max(skipna=True)) * 1.05
    min_val = min(baseline.min(skipna=True), new_values.min(skipna=True)) * 0.95

    na_indices = baseline.isna() | new_values.isna()

    if lower_is_better:
        baseline = baseline.fillna(max_val)
        new_values = new_values.fillna(max_val)
    else:
        baseline = baseline.fillna(min_val)
        new_values = new_values.fillna(min_val)

    if na_indices.any():
        ax.scatter(
            baseline[na_indices],
            new_values[na_indices],
            marker="s",
            color=scatter_kwargs["color"],
            label="N/A Values",
            zorder=2,
        )

    ax.scatter(
        baseline[~na_indices],
        new_values[~na_indices],
        **scatter_kwargs,
        zorder=2,
    )

    ax.plot([min_val, max_val], [min_val, max_val], zorder=1, **line_kwargs)

    x = np.linspace(min_val, max_val, 500)
    if lower_is_better:
        ax.fill_between(x, min_val, x, zorder=0, **fill_improve_kwargs)
        ax.fill_between(x, x, max_val, zorder=0, **fill_decline_kwargs)
    else:
        ax.fill_between(x, x, max_val, zorder=0, **fill_improve_kwargs)
        ax.fill_between(x, min_val, x, zorder=0, **fill_decline_kwargs)

    for old_val, new_val in zip(baseline, new_values):
        if pd.isna(old_val) and pd.isna(new_val):
            continue
        if pd.isna(old_val):
            old_val = min_val if lower_is_better else max_val
        if pd.isna(new_val):
            new_val = min_val if lower_is_better else max_val

        if lower_is_better and new_val < old_val:
            ax.plot([old_val, old_val], [old_val, new_val], color="green", linewidth=1.0, zorder=1)
        elif not lower_is_better and new_val > old_val:
            ax.plot([old_val, old_val], [old_val, new_val], color="green", linewidth=1.0, zorder=1)
        elif lower_is_better and new_val > old_val:
            ax.plot([old_val, old_val], [old_val, new_val], color="red", linewidth=1.0, zorder=1)
        elif not lower_is_better and new_val < old_val:
            ax.plot([old_val, old_val], [old_val, new_val], color="red", linewidth=1.0, zorder=1)

    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.set_xlabel(kwargs.get("xlabel", f"{BASELINE_SOLVER}"))
    ax.set_ylabel(kwargs.get("ylabel", f"{NEW_SOLVER}"))
    if title:
        ax.set_title(title)
    ax.legend()


def build_baseline_and_new_data(
    csv_files,
    baseline_solver: str,
    new_solver: str,
    snapshot_time: float,
    metric: str,
    gap_relative: bool = True,
):
    data = build_snapshot_dataframe(csv_files, snapshot_time=snapshot_time)

    if metric == "gap":
        data = add_gap_column(
            data,
            objective_col="objective",
            lower_bound_col="bound",
            gap_col="gap",
            relative=gap_relative,
        )
        metric_column = "gap"
        lower_is_better = True
    elif metric == "objective":
        metric_column = "objective"
        lower_is_better = True
    elif metric == "bound":
        metric_column = "bound"
        lower_is_better = False
    else:
        raise ValueError("METRIC must be one of: 'objective', 'bound', 'gap'")

    compare = data[data["solver"].isin([baseline_solver, new_solver])].copy()
    if compare.empty:
        raise ValueError(
            f"Keine Daten für Solver '{baseline_solver}' und '{new_solver}' gefunden.\n"
            f"Vorhandene Solver: {sorted(data['solver'].dropna().unique())}"
        )

    wide = compare.pivot_table(
        index="instance",
        columns="solver",
        values=metric_column,
        aggfunc="median",
    )

    if baseline_solver not in wide.columns:
        raise ValueError(f"Solver '{baseline_solver}' wurde in den Daten nicht gefunden.")
    if new_solver not in wide.columns:
        raise ValueError(f"Solver '{new_solver}' wurde in den Daten nicht gefunden.")

    baseline = wide[baseline_solver]
    new_values = wide[new_solver]

    return baseline, new_values, lower_is_better


def main():
    csv_files = sorted(INPUT_DIR.glob("*.csv"))
    if not csv_files:
        raise ValueError(f"Keine CSV-Dateien in {INPUT_DIR} gefunden.")

    baseline, new_values, lower_is_better = build_baseline_and_new_data(
        csv_files=csv_files,
        baseline_solver=BASELINE_SOLVER,
        new_solver=NEW_SOLVER,
        snapshot_time=SNAPSHOT_TIME,
        metric=METRIC,
        gap_relative=GAP_RELATIVE,
    )

    fig, ax = plt.subplots(figsize=(7, 7))
    plot_performance_scatter(
        ax=ax,
        baseline=baseline,
        new_values=new_values,
        lower_is_better=lower_is_better,
        title=f"{METRIC} at t={SNAPSHOT_TIME}s",
        xlabel=f"{BASELINE_SOLVER}",
        ylabel=f"{NEW_SOLVER}",
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=300)
    print(f"Plot gespeichert als: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
