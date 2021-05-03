# `MNP` Class

## Attributes
- `id`: This is a required positional argument which uses a whole number to designate the
  MNP assembly. If you pass `-1` for the id, the id will be automatically generated
  based on how many existing mnp_* folders are in the directory `[directory]/[name]`, starting
  with 0 if there are none.
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