from cx_Freeze import setup, Executable

executables = [Executable("find_socials.py")]

setup(
    name="FindSocials",
    version="1.0",
    description="Your application description",
    executables=executables
)
