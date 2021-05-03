# MAGnetic Nanoparticle Assembly Utilities (MAGNA-U)

[![Github](https://img.shields.io/static/v1?label=Github&message=MAGNA-U&color=red&style=for-the-badge&logo=github)](https://github.com/sammysiegel/MAGNA-U) 

[![Release](https://img.shields.io/github/v/release/sammysiegel/MAGNA-U?logo=github&style=for-the-badge)](https://github.com/sammysiegel/MAGNA-U/releases/latest)

##About
MAGNA-U is a Python module that provides tools to simplify the
modeling and simulation of magnetic nanoparticles (MNPs). MAGNA-U
combines into one place all the previous code that has been
written to model shell/core MnFe2O4/Fe3O4 magnetic nanoparticle
assemblies [^1]. The code is primarily made up of two classes:
[`Lattice`](Lattice.md) and  [`MNP`](MNP.md). 

The `Lattice` class is used to generate arbitrary lattices of
close packed spheres in part using code developed by Kathryn Krycka,
Ian Hunt-Isaak, and Yumi Ijiri. The `MNP` class is a subclass of
`Lattice` that models the physical parameters of a magnetic
nanoparticle core-shell assembly and provides tools to simplify
the simulation of such assemblies in [Ubermag](https://github.com/ubermag/workshop) [^2] using [OOMMF](https://math.nist.gov/oommf/) [^3].



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



## References
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