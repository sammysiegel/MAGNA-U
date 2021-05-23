# MNP HysteresisDriver

The `MNP_HysteresisDriver` class is designed to run hysteresis loops on `MNP` objects. It is a
child class of `oommfc.HysteresisDriver`.

`magna.utils.MNP_HysteresisDriver(**kwargs)` (the `**kwargs*` get passed to the parent class)

### Driving an MNP

To drive a hysteresis of an MNP, use the `drive_hysteresis()` method:
```python
MNP_HysteresisDriver.drive_hysteresis(self, mnp, 
                                      Hmin=(0, 10, -1 / micromagneticmodel.consts.mu0), 
                                      Hmax=(0, 0, 1 / micromagneticmodel.consts.mu0), 
                                      n=10, **kwargs)
```
Pass to this method the `MNP` object to be driven, the minimum Zeeman field to be applied (in A/m),
the maximum Zeeman field to be applied (also in A/m), the number of steps between min and max, and
any additional keyword arguments that will then be passed to the driver, such as `runner`.

Here's a full example:
```python
import magna.utils as mu
my_mnp = mu.MNP(0, name = 'my_mnp')
hd = mu.MNP_HysteresisDriver()
hd.drive(my_mnp, n = 5)
```

The MNP will then be driven through the specified number of steps between minimum field and maximum
field and back again. For each step, summary data of the run will be saved and the data for all the
runs will get saved to the file `hysteresis_data.csv` in the MNP's data folder. The final magnetizations
for each step will get saved to the `drives` directory in the MNP's data folder.