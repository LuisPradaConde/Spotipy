#!bin/bash
 
docker pull borjius99/pi-borja-luis-pablo:entrega

docker run -itd -p 8000:8000 borjius99/pi-borja-luis-pablo:entrega python3 musicpy/manage.py runserver 0.0.0.0:8000
