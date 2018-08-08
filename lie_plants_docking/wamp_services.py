# -*- coding: utf-8 -*-

from lie_plants_docking.plants_docking import PlantsDocking
from lie_plants_docking.utils import (
    copy_exec_to_workdir, prepare_work_dir)
from mdstudio.component.session import ComponentSession
from mdstudio.api.endpoint import endpoint
import base64
import os


class DockingWampApi(ComponentSession):

    def authorize_request(self, uri, claims):
        return True

    @endpoint('docking', 'docking_request', 'docking_response')
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

        # Prepare docking directory
        workdir = os.path.abspath(request['workdir'])
        plants_config["workdir"] = prepare_work_dir(
            workdir, create=True)

        exec_path = request['exec_path']
        encoding = exec_path['encoding'].lower()

        # The binaries are first encode to base64 then decode to ascii
        # To get the original binary the inverse operation is applied
        if 'bytes' == encoding:
            content = exec_path['content']
            binary = base64.b64decode(content.encode())
            copy_exec_to_workdir(binary, workdir)
        else:
            msg = "expecting binary exec_path but the encoding is: {}".format(encoding)
            raise RuntimeError(msg)

        # Run d ocking
        docking = PlantsDocking(**plants_config)
        success = docking.run(
            plants_config['protein_file'], plants_config['ligand_file'])

        if success:
            status = 'completed'
            output = docking.results()
        else:
            self.log.error('PLANTS docking FAILS!!')
            docking.delete()
            status = 'failed'
            output = None

        return {'status': status, 'output': output}
