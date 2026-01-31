import datetime
from nurse_rostering.data_schema import NurseRosteringInstance, Shift, Nurse

def read_instance(file_path: str) -> NurseRosteringInstance:
    """Reads a NurseRosteringInstance from a JSON file."""
    from nurse_rostering.data_schema import NurseRosteringInstance
    import json

    # using 2018 since it's a non-leap year starting on a Monday
    start_date = datetime.date(2018, 1, 1)

    with open(file_path, 'r') as f:
        file_content = f.read()
    # remove comments
    lines = file_content.splitlines()
    file_content = '\n'.join(line for line in lines if not line.strip().startswith('#'))
    
    
    # get planing horizon
    sections = file_content.split("SECTION_")
    # remove empty sections
    sections = [section for section in sections if section.strip() != ''] 
    
    
    horizon_section = next((section for section in sections if section.startswith("HORIZON")), None)
    horizon = 0
    if horizon_section:
        # find the line that is a number
        horizon_lines = horizon_section.splitlines()
        for line in horizon_lines:
            line = line.strip()
            if line.isdigit():
                horizon = int(line)
                break
    
    shifts_model = []
    shifts_section = next((section for section in sections if section.startswith("SHIFTS")), None)
    shifts = shifts_section.splitlines()[1:-1]
    for shift_data in shifts:
        for i in range(horizon):
            shift_parts = shift_data.split(',')
            type = shift_parts[0].strip()
            length_mins = int(shift_parts[1].strip())
            not_followed_by = shift_parts[2].strip().split('|') if len(shift_parts) > 2 and shift_parts[2].strip() != '' else []
            
            start_time = datetime.datetime.combine(start_date + datetime.timedelta(days=i), datetime.time(0,0))
            end_time = start_time + datetime.timedelta(minutes=length_mins)
            
            shifts_model.append(
                Shift(
                    name=f"{i}_{type}",
                    start_time=start_time,
                    end_time=end_time,
                    demand=0,  # demand will be set in the COVER section
                    type=type,
                    not_followed_by_shift_types=set(not_followed_by) if not_followed_by != [''] else set()
                )
            )
    
    nurses_model = []
    staff_section = next((section for section in sections if section.startswith("STAFF")), None)
    staff = staff_section.splitlines()[1:-1]
    for staff_data in staff:
        staff_parts = staff_data.split(',')
        nurse_id = staff_parts[0].strip()
        max_shifts_list = [max_shifts_per_type.split("=") for max_shifts_per_type in staff_parts[1].strip().split('|')]
        max_shifts_dict = {item[0]: int(item[1]) for item in max_shifts_list}
        
        
        max_total_minutes = int(staff_parts[2])
        min_total_minutes = int(staff_parts[3])
        max_consecutive_shifts = int(staff_parts[4])
        min_consecutive_shifts = int(staff_parts[5])
        min_consecutive_days_off = int(staff_parts[6])
        max_weekends = int(staff_parts[7])
        
        nurses_model.append(
            Nurse(
                name=nurse_id,
                maximum_number_of_shifts_per_type=max_shifts_dict,
                maximum_work_time=max_total_minutes,
                minimum_work_time=min_total_minutes,
                maximum_consecutive_shifts=max_consecutive_shifts,
                minimum_consecutive_shifts=min_consecutive_shifts,
                minimum_consecutive_days_off=min_consecutive_days_off,
                maximum_weekends=max_weekends,
                days_off=set(),
                preferred_shifts=set(),
                blocked_shifts=set(),
                staff=True,
                min_time_between_shifts=datetime.timedelta(hours=0),
            )
        )
    
    cover_section = next((section for section in sections if section.startswith("COVER")), None)
    cover = cover_section.splitlines()[1:]
    cover = [cover_data.split(",") for cover_data in cover]
    
    

    for shift in shifts_model:
        for cover_data in cover:
            day = int(cover_data[0].strip())
            shift_type = cover_data[1].strip()
            requirement = int(cover_data[2].strip())
            weight_under = int(cover_data[3].strip())
            weight_over = int(cover_data[4].strip())
            if shift.name == f"{day}_{shift_type}":
                shift.demand = requirement
                shift.weight_below_demand = weight_under
                shift.weight_above_demand = weight_over
    
    
    days_off_section = next((section for section in sections if section.startswith("DAYS_OFF")), None)
    days_off = days_off_section.splitlines()[1:-1]
    days_off = [day_off_data.split(",") for day_off_data in days_off]
    
    
    for nurse in nurses_model:
        for day_off_data in days_off:
            nurse_id = day_off_data[0].strip()
            day_indexes = [int(day.strip()) for day in day_off_data[1:]]
            if nurse.name == nurse_id:
                for day_index in day_indexes:
                    for shift in shifts_model:
                        if shift.start_time.date() == start_date + datetime.timedelta(days=day_index):
                            nurse.blocked_shifts.add(shift.uid)
                    
                    nurse.days_off.add(start_date + datetime.timedelta(days=day_index))
    
    
    shift_on_requests_section = next((section for section in sections if section.startswith("SHIFT_ON_REQUESTS")), None)
    shift_on_requests = shift_on_requests_section.splitlines()[1:-1]
    shift_on_requests = [request_data.split(",") for request_data in shift_on_requests]
    
    for nurse in nurses_model:
        for request_data in shift_on_requests:
            nurse_id = request_data[0].strip()
            day = int(request_data[1].strip())
            shift_type = request_data[2].strip()
            weight = int(request_data[3].strip())
            if nurse.name == nurse_id:
                for shift in shifts_model:
                    if shift.name == f"{day}_{shift_type}":
                        nurse.preferred_shifts.add(shift.uid)
                        nurse.preferred_shift_weight[shift.uid] = weight
    
    
    shift_off_requests_section = next((section for section in sections if section.startswith("SHIFT_OFF_REQUESTS")), None)
    shift_off_requests = shift_off_requests_section.splitlines()[1:-1]
    shift_off_requests = [request_data.split(",") for request_data in shift_off_requests]
    for nurse in nurses_model:
        for request_data in shift_off_requests:
            nurse_id = request_data[0].strip()
            day = int(request_data[1].strip())
            shift_type = request_data[2].strip()
            weight = int(request_data[3].strip())
            if nurse.name == nurse_id:
                for shift in shifts_model:
                    if shift.name == f"{day}_{shift_type}":
                        nurse.preferred_off_shifts.add(shift.uid)
                        nurse.preferred_off_shift_weight[shift.uid] = weight
    
    
                    
    shifts_model.sort(key=lambda s: s.start_time)
        
    
    instance = NurseRosteringInstance(
        nurses=nurses_model,
        shifts=shifts_model,
    )
    
    
    
    return instance
    
    
    
    
    
    
if __name__ == "__main__":
    for i in range (1,25):
        
        instance = read_instance(f"backend/app/nurse_rostering/examples/data/Instance{i}.txt")
        print(f"Instance {i} read with {len(instance.nurses)} nurses and {len(instance.shifts)} shifts.")
        
        
        with open(f"backend/app/nurse_rostering/examples/data_processed/Instance{i}.json", 'w') as f:
            f.write(instance.model_dump_json(indent=4))
