import json
import numpy as np
import csv
import random
from ast import literal_eval as make_list
import discretisedfield as df
from discretisedfield import util as dfu
import os
import micromagneticmodel as mm
import oommfc as mc
import time
import matplotlib
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt
import k3d
import pandas as pd
import cv2
from scipy.spatial.distance import cdist
import networkx as nx


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
                    coords = gen_coords(length=1, num=num_points(layer_radius)).reshape(-1, 2)
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
            coords = hexa_packing_coords(layer_radius=self.layer_radius, layer_dims=self.layer_dims,
                                         shape=self.shape)
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
            coords = cubic_packing_coords(layer_radius=self.layer_radius, layer_dims=self.layer_dims,
                                          shape=self.shape)
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
        ax.set_aspect(1.0, adjustable='box')
        plt.show()

    def k3d(self, point_size=.8, color=True):
        '''makes a 3d plot of the lattice using k3d visualization'''
        import k3d
        plot = k3d.plot(name='lattice_plot')
        if not color:
            for layer in range(self.n_layers):
                plot += k3d.points(positions=self.layer_coords(layer, z=True), point_size=point_size)
        if color:
            color_list = [0x0054a7, 0xe41134, 0x75ac4f, 0xf4ea19, 0xffaff8, 0xa35112, 0x15e3f4, 0xcfc7ff]
            for layer in range(self.n_layers):
                plot += k3d.points(positions=self.layer_coords(layer, z=True), point_size=point_size,
                                   color=color_list[layer % 8])
        plot.display()

    def list_coords(self):
        '''returns a -1x3 numpy array with the list of all of the coordinates of sphere centers in the lattice'''
        all_coords = np.empty((0, 0))
        for layer in range(self.n_layers):
            all_coords = np.append(all_coords, self.layer_coords(layer, z=True))
        return all_coords.reshape(-1, 3)


