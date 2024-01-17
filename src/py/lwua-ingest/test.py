import os
CURRENTPATH = os.path.dirname(os.path.realpath(__file__))
PROJECTPATH = os.path.abspath(os.path.join(CURRENTPATH, '..', '..', '..'))

print(CURRENTPATH)
print(PROJECTPATH)