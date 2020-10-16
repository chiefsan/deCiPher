from setuptools import setup, find_packages
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    REQUIRED_PACKAGES = f.read().splitlines()

setup(
    name="deCiPher",
    version="0.0.1",
    description="Decipher programming problems",
    url="https://github.com/chiefsan/deCiPher",
    author="Sanjay Seetharaman",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    include_package_data=True,
    # packages=["decipher", "decipher.scripts", "decipher.framework", "decipher.codeforces_scraper"],
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    entry_points={
        "console_scripts": [
            "decipher_setup_initial_db=decipher.scripts.fill_db_init:main",
            "decipher_scrap_cf_problemset=decipher.scripts.scrap_codeforces_problemset:main"
        ]
    },
)
