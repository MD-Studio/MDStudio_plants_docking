# -*- coding: utf-8 -*-

import os
from autobahn.wamp import RegisterOptions

from mdstudio_plants_docking.plants_docking import PlantsDocking
from mdstudio_plants_docking.utils import prepare_work_dir
from mdstudio.component.session import ComponentSession
from mdstudio.api.endpoint import endpoint


def encoder(file_path):
    """
    Encode the content of `file_path` into a simple dict.
    """
    extension = os.path.splitext(file_path)[1]

    return {"path": file_path, "extension": extension.lstrip('.'),
            "content": None, "encoding": "utf8"}


def encode_file(d):
    """ Serialize the file containing the molecular representation"""
    d['path'] = encoder(d['path'])
    return d


class DockingWampApi(ComponentSession):

    def authorize_request(self, uri, claims):
        return True

    @endpoint('docking', 'docking_request', 'docking_response', options=RegisterOptions(invoke='roundrobin'))
    def run_docking(self, request, claims):
        """
        Perform a PLANTS (Protein-Ligand ANT System) molecular docking.
        For a detail description of the input see the file:
        schemas/endpoints/docking-request.v1.json
        """
        task_id = self.component_config.session.session_id
        self.log.info("Plants Docking ID: {}".format(task_id))

        # Docking options are equal to the request
        plants_config = request.copy()

        # Transfer the files content
        plants_config['protein_file'] = request['protein_file']['content']
        plants_config['ligand_file'] = request['ligand_file']['content']

        # Prepare docking directory
        workdir = os.path.abspath(request['workdir'])
        plants_config["workdir"] = prepare_work_dir(
            workdir, create=True)

        # location of the executable
        file_path = os.path.realpath(__file__)
        root = os.path.split(file_path)[0]

        plants_config['exec_path'] = os.path.join(root, 'plants_linux')

        # Run docking
        docking = PlantsDocking(**plants_config)
        success = docking.run(plants_config['protein_file'], plants_config['ligand_file'])

        if success:
            status = 'completed'
            results = docking.results()
            output = {key: encode_file(value) for key, value in results.items()}

            # Add path to cluster dendrogram
            clusterplot = os.path.join(workdir, 'cluster_dendrogram.pdf')
            if os.path.isfile(clusterplot):
                results['clusterplot'] = {'content': None, 'extension': 'pdf', 'path': clusterplot}

        else:
            self.log.error('PLANTS docking FAILS!!')
            docking.delete()
            status = 'failed'
            output = None

        return {'status': status, 'output': output}
