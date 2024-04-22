# Introduction to MkDocs

This documentation is built with the Material template for MkDocs. The documentation is stored in the main `digital_twin_framework` folder, where the `mkdocs.yml` contains all layout configurations of the webpage (e.g., order of pages, color scheme, etc.) while the folder `digital_twin_framework/docs/` holds the contents of the documentation (e.g., the texts, a folder for images). The documentation could later be published through GitHub Pages. For now let's edit and view it locally. For that, follow the following steps:

* In a terminal, actiavte your virtual/conda environment (if you use one) and navigate to the `digital_twin_framework` root folder.
* Install `mkdocs-material` using `pip install mkdocs-material`. (To check if you have installed the python package manager `pip` run `pip --version`.)
* Run `mkdocs serve` in the terminal to build the documentation locally. In the terminal you will be provided with a localhost link.
* Click the localhost link or copy it into a browser to view the documentation.
* Make changes to the `mkdocs.yml` file or the `docs/*.md` files. Upon saving, the locally hosted website will update auotmatically.

For building this website, I closely followed [this tutorial](https://www.youtube.com/watch?v=Q-YA_dA8C20&t=116s). The detailed documentation of MkDocs can be found [here](https://www.mkdocs.org), the detailed documentation of the Material template can be found [here](https://squidfunk.github.io/mkdocs-material/).


## Overview on some useful feautures

### Create in-line code

Some `code` goes here.

### Create codeblocks for Python and Julia

```py title="code_block.py" linenums="1" hl_lines="3"
def func()
    hello
    hi
    hey
```

```jl
function add_numbers(x, y)
    return x + y
end
```

### Create figures with alignment and captions

![Image title](images/logo_taiger_round.png){ width="200", align=left }

<figure markdown>
  ![Image title](images/logo_taiger_round.png){ width="300" }
  <figcaption>TAiGER's logo</figcaption>
</figure>

### Create admonitions

!!! tip

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et euismod
    nulla. Curabitur feugiat, tortor non consequat finibus, justo purus auctor
    massa, nec semper lorem quam in massa.

### Create text boxes

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.

### Important MkDocs commands

* `mkdocs new [dir-name]` - Create a new project :P.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

### Create footnotes

Some text goes here [^1].

[^1]: "Hey, design a logo for the scientific software TAiGER. Include the head of a tiger carrying a chemical test tube in his paws. Design the logo in a low poly style." https://deepai.org/