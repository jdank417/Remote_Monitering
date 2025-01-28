import json

import self

with open("../DSPM/src/DSPM/resources/machines.json", "r") as file:
    self.machines = json.load(file)