class MNP(Lattice):
    def __init__(self, id,
                 r_tuple=(4.25e-9, 3.7e-9, 3.2e-9),
                 discretizations=(4, 4, 4),
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
                 axes_type='random_hexagonal',
                 directory=os.path.join(os.getcwd(), 'MNP_Data'),
                 mesh_csv=None,
                 loaded_fields=''):
        super().__init__(name=name, form=form, shape=shape, n_layers=n_layers, layer_radius=layer_radius,
                         layer_dims=layer_dims)

        self.axes_type = axes_type
        self.coord_list = self.list_coords()
        self.mesh_csv = mesh_csv

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

        self.distance_matrix = None
        self.is_in_mnp = None
        self.point_list = None
        self.n = 0

        if 'm' in loaded_fields:
            self.m_field = self.load_fields(fields='m')[0]
            self.initialized = True
        if 'a' in loaded_fields:
            self.a_field = self.load_fields(fields='a')[0]
            self.initialized = True
        if 'k' in loaded_fields:
            self.k_field = self.load_fields(fields='k')[0]
            self.initialized = True
        if 'u' in loaded_fields:
            self.u_field = self.load_fields(fields='u')[0]
            self.initialized = True

    @property
    def scaled_coords(self):
        scaled = []
        for n in self.coord_list:
            i, j, k = n
            scaled.append((2 * i * self.r_total, 2 * j * self.r_total, 2 * k * self.r_total))
        return np.array(scaled)

    def make_easy_axes(self):
        possible_axes = [(0, 1, 0), (3 ** .5 / 2, .5, 0), (3 ** .5 / 2, -.5, 0)]
        if self.axes_type == 'random_hexagonal':
            axes_list = [(possible_axes[random.randint(0, 2)]) for _ in range(len(self.coord_list))]
        elif self.axes_type == 'random_plane':
            axes_list = [(2 * np.random.random() - 1, 2 * np.random.random() - 1, 0) for _ in
                         range(len(self.coord_list))]
        elif self.axes_type == 'all_random':
            axes_list = [(2 * np.random.random() - 1, 2 * np.random.random() - 1, 2 * np.random.random() - 1) for _ in
                         range(len(self.coord_list))]
        elif self.axes_type == 'random_nn':
            G = nx.Graph()
            for i in range(len(self.coord_list)):
                G.add_node(i)
            for i in range(len(self.coord_list)):
                for j in range(len(self.coord_list)):
                    r = self.coord_list[i] - self.coord_list[j]
                    if 0 < (r[0] ** 2 + r[1] ** 2 + r[2] ** 2) < 1.0001:
                        G.add_edge(i, j)

            axes_list = []
            for i in range(len(self.coord_list)):
                axes_list.append(tuple(self.coord_list[i] - self.coord_list[list(G.adj[i])[random.randint(0, len(G.adj[i])-1)]]))

        else:
            raise AttributeError(
                "axes_type parameter must be one of 'random_hexagonal', 'random_plane', 'all_random', or 'random_nn'.")
        return axes_list

    def find_distances(self):
        self.point_list = list(self.mesh)
        self.distance_matrix = cdist(np.array(self.point_list), self.scaled_coords)
        self.is_in_mnp = np.any(self.distance_matrix < self.r_shell, axis=1)

    def if_circle(self, point, r):
        '''Deprecated'''
        x, y, z = point
        for n in self.coord_list:
            i, j, k = n
            if ((x - 2 * i * self.r_total) ** 2 + (y - 2 * j * self.r_total) ** 2 + (
                    z - 2 * k * self.r_total) ** 2) ** .5 < r:
                return True
        else:
            return False

    def if_coreshell(self, point):
        x, y, z = point
        for n in self.coord_list:
            i, j, k = n
            dist = ((x - 2 * i * self.r_total) ** 2 + (y - 2 * j * self.r_total) ** 2 + (z - 2 * k * self.r_total) ** 2)** .5
            if dist <= self.r_core:
                return 2
            elif dist <= self.r_shell:
                return 1
        else:
            return 0

    def ms_func(self, point):
        if self.if_circle(point, self.r_shell) and self.if_circle(point, self.r_core):
            return self.ms_core  # Fe3O4 Exchange stiffness constant (J/m)
        elif self.if_circle(point, self.r_shell) and not self.if_circle(point, self.r_core):
            return self.ms_shell  # MnFe2O4 Exchange stiffness constant (J/m)
        else:
            return 0

    def alt_ms_func(self, point):
        if int(self.arrayz[self.n][3]) == 2:
            self.n +=1
            return self.ms_core
        elif int(self.arrayz[self.n][3]) == 1:
            self.n+=1
            return self.ms_shell
        else: 
            self.n+=1
            return 0

    def a_func(self, point):
        if self.if_circle(point, self.r_shell) and self.if_circle(point, self.r_core):
            return self.a_core  # Fe3O4 Exchange stiffness constant (J/m)
        elif self.if_circle(point, self.r_shell) and not self.if_circle(point, self.r_core):
            return self.a_shell  # MnFe2O4 Exchange stiffness constant (J/m)
        else:
            return 0

    def alt_a_func(self, point):
        if int(self.arrayz[self.n][3]) == 2:
            self.n +=1
            return self.a_core
        elif int(self.arrayz[self.n][3]) == 1:
            self.n+=1
            return self.a_shell
        else: 
            self.n+=1
            return 0


    def k_func(self, point):
        if self.if_circle(point, self.r_shell) and self.if_circle(point, self.r_core):
            return self.k_core  # Fe3O4 Exchange stiffness constant (J/m)
        elif self.if_circle(point, self.r_shell) and not self.if_circle(point, self.r_core):
            return self.k_shell  # MnFe2O4 Exchange stiffness constant (J/m)
        else:
            return 0

    def alt_k_func(self, point):
        if int(self.arrayz[self.n][3]) == 2:
            self.n +=1
            return self.k_core
        elif int(self.arrayz[self.n][3]) == 1:
            self.n+=1
            return self.k_shell
        else: 
            self.n+=1
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

    def alt_u_func(self, point):
        if int(self.arrayz[self.n][3]) == 0:
            self.n += 1
            return (0, 0, 1)
        else:
            self.n += 1
            return self.easy_axes[self.circle_index(point, self.coord_list)]

    @property
    def mesh(self):
        if self.shape != 'rectangle':
            return df.Mesh(
                p1=(-2 * self.layer_radius * self.r_total, -2 * self.layer_radius * self.r_total, -self.r_total),
                p2=(2 * self.layer_radius * self.r_total, 2 * self.layer_radius * self.r_total,
                    2 * self.n_layers * self.r_total),
                cell=(self.r_total / self.x_divs, self.r_total / self.y_divs, self.r_total / self.z_divs))
        elif self.shape == 'rectangle':
            return df.Mesh(
                p1=(-self.r_total, -self.r_total, -self.r_total),
                p2=(4 * self.layer_dims[0] * self.r_total, self.layer_dims[1] * self.r_total + self.r_total,
                    2 * self.n_layers * self.r_total),
                cell=(self.r_total / self.x_divs, self.r_total / self.y_divs, self.r_total / self.z_divs))

    def make_m_field(self, m0='random'):
        t0 = time.time()
        if m0 == 'random':
            self.m_field = df.Field(self.mesh, dim=3,
                                    value=lambda point: [2 * random.random() - 1 for _ in range(3)],
                                    norm=self.ms_func)
        elif type(m0) == type((0, 0, 0)):
            self.m_field = df.Field(self.mesh, dim=3,
                                    value=m0,
                                    norm=self.ms_func)
        print('M Field made in {} s'.format(time.time()-t0))

    def alt_make_m_field(self, m0='random'):
        self.n = 0
        self.arrayz = np.genfromtxt(self.mesh_csv, delimiter=',')
        t0 = time.time()
        if m0 == 'random':
            self.m_field = df.Field(self.mesh, dim=3,
                                    value=lambda point: [2 * random.random() - 1 for _ in range(3)],
                                    norm=self.alt_ms_func)
        elif type(m0) == type((0, 0, 0)):
            self.m_field = df.Field(self.mesh, dim=3,
                                    value=m0,
                                    norm=self.alt_ms_func)
        print('M Field made in {} s'.format(time.time()-t0))

    def make_a_field(self):
        t0 = time.time()
        self.a_field = df.Field(self.mesh, dim=1, value=self.a_func)
        print('A Field made in {} s'.format(time.time()-t0))

    def alt_make_a_field(self):
        t0 = time.time()
        self.n = 0
        self.arrayz = np.genfromtxt(self.mesh_csv, delimiter=',')
        self.a_field = df.Field(self.mesh, dim=1, value=self.alt_a_func)
        print('A Field made in {} s'.format(time.time()-t0))

    def make_k_field(self):
        t0 = time.time()
        self.k_field = df.Field(self.mesh, dim=1, value=self.k_func)
        print('K Field made in {} s'.format(time.time()-t0))

    def alt_make_k_field(self):
        t0 = time.time()
        self.n = 0
        self.arrayz = np.genfromtxt(self.mesh_csv, delimiter=',')
        self.k_field = df.Field(self.mesh, dim=1, value=self.alt_k_func)
        print('K Field made in {} s'.format(time.time()-t0))

    def make_u_field(self):
        t0 = time.time()
        self.u_field = df.Field(self.mesh, dim=3, value=self.u_func)
        print('U Field made in {} s'.format(time.time()-t0))

    def alt_make_u_field(self):
        t0 = time.time()
        self.n = 0
        self.arrayz = np.genfromtxt(self.mesh_csv, delimiter=',')        
        self.u_field = df.Field(self.mesh, dim=3, value=self.alt_u_func)
        print('U Field made in {} s'.format(time.time()-t0))

    def initialize(self, fields='maku', autosave=True, m0='random'):
        if self.mesh_csv is None:
            if 'm' in fields:
                self.make_m_field(m0=m0)
            if 'a' in fields:
                self.make_a_field()
            if 'k' in fields:
                self.make_k_field()
            if 'u' in fields:
                self.make_u_field()
        else:
            if 'm' in fields:
                self.alt_make_m_field(m0=m0)
            if 'a' in fields:
                self.alt_make_a_field()
            if 'k' in fields:
                self.alt_make_k_field()
            if 'u' in fields:
                self.alt_make_u_field()            
        self.initialized = True
        if autosave:
            save_mnp(self)
            self.save_fields(fields=fields)

    def maku(self):
        if not self.initialized:
            self.initialize()
        return self.m_field, self.a_field, self.k_field, self.u_field

    def save_fields(self, filepath='default', fields='maku'):
        if not self.initialized:
            self.initialize(fields=fields)
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
            self.u_field.write(os.path.join(path, 'u_field_mnp_{}.ovf'.format(self.id)))

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
        return (('###             MNP {} Summary                       \n'
                 '|                Property                |   Value    |\n'
                 '| -------------------------------------- | ---------- |\n'
                 '| ID                                     | {:<10} |\n'
                 '| R_Total (m)                            | {:<10.2e} |\n'
                 '| R_Shell (m)                            | {:<10.2e} |\n'
                 '| R_Core (m)                             | {:<10.2e} |\n'
                 '| Discretizations per R_total (x, y, z)  | ({},{},{})    |\n'
                 '| Ms_Shell (A/m)                         | {:<10.2e} |\n'
                 '| Ms_Core (A/m)                          | {:<10.2e} |\n'
                 '| A_Shell J/m)                           | {:<10.2e} |\n'
                 '| A_Core (J/m)                           | {:<10.2e} |\n'
                 '| K_Shell (J/m^3)                        | {:<10.2e} |\n'
                 '| K_Core (J/m^3)                         | {:<10.2e} |\n'
                 '| Lattice Name                           | {:<10} |\n'
                 '| Lattice Form                           | {:<10} |\n'
                 '| Lattice Shape                          | {:<10} |\n'
                 '| Number of Lattice Layers               | {:<10} |\n'
                 '| Lattice Layer Radius (# of Spheres)    | {:<10} |\n'
                 '| Lattice Layer Dimensions (# of spheres)| ({:<2}, {:<2})   |\n'
                 '\n'
                 'Easy Axes List: {}').format(self.id, self.id, self.r_total, self.r_shell, self.r_core,
                                              self.x_divs, self.y_divs, self.z_divs,
                                              self.ms_shell, self.ms_core,
                                              self.a_shell, self.a_core,
                                              self.k_shell, self.k_core,
                                              self.name,
                                              self.form,
                                              self.shape, self.n_layers, self.layer_radius, self.layer_dims[0],
                                              self.layer_dims[1],
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
                 mnp.layer_radius, mnp.easy_axes, mnp.layer_dims]
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
        return MNP(id, r_tuple=make_list(mnp_data[1]), discretizations=make_list(mnp_data[2]),
                   ms_tuple=make_list(mnp_data[3]),
                   a_tuple=make_list(mnp_data[4]), k_tuple=make_list(mnp_data[5]), name=str(mnp_data[6]),
                   form=str(mnp_data[7]),
                   shape=str(mnp_data[8]), n_layers=int(mnp_data[9]), layer_radius=int(mnp_data[10]),
                   layer_dims=make_list(mnp_data[12]), axes=make_list(mnp_data[11]), directory=filepath,
                   loaded_fields=fields)


class MNP_System(mm.System):
    def __init__(self, mnp, **kwargs):
        super().__init__(name='DELETE', **kwargs)
        self.mnp = mnp

    def initialize(self, m0='random', Demag=True, Exchange=True, UniaxialAnisotropy=True, Zeeman=True,
                   H=(0, 0, .1 / mm.consts.mu0)):
        if not self.mnp.initialized:
            self.mnp.initialize(m0=m0)
        self.m = self.mnp.m_field
        self.energy = 0
        if Demag:
            self.energy += mm.Demag()
        if Exchange:
            self.energy += mm.Exchange(A=self.mnp.a_field)
        if UniaxialAnisotropy:
            self.energy += mm.UniaxialAnisotropy(K=self.mnp.k_field, u=self.mnp.u_field)
        if Zeeman:
            self.energy += mm.Zeeman(H=H)


def how_many_m_finals(mnp):
    path, dirs, files = next(os.walk(os.path.join(mnp.filepath, 'drives')))
    number = 0
    for f in files:
        if 'm_final' in f:
            number += 1
    return number


class MNP_MinDriver(mc.MinDriver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def drive_mnp(self, mnp, make_json=True, **kwargs):
        drivepath = os.path.join(mnp.filepath, 'drives')
        if not os.path.isdir(drivepath):
            os.mkdir(drivepath)
        system = MNP_System(mnp)
        system.initialize()
        self.drive(system, **kwargs)
        mnp.save_any_field(system.m, field_name='m_final_{}'.format(how_many_m_finals(mnp)), filepath=drivepath)
        if make_json:
            self.drive_json(system, drivepath)

    def drive_system(self, system, make_json=True, **kwargs):
        drivepath = os.path.join(system.mnp.filepath, 'drives')
        if not os.path.isdir(drivepath):
            os.mkdir(drivepath)
        self.drive(system, **kwargs)
        system.mnp.save_any_field(system.m, field_name='m_final_{}'.format(how_many_m_finals(system.mnp)),
                                  filepath=drivepath)
        if make_json:
            self.drive_json(system, drivepath)

    def drive_json(self, system, drivepath):
        Bx, By, Bz = system.energy.zeeman.H[0] * mm.consts.mu0, system.energy.zeeman.H[1] * mm.consts.mu0, \
                     system.energy.zeeman.H[2] * mm.consts.mu0
        drive_dict = {'Id': system.mnp.id,
                      'Name': system.mnp.name,
                      'Layer Radius': system.mnp.layer_radius,
                      'Layer Dims': system.mnp.layer_dims,
                      'Number of Layers': system.mnp.n_layers,
                      'Discretizations': (system.mnp.x_divs, system.mnp.y_divs, system.mnp.z_divs),
                      'Ms Core': system.mnp.ms_core,
                      'Ms Shell': system.mnp.ms_shell,
                      'A Core': system.mnp.a_core,
                      'A Shell': system.mnp.a_shell,
                      'K Core': system.mnp.k_core,
                      'K Shell': system.mnp.k_shell,
                      'Easy Axis Type': system.mnp.axes_type,
                      'Bx': Bx,
                      'By': By,
                      'Bz': Bz,
                      'Drive Number': how_many_m_finals(system.mnp),
                      'Date': time.asctime()
                      }
        with open(os.path.join(drivepath, 'drive_{}_info.json'.format(how_many_m_finals(system.mnp))),
                  'w') as outfile:
            json.dump(drive_dict, outfile)


def make_h_list(Hmin, Hmax, n):
    hmin = np.array(Hmin)
    hmax = np.array(Hmax)
    interval = (1 / n) * np.add(hmax, -1 * hmin)
    h_list = [np.add(hmin, interval * k) for k in range(n)] + [np.add(hmax, -1 * interval * k) for k in range(n + 1)]
    return h_list


class MNP_HysteresisDriver(mc.HysteresisDriver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def drive_hysteresis(self, mnp, Hmin=(0, 10, -1 / mm.consts.mu0), Hmax=(0, 0, 1 / mm.consts.mu0), n=10,
                         **kwargs):
        drivepath = os.path.join(mnp.filepath, 'drives')
        if not os.path.isdir(drivepath):
            os.mkdir(drivepath)
        system = mm.System(name='DELETE')
        M, A, K, U = mnp.maku()
        system.m = M
        data_rows = []
        h_list = make_h_list(Hmin, Hmax, n)
        stage = 0
        for h in h_list:
            system.energy = mm.Demag() + mm.Exchange(A=A) + mm.UniaxialAnisotropy(K=K, u=U) + mm.Zeeman(H=h)
            md = mc.MinDriver()
            md.drive(system, **kwargs)
            mnp.save_any_field(system.m, field_name='m_final_{}'.format(how_many_m_finals(mnp)), filepath=drivepath)
            system.table.data['stage'] = stage
            stage += 1
            system.table.data['B'] = np.linalg.norm(h) * mm.consts.mu0
            system.table.data['Bx'] = h[0] * mm.consts.mu0
            system.table.data['By'] = h[1] * mm.consts.mu0
            system.table.data['Bz'] = h[2] * mm.consts.mu0
            data_rows.append(system.table.data)
        table = pd.concat([data for data in data_rows])
        table.to_csv(os.path.join(mnp.filepath, 'hysteresis_data.csv'))
        print('Hysteresis data saved to ', os.path.join(mnp.filepath, 'hysteresis_data.csv'))


def quick_drive(mnp, **kwargs):
    md = MNP_MinDriver()
    md.drive_mnp(mnp, **kwargs)


class MNP_Analyzer:
    def __init__(self, mnp, step=0, preload_field=True):
        self.mnp = mnp
        self.path = os.path.join(self.mnp.filepath, 'plots')
        self.step = step
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        if preload_field:
            if step == 0 and os.path.isfile(os.path.join(self.mnp.filepath, 'm_final_mnp_{}.ovf'.format(self.mnp.id))):
                self.field = self.mnp.load_any_field('m_final')
            else:
                self.field = self.mnp.load_any_field('m_final_{}'.format(step),
                                                     filepath=os.path.join(self.mnp.filepath, 'drives'))

    def load_step(self, step):
        self.step = step
        self.field = self.mnp.load_any_field('m_final_{}'.format(step),
                                             filepath=os.path.join(self.mnp.filepath, 'drives'))

    def xy_plot(self, ax=None, title=None, z_plane=0, figsize=(50, 50), filename=None, filetype=None,
                scalar_cmap='hsv', vector_cmap='binary', scalar_clim=(0, 6.28), **kwargs):
        if filetype is None:  # filetype defautls to .png
            filetype = 'png'
        if filename is None:
            thefilename = 'angle_plot.' + filetype
            filename = os.path.join(self.path, thefilename)
        if title is None:
            title = 'MNP {} XY Plot'.format(self.mnp.id)
        if ax is None:
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)

            ax.set_title(title)
        self.field.orientation.plane(z=z_plane).mpl(ax=ax, figsize=figsize,
                                                    scalar_field=self.field.orientation.plane(z=z_plane).angle,
                                                    vector_color_field=self.field.orientation.z,
                                                    vector_color=True,
                                                    vector_colorbar=True, scalar_cmap=scalar_cmap,
                                                    vector_cmap=vector_cmap,
                                                    scalar_clim=scalar_clim,
                                                    filename=filename, **kwargs)

    def z_plot(self, ax=None, title=None, z_plane=0, figsize=(50, 50), filename=None, filetype=None,
               scalar_cmap='viridis', **kwargs):
        if filetype is None:  # filetype defautls to .png
            filetype = 'png'
        if filename is None:
            thefilename = 'z_plot.' + filetype
            filename = os.path.join(self.path, thefilename)
        if title is None:
            title = 'MNP {} Z Plot'.format(self.mnp.id)
        if ax is None:
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)

            ax.set_title(title)
        self.field.orientation.plane(z=z_plane).mpl(ax=ax, figsize=figsize,
                                                    filename=filename, scalar_cmap=scalar_cmap, **kwargs)

    def xy_scalar_plot(self, ax=None, title=None, z_plane=0, figsize=(40, 10), filename=None, filetype=None,
                       cmap='hsv', clim=(0, 6.28), **kwargs):
        if filetype is None:  # filetype defautls to .png
            filetype = 'png'
        if filename is None:
            thefilename = 'xy_scalar_plot.' + filetype
            filename = os.path.join(self.path, thefilename)
        if title is None:
            title = 'MNP {} XY Scalar Plot'.format(self.mnp.id)
        if ax is None:
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)

            ax.set_title(title)
        self.field.orientation.plane(z=z_plane).angle.mpl_scalar(ax=ax,
                                                                 filename=filename,
                                                                 figsize=figsize, filter_field=self.field.x,
                                                                 cmap=cmap, clim=clim, **kwargs)

    def z_scalar_plot(self, ax=None, title=None, z_plane=0, figsize=(40, 10), filename=None, filetype=None,
                      cmap='viridis', **kwargs):
        if filetype is None:  # filetype defautls to .png
            filetype = 'png'
        if filename is None:
            thefilename = 'z_scalar_plot.' + filetype
            filename = os.path.join(self.path, thefilename)
        if title is None:
            title = 'MNP {} Z Scalar Plot'.format(self.mnp.id)
        if ax is None:
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111)

            ax.set_title(title)
        self.field.orientation.plane(z=z_plane).z.mpl_scalar(ax=ax,
                                                             filename=filename,
                                                             figsize=figsize, filter_field=self.field.x,
                                                             cmap=cmap, **kwargs)

    def extract(self):
        t0 = time.time()
        print("Extracting center magnetization values...")
        x, y, z = self.mnp.scaled_coords[:, 0], self.mnp.scaled_coords[:, 1], self.mnp.scaled_coords[:, 2]
        mx = []
        my = []
        mz = []
        angle = []
        for point in self.mnp.scaled_coords:
            h, j, k = point
            mx.append(self.field.orientation.line(p1=(point), p2=(0, 0, 0), n=2).data.vx[0]),
            my.append(self.field.orientation.line(p1=(point), p2=(0, 0, 0), n=2).data.vy[0]),
            mz.append(self.field.orientation.line(p1=(point), p2=(0, 0, 0), n=2).data.vz[0])
            angle.append(self.field.plane(z=k).angle.line(p1=point, p2=(0, 0, k), n=2).data.v[0])
        table = np.column_stack((x, y, z, mx, my, mz, angle))
        table.tofile(os.path.join(self.mnp.filepath, 'centers_data.csv'), sep=',')
        print('Values extracted in {} s'.format(time.time()-t0))

    def mpl_center_vectors(self, color_field='z', ax=None, title=None, x_label=None, y_label=None, figsize=None,
                           filename=None,
                           filetype=None, **kwargs):
        if not os.path.isfile(os.path.join(self.mnp.filepath, 'centers_data.csv')):
            self.extract()
        data = np.genfromtxt(os.path.join(self.mnp.filepath, 'centers_data.csv'), delimiter=',')
        data = data.reshape(-1, 7)

        if figsize is None:
            figsize = (50, 50)
        if filetype is None:  # filetype defautls to .png
            filetype = 'png'
        if filename is None:
            if color_field == 'z':
                thefilename = '2d_vector_plot_z.' + filetype
            elif color_field == 'angle':
                thefilename = '2d_vector_plot_xy.' + filetype
            else:
                raise AttributeError("color_field should be either 'z' or 'angle'")
            filename = os.path.join(self.path, thefilename)
        if title is None:
            title = 'MNP {} 2D Vector Plot'.format(self.mnp.id)
        if x_label is None:
            x_label = 'x'
        if y_label is None:
            y_label = 'y'
        if ax is None:
            plt.figure(figsize=figsize)
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(title)

        if color_field == 'z':
            plt.quiver(data[:, 0], data[:, 1], data[:, 3], data[:, 4], data[:, 5], cmap='viridis')
        elif color_field == 'angle':
            plt.quiver(data[:, 0], data[:, 1], data[:, 3], data[:, 4], data[:, 6], cmap='hsv')
        plt.savefig(fname=filename)

    def k3d_center_vectors(self, color_field='z', cmap=None, scale=None):
        if scale is None:
            scale = [1, 1, 1]
        model_matrix = [
            7.0, 5.0, -5.0, 0.0,
            0.0, 7.0, 7.0, 5.0,
            7.0, -5.0, 5.0, 0.0,
            0.0, 0.0, 0.0, 1.0
        ]
        if not os.path.isfile(os.path.join(self.mnp.filepath, 'centers_data.csv')):
            self.extract()
        data = np.genfromtxt(os.path.join(self.mnp.filepath, 'centers_data.csv'), delimiter=',')
        data = data.reshape(-1, 7)
        center_magnetization = np.column_stack((data[:, 3], data[:, 4], data[:, 5]))
        origins = self.mnp.coord_list.astype(np.float32)
        origins[:, 0] *= scale[0]
        origins[:, 1] *= scale[1]
        origins[:, 2] *= scale[2]

        if color_field == 'z':
            if cmap is None:
                cmap = 'viridis'
            print('Getting Z values...')
            color_values = center_magnetization[:, 2]
        elif color_field == 'angle':
            print("Getting XY angle values...")
            if cmap is None:
                cmap = 'hsv'
            color_values = data[:, 6]
        elif color_field == 'layer':
            print("Getting Layer...")
            if cmap is None:
                cmap = 'rainbow'
            color_values = data[:, 2]
        else:
            raise AttributeError("color_field should be 'z', 'angle', or 'layer'.")

        color_values = dfu.normalise_to_range(color_values, (0, 255))
        # Generate double pairs (body, head) for colouring vectors.
        cmap = matplotlib.cm.get_cmap(cmap, 256)
        cmap_int = []
        for i in range(cmap.N):
            rgb = cmap(i)[:3]
            cmap_int.append(int(matplotlib.colors.rgb2hex(rgb)[1:], 16))

        colors = []
        for cval in color_values:
            colors.append(2 * (cmap_int[cval],))

        plot = k3d.plot()
        plot.display()
        plot += k3d.vectors(origins=origins,
                            vectors=center_magnetization.astype(np.float32), model_matrix=model_matrix,
                            colors=colors,
                            line_width=.02, head_size=2, use_head=True)


