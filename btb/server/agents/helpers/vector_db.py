import chromadb

class VectorDB:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.collection = self.client.get_or_create_collection("tool_descriptions")

    def clear_collection(self):
        self.client.delete_collection("tool_descriptions")

    def add_tool(self, id: str, description: str):
        # document is description of a tool
        # we need to embed the document and add it to the vector database
        self.collection.add(
            documents=[description],
            ids=[id],
        )

    def query(self, query: str):
        # query is a description of a tool
        # we need to embed the query and search the vector database
        results = self.collection.query(
            query_texts=[query],
            n_results=1,
        )
        return results

    def get_tool(self, id: str):
        # get a tool from the vector database
        results = self.collection.get(
            ids=[id],
        )
        return results

    def remove_tool(self, id: str):
        # remove a tool from the vector database
        self.collection.delete(
            ids=[id],
        )
    
    def update_tool(self, id: str, description: str):

        if description is not None:
            # update a tool in the vector database
            self.collection.update(
                ids=[id],
                documents=[description],
            )
