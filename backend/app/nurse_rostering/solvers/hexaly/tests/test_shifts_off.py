from nurse_rostering.solvers.hexaly.model.modules import MinTimeBetweenShifts
from datetime import timedelta

from nurse_rostering.solvers.hexaly.model.nurse_vars import NurseDecisionVars
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.data_schema import NurseRosteringInstance


import hexaly.optimizer

def run_min_rest_test(
    assignments: list[bool | None],
    expected_feasible: bool,
    shift_length: int = 8,
    min_time_in_between: timedelta = timedelta(hours=16),
):
    shifts = create_shifts(len(assignments), shift_length=shift_length)
    nurse = create_nurse("Nurse A", min_time_between_shifts=min_time_in_between)
    instance = NurseRosteringInstance(nurses=[nurse], shifts=shifts)

    # context = AssertModelFeasible() if expected_feasible else AssertModelInfeasible()

    with hexaly.optimizer.HexalyOptimizer() as optimizer:
        model = optimizer.model
        nurse_vars = NurseDecisionVars(nurse, shifts, model)
        MinTimeBetweenShifts().build(instance, model, [nurse_vars])
        for s, assign in zip(shifts, assignments):
            if assign is None:
                continue  # skip free assignments
            nurse_vars.fix(s.uid, assign)
        model.minimize(0)
        model.close()
        optimizer.solve()
        if expected_feasible:
            if optimizer.solution.status != hexaly.optimizer.HxSolutionStatus.OPTIMAL and optimizer.solution.status != hexaly.optimizer.HxSolutionStatus.FEASIBLE:
                raise Exception(f"Expected feasible, but got status {optimizer.solution.status}")
        else:
            if optimizer.solution.status != hexaly.optimizer.HxSolutionStatus.INFEASIBLE and optimizer.solution.status != hexaly.optimizer.HxSolutionStatus.INCONSISTENT:
                raise Exception(f"Expected infeasible, but got status {optimizer.solution.status}")



def test_pattern_false_true_true_false():
    run_min_rest_test(assignments=[None, True, True, None], expected_feasible=False)


def test_pattern_true_false_true_false():
    run_min_rest_test(
        assignments=[True, False, True, False],
        expected_feasible=True,
        shift_length=8,
        min_time_in_between=timedelta(hours=8),
    )


def test_pattern_true_false_false_true():
    run_min_rest_test(assignments=[True, False, False, True], expected_feasible=True)


def test_pattern_true_false_false_false_true():
    run_min_rest_test(
        assignments=[True, False, False, False, True], expected_feasible=True
    )


def test_pattern_all_false():
    run_min_rest_test(assignments=[False, False, False, False], expected_feasible=True)


def test_pattern_all_true_should_fail():
    run_min_rest_test(assignments=[True, True, True, True], expected_feasible=False)


def test_pattern_single_shift():
    run_min_rest_test(assignments=[True], expected_feasible=True)


def test_pattern_two_shifts_pause():
    run_min_rest_test(
        assignments=[True, False, True, False],
        expected_feasible=False,
        shift_length=8,
        min_time_in_between=timedelta(hours=16),
    )


def test_pattern_two_shifts_pause2():
    run_min_rest_test(
        assignments=[True, False, False, True],
        expected_feasible=True,
        shift_length=8,
        min_time_in_between=timedelta(hours=16),
    )
