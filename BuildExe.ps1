poetry install
poetry run python .\versionmetadata.py
poetry run pyinstaller .\src\main.py -F -n RegisterUnchainedServer -p .\src\ --version-file=.\build\versionfile.rc
poetry run pip-licenses --format=plain-vertical --with-license-file --no-license-path | Out-File dist\Licenses.txt