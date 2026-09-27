from pythonforandroid.recipe import CythonRecipe


class PygameRecipe(CythonRecipe):
    version = "2.6.1"
    url = "https://github.com/pygame/pygame/releases/download/2.6.1/pygame-2.6.1.tar.gz"
    depends = ["python3", "sdl2", "sdl2_image", "sdl2_mixer", "sdl2_ttf"]
    cythonize = False


recipe = PygameRecipe()
