# Delete all recipe images
from os.path import dirname, abspath, join

CWD = dirname(abspath(__file__))
recipe_img_dir = join(CWD, '../app/static/img/recipe_images')
try:
    import shutil
    shutil.rmtree(recipe_img_dir)
    import os
    os.mkdir(recipe_img_dir)
except:
    pass