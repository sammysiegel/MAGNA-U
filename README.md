# Magnetic Nanoparticle Assembly Utilities (MAGNA-U)
#### Version 2.1.0

Version 2.1.0 documentation is still a WIP.

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

***NEW*** Unfortunately, due to the new file structuring system in Version 2.0.0,
files created using an older version will not be compatible with the new
version using the `load_mnp()` function.

### Contents: 
1. **Instructions**
    - Setup and Dependencies
    - Creating an MNP Assembly
    - Simulating an MNP Assembly
    - Saving, Loading, and Managing Data
    - Plotting Data  
2. **Full Documentation** 
3. Changelog
4. References

## Instructions
### Setup and Dependencies

There are two ways to install MAGNA-U:
1. Place the python file in inside your current working directory (the folder you
   are running the code from). You can find the code on Box at 
   `/oommf/Sammy/ubermag/MAGNA-U/magna/utils.py`.
   If the file is in the right place, you should be able to import it like so:
    ```python
    import utils as mu
    ```
2. To avoid having to transfer files between devices, you can download the MAGNA-U
    package from Github at [https://github.com/sammysiegel/MAGNA-U](https://github.com/sammysiegel/MAGNA-U). This is easy
   to do on the command line. Just go to the directory you wish to download to and do:
   ```bash
   git init
   git clone https://github.com/sammysiegel/MAGNA-U
   ```
   From there you can access the file. Additionally, it is pretty easy to install
    the package with pip so you can make it available in your environment without
   having to worry about whether it is in your directory or not. You just need to
   find the right path. If you are using an Anaconda environment, that will look
   something like `/[path_to_anaconda]/envs/[env_name]/lib/python3.8/site-packages`.
   Once you have downloaded the MAGNA-U repository from Github, do the following:
   ```bash
   cd MAGNA-U
   PYTHONUSERBASE=/[path_to_anaconda]/envs/[env_name]/lib/python3.8/site-packages pip install .
   ```
   
    If this doesn't work you can check what the correct path is by running in Python:
    ```python
    import sys
    print(sys.path)
    ```
    This will give you a list of places which will work to put the package.
   
   Once it is installed you can import using:
    ```python
    import magna.utils as mu
    ```

MAGNA-U requires an environment with Python 3.8. It also requires Ubermag to be
installed in your environment. Specifically, the following packages currently
must be available in your environment in order to work:
 - `ast, csv, random, time, os` from Python Standard Library
 - `numpy`
 - `discretisedfield` from Ubermag

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
***NEW*** If you give the id argument a value of `-1` instead, an id number will be generated for you based on
how many `mnp_*` directories are located in your `directory/name` directory, starting with
0 if there are 0. Here are a list of keyword arguments which you can pass if
you want to change their values from the default values:
 - ***New*** `name`: This can be any string you want. The name can be used to describe the
   usage of the MNP, for example `'varying_a'`, but by default it will just be the
   date that the mnp is created.
   - *default value:* `time.strftime('%b_%d', time.localtime())` (The current date in
     the format like 'Apr-14')
 - ***NEW*** `directory`: A string with the directory in which data relating to the MNP
   assembly will be stored. If you pass the name of a directory that does not
   already exist, the program will create it for you.
    - *default value*: `'./MNP_Data'`
 - `r_tuple`: This function takes a tuple of three values in the form
   `(r_total, r_shell, r_core)`where r_total is the total radius between
   individual MNPs, r_shell is the radius of the shell, and r_core is the radius
   of the core, all in meters.
    - *default value*: `(3.5e-9, 3.5e-9, 3e-9)`
 -  `discretizations`: this takes a tuple of three values in the form (x, y, z), 
    where x, y, and z are the number of divisions per r_total that determines how
    small each cell is in your simulation for each respective axis. A larger number
    makes more divisions and smaller cells. For example, putting 7 for x would
    result in a total x discretization length of r_total/7.
     - *default value:* `(7,7,7)`
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
***NEW*** In order to drive a custom `MNP_System`, you can you the 'MNP_MinDriver' class:
```python
import magna.utils as mu
my_mnp = mu.MNP(0, name = 'my_name', directory = 'my_MNP_data')
my_system = mu.MNP_System(my_mnp)
my_system.initialize(m0 = (0, 0, 1), Zeeman = False)
md = mu.MNP_MinDriver()
md.drive_system(my_system)
```

#### Accessing Individual `discretisedfield` Attributes:
***WARNING: Deprecated*** MAGNA-U makes it easy to access the various fields created by `discretisedfield` in
Ubermag. These are all implemented using the `@property` decorator, meaning you
can use them like you would use any attribute of the class. WARNING: these objects
may take a long time to generate depending on the size of your MNP assembly.
 - `mesh`: a Mesh object that is of the right size and cell size for the
   MNP assembly.
 - `m_field`: a three-dimensional Field object representing the initial
   magnetization of your MNP assembly. Initial magnetization directions are
   generated randomly.
 - `a_field`: a one-dimensional Field object representing the exchange stiffness
   constant for every cell in the mesh.
 - `k_field`: a one-dimensional Field object representing the magnetic anisotropy
   constant for every cell in the mesh.
 - `u_field`: a three-dimensional Field object representing the uniaxial anisotropy
   easy axis for each point in the mesh.
   
#### Generating All Attributes at Once
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
***NEW*** You can use the `MNP_Analyzer` class to generate plots to analyze the magnetization data
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

## Full Documentation
***WARNING: Some of this is Deprecated***
#### Lattice Class Attributes
- `name`: This is currently optional and can be whatever you want. The default is just
  `'lattice'`.
- `form`: This specifies the kind of packing. Options are `'hcp'` (default), `'fcc'`,
  `'scp'`, and `'bcc'`.
- `shape`: This specifies the shape of a lattice layer. Options are `'circle'`
  (default), `'hexagon'`, and `'rectangle'`.
- `n_layers`: The number of lattice layers stacked on top of each other. The default
  is `n_layers = 3`
- `layer_radius`: This attribute must be specified for circle and hexagon shapes.
  For circles, this is the radius of the circle in # of spheres. For hexagons, this is
  the circumradius/side length of the hexagon in # of spheres.
- `layer_dims`: This attribute must be specified for rectangular shapes. Provide a
  tuple in the form (x, y), where x and y are an integer number of spheres.

#### Lattice Class Primary Methods
- `__init__(self, name='lattice', form = 'hcp', shape = 'circle', n_layers = 3, 
  layer_radius = 0, layer_dims=(0,0))`: initialization function
- `layer_coords(self, layer, z=False)`: A function to return the coordinates of a 
  specified layer. The `layer` argument is the index of the layer, starting at 0 and
  ending with `n_layers - 1`. The argument `z` specifies whether the z coordinates
  of the layer are returned or not. If `False`, a 2D array is returned with the
  x and y coordinates of the layer. If `True`, a 3D array is returned with the
  x, y, and z coordinates.
- `list_coordinates(self)`: A function that returns all of the coordinates of the
  lattice, including all of the layers. Use this if you need a list of all of the
  coordinates of sphere centers in the lattice.
- `mpl(self)`: This method will make a 2D plot of the lattice using matplotlib,
  showing all of the layers projected onto the xy plane.
- `k3d(self, point_size=.8, color = True)`: This will make a 3D plot of the lattice
  using k3d using the x, y, and z coordinates of all of the layers. `point_size`
  will adjust the size of the spheres in the lattice, and `color` will determine
  whether or not each layer of the lattice is in a different color.

#### Lattice Class Other Functions
- `gen_coords(num=37, length=10)`: This function is used to generate the (x, y)
  coordinates for a hexagon-shaped layer of hcp/fcc lattice. This code was developed
  for earlier research by Kathryn Krycka, Ian Hunt-Isaak, and Yumi Ijiri.
    - `num_rings(num)`: Returns the number of rings in a hexagon of `num` spheres,
      rounded up if the number of points passed is not able to generate a complete 
      hexagon. This is used by `gen_coords()` function.
    - `num_points(rings)`: This is the inverse of `num_rings`; it returns the number
      of points in a hexagon of `rings` rings.
- `cubic_packing_coords(layer_spacing=1, layer_radius=0, shape='circle',
  layer_dims=(0,0))`: This function is used to generate the (x, y) coordinates of a
  layer of scp/bcc lattice in any of the three shapes.
- `hexa_packing_coords(layer_spacing=1/(3**.5 * 2/3), layer_radius=0,
  shape='circle', layer_dims=(0,0))`: This function is used to generate the
  (x, y) coordinates of a layer of hcp/fcc lattice. It can generate in any of
  the three shapes, and it calls the `gen_coords()` function for hexagons.
  
#### MNP Class Base Attributes
- `directory`: A string with the directory in which data relating to the MNP
   assembly will be stored. If you pass the name of a directory that does not
   already exist, the program will create it for you.
    - *default value*: `'./MNP_Data'`
 - `r_tuple`: This function takes a tuple of three values in the form
   `(r_total, r_shell, r_core)`where r_total is the total radius between
   individual MNPs, r_shell is the radius of the shell, and r_core is the radius
   of the core, all in meters.
    - *default value*: `(3.5e-9, 3.5e-9, 3e-9)`
 -  `discretizations`: this takes a tuple of three values in the form (x, y, z), 
    where x, y, and z are the number of divisions per r_total that determines how
    small each cell is in your simulation for each respective axis. A larger number
    makes more divisions and smaller cells. For example, putting 7 for x would
    result in a total x discretization length of r_total/7.
     - *default value:* `(7,7,7)`
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
   
#### MNP Class `discretisedfield` Attributes
 - `mesh`: a Mesh object that is of the right size and cell size for the
   MNP assembly.
 - `m_field`: a three-dimensional Field object representing the initial
   magnetization of your MNP assembly. Initial magnetization directions are
   generated randomly.
 - `a_field`: a one-dimensional Field object representing the exchange stiffness
   constant for every cell in the mesh.
 - `k_field`: a one-dimensional Field object representing the magnetic anisotropy
   constant for every cell in the mesh.
 - `u_field`: a three-dimensional Field object representing the uniaxial anisotropy
   easy axis for each point in the mesh.
   
#### MNP Class Other Attributes
 - `coord_list`: a list of the coordinates of all of the centers of a sphere, generated
   automatically when a new MNP is instantiated. The spacing between each center is one unit.
 - `scaled_coords`: a list of coordinates of all of the centers of spheres, scaled by `r_total`
   to be phyisically representative of the MNP scale.
 - `summary`: a string of text containing formatted summary information about an MNP  
   
Tuples are also unpacked and stored as follows:
 - `self.r_total, self.r_shell, self.r_core = r_tuple` 
 - `self.x_divs, self.y_divs, self.z_divs = discretizations`
 - `self.ms_shell, self.ms_core = ms_tuple`
 - `self.a_shell, self.a_core = a_tuple`
 - `self.k_shell, self.k_core = k_tuple`

#### MNP Class Methods
 - `maku(self)`: returns the `m_field`, `a_field`, `k_field`, and `u_field` in that order.
 - `save_fields(self,  filepath='default', fields='maku')`: saves all of the fields specified
    by `fields` to the directory specified by `filepath` (if `default` or unspecified, it is
    saved to `self.filepath`). `fields` takes a string of letters in any order where `'m'`
    corresponds to `self.m_field`, `'a'` corresponds to `self.a_field`, `'k'` corresponds to
    `self.k_field`, and `'u'` corresponds to `self.u_field`.
 - `load_fields(self, fields='maku', filepath = 'default')`: Loads fields associated with an `MNP`.
    The `fields` and `filepath` arguments function the same way as for `save_fields()`. Returns
    the fields as a list in the order they are specified by `fields`.

The other functions in the class are used by other methods/attributes and will not
usually need to be called by the user:
 - `make_easy_axes(self)`: generates a list of random easy axes
 - `if_circle(self, point, r)`: for a given 3D point determines whether that point is
   within a radius `r` of any sphere center in `coord_list`
 - `ms_func(self, point)`: used to determine the saturation magnetization value of a
   point based on whether it is in the outside, shell, or core of an MNP
 - `a_func(self, point)`: used to determine the exchange stiffness constant of a
   point based on whether it is in the outside, shell, or core of an MNP
 - `k_func(self, point)`: used to determine the magnetic anisotropy constant of a
   point based on whether it is in the outside, shell, or core of an MNP
 - `circle_index(self, point, n_list)`: returns the index of a sphere center in `n_list`
   which is closest to the point.
 - `u_func(self, point)`: used to determine the uniaxial anisotropy easy axis of a
   point based on whether it is in the outside, shell, or core of an MNP
   
#### Additional Functions
 - `save_mnp(mnp, summary=True, filepath='default')`: saves the specified `mnp` to a
   file in the directory given by `filepath` with the name `data_mnp_{id#}.mnp`. If
   `summary=True`, it also saves a markdown formatted readable file with summary 
   information with the name `summary_mnp_{id#}.md`
   
### Changelog

- Version 2.1.0 (3 May 2021)
  - Added new method `MNP_Analyzer.mpl_center_vectors()` for plotting and saving 2D vector plots 
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
