# CiteTeX
## A Sublime Text 3 plugin for cite and ref completions

This plugin is not aimed at replacing LaTeXTools, its goal is rather to add some features regarding citation and reference completions.


## Features

### Concerning citations
 - Preview of citation reference when hovered over `\cite{...}`
 - Display of title and year after a citation as a phantom
 - Go to BibTeX entry of reference
 - Preview of rendered entry according to given cite style  
 - Error check of `.bib` files and inline display of warnings
 - Support of multiple `.bib` files (more testing required, though)
 - Add new .bib entry from DOI Link
 - Open URL or DOI in browser

### Concerning references
 - Preview of referenced label when hovering over `\ref{...}`
 - Go to label definition (from hovered reference or by quick menu)
 - Sophisticated reference insertion (see below)
 - locale- and scope-dependent insertion of referenced type

### TODO
 - If resource is stored locally, provide `open document` in popup for quick access
 - Raise warning in case of multiply defined labels or cite keys

### Sophisticated reference insertion

While LaTeXTools provides a fairly helpful completion menu when inserting references, reference insertion of CiteTeX not only lists defined labels, it also lists its labeled title or caption and its origin to make inter-document referencing less painful. When inserting a reference, it recognizes its type (e.g. section, chapter, figure) and prepends its corresponding prefix (i.e. Sec., Ch., Fig.) according to the specified language.


## Installation
So far, this plugin has only been tested on the following Linux distributions:

 - Arch Linux

Testers on Mac and Windows are welcome! (I will not put too much effort in getting it to work under Windows, though.)

### Dependencies
This plugin relies on LaTeX and BibTeX for rendering and handling tex files. Specifically, `latex` and `dvipng` should be availiable in your `PATH`. Other than that, no special python packages or executables are required.

### Temporary files
CiteTeX uses the sublime text cache folder.

### Using the Package
For now, CiteTeX is not in Package Control. I aim to change this, though. For now it is best to clone this repository, and put a symlink into your `.config/sublime-text-3/Packages/` folder (bad luck for Windows users, you have to copy or clone it there):

```(in .config...Packages): ln -s <path to your cloned repo of CiteTeX> CiteTeX ```

Sublime Text will automatically recognize the new Folder as CiteTeX package.

## How To

### Reference completion
Sophisticated reference completion is triggered by typing `ref<TAB>` in a `.tex` file. All defined symbols in other `.tex` files in the same folder will be listed. 