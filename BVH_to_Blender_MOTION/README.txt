python 3.10.8 install 
blender 3.3.2 install 

C:\Program Files\Blender Foundation\Blender 3.3\3.3 -> python folder right click -> properties -> security -> Users -> edit -> Users -> write right check apply

pip install fake-bpy-module-latest for bpy
download blender extension created by Jacques Lucke
ctrl + shift + p -> blender : start -> choose a new blender executable -> select blender.exe -> vscode ctrl + shift + p -> blender : run script


**SQL ODBC 설정**

if ! [[ "18.04 20.04 22.04 23.04" == *"$(lsb_release -rs)"* ]];
then
    echo "Ubuntu $(lsb_release -rs) is not currently supported.";
    exit;
fi

curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc

curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
# optional: for bcp and sqlcmd
sudo ACCEPT_EULA=Y apt-get install -y mssql-tools18
echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
source ~/.bashrc
# optional: for unixODBC development headers
sudo apt-get install -y unixodbc-dev

pip install pyodbc