from setuptools import find_packages, setup


def read_requirements(filename="requirements.txt"):
    "Read the requirements"
    with open(filename) as f:
        return [line.strip() for line in f \
                if line.strip() and \
                line[0].strip() != '#' and \
                not line.startswith('-e ')]


def get_version(filename='diet/__init__.py', name='VERSION'):
    "Get the version"
    with open(filename) as f:
        s = f.read()
        d = {}
        exec(s, d)
        return d[name]


setup(
    name='django-hackers-diet',
    version=get_version(),
    author='Dave Gabrielson',
    author_email='Dave.Gabrielson@gmail.com',
    description='Hackers Diet, DCG implementation',
    url="",
    license="",
    packages=find_packages(),
    install_requires=read_requirements(),
    zip_safe=False,
    include_package_data=True,
)
