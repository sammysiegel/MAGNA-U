# MAGnetic Nanoparticle Assembly Utilities (MAGNA-U)

[![Github](https://img.shields.io/static/v1?label=Github&message=MAGNA-U&color=red&style=for-the-badge&logo=github)](https://github.com/sammysiegel/MAGNA-U) 

[![Release](https://img.shields.io/github/v/release/sammysiegel/MAGNA-U?logo=github&style=for-the-badge)](https://github.com/sammysiegel/MAGNA-U/releases/latest)

Sammy Siegel, Niels Vanderloo, and Yumi Ijiri
 
*Oberlin College, Department of Physics and Astronomy, Oberlin OH, 44074*

##About
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
|[`MNP_HysteresisDriver`](MNP_HysteresisDriver.md) | A child class of `oommfc.HysteresisDriver` used to run hysteresis drives of a specific `MNP` instance.|
|[`MNP_Analyzer`](MNP_Analyzer.md)| Used to make plots data from MNP drives|
|[`MNP_Hysteresis_Analyzer`](MNP_Hysteresis_Analyzer.md)| Used to make plots and movies from MNP hysteresis drives|
|[`MNP_Domain_Analyzer`](MNP_Domain_Analyzer.md)| Used to analyze the domain regions that are formed in an MNP Assembly


### Functions

| Name | Description |
| :-------: | ------- |
|[`save_mnp`](Save-Load MNPs.md#saving-mnps)| Saves MNP attribute and summary data|
|[`load_mnp`](Save-Load MNPs.md#loading-mnps)| Instantiates an MNP from data stored in files|
|[`quick_drive`](Quick_Drive.md)| Easy way to drive an MNP assembly|

## Changelog
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
- Version 2.3.4 (9 June 2021)
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