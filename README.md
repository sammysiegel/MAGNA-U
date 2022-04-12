# Magnetic Nanoparticle Assembly Utilities (MAGNA-U)
#### Version 2.8.2

| Description| Badge|
| --------|-------|
| Documentation| [![Docs](https://img.shields.io/static/v1?label=Documentation&message=MAGNA-U&color=red&logo=Read%20the%20Docs&style=for-the-badge)](https://magna-u.readthedocs.io/en/latest/)| 
| Latest Release| [![Release](https://img.shields.io/github/v/release/sammysiegel/MAGNA-U?logo=github&style=for-the-badge)](https://github.com/sammysiegel/MAGNA-U/releases/latest)|



MAGNA-U is a Python module that provides tools to simplify the
modeling and simulation of magnetic nanoparticles (MNPs). MAGNA-U
combines into one place all the previous code that has been
written to model shell/core MnFe2O4/Fe3O4 magnetic nanoparticle
assemblies [^1]. The code is primarily made up of two classes:
`Lattice` and  `MNP`. 

The `Lattice` class is used to generate arbitrary lattices of
close packed spheres in part using code developed by Kathryn Krycka,
Ian Hunt-Isaak, and Yumi Ijiri. The `MNP` class is a subclass of
`Lattice` that models the physical parameters of a magnetic
nanoparticle core-shell assembly and provides tools to simplify
the simulation of such assemblies in [Ubermag](https://github.com/ubermag/workshop) [^2] using [OOMMF](https://math.nist.gov/oommf/) [^3].

Unfortunately, due to the new file structuring system in Version 2.0.0,
files created using an older version will not be compatible with the new
version using the `load_mnp()` function.

### Contents: 
1. **Instructions**
    - Installation and Dependencies
    - Creating an MNP Assembly
    - Simulating an MNP Assembly
    - Saving, Loading, and Managing Data
    - Plotting Data  
2. **Full Documentation** 
3. Changelog
4. References

## Instructions
### Installation and Dependencies

It is recommended that you  download the MAGNA-U
    package directly from Github at [https://github.com/sammysiegel/MAGNA-U](https://github.com/sammysiegel/MAGNA-U). This is easy
   to do on the command line. Just go to the directory you wish to download to and do:
   
```bash
git init
git clone https://github.com/sammysiegel/MAGNA-U
```

If you are running in an Anaconda environment, you can use the `install.py` script that
comes with MAGNA-U to easily install to the right place. Simply run:

```bash
cd MAGNA-U
python install.py
```

This will install MAGNA-U to a location like `/[path_to_anaconda]/envs/[env_name]/lib/python3.8/site-packages`.
If you are not in an Anaconda environment, you can run a command like this:

```bash
cd MAGNA-U
PYTHONUSERBASE=/path/to/install/location pip install .
```

You can check what the correct path is by running in Python:
```python
import sys
print(sys.path)
```

This will give you a list of places which will work to put the package.

You can test to see whether MAGNA-U is working by running in the MAGNA-U directory:

```python
python testthis.py
```
   
Once it is installed you can import using:
```python
import magna.utils as mu
```

MAGNA-U requires an environment with Python 3.8. It also requires Ubermag to be
installed in your environment. Specifically, the following packages currently
must be available in your environment in order to work:
 - `ast, csv, random, time, os` from Python Standard Library
 - `numpy`, `pandas`, and `scipy`
 - `discretisedfield`, `micromagneticmodel`, and `oommfc` from Ubermag
 - `matplotlib` and `k3d` for plotting
 - `opencv-python` (import as `cv2`) 
 - `networkx` for constructing graphs

### Creating an MNP Assembly
Generating an MNP assembly is done through the `MNP` class. `MNP` is also a
subclass of `Lattice`, so any argument that `Lattice` accepts will also be
accepted by `MNP`. To generate an MNP assembly, simply create a new instance
of the class:
```python
my_mnp = mu.MNP(id, **kwargs)
```
The argument `id` is a required positional argument that should be an integer
number by which the assembly you create will be referenced. 
If you give the id argument a value of `-1` instead, an id number will be generated for you based on
how many `mnp_*` directories are located in your `directory/name` directory, starting with
0 if there are 0. Here are a list of keyword arguments which you can pass if
you want to change their values from the default values:
 - `name`: This can be any string you want. The name can be used to describe the
   usage of the MNP, for example `'varying_a'`, but by default it will just be the
   date that the mnp is created.
   - *default value:* `time.strftime('%b_%d', time.localtime())` (The current date in
     the format like 'Apr-14')
 - `directory`: A string with the directory in which data relating to the MNP
   assembly will be stored. If you pass the name of a directory that does not
   already exist, the program will create it for you.
    - *default value*: `'./MNP_Data'`
 - `r_tuple`: This function takes a tuple of three values in the form
   `(r_total, r_shell, r_core)`where r_total is the total radius between
   individual MNPs, r_shell is the radius of the shell, and r_core is the radius
   of the core, all in meters.
    - *default value*: `(4e-9, 3.5e-9, 3e-9)`
 -  `discretizations`: this takes a tuple of three values in the form (x, y, z), 
    where x, y, and z are the number of divisions per r_total that determines how
    small each cell is in your simulation for each respective axis. A larger number
    makes more divisions and smaller cells. For example, putting 7 for x would
    result in a total x discretization length of r_total/7.
     - *default value:* `(4,4,4)`
 - `ms_tuple`: This function takes a tuple of two values in the form
   `(ms_shell, ms_core)`where ms_shell is the saturation magnetization of the
   shell, and ms_core is the saturation magnetization of the core, all in A/m.
    - *default value*: `(2.4e5, 3.9e5)`
 - `a_tuple`: This function takes a tuple of two values in the form
   `(a_shell, a_core)`where a_shell is the exchange stiffness constant of the
   shell, and a_core is the exchange stiffness constant of the core, all in J/m.
    - *default value*: `(5e-12, 9e-12)` 
 - `k_tuple`: This function takes a tuple of two values in the form
   `(k_shell, k_core)`where k_shell is the magnetic anisotropy constant of the
   shell, and k_core is the magnetic anisotropy constant of the core, all in J/m^3.
    - *default value*: `(2e4, 5.4e4)`
 - `axes`: This is used to specify the easy axes for uniaxial anistropy in each MNP.
   If you omit this argument, a new random set of easy axes will be generated, but
   you can pass a list of axes here if you want to use predefined easy axes.
    - *default value:* `None`
 - `shape`: the shape of one layer of MNPs. Current options are `'hexagon'`, `'circle'`, and `'rectangle'`.
    - *default value:* `'hexagon'`
 - `form`: the method of packing/stacking. Current options are `'fcc'` (face-centered cubic),
   `'hcp'` (hexagonal close-packing), `'scp'` (simple close-packing), and `'bcc'` (body-centered cubic).
   - *default value:* `'fcc'`
 - `layer_radius`: Specify this for circle or hexagon shapes.For circles, this is the radius of the 
   circle in # of spheres. For hexagons, this is the circumradius/side length of the hexagon in # of spheres.
   - *default value:* `3`
- `layer_dims`: Specify this for rectangular shapes. This is a tuple (x, y) with the dimensions of a
  layer in # of spheres. Note that because the y spacing is smaller than the x spacing, a `layer_dims`
  of `(3, 3)` will not be a square. Rather, y should be multiplied by 2*sqrt(3), so the closest
  dimensions for a square would be `layer_dims = (3, 10)`
   - *default value:* `(3, 10)`
- `n_layers`: The number of lattice layers stacked on top of each other.
   - *default value:* `1`
   
### Simulating an MNP Assembly
#### The Easy Way: `quick_drive()`
***NEW***
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
field, will be saved to the 'directory/name/mnp_id' directory for later access.

Note that all of the default `MNP_System` attributes will be used when generating the
system, meaning that Exchange, Uniaxial Anisotropy, Demag, and a Zeeman field of +0.1 T
in the +z direction will be included in the energy equation.

#### Creating a Custom System
***NEW***
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
    
#### Driving a Custom System
In order to drive a custom `MNP_System`, you can you the 'MNP_MinDriver' class:
```python
import magna.utils as mu
my_mnp = mu.MNP(0, name = 'my_name', directory = 'my_MNP_data')
my_system = mu.MNP_System(my_mnp)
my_system.initialize(m0 = (0, 0, 1), Zeeman = False)
md = mu.MNP_MinDriver()
md.drive_system(my_system)
```

#### Generating All "MAKU" Attributes at Once
When running an Ubermag simulation, it is often necessary to generate fields for
magnetization (M), exchange stiffness constant (A), magnetic anisotropy constant (K),
and uniaxial anisotropy easy axes (U). As such there is a way to generate all four
fields at once using the `maku()` function. For example:
```python
M, A, K, U = my_mnp.maku()
```
The name "maku" tells you the order in which to put the four variables which you want
to assign to the respective fields: `m_field`, `a_field`, `k_field`, and `u_field`.
Storing the fields in the form of variables like this is also very helpful as it will 
require less typing and make it so that you don't have to generate a field every time
you call a field attribute.

#### Setting up an Ubermag `System`
By using the field attributes of an MNP assembly, it makes it easy to set up a `System`
object using the `micromagneticmodel` package of Ubermag. An example is shown below:
```python
import magna.utils as mu
import micromagneticmodel as mm
my_mnp = mu.MNP(id, **kwargs)
M, A, K, U = my_mnp.maku()

system = mm.System(name='my_system')
system.m = M
system.energy = (mm.Demag() +
                 mm.Exchange(A=A) +
                 mm. UniaxialAnisotropy(K=K, u=U))
```
Of course, you can add whatever energy terms are appropriate for your simulation.

### Saving, Loading, and Managing Data
MAGNA-U provides several tools for managing the data pertaining to an MNP assembly.
#### Saving an MNP
If you have generated an MNP object within your code, you can save a record of all of
its basic attributes to a file using the `save_mnp()` function. The function takes as
a positional argument the name of an instance of an MNP object. By default, the file
is saved to the same directory as specified by the `directory` attribute of the MNP,
but you can also change where it gets saved to by passing the argument `filepath` with a
string with the desired directory. Here's an example:

```python
import magna.utils as mu
my_mnp = mu.MNP(0, name = 'my_name', filepath = './my_directory')
mu.save_mnp(my_mnp, filepath = './my_other_directory')
```
By default, another file is also created which contains a summary of the basic
attributes of the MNP in a markdown format easily readable by a human. If for some
reason you don't want a summary file to be written, pass the argument `summary = False`.

The files that get written will have the names `data_mnp_{id#}.mnp` for the data and
`summary_mnp_{id#}` for the summary files respectively. You should also get printed
confirmation of the file name and path.

#### Loading an MNP
***NEW*** You can use the `load_mnp()` function to load an mnp from a file. Give the id number
of the MNP with the positional `id` argument , the name of the MNP with the keyword argument
`name`, and the and the directory of the MNP with the keyword argument `fukepath`. The default
filepath is `./MNP_Data'. For example:
```python
import magna.utils as mu
my_mnp = mu.load_mnp(0, name = 'my_name', filepath = './my_other_directory')
```
Additionally, you can have m, a, k, and/or u fields be preloaded from files by passing the
`fields` argument with a string containing the fields you want to be loaded. None will be
loaded by default, but you could might want to pass `fields = 'maku'`, for example. The fields
that you want to load have to already be saved to that MNP's data folder.

#### Viewing MNP Data in Python
If you have an active MNP object, you can view the summary data by using the attribute
`summary`. For example:
```python
import magna.utils as mu
my_mnp = mu.MNP(0, name = 'my_name')
print(my_mnp.summary)
```
This will provide output that looks something like:
```md
###             MNP 0 Summary                       
|                Property                |   Value    |
| -------------------------------------- | ---------- |
| ID                                     | 0          |
| R_Total (m)                            | 3.50e-09   |
| R_Shell (m)                            | 3.50e-09   |
| R_Core (m)                             | 3.00e-09   |
| Discretizations per R_total (x, y, z)  | (7,7,7)    |
| Ms_Shell (A/m)                         | 2.40e+05   |
| Ms_Core (A/m)                          | 3.90e+05   |
| A_Shell J/m)                           | 2.50e-12   |
| A_Core (J/m)                           | 4.50e-12   |
| K_Shell (J/m^3)                        | 2.00e+04   |
| K_Core (J/m^3)                         | 5.40e+04   |
| Lattice Name                           | my_name    |
| Lattice Form                           | fcc        |
| Lattice Shape                          | hexagon    |
| Number of Lattice Layers               | 1          |
| Lattice Layer Radius (# of Spheres)    | 3          |
| Lattice Layer Dimensions (# of spheres)| (0 , 0 )   |

Easy Axes List: [(0.8660254037844386, 0.5, 0), ...]
```

#### Saving and Loading Fields
If you want to save the fields associated with an MNP Assembly (m_field, a_field, k_field,
u_field), you can do this with the `save_fields()` method of the `MNP` class. You can pass
the argument `filepath` to change the directory the fields get saved to, and you can change
which fields get saved with the `fields` parameter. `fields` takes a string of letters
corresponding to the names of fields, such as `maku`. Put in this string the fields that you
want to save. For example, if you only want to save the m_field and a_field, put `fields = 'ma'`.
The default is `fields = 'maku'`.
Here's a full example:
```python
import magna.utils as mu
my_mnp = mu.MNP(5, name = 'my_name', filepath = './my_directory')
my_mnp.save_fields(filepath = './my_other_directory', fields='ma')
```
You can then load fields of an MNP Assembly by using the `load_fields()` method. It takes the same
two parameters as `save_fields()`, but it is important that the order in which you put the letters
in the string `fields` will determine in what order the fields are outputted. The default is 
`fields = 'maku'`.
```python
import magna.utils as mu
my_mnp = mu.MNP(5, name = 'my_name', filepath = './my_directory')
M, A = my_mnp.load_fields(filepath = './my_other_directory', fields='ma')
```

### Plotting Data
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

#### 2D Vector Plot
The method `MNP_Analyzer.mpl_center_vectors()` will create a 2D plot of the magnetization vectors for the center of each MNP sphere using Matplotlib. The vectors are colored by their z component. This method only supports 1 layer MNP assemblies currently. 

#### 3D Vector Plot
The method `MNP_Analyzer.k3d_center_vectors()` will create a 3D plot of the magnetization
vectors for the center of each MNP sphere using k3d. You can have the vector field be
colored by either the z component (default) or the xy angle component by using
`color_field = 'z'` or `color_field = 'angle'` respectively. Coloring using the xy angles
will likely take significantly longer than coloring using z.
   
### Changelog
 - Version 2.8.2 (12 April 2022)
    - `genmesh2.py` now removes the first line of zeros in array before saving it
 - Version 2.8.1 (6 April 2022)
    - bug fixes
 - Version 2.8.0 (21 March 2022)
    - Changed 864 axes choices to 24 for `save_averaged_data()`
    - Added `'random_nn'` (one of 12 nearest neighbors) as option for easy axes
    - Allows pre-generated csv files for mesh points to be used to more efficiently generate MAKU fields
    - Pre-written code for pre-generating csvs in the `MAGNA-U/mesh-making` folder
- Version 2.7.1 (7 February 2022)
    - When saving data with `save_averaged_data`, `extract_domain_csv`, or `extract_average_domain_data`, the list of region/domain sizes are now saved in the csv files
    - When saving data with `extract_domain_csv`, or `extract_average_domain_data`, the applied X and Y magnetic fields (`Bx`, and `By`) are now saved in addition to the Z field (`Bz`)
 - Version 2.7.0 (26 January 2022)
    - New statistic: 2-3 Particle Fraction
    - Can save multiple `axes_range_data` csv files with `save_averaged_data()` by if you iterate the `step` attribute of each `MNP_Domain_Analyzer`.
    - You can extract multiple steps for an MNP with `extract_average_domain_data`
    - Print statements to indicate the time taken to perform various tasks
    - some bug fixes
- Version 2.6.1 (10 November 2021)
    - fixed bug with `save_averaged_data`
    - `extract_average_domain_data` can specify the start mnp and the end mnp
- Version 2.6.0 (1 November 2021)
    - `drives generate json files
    - `extract_domain_csvs` can get the magnetic field data from the .json files
    - angle_finder can offset theta/phi by specified d_theta, d_phi
    -you can now perform domain statistics for many values of d_theta/d_phi and save those with `mu.MNP_Domain_Analyzer.save_averaged_data`
    - you can average data from the different d_theta/d_phi from multiple MNPs and save it to one csv with `mu.extract_average_domain_data`
- Version 2.5.2 (17 August 2021)
    - `install.py` bugfixes
    - updated documentation to reflect new default values for `MNP` attributes
- Version 2.5.1 (16 August 2021)
    - updated `testthis.py` to test new features/dependencies
    -  updated extract_domain_csv() to add `number` parameter, which allows you to specify the number of mnps to extract data from
- Version 2.5.0 (15 Aug 2021)
    - reverted back to original distance finding method from cdist
    - added MNP_Domain_Analyzer
         - now using networks to find domain regions
         - metrics: characteristic size, max size, mean size, free particle fraction
         - region plots: as spheres or vectors
         - saving domain region data/getting summary data
    - added choice of easy axes with axes_type:'random_hexagonal', 'random_plane', 'all_random'
    - extract_domain_csv, to return domain data from several mnps as one csv
- Version 2.4.0 (11 June 2021)
    - `k3d_center_vectors()`: addition of coloring by layer with `color_field = 'layer'`, 
      scaling with `scale`, and color mapping with `cmap`.
- Version 2.3.4 (9 Jun 2021)
    - fixed `MNP_Analyzer.extract()` to allow it to extract angle values for centers
        not in the `z = 0` plane
- Version 2.3.1 (27 May 2021)
    - addition of testthis.py
    - MNP_Analyzer Preloading fixes
    - MNP_system name attribute changed to 'DELETE'
    - install.py can add `matplotlib.use('Agg')`
- Version 2.3.0 (22 May 2021)
    - Multiple drives of an MNP can now be run and saved in the `Drives` directory, with the
        `step` parameter added to the `MNP_Analyzer` to load a specific drive.
    - The `MNP_HysteresisDriver` can run hysteresis on an MNP, saving final magnetic field and
        summary data for each step.
    - The `MNP_Hysteresis_Analyzer` can be used to plot hysteresis loops, plots for each step
        of the hysteresis, and movies of the hysteresis.
    - `Install.py` will now prompt you to install `opencv-python` package if not already installed
      (used for making hysteresis movies)
- Version 2.2.0 (12 May 2021)
    - `MNP_Analyzer` now has the `extract()` method which saves center magnetization data,
        and vector center plots now use this data, making them much faster if already extracted.
    -  `MNP_Analyzer.mpl_vector_centers()` method can now plot colored by z component or xy angle
        using the `color_field` parameter.
- Version 2.1.2 (4 May 2021)
    - Fixed markdown parsing errors in the documentation
    - Added `install.py` for easy install on Anaconda
- Version 2.1.1 (3 May 2021)
    - Updated documentation using readthedocs.io and mkdocs
    - Updated `README.md` to remove full documentation and instead link to the readthedocs website
    - `MNP.save_fields` method will now initialize fields before saving if not already initialized
- Version 2.1.0 (3 May 2021)
  - Added new method `MNP_Analyzer.mpl_center_vectors()` for plotting and saving 2D vector plots 
  - Changed default file type for plots to PNG from PDF (can be specified)
- Version 2.0.0 (14 April 2021)
  - Added new classes (`MNP_System`, `MNP_MinDriver`, `MNP_Analyzer`)
  - Added `quick_drive()` function
  - Restructured file system to by name/mnp id, keeping all files in one folder
  - built in plot options with `MNP_Analyzer`: xy angle, z, xy angle scalar only,
    z scalar only, k3d sphere center magnetization vector plot
  - Changed m_field, a_field, k_field, and u_field attributes from being properties
    that automatically generate a field to needing to be specifically initialized with
    the new `MNP.initialize()` method. These fields then don't have to be regenerated
    once this is done.
- Version 1.1.1 (1 April 2021)
  - Improved documentation for rectangular shapes
  - Changed default `layer_dims` for `MNP` to `(3,10)`  
- Version 1.1.0 (1 April 2021)
  - addition of `save_fields()` and `load_fields()` methods for `MNP`
  - support for making `'rectangle'` shaped MNP assemblies
  - addition of `scaled_coords` property of `MNP`  
- Version 1.0.1 (23 March 2021)
  - `setup.py` fixes for install on hpc cluster
- Version 1.0.0 (22 March 2021)

### References
[^1]: Y. Ijiri, et. al. Correlated spin canting in ordered core-shell
Fe3O4/MnFexFe3-xO4 nanoparticle assemblies.
*Physical Review B* **99**, 094421 (2019).

[^2]: M. Beg, R. A. Pepper, and H. Fangohr. User interfaces for computational
science: A domain specific language for OOMMF embedded in Python.
*AIP Advances* **7**, 56025 (2017).
[https://doi.org/10.1063/1.4977225](https://doi.org/10.1063/1.4977225)

[^3]: M.J. Donahue and D. G. Porter. OOMMF User's Guide, Version 1.0,
Interagency Report NISTIR 6376. National Institute of Standards and
Technology, Gaithersburg, MD (Sept 1999).
