from setuptools import setup

def readme():
    with open('README.txt') as f:
        return f.read()

setup(name='HL7py',
      version='1.0',
      description='HL7 message parser',
      long_description=readme(),
      keywords='hl7 parsing ',
      url='https://github.com/norlowski/HL7py',
      author='Nicholas Orlowski',
      author_email='nick.orlowski@gmail.com',
      license='MIT',
      packages=['HL7py'],
      zip_safe=False)
