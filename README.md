# CiteTeX
## A Sublime Text 3 plugin for cite and ref completions

This plugin is not aimed at replacing LaTeXTools, its goal is rather to add some features regarding citation and reference completions.

## Disclaimer
Despite being stable for quite a time now, I cannot guarantee that errors may affect or even destroy you bib files.
I am not responsible for any damage caused by this plugin, directly or indirectly. That includes in particular corruption or loss of you BibTeX files. Make sure you have a backup!

## How To Use

### Reference completion
Sophisticated reference completion is triggered by typing `ref<TAB>` in a `.tex` file. All defined symbols in other `.tex` files in the same folder will be listed. 

### Resource management

In order to access resources (e.g. PDFs) directly via popups, declare `resource_root` in your project settings:

```
	"settings": {
		"TEXroot": "main.tex",
		"output_directory": "./build",
		"resource_root": "your resource directory here"
	}
```

To link a PDF to your BibTeX entry, add the BibTeX entry to your .bib file. With your .bib file currently open, run the ``Citetex: Add resource to bibentry`` command e.g. via the quick command menu (Ctrl+Shift+P).
You are given a preview list of existent keys and their titles, select the one you want the resource to be added to. In the subsequent menu, you may select your PDF file. Note that it has to be in the folder you specified in your resource_root folder.

The reason why I built it this way is that you may have a Git project for your TeX work, but do not necessarily want to include your PDF material in it. Using this method, you have a per-project folder for your material separated from your work.

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
 - If resource is stored locally, PDF can be opened directly
 - For resources, a 'base' directory must be specified
 - Open PDF resource directly via quick menu

### Concerning references
 - Preview of referenced label when hovering over `\ref{...}`
 - Go to label definition (from hovered reference or by quick menu)
 - Sophisticated reference insertion (see below)
 - locale- and scope-dependent insertion of referenced type

### TODO
 - Raise warning in case of multiply defined labels or cite keys
 - Add support for other types of material (e.g. images)
 - Mac OS, Windows support

### Sophisticated reference insertion

While LaTeXTools provides a fairly helpful completion menu when inserting references, reference insertion of CiteTeX not only lists defined labels, it also lists its labeled title or caption and its origin to make inter-document referencing less painful. When inserting a reference, it recognizes its type (e.g. section, chapter, figure) and adds its corresponding prefix (i.e. Sec., Ch., Fig.) according to the specified language.


## Installation
So far, this plugin has only been tested on the following operating systems:

 - Arch Linux
 - Windows 10

Testers on Mac and Windows are welcome! (I will not put too much effort in getting it to work under Windows, though.)

### Windows
On Windows, you must have MikTeX or similar installed and added to your PATH. Serveral packages may have to be installed in MikTeX (use its Package Manager).

In the `Citetex-default.sublime-settings` file, change `open_resource_pdf` to "C:\\Program Files\\ your PDF READER.exe",

### Dependencies
This plugin relies on LaTeX and BibTeX for rendering and handling tex files. Specifically, `latex` and `dvipng` should be available in your `PATH` (executables are included in TeX packages normally). 

For proper biblatex support, the `LaTeXTools` sublime package is required (provides the Biblatex syntax scheme in Sublime).

## Temporary files
CiteTeX uses a subfolder of the sublime text cache folder.

## Known issues
It may take while to index all entries and provide renderings for the popups when Sublime Text is started. On windows, cite preview rendering is slow.

# Questions?
Send me an e-mail: afk (at) daichronos (dot) net