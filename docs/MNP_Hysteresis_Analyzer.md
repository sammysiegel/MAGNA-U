# MNP Hysteresis Analyzer

The `MNP_Hysteresis_Analyzer` class can be used to produce hysteresis-related plots and movies
based on the hysteresis data of an `MNP`. It is a child class of `MNP_Analyzer`.

`magna.utils.MNP_Hysteresis_Analyzer`

### Hysteresis Loop Plots
To plot a hysteresis loop, use the `hyst_loop_plot()` method.

```python
MNP_Hysteresis_Analyzer.hyst_loop_plot(self, x=None, y=None, figsize=(10,10), 
                                        x_label = 'Applied Field (T)', 
                                        y_label = 'Sample Magnetization (a.u.)',
                                        title = None, filename = None, 
                                        filetype = None, **kwargs)

```
By default, the plot will be of `Bz`, the z component of the external magnetic field, on the x axis (in T)
and `mz`, the z component of the magnetization (normalized from -1 to 1). You can also change the
`x_label` label of the x-axis, the `y_label` label of the y-axis, and the `title`.

### Hysteresis Steps Plots
The `hyst_steps_plot()` method makes a 2D plot of the magnetic field using one of the plots
available from the [MNP_Analyzer](MNP_Analyzer.md#whole-system-plots).

```python
MNP_Hysteresis_Analyzer.hyst_steps_plot(self, type = 'xy', name=None, ax=None, title=None,
                                        z_plane=0, figsize=(50, 50), filename=None, 
                                        filetype=None, scalar_cmap=None, vector_cmap=None, 
                                        scalar_clim=None, **kwargs)
```

The `type` parameter determines what kind of plot gets made: either `'xy'`, `'z'`, `'xy_scalar'`,
or `'z_scalar'`. The remaining arguments are all the same as are accepted by the respective
2D-plotting methods. The images will be saved to the Plots directory in the MNP data folder
under a new directory called `name` (defaults to the kind of plot made).

### Hysteresis Movies
You can make a movie stitching together one type of 2D magnetic field plots from each step
of the hysteresis using the `hyst_movie` method. This makes use of the OpenCV python package.

```python
MNP_Hysteresis_Analyzer.hyst_movie(self, type = 'xy', movie_name=None, name=None, **kwargs)
```

The `type` parameter determines what kind of plot gets made: either `'xy'`, `'z'`, `'xy_scalar'`,
or `'z_scalar'`. The `movie_name` determines the filepath the movie gets saved to.
