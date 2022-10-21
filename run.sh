if [ which dpgk-query ]; then
    if [ "$(dpkg-query -W -f='${Version}' python3-venv)" == "" ]; then
        echo "python3-venv not found - installing it with apt"
        sudo apt install python3-venv
    fi
fi
if [ ! -f requirements.txt ]; then
    echo "Cd to dir containing project files!"
else
    if [ ! -d venv ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    if [ ! -d venv/lib/*/site-packages/discord ]; then
        pip3 install -r requirements.txt --user
    fi
    python3 main.py
fi