# Quick Drive
It is very easy to quickly drive an MNP assembly you have created just with the 
`quick_drive()` function. It's as easy as this:

```python
import magna.utils as mu
mnp = mu.MNP(0, name = 'my_name', directory = 'my_MNP_data')
mu.quick_drive(mnp)
```
With that, a system will automatically be created for you, and all of the necessary
fields will be generated, and the system will be driven with an OOMMF MinDriver.
The MNP data and all of the fields generated, including the final driven magnetization
field, will be saved to the `'{directory}/{name}/{mnp_id}'` directory for later access.

Note that all of the default `MNP_System` attributes will be used when generating the
system, meaning that Exchange, Uniaxial Anisotropy, Demag, and a Zeeman field of +0.1 T
in the +z direction will be included in the energy equation.