class MNP_Hysteresis_Analyzer(MNP_Analyzer):
    def __init__(self, mnp, step=None, preload_field=False):
        super().__init__(mnp, step, preload_field)

    def hyst_loop_plot(self, x=None, y=None, figsize=(10, 10), x_label='Applied Field (T)',
                       y_label='Sample Magnetization (a.u.)',
                       title=None, filename=None, filetype=None, **kwargs):
        if filetype is None:  # filetype defautls to .png
            filetype = 'png'
        if filename is None:
            thefilename = 'hysteresis_loop.' + filetype
            filename = os.path.join(self.path, thefilename)
        if title is None:
            title = 'MNP {} Hysteresis Loop'.format(self.mnp.id)
        plt.figure(figsize=figsize)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        if y is None:
            y = ['mz']
        if x is None:
            x = ['Bz']
        data = pd.read_csv(os.path.join(self.mnp.filepath, 'hysteresis_data.csv'))
        for i in y:
            plt.plot(data[x], data[i], **kwargs)
        plt.legend(y)
        plt.savefig(fname=filename)

    def hyst_steps_plot(self, type='xy', name=None, ax=None, title=None, z_plane=0, figsize=(50, 50), filename=None,
                        filetype=None,
                        scalar_cmap=None, vector_cmap=None, scalar_clim=None, **kwargs):
        if name is None:
            name = type + '_hysteresis_plot'
        savepath = os.path.join(self.path, name)
        if not os.path.isdir(savepath):
            os.mkdir(savepath)
        print('Plotting...')
        max = how_many_m_finals(self.mnp)
        for n in range(max):
            print('\r' + "|{}{}| {}/{}".format('-' * (n) + '>', ' ' * (max - n - 1), n + 1, max), end='')
            self.field = self.mnp.load_any_field('m_final_{}'.format(n),
                                                 filepath=os.path.join(self.mnp.filepath, 'drives'))
            if type == 'xy':
                title = 'MNP {} XY Plot Step {}'.format(self.mnp.id, n)
                filename = os.path.join(savepath, 'xy_plot_{}.png'.format(n))
                if scalar_cmap is None:
                    scalar_cmap = 'hsv'
                if vector_cmap is None:
                    vector_cmap = 'binary'
                if scalar_clim is None:
                    scalar_clim = (0, 6.28)
                self.xy_plot(title=title, ax=ax, z_plane=z_plane, figsize=figsize, filename=filename,
                             filetype=filetype,
                             scalar_cmap=scalar_cmap, vector_cmap=vector_cmap, scalar_clim=scalar_clim, **kwargs)
            elif type == 'z':
                title = 'MNP {} Z Plot Step {}'.format(self.mnp.id, n)
                filename = os.path.join(savepath, 'z_plot_{}.png'.format(n))
                if scalar_cmap is None:
                    scalar_cmap = 'viridis'
                if scalar_clim is None:
                    scalar_clim = (-1, 1)
                self.z_plot(title=title, ax=ax, z_plane=z_plane, figsize=figsize, filename=filename,
                            filetype=filetype,
                            scalar_cmap=scalar_cmap, scalar_clim=scalar_clim, **kwargs)
            elif type == 'xy_scalar':
                title = 'MNP {} XY Scalar Plot Step {}'.format(self.mnp.id, n)
                filename = os.path.join(savepath, 'xy_scalar_plot_{}.png'.format(n))
                if scalar_cmap is None:
                    scalar_cmap = 'hsv'
                if scalar_clim is None:
                    scalar_clim = (0, 6.28)
                self.xy_scalar_plot(title=title, ax=ax, z_plane=z_plane, figsize=figsize, filename=filename,
                                    filetype=filetype,
                                    cmap=scalar_cmap, clim=scalar_clim, **kwargs)
            elif type == 'z_scalar':
                title = 'MNP {} Z Scalar Plot Step {}'.format(self.mnp.id, n)
                filename = os.path.join(savepath, 'z_scalar_plot_{}.png'.format(n))
                if scalar_cmap is None:
                    scalar_cmap = 'viridis'
                if scalar_clim is None:
                    scalar_clim = (-1, 1)
                self.z_scalar_plot(ax=ax, title=title, z_plane=z_plane, figsize=figsize, filename=filename,
                                   filetype=filetype,
                                   cmap=scalar_cmap, scalar_clim=scalar_clim, **kwargs)
        print('\r')

    def hyst_movie(self, type='z', movie_name=None, name=None, **kwargs):
        if movie_name is None:
            movie_name = os.path.join(self.path, '{}_hysteresis.mp4'.format(type))
        if name is None:
            if type == 'xy':
                name = 'xy_hysteresis_plot'
            elif type == 'z':
                name = 'z_hysteresis_plot'
            elif type == 'xy_scalar':
                name = 'xy_scalar_hysteresis_plot'
            elif type == 'z_scalar':
                name = 'z_scalar_hysteresis_plot'
        findpath = os.path.join(self.path, name)
        if not os.path.isdir(findpath):
            self.hyst_steps_plot(type=type, name=name, **kwargs)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        images = []
        for n in range(how_many_m_finals(self.mnp)):
            if type == 'xy':
                images.append(os.path.join(findpath, 'xy_plot_{}.png'.format(n)))
            if type == 'z':
                images.append(os.path.join(findpath, 'z_plot_{}.png'.format(n)))
            if type == 'xy_scalar':
                images.append(os.path.join(findpath, 'xy_scalar_plot_{}.png'.format(n)))
            if type == 'z_scalar':
                images.append(os.path.join(findpath, 'z_scalar_plot_{}.png'.format(n)))
        frame = cv2.imread(images[0])
        height, width, layers = frame.shape
        video = cv2.VideoWriter(movie_name, fourcc, 1.0, (width, height))
        dim = (int(width), int(height))
        for image in images:
            frame = cv2.imread(image)
            frame = cv2.resize(frame, dim)
            video.write(frame)
        cv2.destroyAllWindows()
        video.release()
        print('Movie saved to ' + movie_name)


