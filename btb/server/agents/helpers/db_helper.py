from .postgres import PostgresDB
from .vector_db import VectorDB
import weave

class DBAdapter:
    def __init__(self):
        self.postgres = PostgresDB()
        self.vector_db = VectorDB()

    @weave.op
    def add_tool(self, id, description, arguments, argument_types, env_variables, command, implementation, dependencies):
        # document is description of a tool
        # we need to embed the document and add it to the vector database
        self.postgres.add_tool(id, description, arguments, argument_types, env_variables, command, implementation, dependencies)
        self.vector_db.add_tool(id, description)

    def query(self, query: str):
        return self.vector_db.query(query)

    def get_tool(self, id: str):
        # get a tool from the postgres database
        return self.postgres.get_tool(id)

    def remove_tool(self, id: str):
        # remove a tool from the vector database and postgres database
        self.vector_db.remove_tool(id)
        self.postgres.remove_tool(id)

    def update_tool(self, id, description=None, arguments=None, argument_types=None, env_variables=None, command=None, implementation=None):
        # update a tool in the vector database
        self.postgres.update_tool(id, description, arguments, argument_types, env_variables, command, implementation)
        if description is not None:
            self.vector_db.update_tool(id, description)

    def clear_db(self):
        self.postgres.delete_table()
        self.vector_db.clear_collection()
