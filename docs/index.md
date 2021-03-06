# MAGnetic Nanoparticle Assembly Utilities (MAGNA-U)

[![Github](https://img.shields.io/static/v1?label=Github&message=MAGNA-U&color=red&style=for-the-badge&logo=github)](https://github.com/sammysiegel/MAGNA-U) 

[![Release](https://img.shields.io/github/v/release/sammysiegel/MAGNA-U?logo=github&style=for-the-badge)](https://github.com/sammysiegel/MAGNA-U/releases/latest)

Sammy Siegel, Niels Vanderloo, and Yumi Ijiri
 
*Oberlin College, Department of Physics and Astronomy, Oberlin OH, 44074*

## About
MAGNA-U is a Python module that provides tools to simplify the
modeling and simulation of magnetic nanoparticles (MNPs). MAGNA-U
combines into one place all the previous code that has been
written to model shell/core MnFe2O4/Fe3O4 magnetic nanoparticle
assemblies [1]. The code is primarily made up of two classes:
[`Lattice`](Lattice.md) and  [`MNP`](MNP.md). 

The `Lattice` class is used to generate arbitrary lattices of
close packed spheres in part using code developed by Kathryn Krycka,
Ian Hunt-Isaak, and Yumi Ijiri. The `MNP` class is a subclass of
`Lattice` that models the physical parameters of a magnetic
nanoparticle core-shell assembly and provides tools to simplify
the simulation of such assemblies in [Ubermag](https://github.com/ubermag/workshop) [2] using [OOMMF](https://math.nist.gov/oommf/) [3].

Unfortunately, due to the new file structuring system in Version 2.0.0,
files created using an older version will not be compatible with the new
version using the `load_mnp()` function.

## Quick Documentation

### Classes 
|    Name                  |Description      |
|:------------:        |      -----------      |
|[`MNP`](MNP.md)        |   The main class responsible for creating, initializing, and simulating MNPs and for storing and managing data about MNPs. A child class of `Lattice`.|
|[`Lattice`](Lattice.md)|   The parent class for `MNP` which is used to create a lattice geometry of the specified size, shape, and stacking type.|
|[`MNP_System`](MNP_System.md)|  A child class of `micromagneticmodule.System` used to create systems based on a specific `MNP` instance and initialize an MNP for simulation.|
|[`MNP_MinDriver`](MNP_Min_Driver.md) |   A child class of `oommfc.MinDriver` used to run an energy minimization drive of a specific `MNP` instance or `MNP_System` instance.|

### Functions

| Name | Description |
| :-------: | ------- |
|[`save_mnp`](Save-Load MNPs.md#saving-mnps)| Saves MNP attribute and summary data|
|[`load_mnp`](Save-Load MNPs.md#loading-mnps)| Instantiates an MNP from data stored in files|
|[`quick_drive`](Quick_Drive.md)| Easy way to drive an MNP assembly|

## Changelog

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

## References
[1]: Y. Ijiri, et. al. Correlated spin canting in ordered core-shell
Fe3O4/MnFexFe3-xO4 nanoparticle assemblies.
*Physical Review B* **99**, 094421 (2019).

[2]: M. Beg, R. A. Pepper, and H. Fangohr. User interfaces for computational
science: A domain specific language for OOMMF embedded in Python.
*AIP Advances* **7**, 56025 (2017).
[https://doi.org/10.1063/1.4977225](https://doi.org/10.1063/1.4977225)

[3]: M.J. Donahue and D. G. Porter. OOMMF User's Guide, Version 1.0,
Interagency Report NISTIR 6376. National Institute of Standards and
Technology, Gaithersburg, MD (Sept 1999).