def angle_finder(point, d_theta, d_phi):
    x, y, z = point
    return [((np.math.acos(z / np.math.sqrt(x ** 2 + y ** 2 + z ** 2)) * 180 / np.pi)+d_theta)%180,
            ((np.math.atan2(y, x) * 180 / np.pi)+180+d_phi)%360]


class MNP_Domain_Analyzer(MNP_Analyzer):
    def __init__(self, mnp, step=0, preload_field=True, d_theta=0, d_phi=0):
        super().__init__(mnp, step, preload_field)

        self.region_list = None
        self.d_theta = d_theta
        self.d_phi = d_phi

    @property
    def discretized_cmag(self):
        if not os.path.isfile(os.path.join(self.mnp.filepath, 'centers_data.csv')):
            self.extract()
        data = np.genfromtxt(os.path.join(self.mnp.filepath, 'centers_data.csv'), delimiter=',')
        data = data.reshape(-1, 7)
        center_magnetization = np.column_stack((data[:, 3], data[:, 4], data[:, 5]))

        theta_list = []
        phi_list = []
        for point in center_magnetization:
            theta, phi = angle_finder(point, self.d_theta, self.d_phi)
            theta_list.append(theta)
            phi_list.append(phi)

        theta_bins = np.digitize(theta_list, [180 * i / 6 for i in range(1, 7)], right=True)
        phi_bins = []
        for i in range(len(phi_list)):
            z = theta_bins[i]
            if z == 0 or z == 5:
                phi_bins.append(np.digitize(phi_list[i], [180, 360], right=True))
            if z == 1 or z == 4:
                phi_bins.append(np.digitize(phi_list[i], [90, 180, 270, 360], right=True))
            if z == 2 or z == 3:
                phi_bins.append(np.digitize(phi_list[i], [60, 120, 180, 240, 300, 360], right=True))

        region_index_dict = {
            (2, 0): 1,
            (2, 1): 2,
            (2, 2): 3,
            (2, 3): 4,
            (2, 4): 5,
            (2, 5): 6,
            (3, 0): 7,
            (3, 1): 8,
            (3, 2): 9,
            (3, 3): 10,
            (3, 4): 11,
            (3, 5): 12,
            (1, 0): 13,
            (1, 1): 14,
            (1, 2): 15,
            (1, 3): 16,
            (4, 0): 17,
            (4, 1): 18,
            (4, 2): 19,
            (4, 3): 20,
            (0, 0): 21,
            (0, 1): 22,
            (5, 0): 23,
            (5, 1): 24
        }

        region_indices = []
        for i in range(len(center_magnetization)):
            region_indices.append(region_index_dict.get((theta_bins[i], phi_bins[i])))

        return region_indices

    def plot_regions(self, cmap='hsv', point_size=.9, scale=(1, 1, 1)):
        cmap = cmap
        color_values = np.array(self.discretized_cmag).astype(float)
        color_values = dfu.normalise_to_range(color_values, (0, 255))
        # Generate double pairs (body, head) for colouring vectors.
        cmap = matplotlib.cm.get_cmap(cmap, 256)
        cmap_int = []
        for i in range(cmap.N):
            rgb = cmap(i)[:3]
            cmap_int.append(int(matplotlib.colors.rgb2hex(rgb)[1:], 16))

        colors = []
        for cval in color_values:
            colors.append((cmap_int[cval],))

        origins = self.mnp.coord_list.astype(np.float32)
        origins[:, 0] = scale[0] * origins[:, 0]
        origins[:, 1] = scale[1] * origins[:, 1]
        origins[:, 2] = scale[2] * origins[:, 2]
        plot = k3d.plot()
        plot.display()
        plot += k3d.points(positions=origins,
                           colors=colors,
                           point_size=point_size)

    def plot_regions_vectors(self, cmap='hsv', head_size=2, scale=(1, 1, 1)):
        if not os.path.isfile(os.path.join(self.mnp.filepath, 'centers_data.csv')):
            self.extract()
        data = np.genfromtxt(os.path.join(self.mnp.filepath, 'centers_data.csv'), delimiter=',')
        data = data.reshape(-1, 7)
        center_magnetization = np.column_stack((data[:, 3], data[:, 4], data[:, 5]))

        cmap = cmap
        color_values = np.array(self.discretized_cmag).astype(float)
        color_values = dfu.normalise_to_range(color_values, (0, 255))
        # Generate double pairs (body, head) for colouring vectors.
        cmap = matplotlib.cm.get_cmap(cmap, 256)
        cmap_int = []
        for i in range(cmap.N):
            rgb = cmap(i)[:3]
            cmap_int.append(int(matplotlib.colors.rgb2hex(rgb)[1:], 16))

        colors_2 = []
        for cval in color_values:
            colors_2.append(2 * (cmap_int[cval],))

        origins = self.mnp.coord_list.astype(np.float32)
        origins[:, 0] = scale[0] * origins[:, 0]
        origins[:, 1] = scale[1] * origins[:, 1]
        origins[:, 2] = scale[2] * origins[:, 2]

        model_matrix = [
            7.0, 5.0, -5.0, 0.0,
            0.0, 7.0, 7.0, 5.0,
            7.0, -5.0, 5.0, 0.0,
            0.0, 0.0, 0.0, 1.0
        ]

        plot = k3d.plot()
        plot.display()
        plot += k3d.vectors(origins=origins,
                            vectors=center_magnetization.astype(np.float32), model_matrix=model_matrix,
                            colors=colors_2,
                            line_width=.02, head_size=head_size, use_head=True)

    def find_regions(self):
        region_indices = self.discretized_cmag
        G = nx.Graph()
        for i in range(len(self.mnp.coord_list)):
            G.add_node(i)
        for i in range(len(self.mnp.coord_list)):
            for j in range(len(self.mnp.coord_list)):
                r = self.mnp.coord_list[i] - self.mnp.coord_list[j]
                if 0 < (r[0] ** 2 + r[1] ** 2 + r[2] ** 2) < 1.0001:
                    G.add_edge(i, j)

        def neighbor_network_checker(i, used, matches):
            for j in G.adj[i]:
                if region_indices[i] == region_indices[j]:
                    if j not in matches:
                        matches.append(j)
            used.append(i)

        def region_finder(n):
            used = []
            matches = [n]
            for m in matches:
                neighbor_network_checker(m, used, matches)
            return len(used)

        def clump_lister():
            clumps = []
            for i in range(len(self.mnp.coord_list)):
                clumps.append(region_finder(i))
            clump_list = []
            for i in clumps:
                num = clumps.count(i) // i
                if i not in clump_list:
                    for _ in range(num):
                        clump_list.append(i)
            return clump_list

        self.region_list = clump_lister()

    @property
    def characteristic_size(self):
        n = 0
        for i in self.region_list:
            n += i * (i)
        return (n / len(self.mnp.coord_list))

    @property
    def free_particle_fraction(self):
        return self.region_list.count(1) / len(self.mnp.coord_list)

    @property 
    def two_three_particle_fraction(self):
        return (2*self.region_list.count(2)+3*self.region_list.count(3)) / len(self.mnp.coord_list)

    @property
    def domains_summary(self):
        csize = self.characteristic_size

        return (('###             MNP {} Domain Summary                       \n'
                 '|                Property                |   Value    |\n'
                 '| -------------------------------------- | ---------- |\n'
                 '| ID                                     | {:<10} |\n'
                 '| Number of MNPs                         | {:<10} |\n'
                 '| Number of Regions                      | {:<10} |\n'
                 '| Characteristic Domain Size             | {:<10} |\n'
                 '| Max Domain Size                        | {:<10} |\n'
                 '| Average Domain Size                    | {:<10} |\n'
                 '| Free Particle Fraction                 | {:<10} |\n'
                 '| 2-3 Particle Fraction                  | {:<10} |\n'
                 '\n'
                 'Domain Size List: {}').format(self.mnp.id, self.mnp.id, len(self.mnp.coord_list),
                                                len(self.region_list), csize,
                                                max(self.region_list), np.mean(self.region_list),
                                                self.free_particle_fraction, self.two_three_particle_fraction, self.region_list))

    def save_domains(self):
        data_list = [self.mnp.id, len(self.mnp.coord_list),
                     len(self.region_list), self.characteristic_size,
                     max(self.region_list), np.mean(self.region_list), self.region_list, self.free_particle_fraction, self.two_three_particle_fraction]
        with open(os.path.join(self.mnp.filepath, 'domain_data_mnp_{}.csv'.format(self.mnp.id)), 'w') as f:
            write = csv.writer(f)
            write.writerow(data_list)

        with open(os.path.join(self.mnp.filepath, 'domain_summary_mnp_{}.md'.format(self.mnp.id)), 'w') as f:
            f.write(self.domains_summary)
        print('MNP Summary Saved: ', os.path.join(self.mnp.filepath, 'summary_mnp_{}.md'.format(self.mnp.id)))

    def save_averaged_data(self):
        t0 = time.time()
        with open(os.path.join(self.mnp.filepath, 'axes_range_data_{}.csv'.format(self.step)), 'w') as f:
            write = csv.writer(f)
            write.writerow(
                ["d_theta", "d_phi", "Characteristic Domain Size", "Max Domain Size", "Free Particle Fraction", "2-3 Particle Fraction", "Region List"])
            angle_pairs = [(0, 0), (0,180), 
                          (30,0), (30, 90), (30, 180), (30, 270), 
                          (60, 0), (60, 60), (60, 120), (60, 180), (60, 240), (60, 300),
                          (90, 0), (90, 60), (90, 120), (90, 180), (90, 240), (90, 300),
                          (120,0), (120, 90), (120, 180), (120, 270),
                          (150, 0), (150,180)]
           
            for pair in angle_pairs:
                    self.d_theta, self.d_phi = pair
                    self.find_regions()
                    data = [self.d_theta, self.d_phi, self.characteristic_size, max(self.region_list),
                            self.free_particle_fraction, self.two_three_particle_fraction, self.region_list]
                    write.writerow(data)
        print("Averaged domain data saved in {} s".format(time.time()-t0))


