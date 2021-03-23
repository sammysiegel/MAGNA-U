# Magnetic Nanoparticle Assembly Utilities (MAGNA-U)
#### Version 1.0
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

### Contents: 
1. **Instructions**
    - Setup and Dependencies
    - Creating an MNP Assembly
    - Simulating an MNP Assembly
    - Saving, Loading, and Managing Data
2. **Full Documentation** 
3. Changelog
4. References

## Instructions
### Setup and Dependencies
To use MAGNA-U, the `magna.py` file should be located inside your
current working directory (the folder you are running the code from).

If the file is in the right place, you should be able to import it like so:
```python
import magna as mu
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
number by which the assembly you create will be referenced. If you give the id
argument a value of `-1` instead, an id number will be generated for you based on
how many `.mnp` data files are located in your `filepath` directory, starting with
0 if there are 0 files. Here are a list of keyword arguments which you can pass if
you want to change their values from the default values:
 - `filepath`: A string with the directory in which data relating to the MNP
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
   
In addition, you can also pass any arguments accepted by the `Lattice` class, which will
determine the shape, size, and packing method of the MNP assembly:
 - `shape`: the shape of one layer of MNPs. Current options are `'hexagon'` and `'circle'`.
    - *default value:* `'hexagon'`
 - `form`: the method of packing/stacking. Current options are `'fcc'` (face-centered cubic),
   `'hcp'` (hexagonal close-packing), `'scp'` (simple close-packing), and `'bcc'` (body-centered cubic).
   - *default value:* `'fcc'`
 - `layer_radius`: For circles, this is the radius of the circle in # of spheres. For hexagons,
   this is the circumradius/side length of the hexagon in # of spheres.
   - *default value:* `3`
- `n_layers`: The number of lattice layers stacked on top of each other.
   - *default value:* `1`
   
### Simulating an MNP Assembly
#### Accessing Individual `discretisedfield` Attributes:
MAGNA-U makes it easy to access the various fields created by `discretisedfield` in
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
import magna as mu
import micromagneticmodel as mm
my_mnp = mu.MNP(id, **kwargs)
M, A, K, U = my_mnp.maku()

system = mm.System(name='my_system')
system.m = M
system.energy = (mm.Demag +
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
is saved to the same directory as specified by the `filepath` attribute of the MNP,
but you can also change where it gets saved to by passing the argument `path` with a
string with the desired directory. Here's an example:

```python
import magna as mu
my_mnp = mu.MNP(0, filepath = './my_directory')
mu.save_mnp(my_mnp, filepath = './my_other_directory')
```
By default, another file is also created which contains a summary of the basic
attributes of the MNP in a markdown format easily readable by a human. If for some
reason you don't want a summary file to be written, pass the argument `summary = False`.

The files that get written will have the names `data_mnp_{id#}.mnp` for the data and
`summary_mnp_{id#}` for the summary files respectively. You should also get printed
confirmation of the file name and path.

#### Loading an MNP
You can use the `load_mnp()` function to load an mnp from a file. Give the id number
of the MNP with the positional `id` argument and the directory of the MNP with the
keyword argument `path`. The default path is `./MNP_Data'. For example:
```python
import magna as mu
my_mnp = mu.load_mnp(0, filepath = './my_other_directory')
```

#### Viewing MNP Data in Python
If you have an active MNP object, you can view the summary data by using the attribute
`summary`. For example:
```python
import magna as mu
my_mnp = mu.MNP(0)
print(my_mnp.summary)
```
This will provide output that looks something like:
```md
###             MNP 0 Summary                       
|                Property                |  Value   |
| -------------------------------------- | -------- |
| ID                                     | 0        |
| R_Total (m)                            | 3.50e-09 |
| R_Shell (m)                            | 3.50e-09 |
| R_Core (m)                             | 3.00e-09 |
| Discretizations per R_total (x, y, z)  | (7,7,7)  |
| Ms_Shell (A/m)                         | 2.40e+05 |
| Ms_Core (A/m)                          | 3.90e+05 |
| A_Shell J/m)                           | 5.00e-12 |
| A_Core (J/m)                           | 9.00e-12 |
| K_Shell (J/m^3)                        | 2.00e+04 |
| K_Core (J/m^3)                         | 5.40e+04 |
| Lattice Name                           | lattice  |
| Lattice Form                           | fcc      |
| Lattice Shape                          | hexagon  |
| Number of Lattice Layers               | 1        |
| Lattice Layer Radius (# of Spheres)    | 3        |

Easy Axes List: [(0.8660254037844386, -0.5, 0), (0.8660254037844386, 0.5, 0), 
(0.8660254037844386, 0.5, 0), (0.8660254037844386, -0.5, 0), 
(0.8660254037844386, -0.5, 0), (0.8660254037844386, 0.5, 0), 
(0.8660254037844386, 0.5, 0), (0.8660254037844386, 0.5, 0), (0, 1, 0), 
(0.8660254037844386, 0.5, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), 
(0, 1, 0), (0.8660254037844386, -0.5, 0), (0.8660254037844386, -0.5, 0), 
(0.8660254037844386, -0.5, 0), (0, 1, 0)]
```
## Full Documentation
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
- `filepath`: A string with the directory in which data relating to the MNP
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
   automatically when a new MNP is instantiated. 
 - `summary`: a string of text containing formatted summary information about an MNP  
   
Tuples are also unpacked and stored as follows:
 - `self.r_total, self.r_shell, self.r_core = r_tuple` 
 - `self.x_divs, self.y_divs, self.z_divs = discretizations`
 - `self.ms_shell, self.ms_core = ms_tuple`
 - `self.a_shell, self.a_core = a_tuple`
 - `self.k_shell, self.k_core = k_tuple`

#### MNP Class Methods
 - `maku(self)`: returns the `m_field`, `a_field`, `k_field`, and `u_field` in that order.

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

- Version 1.0

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