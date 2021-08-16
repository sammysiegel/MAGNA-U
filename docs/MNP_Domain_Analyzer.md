# MNP Domain Analyzer

The `MNP_Domain_Analyzer` class can be used to analyze domain regions formed in an MNP
Assembly. It is a child class of `MNP_Analyzer`.

```python
magna.utils.MNP_Domain_Analyzer
```

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
