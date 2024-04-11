FROM python:3.8-slim

COPY cplex_studio2210.linux_x86_64.bin installer.properties /tmp/

WORKDIR /tmp/

RUN chmod +x cplex_studio2210.linux_x86_64.bin && ./cplex_studio2210.linux_x86_64.bin -f "./installer.properties" && rm cplex_studio2210.linux_x86_64.bin

WORKDIR /opt/ibm/ILOG/CPLEX_Studio221/cplex/python/3.8/x86-64_linux

RUN python3 setup.py install

#RUN python /opt/ibm/ILOG/CPLEX_Studio221/python/setup.py install