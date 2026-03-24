from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from pathlib import Path
from typing import Iterable


def _load_snapshot_from_csv(
    csv_path: str | Path,
    solver_col: str = "solver",
    time_col: str = "time",
    objective_col: str = "objective",
    lower_bound_col: str = "bound",
    snapshot_time: float = 60.0,
    instance_name: str | None = None,
) -> pd.DataFrame:
    """
    Liest eine Instanz-CSV ein und extrahiert pro Solver den letzten bekannten Stand
    bis einschließlich `snapshot_time`.

    Erwartet Zeilen wie:
      solver, time, objective, lower_bound

    Falls ein Solver bis `snapshot_time` nicht vorkommt, erscheint er für diese
    Instanz gar nicht in der Rückgabe. Das wird später als fehlender Wert behandelt.
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

    if instance_name is None:
        instance_name = csv_path.stem

    if df.empty:
        return pd.DataFrame(
            columns=["instance", "solver", "time", "objective", "bound"]
        )

    # Pro Solver den letzten Stand bis snapshot_time nehmen
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
    snap["instance"] = instance_name

    return snap[["instance", "solver", "time", "objective", "bound"]]


def build_snapshot_dataframe(
    csv_files: Iterable[str | Path],
    solver_col: str = "solver",
    time_col: str = "time",
    objective_col: str = "objective",
    lower_bound_col: str = "bound",
    snapshot_time: float = 60.0,
) -> pd.DataFrame:
    """
    Baut aus vielen Instanz-CSVs ein gemeinsames DataFrame mit Snapshot pro Solver/Instanz.
    """
    parts = []
    for csv_file in csv_files:
        parts.append(
            _load_snapshot_from_csv(
                csv_path=csv_file,
                solver_col=solver_col,
                time_col=time_col,
                objective_col=objective_col,
                lower_bound_col=lower_bound_col,
                snapshot_time=snapshot_time,
            )
        )

    if not parts:
        raise ValueError("Keine CSV-Dateien übergeben.")

    data = pd.concat(parts, ignore_index=True)

    if data.empty:
        raise ValueError(
            f"Kein Solver hat bis zur Zeitgrenze {snapshot_time} einen Eintrag."
        )

    return data


def add_gap_column(
    data: pd.DataFrame,
    objective_col: str = "objective",
    lower_bound_col: str = "bound",
    gap_col: str = "gap",
    relative: bool = True,
) -> pd.DataFrame:
    """
    Fügt eine Gap-Spalte hinzu.

    relative=True:
        gap = (objective - lower_bound) / abs(objective)
        Falls objective == 0, wird NaN gesetzt.
    relative=False:
        gap = objective - lower_bound
    """
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


def plot_performance_profile(
    data: pd.DataFrame,
    instance_column: str,
    strategy_column: str,
    metric_column: str,
    direction: str,
    comparison: str = "relative",
    title: str | None = None,
    highlight_best: bool = False,
    ax: Axes | None = None,
    scale: str | None = None,
    log_base: int = 2,
    figsize: tuple = (9, 6),
    missing_to_worst: bool = True,
) -> Axes:
    """
    Performance Profile mit robuster Behandlung fehlender Solver-Werte.

    missing_to_worst=True:
      Fehlende Werte werden als "nicht gelöst / kein Ergebnis" interpretiert und
      deshalb als schlechter als alle vorhandenen Werte behandelt.
      Dadurch ist im Plot sichtbar, dass der Solver manche Instanzen nicht schafft.
    """
    if direction not in ("min", "max"):
        raise ValueError("`direction` must be 'min' or 'max'.")
    if comparison not in ("relative", "absolute"):
        raise ValueError("`comparison` must be 'relative' or 'absolute'.")

    # Alle Solver global erfassen, auch wenn sie nicht in jeder Instanz vorkommen
    all_strategies = sorted(data[strategy_column].dropna().unique())
    all_instances = sorted(data[instance_column].dropna().unique())

    # Pro Instanz bestes vorhandenes Ergebnis
    if direction == "min":
        best_val = data.groupby(instance_column)[metric_column].min()
    else:
        best_val = data.groupby(instance_column)[metric_column].max()

    # Matrix Instanz x Solver
    pivot = (
        data.groupby([instance_column, strategy_column])[metric_column]
        .median()
        .unstack()
        .reindex(index=all_instances, columns=all_strategies)
    )

    comp = pd.DataFrame(index=pivot.index, columns=pivot.columns, dtype=float)

    if comparison == "relative":
        for strat in pivot.columns:
            if direction == "min":
                comp[strat] = pivot[strat] / best_val
            else:
                comp[strat] = best_val / pivot[strat]
        comp = comp.replace([np.inf, -np.inf, 0.0], np.nan)

        if missing_to_worst:
            finite_vals = comp.to_numpy().flatten()
            finite_vals = finite_vals[np.isfinite(finite_vals)]
            worst = finite_vals.max() if len(finite_vals) else 1.0
            penalty = max(worst * 1.05, worst + 1.0)
            comp = comp.fillna(penalty)

        baseline = 1.0

    else:
        for strat in pivot.columns:
            if direction == "min":
                comp[strat] = pivot[strat] - best_val
            else:
                comp[strat] = best_val - pivot[strat]
        comp = comp.replace([np.inf, -np.inf], np.nan)

        if missing_to_worst:
            finite_vals = comp.to_numpy().flatten()
            finite_vals = finite_vals[np.isfinite(finite_vals)]
            worst = finite_vals.max() if len(finite_vals) else 0.0
            penalty = max(worst * 1.05, worst + 1.0)
            comp = comp.fillna(penalty)

        baseline = 0.0

    all_vals = comp.values.flatten()
    finite_vals = all_vals[np.isfinite(all_vals)]
    all_x = np.unique(np.sort(finite_vals))
    all_x = np.concatenate(([baseline], all_x))
    all_x = np.unique(np.sort(all_x))
    max_x = 3
    all_x = all_x[all_x <= max_x]

    n_instances = comp.shape[0]
    profile = pd.DataFrame(index=all_x, columns=comp.columns, dtype=float)

    for x in all_x:
        leq = (comp <= x).sum(axis=0)
        profile.loc[x] = leq / n_instances

    best_solver = None
    if highlight_best:
        areas = {}
        if comparison == "relative":
            positive_x = np.maximum(all_x, 1e-12)
            log_x = np.log(positive_x)
            for strat in profile.columns:
                y = profile[strat].astype(float).values
                areas[strat] = np.trapz(y, x=log_x)
        else:
            for strat in profile.columns:
                y = profile[strat].astype(float).values
                areas[strat] = np.trapz(y, x=all_x)
        best_solver = max(areas, key=areas.get)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    if scale is None:
        use_log = comparison == "relative" and all_x[-1] > 10
    else:
        use_log = scale == "log"

    for strat in profile.columns:
        y = profile[strat].astype(float)
        if highlight_best and strat == best_solver:
            ax.step(all_x, y, where="post", label=strat, linewidth=3.0, alpha=1.0)
        else:
            ax.step(
                all_x,
                y,
                where="post",
                label=strat,
                linewidth=1.5,
                alpha=0.6 if highlight_best else 1.0,
            )

    if comparison == "relative":
        if use_log:
            ax.set_xscale("log", base=log_base)
            xmin = min(v for v in all_x if v > 0)
            ax.set_xlim(xmin, max_x)
        else:
            ax.set_xscale("linear")
            ax.set_xlim(1.0, all_x[-1] * 1.1)
        xlabel = (
            f"Within this factor of the best (log{log_base} scale)"
            if use_log
            else "Within this factor of the best (linear scale)"
        )
    else:
        ax.set_xscale("linear")
        ax.set_xlim(0.0, all_x[-1] * 1.1)
        xlabel = "Absolute difference from the best"

    ax.set_ylim(0.0, 1.02)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("Proportion of problems", fontsize=12)
    ax.set_title(title or "Performance Profile", fontsize=14, pad=14)
    ax.axvline(x=baseline, color="gray", linestyle="--", alpha=0.7)
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)
    ax.legend(loc="lower right", frameon=False)

    fig.tight_layout()
    return ax


def plot_profile_from_instance_csvs(
    csv_files: Iterable[str | Path],
    metric: str = "objective",
    snapshot_time: float = 60.0,
    solver_col: str = "solver",
    time_col: str = "time",
    objective_col: str = "objective",
    lower_bound_col: str = "bound",
    comparison: str = "relative",
    highlight_best: bool = True,
    gap_relative: bool = True,
    title: str | None = None,
    ax: Axes | None = None,
    selected_solvers=None
    ) -> Axes:
    """
    Erstellt direkt einen Performance Plot aus vielen Instanz-CSVs.

    metric:
      - "objective"   -> minimieren
      - "lower_bound" -> maximieren
      - "gap"         -> minimieren
    """
    data = build_snapshot_dataframe(
        csv_files=csv_files,
        solver_col=solver_col,
        time_col=time_col,
        objective_col=objective_col,
        lower_bound_col=lower_bound_col,
        snapshot_time=snapshot_time,
    )
    if selected_solvers is not None:
        data = data[data["solver"].isin(selected_solvers)].copy()

    if metric == "gap":
        data = add_gap_column(
            data,
            objective_col="objective",
            lower_bound_col="bound",
            gap_col="gap",
            relative=gap_relative,
        )
        metric_column = "gap"
        direction = "min"
        default_title = f"Performance Profile on Gap at t={snapshot_time}s"
    elif metric == "objective":
        metric_column = "objective"
        direction = "min"
        default_title = f"Performance Profile on Objective at t={snapshot_time}s"
    elif metric == "bound":
        metric_column = "bound"
        direction = "max"
        default_title = f"Performance Profile on Lower Bound at t={snapshot_time}s"
    else:
        raise ValueError("metric must be one of: 'objective', 'lower_bound', 'gap'")

    return plot_performance_profile(
        data=data,
        instance_column="instance",
        strategy_column="solver",
        metric_column=metric_column,
        direction=direction,
        comparison=comparison,
        title=title or default_title,
        highlight_best=highlight_best,
        ax=ax,
        missing_to_worst=True,
    )

from pathlib import Path
import pandas as pd


def merge_instance_csvs(
    instances,
):


    folder = Path("output")


    all_files = {}
    for instance in instances:
        for f in folder.glob(f"*instance_{instance}_*"):
            all_files.setdefault(instance, []).append(f)

    for instance, file_list in all_files.items():
        dfs = []

        for f in file_list:
            df = pd.read_csv(f)


            dfs.append(df)

        merged = pd.concat(dfs, ignore_index=True)

        out_path = Path(f"merged/instance_{instance}.csv")
        merged.to_csv(out_path, index=False)



def example_usage(time_limit):
    from pathlib import Path

    csv_files = list(Path("merged").glob("*.csv"))
    selected_solvers = ["cpsat-ip", "hexaly-ip", "gurobi-ip", "hexaly-table", "hybrid", "cpsat-ip-heuristics", "gurobi-ip-heuristics", "hexaly-set", "cpsat-automaton"]
    ax = plot_profile_from_instance_csvs(
        csv_files=csv_files,
        metric="objective",
        snapshot_time=time_limit,
        comparison="relative",
        highlight_best=True,
        selected_solvers=selected_solvers

    )
    ax.figure.savefig(f"plots/performance_profile_objective_ip_t{datetime.now()}.png", dpi=300)

    ax = plot_profile_from_instance_csvs(
        csv_files=csv_files,
        metric="bound",
        snapshot_time=time_limit,
        comparison="relative",
        highlight_best=True,
        selected_solvers=selected_solvers
    )
    ax.figure.savefig(f"plots/performance_profile_lb_t{datetime.now()}.png", dpi=300)

    ax = plot_profile_from_instance_csvs(
        csv_files=csv_files,
        metric="gap",
        snapshot_time=time_limit,
        comparison="relative",
        highlight_best=True,
        gap_relative=True,
        selected_solvers=selected_solvers
    )
    ax.figure.savefig(f"plots/performance_profile_gap_t{datetime.now()}.png", dpi=300)


if __name__ == "__main__":
    # example_usage(60.0)

    merge_instance_csvs(range(1,21))
    example_usage(120.0)
