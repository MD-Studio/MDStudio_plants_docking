from mdstudio.deferred.chainable import chainable
from mdstudio.component.session import ComponentSession
from mdstudio.runner import main
import os

file_path = os.path.realpath(__file__)
root = os.path.split(file_path)[0]


def create_path_file_obj(path):
    """
    Encode the input files
    """
    extension = os.path.splitext(path)[1]
    with open(path, 'r') as f:
        content = f.read()

    return {
        'path': path, 'content': content,
        'extension': extension}


workdir = "/tmp"
cwd = os.getcwd()
os.makedirs(workdir, exist_ok=True)

protein_file = create_path_file_obj(
    os.path.join(root, "DT_conf_1.mol2"))
ligand_file = create_path_file_obj(
    os.path.join(root, "ligand.mol2"))


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
             "workdir": workdir})

        assert result['status'] == 'completed'
        print("Docking finished successfully!")


if __name__ == "__main__":
    main(Run_docking)
