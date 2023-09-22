How to use Sphinx for Documentation:
# prerequisites
The packages that are imported in `conf.py` must be installed.
Also, python is therefore also necessary

# Building the html
Simply run
```
make html
```

# Checking your changes
After builing the html (`make html`), simly run e.g. 
```
firefox ./_build/html/index.html
```
or simply open the `index.html` file via some file manager in the browser

Most browsers should support clicking through the pages

# Structure
Generally, the documentation consists of an index (`index.rst`) and 
multiple documentation pages (`rst` and `md` files)
For syntax of rst/md especially concerning referencing of e.g. the code, checkout
how it's done in `getting_started.rst`

## How to add to an existing page
Simply add code in the correct syntax to the relevant file, e.g. add code in
`rst` syntax to `getting_started.rst`

## Add a new page
Create a new `md` or `rst` file and give it's filename in `index.rst`, as it
was done already with e.g. `getting_started.rst`
Generally, `rst` format seems to be more powerful than `md`, but use whatever
format is comfortable or enough.
Sphinx probably supports more formats, but `conf.py` must be changed for 
support for other packages

## Code documentation
The code documentation is read automatically from the docstrings, so simply 
change the docstrings of e.g. the AppState class. If you want to add anything 
else or change the order of the code documentation, checkout `code.rst`

