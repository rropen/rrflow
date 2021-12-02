from fastapi import Query
from rrflow.utility_classes import OID
import rrflow.utils as utils

class Program_Params:
    """
    Custom parameter class for GET flow metric routes.
    This format enables a custom description field for each parameter that will display
    in the backend swagger docs.
    """
    def __init__(
        self,
        program_name: str = Query(
            None,
            description="This parameter selects the program by name.",
        ),
        program_id: OID= Query(
            None,
            description="This parameter selects the program by ID.",
        ),
    ):

        self.program = utils.program_selector(program_name, program_id)
        self.program_id = self.program.id
        self.program_name = self.program.name