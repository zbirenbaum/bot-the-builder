# Check if the table exists before creating it
import psycopg2

conn = psycopg2.connect(database="postgres", user='postgres', password='postgres', host="localhost", port=5432)
cursor = conn.cursor()

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(database="postgres", user='postgres', password='postgres', host="localhost", port=5432)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        sql_context = """
        CREATE TABLE IF NOT EXISTS tools (
            id TEXT PRIMARY KEY,                  -- Unique identifier for each tool
            description TEXT NOT NULL,            -- Description of what the tool does
            arguments TEXT,                       -- Comma-separated list of input parameters
            argument_types TEXT,                  -- Comma-separated list of input parameter types
            env_variables TEXT,                   -- Comma-separated list of environment variables to load
            command TEXT,                         -- The command to run the tool
            implementation TEXT NOT NULL,         -- The actual code implementation of the tool
            dependencies TEXT NOT NULL            -- The actual code implementation of the tool
        );
        """
        self.cursor.execute(sql_context)
        self.conn.commit()

    def delete_table(self):
        sql_context = """
        DROP TABLE IF EXISTS tools;
        """
        self.cursor.execute(sql_context)
        self.conn.commit()

    def add_tool(self, id, description, arguments, argument_types, env_variables, command, implementation, dependencies):
        sql_context = """
        INSERT INTO tools (id, description, arguments, argument_types, env_variables, command, implementation, dependencies)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        self.cursor.execute(sql_context, (id, description, arguments, argument_types, env_variables, command, implementation, dependencies))
        self.conn.commit()

    def remove_tool(self, id):
        sql_context = """
        DELETE FROM tools WHERE id = %s;
        """
        self.cursor.execute(sql_context, (id,))
        self.conn.commit()

    # Take a series of optional arguments and update the tool with the new values
    def update_tool(self, id, description=None, arguments=None, argument_types=None, env_variables=None, command=None, implementation=None, dependencies=None):
        prefix = "UPDATE tools SET"
        if description is not None:
            prefix += " description = %s, "
        if arguments is not None:
            prefix += " arguments = %s, "
        if argument_types is not None:
            prefix += " argument_types = %s, "
        if env_variables is not None:
            prefix += " env_variables = %s, "
        if command is not None:
            prefix += f" command = '{command}', "
        if implementation is not None:
            prefix += f" implementation = '{implementation}', "
        if dependencies is not None:
            prefix += f" dependencies = '{dependencies}', "

        suffix = "WHERE id = %s;"
        prefix += suffix

        params = []
        if description is not None:
            params.append(description)
        if arguments is not None:
            params.append(arguments)
        if argument_types is not None:
            params.append(argument_types)
        if env_variables is not None:
            params.append(env_variables)
        if command is not None:
            params.append(command)
        if implementation is not None:
            params.append(implementation)
        if dependencies is not None:
            params.append(dependencies)
        params.append(id)
        self.cursor.execute(prefix, params)
        self.conn.commit()

    # Get a tool from the database by id
    def get_tool(self, id):
        sql_context = """
        SELECT * FROM tools WHERE id = %s;
        """
        self.cursor.execute(sql_context, (id,))
        result = self.cursor.fetchone()
        print(result)
        if result:
            return {
                "id": result[0],
                "description": result[1],
                "arguments": result[2],
                "argument_types": result[3],
                "env_variables": result[4],
                "command": result[5],
                "implementation": result[6],
                "dependencies": result[7]
            }
        print(f"ERROR(401): Tool {id} not found")
        return None
