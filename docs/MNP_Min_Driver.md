# MNP MinDriver

The `MNP_MinDriver` class is a child class of `oommfc.MinDriver` and is used to drive both `MNP`
objects and `MNP_System` objects.

`magna.utils.MNP_MinDriver(**kwargs)` (the `**kwargs*` get passed to the parent class)

### Driving an MNP
Use the `drive_mnp(mnp, **kwargs)` method to drive an `MNP` object which is specified by the
`mnp` positional argument. You can also pass any `**kwargs**` that you wish, which will be passed
to the `oommfc.MinDriver.drive(**kwargs)` parent method.

### Driving an MNP System
Use the `drive_system(system, **kwargs)` method to drive an `MNP_System` object which is specified by the
`system` positional argument. You can also pass any `**kwargs**` that you wish, which will be passed
to the `oommfc.MinDriver.drive(**kwargs)` parent method.