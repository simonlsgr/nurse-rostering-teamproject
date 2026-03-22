import datetime

from nurse_rostering.solvers.hexaly.model.modules_set import OneShiftPerDayModuleSet
from nurse_rostering.solvers.hexaly.model.modules_table import OneShiftPerDayModuleTable
from nurse_rostering.solvers.hexaly.model.nurse_vars import ShiftDecisionVars, NurseDecisionVarsTable
from nurse_rostering.data_schema import Shift
from nurse_rostering.utils._generate import create_shifts, create_nurse
from nurse_rostering.solvers.hexaly.utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance
import hexaly.optimizer as hx

from nurse_rostering.utils.data_utils import group_shifts_by_date

def test_one_shift_per_day_infeasible_table():
    shifts = [
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 8, 0),
            end_time=datetime.datetime(2018, 1, 1, 16, 0),
            name="Morning Shift",
        ),
        Shift(
            demand=1,
            start_time=datetime.datetime(2018, 1, 1, 16, 0),
            end_time=datetime.datetime(2018, 1, 2, 0, 0),
            name="Evening Shift",
        ),
    ]

    nurse1 = create_nurse("N1", min_time_between_shifts=datetime.timedelta(hours=0))
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)

    dates = group_shifts_by_date(instance)

    with AssertModelInfeasible() as model:
        nv = NurseDecisionVarsTable(instance.shifts, model)

        OneShiftPerDayModuleTable().build(instance, model, [nv], dates)

        nv.fix(datetime.date(2018, 1, 1), 1)
        nv.fix(datetime.date(2018, 1, 1), 2)