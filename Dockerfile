FROM mdstudio/mdstudio_docker3:0.0.3

COPY . /home/mdstudio/mdstudio_plants_docking

RUN chown mdstudio:mdstudio /home/mdstudio/mdstudio_plants_docking

WORKDIR /home/mdstudio/mdstudio_plants_docking

RUN pip install numpy scipy && pip install .

# USER mdstudio

CMD ["bash", "entry_point_mdstudio_plants_docking.sh"]
