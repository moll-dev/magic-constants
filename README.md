# magic-constants
Make constants in python more magic 🪄

A constant library with types in mind. Define a hierarchy of constants, with magic self-validation built in!
More powerful when combined with [multimethods](https://pypi.org/project/multimethod/)!

[SRE NL Talk + Jupyter Notebook](https://moll.dev/slides/magic)

# Features
- Basic immutable value wrapper
- Namespaces for constants
- Input validation / type coercion for any subtype


# Installation 
```bash
pip install magic-constants
```

# Usage
```python
from magic-constants import Constant

class Location(Constant):
    # NB: To make your IDE autocomplete work, you should annotate
    # any sub-constants explicitly. Although, magic-constants will
    # self register with any parent class.
    DataCenter: "DataCenter"

class DataCenter(Location):
    ams1: "ams1"
    lon1: "lon1"

class ams1(DataCenter):
    value = "ams1"

class lon1(DataCenter):
    value = "lon1"

ams1            # DataCenter.ams1('ams1')
ams1()          # DataCenter.ams1('ams1')
ams1().value    # ams1

# Muliple ways to instantiate, type stable output
Location("ams1") == DataCenter("ams1") == Location.DataCenter.ams1 == DataCenter.ams1 == ams1()

# Helpful error messages on validation!

ams1("ams2")
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "/home/tom/repos/magic-constants/magic_constants/metaconstant.py", line 41, in __new__
#     raise ValueError(
# ValueError: 'ams2' cannot be validated as type ams1. Expected 'ams1'

DataCenter("ams2")
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "/home/tom/repos/magic-constants/magic_constants/metaconstant.py", line 32, in __new__
#     raise ValueError(
# ValueError: 'ams2' is not a valid DataCenter. Expected DataCenters: 'ams1', 'lon1'
```

More powerful with Multimethods!

Assume we want to encode some relatively complicated business logic...


| ↓env \ location → | lon1 | ams1 | west1-a | west2-a |
| ----------------- | ---- | ---- | ------- | ------- |
| prod              | ✅  | ✅  | ✅    | ✅       |
| dev               | ❌    | ❌    | ✅       | ✅    |
| pcc               | ❌    | ✅    | ❌       | ❌       |

We want to define a `can_deploy` check that:
- Works in all `Location` for the `Prod` `Environment`
- Works only on `AvailabilityZone`s for the `Dev` `Environment`
- Works only in `ams1` for the `PCC` `Environment`

Define the additonal types...
```python

# Yes, lazy registration works to register AvailabilityZone with Location!
class AvailabilityZone(Location):
    west1_a: "west1_a"
    west2_a: "west2_a"
    
class west1_a(AvailabilityZone):
    value = "west1-a"
    
class west2_a(AvailabilityZone):
    value = "west2-a"

class Environment(Constant):
    pass
    
class Prod(Environment):
    value = "prod"

class Dev(Environment):
    value = "dev"

class PCC(Environment):
    value = "pcc"
```

Define 4 multi methods that dispatch based on the argument types
```python
from multimethod import multimethod

@multimethod
def check(environment:Environment, location:Location):
    # log f"Not a supported deployment combination ({environment}, {location})!"
    # By default, disable all deployments in any Environment or Location
    return False

@multimethod
def check(environment:Prod, location:Location):
    # Works in all `Location` for the `Prod` `Environment`
    return True

@multimethod
def check(environment:Dev, location:AvailabilityZone):
    # Works only on `AvailabilityZone`s for the `Dev` `Environment`
    return True

@multimethod
def check(environment:PCC, location:ams1):
    # Works only in `ams1` for the `PCC` `Environment`
    return True

environments = [Prod(), Dev(), PCC()]
locations = [lon1(), ams1(), west1_a(), west2_a()]

print(f"\t{'\t'.join([str(l) for l in locations])}")
for environment in environments:
    print(environment, end="\t")
    for location in locations:
        val = "✅" if check(environment, location) else "❌"
        print(val, end="\t")
    print()
```