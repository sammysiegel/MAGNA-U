import numpy as np
import csv
import random
from ast import literal_eval as make_list
import discretisedfield as df
import os
import micromagneticmodel as mm
import oommfc as mc
import time
import matplotlib.pyplot as plt


def num_rings(num):
    n = 1
    while 3 * n * (n - 1) + 1 < num:
        n += 1
    return n


def num_points(rings):
    return 3 * rings * (rings - 1) + 1


def gen_coords(num=37, length=10):
    n = 0
    Nrows = num_rings(num)
    coords = np.zeros((3 * Nrows * (Nrows - 1) + 1, 2))
    height_factor = np.sqrt(3.0) / 2.0;

    for row in range(1, Nrows + 1):
        n_in_row = 2 * Nrows - row
        if row % 2 != 0:
            for c in np.arange(-(n_in_row - 1) // 2, (n_in_row - 1) // 2 + 1):
                coords[n][0] = c * length
                coords[n][1] = (row - 1) * length * height_factor
                n += 1
                if row != 1:
                    coords[n][0] = c * length
                    coords[n][1] = -(row - 1) * length * height_factor
                    n += 1
        else:
            for c in np.arange(-n_in_row / 2 + .5, n_in_row / 2):
                coords[n][0] = c * length
                coords[n][1] = (row - 1) * length * height_factor
                n += 1
                coords[n][0] = c * length
                coords[n][1] = -(row - 1) * length * height_factor
                n += 1
    return coords


def cubic_packing_coords(layer_spacing=1, layer_radius=0, shape='circle', layer_dims=(0, 0)):
    coords = []
    if shape == 'rectangle':
        l, w = layer_dims
        for x in range(-l // 2 + 1, l // 2 + 1):
            for y in range(-w // 2 + 1, w // 2 + 1):
                coords.append([x * layer_spacing, y * layer_spacing])
    else:
        for x in range(-layer_radius, layer_radius + 1):
            for y in range(-layer_radius, layer_radius + 1):
                if shape == 'circle':
                    if x ** 2 + y ** 2 < layer_radius ** 2:
                        coords.append([x * layer_spacing, y * layer_spacing])
                if shape == 'hexagon':
                    if abs(x) <= (2 * layer_radius - abs(y) - 1) // 2:
                        coords.append([x * layer_spacing, y * layer_spacing])
    return np.array(coords)


def hexa_packing_coords(layer_spacing=1 / (3 ** .5 * 2 / 3), layer_radius=0, shape='circle', layer_dims=(0, 0)):
    coords = []
    if shape == 'rectangle':
        l, w = layer_dims
        for x in range(0, l):
            for y in range(0, w):
                coords.append(((2 * x + (y) % 2) * layer_spacing, (3 ** .5) * (y / 3) * layer_spacing))
    else:
        for x in range(-2 * layer_radius, 2 * layer_radius + 1):
            for y in range(-2 * layer_radius, 2 * layer_radius + 1):
                if shape == 'circle':
                    if (2 * x + y % 2) ** 2 + ((3 ** .5) * (y / 3)) ** 2 <= layer_radius ** 2:
                        coords.append([(2 * x + (y) % 2) * layer_spacing, (3 ** .5) * (y / 3) * layer_spacing])
                if shape == 'hexagon':
                    coords = gen_coords(length = 1, num = num_points(layer_radius)).reshape(-1, 2)
                    coords = coords.dot([[0, -1], [1, 0]])  # 90° rotation to make it compatible with circle/rect coords
    return np.array(coords)


class Lattice:
    def __init__(self, name='lattice', form='hcp', shape='circle', n_layers=3, layer_radius=0, layer_dims=(0, 0)):
        """name: can be whatever you want

           form: the kind of packing; either 'hcp' (default), 'fcc', 'scp' (simple cubic), or 'bcc'

           shape: the shape of a layer: either 'circle' (default), 'hexagon', or 'rectangle'

           n_layers: the number of layers stacked on top of each other

           layer_radius: for hexagon or circle shapes; this is the radius of the circle or circumradius of the hexagon, in # of spheres

           layer_dims: for rectangle shape; this is the (x, y) dimensions of a layer as a tuple where x and y are # of spheres"""
        self.name = name
        if form != 'hcp' and form != 'fcc' and form != 'scp' and form != 'bcc':
            raise NameError("Form must be one of 'hcp', 'fcc', 'scp', or 'bcc'.")
        self.form = form
        if shape != 'rectangle' and shape != 'circle' and shape != 'hexagon':
            raise NameError("Shape must be one of 'circle', 'hexagon', or 'rectangle'.")
        self.shape = shape
        if type(n_layers) != type(0) or n_layers < 1:
            raise AttributeError("n_layers should have a positive integer value")
        if type(layer_radius) != type(0) or layer_radius < 0:
            raise AttributeError("layer_radius should have a positive integer value")
        if type(layer_dims) != type((0, 0)) or len(layer_dims) != 2:
            raise AttributeError("layer_dims should be an integer tuple of the form (x, y)")
        self.n_layers = n_layers
        if layer_radius == 0 and shape != 'rectangle':
            raise AttributeError("lattice of shape 'hexagon' or 'circle' must have a nonzero layer_radius")
        self.layer_radius = layer_radius
        x, y = layer_dims
        if type(x) != type(0) or type(y) != type(0) or x < 0 or y < 0:
            raise AttributeError("layer_dims should be an integer tuple of the form (x, y)")
        if layer_dims == (0, 0) and shape == 'rectangle':
            raise AttributeError("lattice of shape 'rectangle should have a nonzero (x, y) for layer_dims'")
        self.layer_dims = layer_dims

    def layer_coords(self, layer, z=False):
        if self.form == 'hcp' or 'fcc':
            coords = hexa_packing_coords(layer_radius = self.layer_radius, layer_dims = self.layer_dims,
                                         shape = self.shape)
            if not z:
                if self.form == 'hcp':
                    if layer % 2 == 0:
                        return coords
                    elif layer % 2 == 1:
                        coords[:, 0] = coords[:, 0] + 3 ** .5 / 3
                        return coords
                elif self.form == 'fcc':
                    if layer % 3 == 0:
                        return coords
                    elif layer % 3 == 1:
                        coords[:, 0] = coords[:, 0] + 3 ** .5 / 3
                        return coords
                    elif layer % 3 == 2:
                        coords[:, 0] = coords[:, 0] + 3 ** .5 / 6
                        coords[:, 1] = coords[:, 1] + .5
                        return coords
            elif z:
                if self.form == 'hcp':
                    if layer % 2 == 0:
                        z0 = np.linspace(layer * 6 ** .5 / 3, layer * 6 ** .5 / 3, len(coords[:, 0])).reshape(
                            len(coords[:, 0]), 1)
                        return np.append(coords, z0, 1)
                    elif layer % 2 == 1:
                        coords[:, 0] = coords[:, 0] + 3 ** .5 / 3
                        z1 = np.linspace(layer * 6 ** .5 / 3, layer * 6 ** .5 / 3, len(coords[:, 0])).reshape(
                            len(coords[:, 0]), 1)
                        return np.append(coords, z1, 1)
                elif self.form == 'fcc':
                    if layer % 3 == 0:
                        z0 = np.linspace(layer * 6 ** .5 / 3, layer * 6 ** .5 / 3, len(coords[:, 0])).reshape(
                            len(coords[:, 0]), 1)
                        return np.append(coords, z0, 1)
                    elif layer % 3 == 1:
                        coords[:, 0] = coords[:, 0] + 3 ** .5 / 3
                        z1 = np.linspace(layer * 6 ** .5 / 3, layer * 6 ** .5 / 3, len(coords[:, 0])).reshape(
                            len(coords[:, 0]), 1)
                        return np.append(coords, z1, 1)
                    elif layer % 3 == 2:
                        coords[:, 0] = coords[:, 0] + 3 ** .5 / 6
                        coords[:, 1] = coords[:, 1] + .5
                        z2 = np.linspace(layer * 6 ** .5 / 3, layer * 6 ** .5 / 3, len(coords[:, 0])).reshape(
                            len(coords[:, 0]), 1)
                        return np.append(coords, z2, 1)
        if self.form == 'scp' or 'bcc':
            coords = cubic_packing_coords(layer_radius = self.layer_radius, layer_dims = self.layer_dims,
                                          shape = self.shape)
            if not z:
                if self.form == 'scp':
                    return coords
                elif self.form == 'bcc':
                    if layer % 2 == 0:
                        return coords
                    elif layer % 2 == 1:
                        coords = coords + .5
                        return coords
            if z:
                if self.form == 'scp':
                    z0 = np.linspace(layer, layer, len(coords[:, 0])).reshape(len(coords[:, 0]), 1)
                    return np.append(coords, z0, 1)
                elif self.form == 'bcc':
                    if layer % 2 == 0:
                        z0 = np.linspace(layer / 2, layer / 2, len(coords[:, 0])).reshape(len(coords[:, 0]), 1)
                        return np.append(coords, z0, 1)
                    elif layer % 2 == 1:
                        coords = coords + .5
                        z1 = np.linspace(layer / 2, layer / 2, len(coords[:, 0])).reshape(len(coords[:, 0]), 1)
                        return np.append(coords, z1, 1)

    def mpl(self):
        '''makes a 2d plot of the lattice using matplotlib'''
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for layer in range(self.n_layers):
            plt.scatter(self.layer_coords(layer)[:, 0], self.layer_coords(layer)[:, 1])
        ax.set_aspect(1.0, adjustable = 'box')
        plt.show()

    def k3d(self, point_size=.8, color=True):
        '''makes a 3d plot of the lattice using k3d visualization'''
        import k3d
        plot = k3d.plot(name = 'lattice_plot')
        if not color:
            for layer in range(self.n_layers):
                plot += k3d.points(positions = self.layer_coords(layer, z = True), point_size = point_size)
        if color:
            color_list = [0x0054a7, 0xe41134, 0x75ac4f, 0xf4ea19, 0xffaff8, 0xa35112, 0x15e3f4, 0xcfc7ff]
            for layer in range(self.n_layers):
                plot += k3d.points(positions = self.layer_coords(layer, z = True), point_size = point_size,
                                   color = color_list[layer % 8])
        plot.display()

    def list_coords(self):
        '''returns a -1x3 numpy array with the list of all of the coordinates of sphere centers in the lattice'''
        all_coords = np.empty((0, 0))
        for layer in range(self.n_layers):
            all_coords = np.append(all_coords, self.layer_coords(layer, z = True))
        return all_coords.reshape(-1, 3)


class MNP(Lattice):
    def __init__(self, id,
                 r_tuple=(3.5e-9, 3.5e-9, 3e-9),
                 discretizations=(7, 7, 7),
                 ms_tuple=(2.4e5, 3.9e5),
                 a_tuple=(5e-12, 9e-12),
                 k_tuple=(2e4, 5.4e4),
                 name=time.strftime('%b_%d', time.localtime()),
                 form='fcc',
                 shape='hexagon',
                 n_layers=1,
                 layer_radius=3,
                 layer_dims=(3, 10),
                 axes=None,
                 directory=os.path.join(os.getcwd(), 'MNP_Data'),
                 loaded_fields=''):
        super().__init__(name = name, form = form, shape = shape, n_layers = n_layers, layer_radius = layer_radius,
                         layer_dims = layer_dims)

        self.coord_list = self.list_coords()

        self.dirpath = os.path.join(directory, name)
        if not os.path.isdir(self.dirpath):
            os.makedirs(self.dirpath)
            print('New directory created for MNP Data files: ', self.dirpath)

        if id == -1:
            path, dirs, files = next(os.walk(self.dirpath))
            self.id = len(dirs)
            print('MNP ID Generated: ', self.id)
        else:
            self.id = id

        self.filepath = os.path.join(directory, name, 'mnp_{}'.format(self.id))
        if not os.path.isdir(self.filepath):
            os.makedirs(self.filepath)
        print('Filepath: ', self.filepath)

        self.r_total, self.r_shell, self.r_core = r_tuple
        self.x_divs, self.y_divs, self.z_divs = discretizations
        self.ms_shell, self.ms_core = ms_tuple
        self.a_shell, self.a_core = a_tuple
        self.k_shell, self.k_core = k_tuple

        if axes is None:
            self.easy_axes = self.make_easy_axes()
        else:
            self.easy_axes = axes

        self.initialized = False
        self.m_field = None
        self.a_field = None
        self.k_field = None
        self.u_field = None

        if 'm' in loaded_fields:
            self.m_field = self.load_fields(fields = 'm')[0]
            self.initialized = True
        if 'a' in loaded_fields:
            self.a_field = self.load_fields(fields = 'a')[0]
            self.initialized = True
        if 'k' in loaded_fields:
            self.k_field = self.load_fields(fields = 'k')[0]
            self.initialized = True
        if 'u' in loaded_fields:
            self.u_field = self.load_fields(fields = 'u')[0]
            self.initialized = True

    @property
    def scaled_coords(self):
        scaled = []
        for n in self.coord_list:
            i, j, k = n
            scaled.append((2 * i * self.r_total, 2 * j * self.r_total, 2 * k * self.r_total))
            return scaled

    def make_easy_axes(self):
        possible_axes = [(0, 1, 0), (3 ** .5 / 2, .5, 0), (3 ** .5 / 2, -.5, 0)]
        axes_list = []
        for _ in self.coord_list:
            axes_list.append(possible_axes[random.randint(0, 2)])
        return axes_list

    def if_circle(self, point, r):
        x, y, z = point
        for n in self.coord_list:
            i, j, k = n
            if ((x - 2 * i * self.r_total) ** 2 + (y - 2 * j * self.r_total) ** 2 + (
                    z - 2 * k * self.r_total) ** 2) ** .5 < r:
                return True
        else:
            return False

    def ms_func(self, point):
        if self.if_circle(point, self.r_shell) and self.if_circle(point, self.r_core):
            return self.ms_core  # Fe3O4 Exchange stiffness constant (J/m)
        elif self.if_circle(point, self.r_shell) and not self.if_circle(point, self.r_core):
            return self.ms_shell  # MnFe2O4 Exchange stiffness constant (J/m)
        else:
            return 0

    def a_func(self, point):
        if self.if_circle(point, self.r_shell) and self.if_circle(point, self.r_core):
            return self.a_core  # Fe3O4 Exchange stiffness constant (J/m)
        elif self.if_circle(point, self.r_shell) and not self.if_circle(point, self.r_core):
            return self.a_shell  # MnFe2O4 Exchange stiffness constant (J/m)
        else:
            return 0

    def k_func(self, point):
        if self.if_circle(point, self.r_shell) and self.if_circle(point, self.r_core):
            return self.k_core  # Fe3O4 Exchange stiffness constant (J/m)
        elif self.if_circle(point, self.r_shell) and not self.if_circle(point, self.r_core):
            return self.k_shell  # MnFe2O4 Exchange stiffness constant (J/m)
        else:
            return 0

    def circle_index(self, point, n_list):
        x, y, z = point
        n_list = n_list.tolist()
        for n in n_list:
            i, j, k = n
            if ((x - 2 * i * self.r_total) ** 2 + (y - 2 * j * self.r_total) ** 2 + (
                    z - 2 * k * self.r_total) ** 2) ** .5 < self.r_total:
                return n_list.index(n)

    def u_func(self, point):
        if not self.if_circle(point, self.r_shell):
            return (0, 0, 1)
        else:
            return self.easy_axes[self.circle_index(point, self.coord_list)]

    @property
    def mesh(self):
        if self.shape != 'rectangle':
            return df.Mesh(
                p1 = (-2 * self.layer_radius * self.r_total, -2 * self.layer_radius * self.r_total, -self.r_total),
                p2 = (2 * self.layer_radius * self.r_total, 2 * self.layer_radius * self.r_total,
                      2 * self.n_layers * self.r_total),
                cell = (self.r_total / self.x_divs, self.r_total / self.y_divs, self.r_total / self.z_divs))
        elif self.shape == 'rectangle':
            return df.Mesh(
                p1 = (-self.r_total, -self.r_total, -self.r_total),
                p2 = (4 * self.layer_dims[0] * self.r_total, self.layer_dims[1] * self.r_total + self.r_total,
                      2 * self.n_layers * self.r_total),
                cell = (self.r_total / self.x_divs, self.r_total / self.y_divs, self.r_total / self.z_divs))

    def make_m_field(self, m0 = 'random'):
        if m0 == 'random':
            self.m_field = df.Field(self.mesh, dim = 3, value = lambda point: [2 * random.random() - 1 for _ in range(3)],
                                    norm = self.ms_func)
        elif type(m0) == type((0,0,0)):
            self.m_field = df.Field(self.mesh, dim = 3,
                                    value = m0,
                                    norm = self.ms_func)

    def make_a_field(self):
        self.a_field = df.Field(self.mesh, dim = 1, value = self.a_func)

    def make_k_field(self):
        self.k_field = df.Field(self.mesh, dim = 1, value = self.k_func)

    def make_u_field(self):
        self.u_field = df.Field(self.mesh, dim = 3, value = self.u_func)

    def initialize(self, fields='maku', autosave=True, m0 = 'random'):
        if 'm' in fields:
            self.make_m_field(m0 = m0)
        if 'a' in fields:
            self.make_a_field()
        if 'k' in fields:
            self.make_k_field()
        if 'u' in fields:
            self.make_u_field()
        self.initialized = True
        if autosave:
            save_mnp(self)
            self.save_fields(fields = fields)

    def maku(self):
        if not self.initialized:
            self.initialize()
        return self.m_field, self.a_field, self.k_field, self.u_field

    def save_fields(self, filepath='default', fields='maku'):
        if filepath == 'default':
            path = self.filepath
        else:
            path = filepath
        if 'm' in fields:
            self.m_field.write(os.path.join(path, 'm_field_mnp_{}.ovf'.format(self.id)))
        if 'a' in fields:
            self.a_field.write(os.path.join(path, 'a_field_mnp_{}.ovf'.format(self.id)))
        if 'k' in fields:
            self.k_field.write(os.path.join(path, 'k_field_mnp_{}.ovf'.format(self.id)))
        if 'u' in fields:
            self.a_field.write(os.path.join(path, 'u_field_mnp_{}.ovf'.format(self.id)))

    def save_any_field(self, field, field_name, filepath='default'):
        if filepath == 'default':
            path = self.filepath
        else:
            path = filepath
        field.write(os.path.join(path, '{}_mnp_{}.ovf'.format(field_name, self.id)))

    def load_fields(self, fields='maku', filepath='default'):
        if filepath == 'default':
            path = self.filepath
        else:
            path = filepath
        output = []
        for f in fields:
            output.append(df.Field.fromfile(os.path.join(path, '{}_field_mnp_{}.ovf'.format(f, self.id))))
        return output

    def load_any_field(self, field_name, filepath='default'):
        if filepath == 'default':
            path = self.filepath
        else:
            path = filepath
        return df.Field.fromfile(os.path.join(path, '{}_mnp_{}.ovf'.format(field_name, self.id)))

    def save_all(self):
        save_mnp(self)
        self.save_fields()

    @property
    def summary(self):
        return ('###             MNP {} Summary                       \n'
                '|                Property                |  Value   |\n'
                '| -------------------------------------- | -------- |\n'
                '| ID                                     | {:<8} |\n'
                '| R_Total (m)                            | {:<8.2e} |\n'
                '| R_Shell (m)                            | {:<8.2e} |\n'
                '| R_Core (m)                             | {:<8.2e} |\n'
                '| Discretizations per R_total (x, y, z)  | ({},{},{})  |\n'
                '| Ms_Shell (A/m)                         | {:<8.2e} |\n'
                '| Ms_Core (A/m)                          | {:<8.2e} |\n'
                '| A_Shell J/m)                           | {:<8.2e} |\n'
                '| A_Core (J/m)                           | {:<8.2e} |\n'
                '| K_Shell (J/m^3)                        | {:<8.2e} |\n'
                '| K_Core (J/m^3)                         | {:<8.2e} |\n'
                '| Lattice Name                           | {:<8} |\n'
                '| Lattice Form                           | {:<8} |\n'
                '| Lattice Shape                          | {:<8} |\n'
                '| Number of Lattice Layers               | {:<8} |\n'
                '| Lattice Layer Radius (# of Spheres)    | {:<8} |\n'
                '\n'
                'Easy Axes List: {}'.format(self.id, self.id, self.r_total, self.r_shell, self.r_core,
                                            self.x_divs, self.y_divs, self.z_divs,
                                            self.ms_shell, self.ms_core,
                                            self.a_shell, self.a_core,
                                            self.k_shell, self.k_core,
                                            self.name,
                                            self.form,
                                            self.shape, self.n_layers, self.layer_radius,
                                            self.easy_axes))


def save_mnp(mnp, summary=True, filepath='default'):
    if filepath == 'default':
        path = mnp.filepath
    else:
        path = filepath
    data_list = [mnp.id, (mnp.r_total, mnp.r_shell, mnp.r_core),
                 (mnp.x_divs, mnp.y_divs, mnp.z_divs),
                 (mnp.ms_shell, mnp.ms_core),
                 (mnp.a_shell, mnp.a_core),
                 (mnp.k_shell, mnp.k_core),
                 mnp.name,
                 mnp.form,
                 mnp.shape,
                 mnp.n_layers,
                 mnp.layer_radius, mnp.easy_axes]
    with open(os.path.join(path, 'data_mnp_{}.mnp'.format(mnp.id)), 'w') as f:
        write = csv.writer(f)
        write.writerow(data_list)
    print('MNP Data Saved: ', os.path.join(path, 'data_mnp_{}.mnp'.format(mnp.id)))
    if summary:
        with open(os.path.join(path, 'summary_mnp_{}.md'.format(mnp.id)), 'w') as f:
            f.write(mnp.summary)
        print('MNP Summary Saved: ', os.path.join(path, 'summary_mnp_{}.md'.format(mnp.id)))


def load_mnp(id, name='lattice', filepath='./MNP_Data', fields=''):
    with open(os.path.join(filepath, name, 'mnp_{}'.format(id), 'data_mnp_{}.mnp'.format(id)), 'r') as f:
        csv_reader = list(csv.reader(f))
        mnp_data = []
        for i in csv_reader:
            for j in i:
                mnp_data.append(j)
        return MNP(id, r_tuple = make_list(mnp_data[1]), discretizations = make_list(mnp_data[2]),
                   ms_tuple = make_list(mnp_data[3]),
                   a_tuple = make_list(mnp_data[4]), k_tuple = make_list(mnp_data[5]), name = str(mnp_data[6]),
                   form = str(mnp_data[7]),
                   shape = str(mnp_data[8]), n_layers = int(mnp_data[9]), layer_radius = int(mnp_data[10]),
                   axes = make_list(mnp_data[11]), directory = filepath, loaded_fields = fields)


class System(mm.System):
    def __init__(self, mnp, **kwargs):
        super(System, self).__init__(name = '{}_{}'.format(mnp.name, mnp.id), **kwargs)
        self.mnp = mnp

    def initialize(self, m0='random', Demag=True, Exchange=True, UniaxialAnisotropy=True, Zeeman=True,
                   H=(0, 0, .1 / mm.consts.mu0)):
        if not self.mnp.initialized:
            self.mnp.initialize(m0 = m0)
        self.m = self.mnp.m_field
        self.energy = 0
        if Demag:
            self.energy += mm.Demag()
        if Exchange:
            self.energy += mm.Exchange(A = self.mnp.a_field)
        if UniaxialAnisotropy:
            self.energy += mm.UniaxialAnisotropy(K = self.mnp.k_field, u = self.mnp.u_field)
        if Zeeman:
            self.energy += mm.Zeeman(H = H)


class MinDriver(mc.MinDriver):
    def __init__(self, **kwargs):
        super(MinDriver, self).__init__(**kwargs)

    def drive_mnp(self, mnp, **kwargs):
        system = System(mnp)
        system.initialize()
        self.drive(system, **kwargs)
        mnp.save_any_field(system.m, field_name = 'm_final', filepath = mnp.filepath)

    def drive_system(self, system, **kwargs):
        self.drive(system, **kwargs)
        system.mnp.save_any_field(system.m, field_name = 'm_final', filepath = system.mnp.filepath)


def quick_drive(mnp, **kwargs):
    md = MinDriver()
    md.drive_mnp(mnp, **kwargs)


class Plots:
    def __init__(self, mnp, preload_field=True):
        self.mnp = mnp
        self.path = os.path.join(self.mnp.filepath, 'plots')
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        if preload_field:
            self.field = self.mnp.load_any_field('m_final')

    def xy_plot(self, **kwargs):
        fig = plt.figure(figsize = (50, 50))
        ax = fig.add_subplot(111)

        ax.set_title('MNP {} XY Plot'.format(self.mnp.id))
        self.field.orientation.plane(z = 0).mpl(ax = ax, figsize = (50, 50),
                                                scalar_field = self.field.orientation.plane(z = 0).angle,
                                                vector_color_field = self.field.orientation.z, vector_color = True,
                                                vector_colorbar = True, scalar_cmap = 'hsv', vector_cmap = 'binary',
                                                scalar_clim = (0, 6.28),
                                                filename = os.path.join(self.path, 'angle_plot.pdf'), **kwargs)

    def z_plot(self, **kwargs):
        fig = plt.figure(figsize = (50, 50))
        ax = fig.add_subplot(111)

        ax.set_title('MNP {} XY Plot'.format(self.mnp.id))
        self.field.orientation.plane(z = 0).mpl(ax = ax, figsize = (50, 50),
                                                filename = os.path.join(self.path, 'angle_plot.pdf'), **kwargs)
