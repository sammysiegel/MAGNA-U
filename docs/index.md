# MAGnetic Nanoparticle Assembly Utilities (MAGNA-U)

Github: [https://github.com/sammysiegel/MAGNA-U](https://github.com/sammysiegel/MAGNA-U).

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

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.


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