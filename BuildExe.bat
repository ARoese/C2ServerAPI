poetry install
poetry run pyinstaller .\src\main.py -F -n RegisterUnchainedServer -p .\src\
move dist\RegisterUnchainedServer.exe .
del RegisterUnchainedServer.spec