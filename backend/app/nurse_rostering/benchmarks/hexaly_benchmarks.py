from nurse_rostering.solvers.hexaly.model.solver import NurseRosteringModel
from nurse_rostering.data_schema import NurseRosteringInstance, NurseRosteringSolution

import json
with open("backend/app/nurse_rostering/examples/data_processed/Instance1.json", "r") as f:
    instance_data = f.read()
data = json.loads(instance_data)
instance = NurseRosteringInstance.model_validate_json(instance_data)

nurse_rostering_model = NurseRosteringModel(instance)
solution = nurse_rostering_model.solve()
print(solution)