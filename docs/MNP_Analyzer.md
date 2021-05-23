# MNP Analyzer

You can use the `MNP_Analyzer` class to generate plots to analyze the magnetization data
of an MNP. To start, generate an instance of the class using the MNP you wish to analyze.
```python
import magna.utils as mu
my_mnp = mu.load_mnp(0, name = 'my_name', filepath = './my_directory')
plotter = mu.MNP_Analyzer(my_mnp)
```
If you don't specify, the `MNP_Analyzer` will try to load the `m_final` field you have
written to the MNP's data folder. If you don't wish for this to happen, pass `preload_field = False`.
To use a different field, you should access the `MNP_Analyzer.field` attribute such as:
```python
plotter.field = my_specified_field
```
Once a field is loaded, you can plot it with a combination vector/scalar plot, a
scalar only plot, or a 3D plot of the magnetization vectors of the center of each sphere.
The first two kinds of plots will be automatically saved to your mnp data folder in a
subdirectory called 'plots'.

#### Load a particular drive
As of Version 2.3.0, you can load a particular drive of an MNP if it is saved in the `Drives`
folder by using the `step` argument when initializing. For example:
```python
import magna.utils as mu
my_mnp = mu.load_mnp(0, name = 'my_name', filepath = './my_directory')
plotter = mu.MNP_Analyzer(my_mnp, step = 3)
```

### Whole-System Plots
The following plotting options make a plot of each cell of the MNP system in the
specified plane.
#### Vector/Scalar Plot Options:
 - `MNP_Analyzer.xy_plot()`: A plot with the scalar colors showing the angle of the magnetization
   vectors projected onto the xy plane, in radians.
 - `MNP_Analyzer.z_plot()`: A plot with the scalar colors showing the z component of the magnetization

Both of these plots are based on the `df.Field.mpl()` method and can accept any argument that
it accepts. You can also easily set the title with the `title` argument.

#### Scalar Only Plot Options:
 - `MNP_Analyzer.xy_scalar_plot()`: A plot with the scalar colors showing the angle of the magnetization
   vectors projected onto the xy plane, in radians.
 - `MNP_Analyzer.z_scalar_plot()`: A plot with the scalar colors showing the z component of the magnetization

Both of these plots are based on the `df.Field.mpl_scalar()` method and can accept any argument that
it accepts. You can also easily set the title with the `title` argument.

### Vector Center Magnetization Plots
The following plotting options will produce plots only of the center cells of each MNP.
This makes it easier to analyze but requires this data to be extracted from the field data.
This is done through the `MNP_Analyzer.extract()` method, which will extract the data
and save it to a file called 'centers_data.csv'. This way, it need only be done once.
If you have not already extracted the data and make one of the following plots, the data
will be automatically extracted, which might take some time.
#### 2D Vector Plot
The method `MNP_Analyzer.mpl_center_vectors()` will create a 2D plot of the magnetization vectors for the center of each MNP sphere using Matplotlib. 
The vectors are colored by their z component if the argument `color_field='z'` is given or their xy-angle if `color_field='angle'` is given. 
This method only supports 1 layer MNP assemblies currently. 

#### 3D Vector Plot
The method `MNP_Analyzer.k3d_center_vectors()` will create a 3D plot of the magnetization
vectors for the center of each MNP sphere using k3d. You can have the vector field be
colored by either the z component (default) or the xy angle component by using
`color_field = 'z'` or `color_field = 'angle'` respectively.