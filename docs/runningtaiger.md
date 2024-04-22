# Running TAiGER

The goal of this section is to provide instructions on running TAiGER on your local machine.

## Installations

Start by copying the `digital_twin_framework` repository to your computer, either manually or using Git. The following steps assume that you have conda installed on your system.

1. Open a terminal window and navigate to the folder `digital_twin_framework`.
2. Create a conda environment with the essential packages using the following command.
```
conda create --name digital_twin_environment --file requirements.txt
```
3. Activate your environment using the following command.
```
conda activate digital_twin_environment
```
4. Use `pip install mkdocs-material=9.5.18` to install MkDocs-Material, which is needed for compiling this documentation.
5. Check out the file `digital_twin_framework/run_file.py` and adjust the settings to your need (see next section).
6. Run the file `digital_twin_framework/run_file.py`.

!!! Note
    As **alternative to steps 2 and 3**, execute the following steps one by one in this order:
    ```
    conda create --name digital_twin_environment python=3.10
    conda activate digital_twin_environment
    conda install -c conda-forge ipopt=3.11.1
    conda install numpy=1.25.0
    conda install pandas=1.5.3
    conda install -c conda-forge pyomo=6.6.1
    conda install -c conda-forge matplotlib=3.7.1
    ```
    Expect the installation of pyomo to take a few minutes.





## Choose workflow modus and settings

t.b.d.


