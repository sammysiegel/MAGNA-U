# Saving and Loading MNP Data
MAGNA-U has built-in functions to save MNP data to files and to load them later.

The location that files get saved to and can be accessed from is dependent on the
attributes of the MNP that is being saved. By default all of the files can be found in
the directory `{MNP.directory}/{MNP.name}/mnp-{MNP.id}`
## Saving MNPs
If you have generated an MNP object within your code, you can save a record of all of
its basic attributes to a file using the `save_mnp()` function. 

`magna.utils.save_mnp(mnp, summary=True, filepath='default')` 

For the positional argument `mnp`, the function takes an instance of an MNP object. 
 
By default, the file
is saved to the same directory as specified by the `directory` attribute of the MNP,
but you can also change where it gets saved to by passing the argument `filepath` with a
string with the desired directory.

By default, another file is also created which contains a summary of the basic
attributes of the MNP in a markdown format easily readable by a human. If for some
reason you don't want a summary file to be written, pass the argument `summary = False`.

The files that get written will have the names `data_mnp_{id#}.mnp` for the data and
`summary_mnp_{id#}` for the summary files respectively. You should also get printed
confirmation of the file name and path.

## Loading MNPs
You can use the `load_mnp()` function to load an MNP from a file. The function returns an
instance of `MNP` from the file you specify.

`magna.utils.load_mnp(id, name='lattice', filepath='./MNP_Data', fields='')`

Give the id number of the MNP with the positional `id` argument , the name of the MNP with the keyword argument
`name`, and the and the directory of the MNP with the keyword argument `filepath`. The default
filepath is `'./MNP_Data'`. 

Additionally, you can have m, a, k, and/or u fields be preloaded from files by passing the
`fields` argument with a string containing the fields you want to be loaded. None will be
loaded by default, but you could might want to pass `fields = 'maku'`, for example. The fields
that you want to load have to already be saved to that MNP's data folder.