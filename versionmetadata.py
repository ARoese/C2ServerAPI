import pyinstaller_versionfile
import os

full_version = None


with open("pyproject.toml", "r") as f:
    for line in f.readlines():
        if "version" in line:
            line = line.strip()
            line = line.replace('"', '')
            line = line.replace("'", '')
            line = line.replace(' ', '')
            line = line.replace('version=', '')
            full_version = line
            break

if full_version is None:
    raise RuntimeError("Could not find version in pyproject.toml")


publish_version = '.'.join(full_version.split('.')[:3])

print(f"Building version metadata for {publish_version}")

if not os.path.exists("build"):
    os.mkdir("build")

pyinstaller_versionfile.create_versionfile(
    output_file=".\\build\\versionfile.rc",
    version=publish_version,
    company_name="Chivalry 2 Unchained",
    file_description="An interface with the unofficial chivalry 2 unchained server browser backend",
    internal_name="RegisterUnchainedServer",
    original_filename="RegisterUnchainedServer.exe",
    product_name="Chivalry 2 RCON Interface",
)