from mdstudio.deferred.chainable import chainable
from mdstudio.component.session import ComponentSession
from mdstudio.runner import main
import base64
import os


def create_path_file_obj(path, encoding='utf8'):
    """
    Encode the input files
    """
    extension = os.path.splitext(path)[1]
    mode = 'rb' if encoding == 'bytes' else 'r'
    with open(path, mode) as f:
        content = f.read()
    if encoding == 'bytes':
        content = base64.b64encode(content).decode('ascii')

    return {
        'path': path, 'encoding': encoding,
        'content': content, 'extension': extension}


workdir = "/tmp/lie_plants_docking"
cwd = os.getcwd()
os.makedirs(workdir, exist_ok=True)

protein_file = create_path_file_obj(
    os.path.join(cwd, "DT_conf_1.mol2"))
ligand_file = create_path_file_obj(
    os.path.join(cwd, "ligand.mol2"))
exec_path = create_path_file_obj(
    os.path.join(cwd, "plants_linux"), encoding='bytes')


class Run_docking(ComponentSession):

    def authorize_request(self, uri, claims):
        return True

    @chainable
    def on_run(self):
        result = yield self.call(
            "mdgroup.lie_plants_docking.endpoint.docking",
            {"protein_file": protein_file,
             "ligand_file": ligand_file,
             "min_rmsd_tolerance": 3.0,
             "cluster_structures": 100,
             "bindingsite_radius": 12.0,
             "bindingsite_center": [
                 4.926394772324452, 19.079624537618873, 21.98915631296689],
             "workdir": workdir,
             "exec_path": exec_path})
        assert result['status'] == 'completed'


if __name__ == "__main__":
    main(Run_docking)
