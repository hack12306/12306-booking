
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="booking",
    version="0.0.1",
    author="Meng yangyang",
    author_email="mengyy_linux@163.com",
    description="12306 booking tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/hack12306/12306-booking",
    packages=setuptools.find_packages(),
    install_requires=["Pillow>=5.4.1", "hack12306>=0.1.2", "click==7.0"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
