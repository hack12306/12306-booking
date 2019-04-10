
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="12306-booking",
    version="0.1.18",
    author="Meng.yangyang",
    author_email="mengyy_linux@163.com",
    description="12306 booking assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/hack12306/12306-booking",
    packages=setuptools.find_packages(include=['booking']),
    # include_package_data = True,
    package_data={'': ['station_list.json', 'train.mp3', 'login.wav', '*.html']},
    install_requires=["hack12306>=0.1.16", "click==7.0", "six>=1.12.0", "prettytable==0.7.2"],
    entry_points={
        'console_scripts': [
            '12306-booking=booking.command:booking',
            '12306=booking.command:cli',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
