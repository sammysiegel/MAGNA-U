# MNP Domain Analyzer

The `MNP_Domain_Analyzer` class can be used to analyze domain regions formed in an MNP
Assembly. It is a child class of `MNP_Analyzer`.

```python
magna.utils.MNP_Domain_Analyzer
```
### Attributes:
 - All of those attributes of `mu.MNP_Analyzer`, plus:
     - `d_theta`: the offset in the colatitude when creating discretized domain regions, in degrees.
     - `d_theta`: the offset in the longitude when creating discretized domain regions, in degrees.

## Plots
There are two 3D plots you can create to visualize the domain regions in an MNP
Assembly:

### Spherical Regions Plot
```python
MNP_Domain_Analyzer.plot_regions(cmap='hsv', 
                                 point_size=.9, 
                                 scale=(1, 1, 1))
```
This method plots the different regions by representing each MNP as a sphere,
where MNPs in the same region are plotted in the same color. The color scheme
is given by `cmap`, which by default is `'hsv'`.  `point_size` sets the size
of the spheres, and you can scale the x, y, and z dimensions with `scale`, where
scale takes a tuple in the form `(x scale, y scale, z scale)`.

### Vector Regions Plot
```python
MNP_Domain_Analyzer.plot_regions_vectors(cmap='hsv', 
                                         head_size=2, 
                                         scale=(1, 1, 1))
```
This method plots the different regions by representing each MNP as a vector,
where MNPs in the same region are plotted in the same color. The color scheme
is given by `cmap`, which by default is `'hsv'`.  `head_size` sets the size
of the vector head, and you can scale the x, y, and z dimensions with `scale`, where
scale takes a tuple in the form `(x scale, y scale, z scale)`.

## Data
Before analyzing data, run the `MNP_Domain_Analyzer.find_regions()` method,
which will determine the sizes of each domain in the MNP Assembly.

From there, you can analyze the following domain size statistics:

- Number of Regions: The total number of domain regions within the MNP Assembly
- Characteristic Size: A weighted average representing the typical size of a domain
region in an MNP Assembly, given by:     
   <img src="https://latex.codecogs.com/gif.latex?\frac{1}{\mathrm{Number&space;\&space;of&space;\&space;MNPs}}\sum_{\mathrm{Regions}}(\mathrm{Region&space;\&space;Size})^2" title="\frac{1}{\mathrm{Number \ of \ MNPs}}\sum_{\mathrm{Regions}}(\mathrm{Region \ Size})^2" />

- Max Size: The largest domain region size.
- Average Size: An unweighted average of region sizes.
- Free Particle Fraction: The fraction of MNPs that are not in a domain (that is,
  the number of MNPs in a region of size 1).
- 2-3 Particle Fraction: The percentage of MNPs in an assembly that are in a domain size of either two or three.
  
You can view all of these statistics using the `MNP_Domain_Analyzer.domains_summary()` method,
which returns a formatted summary which also lists the total number of regions and
the size of each region.

You can save the domain region data to a file using the `MNP_Domain_Analyzer.save_domains()`,
method, which saves the summary to a markdown file and the raw data to a
`'domain_data_mnp_{}.csv'` file, both in the mnp's data folder.

## Extracting Data From Multiple MNP Folders
If you have a `'domain_data_mnp_{}.csv'` in multiple mnp folders with the same
name (root folder), you can extract them to a combined csv file.
```python
magna.utils.extract_domain_csv(name,
                               number=27,                            
                               filepath='./MNP_Data', 
                               filename='domain_data.csv', 
                               mode='w', 
                               B=0.001)
```
Note: This function is part of the larger `magna.utils` package, not the `MNP_Domain_Analyzer` class.

The required positional argument `name` is the name of each mnp, or, if you
are storing data in a folder not using the standard MAGNA-U file organization,
this is the *name* of the folder containing the mnp folders. `number` is the number
of MNPs from which you wish to extract data, which is 27 by default. `filepath` is the
path to this aformentioned name folder. `filename` is the desired path/name of the
output file, which by default is `domain_data.csv`. `mode` determines how data
is added to the csv file. If `mode='w'` (write), data is added by overwriting
anything that may already be in the file. If `mode='a'` (append), data is added
at the end of the file, preserving anything that is already there.

`B` is an optional keyword argument which is intended to be used with MNP data generated before drive `.json` files were introduced in Version 2.6.0. You can use this to manually specify the field value (in T).

## Analysis with Multiple Values of &Delta;&theta; and &Delta;&phi;
If you are interested not in one particular orientation of the discretization regions but rather
want to see the effect of applying many orientations, you can use the 
`mu.MNP_Domain_Analyzer.save_averaged_data()` method. This function automatically goes through over
800 possible values of `d_theta` and `d_phi`. It writes the file `axes_range_data_{step #}.csv` in
the MNP's file folder which contains the &Delta;&theta; and &Delta;&phi;, Characteristic Domain Size, 
Max Domain Size, Free Particle Fraction, and 2-3 Particle Fraction for each MNP. `{step #}` is a placeholder for whatever the value of the `step` attribute for the `MNP_Domain_Analyzer` instance is.

## Extracting Average Values from `extract_average_domain_data()` for Mulitple MNPs
If you have a folder of MNPs for which you have already extracted the `axes_range_data` csv
files, you can average the statistics over all values of &Delta;&theta; and &Delta;&phi; and
combine these statistics from all MNPs in one place with `mu.extract_average_domain_data`.

```python
magna.utils.extract_average_domain_data(name, 
                                       filename='sorted_data.csv', 
                                       mode='w', 
                                       start=0, 
                                       end=36, 
                                       start_steps = 0, 
                                       end_steps=None)
```
Here, `name` is the name of the folder located in `./MNP_Data` containing the MNPs you wish to 
extract data from. `filename` is the desired output destination. The mode `w` writes a new file,
overwriting anything that may already be there, while `a` appends to an existing file. `start` 
is the starting MNP id to iterate through and `end` is the ending MNP id (exclusive).
If you wish to extract data for several steps of an MNP, `start_steps` is the starting step number and `end_steps` is the ending step number. If using `axes_range_data` csv files that don't have the step number in their name (all files generated before Version 2.7.0), leave `start_steps` and `end_steps` as their default values.