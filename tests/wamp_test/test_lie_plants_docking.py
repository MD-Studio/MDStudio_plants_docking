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
        u'path': path, u'content': content,
        u'extension': extension}


workdir = u"/tmp"

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
            u"mdgroup.mdstudio_plants_docking.endpoint.docking",
            {u"protein_file": protein_file,
             u"ligand_file": ligand_file,
             u"min_rmsd_tolerance": 3.0,
             u"cluster_structures": 100,
             u"bindingsite_radius": 12.0,
             u"bindingsite_center": [4.926394772324452, 19.079624537618873, 21.98915631296689],
             u"workdir": workdir})

        if result['status'] != 'completed':
            raise AssertionError('Docking failed, status: {0}'.format(result['status']))
        if not all('path' in val for _, val in result['output'].items()):
            raise AssertionError('Not all expected output files created')
        print("Docking finished successfully!")


if __name__ == "__main__":
    main(Run_docking)
