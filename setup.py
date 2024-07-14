from setuptools import setup

setup(
    name="wind2json",
    version="1.0.3",
    description="decode CMA grid-wind product",
    long_description="decode CMA grid-wind product data to leaflet-velocity json type,see https://github.com/pysoer/gridwind2json",
    license="GPL Licence",
    author="pysoer",
    author_email="413188893@qq.com",
    packages=["wind2json"],
    include_package_data=True,
    platforms="Windows",
    python_requires=">=3.5",
    install_requires=["meteva"],
    package_dir={"wind2json": "wind2json"}
)