def extract_domain_csv(name, number=27, filepath='./MNP_Data', filename='domain_data.csv', mode='w', B=0.001):
    with open(filename, mode) as f:
        write = csv.writer(f)
        write.writerow(
            ['MNP Id', 'Bx (T)', 'By (T)', 'Bz (T)', 'Ms_core (A/m)', 'A_core (J/m)', 'K_core (J/m^3)', 'Axes type', 'Characteristic Size',
             'Max Size', 'Free Particle Fraction', '2-3 Particle Fraction', 'Region List'])
        for i in range(number):
            try:
                mnp = load_mnp(i, name=name, filepath=filepath)
                with open(os.path.join(mnp.filepath, 'domain_data_mnp_{}.csv'.format(mnp.id)), 'r') as r:
                    csv_reader = list(csv.reader(r))
                    domain_data = []
                    for q in csv_reader:
                        for j in q:
                            domain_data.append(j)
                csize = domain_data[3]
                maxsize = domain_data[4]
                fpf = domain_data[7]
                pf23 = domain_data[8]
                region_list = domain_data[6]
                m = mnp.ms_core
                a = mnp.a_core
                k = mnp.k_core
                try:
                    drivepath = os.path.join(mnp.filepath, 'drives')
                    with open(os.path.join(drivepath, 'drive_1_info.json'), 'r') as openfile:
                        json_object = json.load(openfile)
                        Bx = json_object.get('Bx')
                        By = json_object.get('By')
                        Bz = json_object.get('Bz')
                except:
                    print('No .json drive file found... Setting B =', B)
                    Bz = B
                if (i // 9) % 3 == 0:
                    axes = 'all_random'
                elif (i // 9) % 3 == 1:
                    axes = 'random_plane'
                elif (i // 9) % 3 == 2:
                    axes = 'random_hexagonal'
                data_list = [mnp.id, Bx, By, Bz, m, a, k, axes, csize, maxsize, fpf, pf23, region_list]
                write.writerow(data_list)
            except:
                print('Failed - MNP {}'.format(i))


def extract_average_domain_data(name, filename='sorted_data.csv', mode='w', start=0, end=36, start_steps = 0, end_steps=None):
    with open(filename, mode) as f:
        write = csv.writer(f)
        write.writerow(["MNP", "Bx (T)", "By (T)", "Bz (T)", "Ms (A/m)", "K (J/szam^3)", "A (J/m)", "Avg. FPF", "\u03C3 FPF", "Avg. C-Size",
                        "\u03C3 C-Size", "Avg. Max Size", "\u03C3 Max Size", "Avg. 2-3 PF", "\u03C3 2-3 PF", "Full Region List"])
        if end_steps is None:
            stepnum=1
        else:
            stepnum=end_steps
        for step in range(start_steps, stepnum):
            for i in range(start, end):
                try:
                    mnp = load_mnp(i, name=name)
                    m = mnp.ms_core
                    a = mnp.a_core
                    k = mnp.k_core
                    if end_steps is None:
                        data = pd.read_csv(os.path.join(mnp.filepath, 'axes_range_data.csv'))
                    else:
                        data = pd.read_csv(os.path.join(mnp.filepath, 'axes_range_data_{}.csv'.format(step)))
                    temp = []
                    for j in range(len(data["Region List"])):
                        temp.append(json.loads(data["Region List"][j]))
                    full_region_list = list(np.concatenate(temp))
                    fpf_mean_data = np.mean(data["Free Particle Fraction"])
                    fpf_st_dv_data = np.std(data['Free Particle Fraction'])
                    c_size_mean_data = np.mean(data["Characteristic Domain Size"])
                    c_size_st_dv_data = np.std(data['Characteristic Domain Size'])
                    max_size_mean_data = np.mean(data["Max Domain Size"])
                    max_size_st_dv_data = np.std(data['Max Domain Size'])
                    try:
                        pf23_mean_data = np.mean(data["2-3 Particle Fraction"])
                        pf23_st_dv_data = np.std(data['2-3 Particle Fraction'])
                    except:
                        pf23_mean_data = None
                        pf23_st_dv_data = None
                    drivepath = os.path.join(mnp.filepath, 'drives')
                    with open(os.path.join(drivepath, 'drive_{}_info.json'.format(step + 1)), 'r') as openfile:
                        json_object = json.load(openfile)
                        Bx = json_object.get('Bx')
                        By = json_object.get('By')
                        Bz = json_object.get('Bz')
                    data_list = [i, Bx, By, Bz, m, k, a, fpf_mean_data, fpf_st_dv_data, c_size_mean_data, c_size_st_dv_data,
                                max_size_mean_data, max_size_st_dv_data, pf23_mean_data, pf23_st_dv_data, full_region_list]
                    write.writerow(data_list)
                except FileNotFoundError:
                    print('Failed - MNP {}'.format(i))
