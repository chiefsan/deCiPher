# deCiPher

_deCiPher_ is a package for deciphering programming problems.

## Install

It is recommended to run deCiPher in a conda environment. For instructions on how to install conda go to this link: https://docs.anaconda.com/anaconda/install/

With conda installed, run these commands to create a new conda environment and download and install deCiPher:

```shell
git clone https://github.com/chiefsan/deCiPher.git
cd deCiPher
conda env create
conda activate deCiPherenv
pip install .
```

**Use deCiPher without conda**

```shell
git clone https://github.com/chiefsan/deCiPher.git
cd deCiPher
pip install .
```





## Getting Started

If you installed deCiPher with conda, you should always make sure the `decipherenv` virtual environment is activated before running deCiPher commands. To activate the environment use:

```shell
conda activate decipherenv
```

### 1. Scraping the codeforces problemset

Once the package has been installed, run the following command to scrap the codeforces problemset:

```shell
decipher_scrap_codeforces_problemset
```

This will create a file `problemset.json` in the package installation path.

### 2. Creating the database

Once the problemset has been scrapped, run the following command to create the database:

```shell
decipher_setup_initial_db
```

**SQLite**

On Linux/Mac you should get a file `/tmp/data.db` containing the database. On Windows you should get a file `data.db` in the  temporary directory returned by the python [tempfile module](https://docs.python.org/3/library/tempfile.html) on your system.

**PostgreSQL**

Create a database and set the environment variable `DATABASE_URL` to point to the URL of the PostgreSQL database. Example: `postgres://chiefsan:password@127.0.0.1:5432/decipher`.

## Docs

The docs can be found [here](https://chiefsan.github.io/deCiPher/docs).
