# MNP System

MAGNA-U has a built in class called `MNP_System` that is a subclass of `micromagneticmodel.System`
which can be used to create a system with customized specifications. The first step is to
generate a system by doing:
```python
import magna.utils as mu
my_mnp = mu.MNP(0, name = 'my_name', directory = 'my_MNP_data')
my_system = mu.MNP_System(my_mnp)
```
Because `MNP_System` is a subclass of `mm.System`, you can also give
any arguments that are also accepted by the parent class.

The next step is to initialize the system. You can do this as you would with an `mm.System`
object, by setting `system.m` and `system.energy`. However, you can do it more easily by
using the `initialize()` method of `MNP_System`. Here are a list of arguments you can pass
to the `initialize()` method:

 - `m0`: this is the initial magnetization of each point in the system. By default, this is
    random, but you can also pass a 3vector tuple like `(0, 0, 1)` to make the initial
    magnetization be in a particular direction.
    - *default value:* `m0 = 'random'`
 - `Demag`: determines whether the system will include Demag in its energy equation
     - *default value:* `Demag = True`
 - `Exchange`: determines whether the system will include Exchange energy   
     - *default value:* `Exchange = True`
 - `UniaxialAnisotropy`: determines whether the system will include uniaxial anisotropy energy   
     - *default value:* `UniaxialAnisotropy = True`
 - `Zeeman`: determines whether the system will include a Zeeman energy term
     - *default value:* `Zeeman = True`
 - `H`: if `Zeeman = True`, this is the 3vector in A/m for the external magnetic field
    to be applied.
     - *default value:* `H = (0, 0, .1/mm.consts.mu0)` (0.1 T in the +Z direction)