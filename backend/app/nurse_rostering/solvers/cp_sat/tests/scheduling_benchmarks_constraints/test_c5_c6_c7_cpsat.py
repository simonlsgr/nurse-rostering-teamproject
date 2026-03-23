import datetime

from nurse_rostering.solvers.cp_sat.model.modules import ConsecutiveShiftsAndDaysModule
from nurse_rostering.solvers.cp_sat.model.nurse_vars import NurseDecisionVars
from nurse_rostering.data_schema import Shift, Nurse
from nurse_rostering.utils._generate import create_shifts, create_nurse
from cpsat_utils.testing import AssertModelFeasible, AssertModelInfeasible
from nurse_rostering.data_schema import NurseRosteringInstance



def test_maximum_consecutive_shifts_feasible():
    
    shifts = [
        Shift(
            demand=1, 
            start_time=datetime.datetime(2018, 1, i, 8, 0), 
            end_time=datetime.datetime(2018, 1, i, 16, 0),
            name="Morning Shift",
        )
        for i in range(1,8)
    ]
    
    nurse1 = Nurse(
        name="n1",
        minimum_consecutive_days_off=2,
        minimum_consecutive_shifts=2,
        maximum_consecutive_shifts=3,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelFeasible() as model:
        nurse_vars = NurseDecisionVars(nurse1, shifts, model)
        ConsecutiveShiftsAndDaysModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        nurse_vars.fix(shifts[1].uid, True)
        nurse_vars.fix(shifts[2].uid, True)
    
        

def test_maximum_consecutive_shifts_infeasible():
    shifts = [
        Shift(
            demand=1, 
            start_time=datetime.datetime(2018, 1, i, 8, 0), 
            end_time=datetime.datetime(2018, 1, i, 16, 0),
            name="Morning Shift",
        )
        for i in range(1,8)
    ]
    
    nurse1 = Nurse(
        name="n1",
        minimum_consecutive_days_off=2,
        minimum_consecutive_shifts=2,
        maximum_consecutive_shifts=2,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelInfeasible() as model:
        nurse_vars = NurseDecisionVars(nurse1, shifts, model)
        ConsecutiveShiftsAndDaysModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        nurse_vars.fix(shifts[1].uid, True)
        nurse_vars.fix(shifts[2].uid, True)
        
        

def test_minimum_consecutive_shifts_feasible():
    
    shifts = [
        Shift(
            demand=1, 
            start_time=datetime.datetime(2018, 1, i, 8, 0), 
            end_time=datetime.datetime(2018, 1, i, 16, 0),
            name="Morning Shift",
        )
        for i in range(1,8)
    ]
    
    nurse1 = Nurse(
        name="n1",
        minimum_consecutive_days_off=2,
        minimum_consecutive_shifts=3,
        maximum_consecutive_shifts=3,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelFeasible() as model:
        nurse_vars = NurseDecisionVars(nurse1, shifts, model)
        ConsecutiveShiftsAndDaysModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        nurse_vars.fix(shifts[1].uid, True)
        nurse_vars.fix(shifts[2].uid, True)
        
        
        

def test_minimum_consecutive_shifts_infeasible():
    shifts = [
        Shift(
            demand=1, 
            start_time=datetime.datetime(2018, 1, i, 8, 0), 
            end_time=datetime.datetime(2018, 1, i, 16, 0),
            name="Morning Shift",
        )
        for i in range(1,8)
    ]
    
    nurse1 = Nurse(
        name="n1",
        minimum_consecutive_days_off=2,
        minimum_consecutive_shifts=2,
        maximum_consecutive_shifts=3,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelInfeasible() as model:
        nurse_vars = NurseDecisionVars(nurse1, shifts, model)
        ConsecutiveShiftsAndDaysModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, False)
        nurse_vars.fix(shifts[1].uid, True)
        nurse_vars.fix(shifts[2].uid, False)
        


def test_minimum_consecutive_days_off_feasible():
    
    shifts = [
        Shift(
            demand=1, 
            start_time=datetime.datetime(2018, 1, i, 8, 0), 
            end_time=datetime.datetime(2018, 1, i, 16, 0),
            name="Morning Shift",
        )
        for i in range(1,8)
    ]
    
    nurse1 = Nurse(
        name="n1",
        minimum_consecutive_days_off=2,
        minimum_consecutive_shifts=0,
        maximum_consecutive_shifts=7,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelFeasible() as model:
        nurse_vars = NurseDecisionVars(nurse1, shifts, model)
        ConsecutiveShiftsAndDaysModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        nurse_vars.fix(shifts[1].uid, False)
        nurse_vars.fix(shifts[2].uid, False)
        nurse_vars.fix(shifts[3].uid, True)
        
        
def test_minimum_consecutive_days_off_infeasible():
    shifts = [
        Shift(
            demand=1, 
            start_time=datetime.datetime(2018, 1, i, 8, 0), 
            end_time=datetime.datetime(2018, 1, i, 16, 0),
            name="Morning Shift",
        )
        for i in range(1,8)
    ]
    
    nurse1 = Nurse(
        name="n1",
        minimum_consecutive_days_off=3,
        minimum_consecutive_shifts=0,
        maximum_consecutive_shifts=7,
        preferred_shifts=set(),
        blocked_shifts=set(),
        staff=True,
        min_time_between_shifts=datetime.timedelta(hours=0),
    )
    
    instance = NurseRosteringInstance(nurses=[nurse1], shifts=shifts)
    with AssertModelInfeasible() as model:
        nurse_vars = NurseDecisionVars(nurse1, shifts, model)
        ConsecutiveShiftsAndDaysModule().build(instance, model, [nurse_vars])
        nurse_vars.fix(shifts[0].uid, True)
        nurse_vars.fix(shifts[1].uid, False)
        nurse_vars.fix(shifts[2].uid, True)
        nurse_vars.fix(shifts[3].uid, False)