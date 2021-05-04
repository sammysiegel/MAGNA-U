# Lattice

### Lattice Class Attributes
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

### Lattice Class Primary Methods
- `__init__(self, name='lattice', form = 'hcp', shape = 'circle', n_layers = 3, 
  layer_radius = 0, layer_dims=(0,0))`: initialization function
- `layer_coords(self, layer, z=False)`: A function to return the coordinates of a 
  specified layer. The `layer` argument is the index of the layer, starting at 0 and
  ending with `n_layers - 1`. The argument `z` specifies whether the z coordinates
  of the layer are returned or not. If `False`, a 2D array is returned with the
  x and y coordinates of the layer. If `True`, a 3D array is returned with the
  x, y, and z coordinates.
- `list_coords(self)`: A function that returns all of the coordinates of the
  lattice, including all of the layers. Use this if you need a list of all of the
  coordinates of sphere centers in the lattice.
- `mpl(self)`: This method will make a 2D plot of the lattice using matplotlib,
  showing all of the layers projected onto the xy plane.
- `k3d(self, point_size=.8, color = True)`: This will make a 3D plot of the lattice
  using k3d using the x, y, and z coordinates of all of the layers. `point_size`
  will adjust the size of the spheres in the lattice, and `color` will determine
  whether or not each layer of the lattice is in a different color.

### Lattice Class Other Functions
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