import chromadb
import uuid


class VectorDbUtils:
    def __init__(self):
        self.persist_directory = "./.chromadb_persist"

    def create_collection(self, pdf_name, username):
        client = self.get_client()
        collection_name = f"{pdf_name}_{username}"
        client.create_collection(collection_name)

    def get_client(self):
        return chromadb.PersistentClient(path=self.persist_directory)

    def upload_chunks(self, pdf_name, username, vectors):
        client = self.get_client()
        collection_name = f"{pdf_name}_{username}"

        try:
            collection = client.get_collection(collection_name)

        except Exception as e:
            print(e)
            del client
            return

        ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        collection.add(
            ids=ids,
            documents=vectors,
        )

        del client

    def get_users_pdfs(self, username):
        user_pdfs = []
        client = self.get_client()
        for collection in client.list_collections():
            if collection.name.endswith(f"_{username}") and not collection.name.startswith("description"):
                user_pdfs.append(collection.name.split(f"_{username}")[0])

        del client
        return user_pdfs

    def get_description_collection(self, username):
        client = self.get_client()
        collection_name = f"description_{username}"
        try:
            collection = client.get_collection(collection_name)
        except Exception as e:
            client.create_collection(collection_name)
            collection = client.get_collection(collection_name)
        del client
        return collection
    def get_collection(self, pdf_name, username):
        client = self.get_client()
        collection_name = f"{pdf_name}_{username}"
        collection = client.get_collection(collection_name)
        del client
        return collection

    def get_chunks(self, collection_name, username, n_results, search_query):
        client = self.get_client()
        collection_name = f"{collection_name}_{username}"
        collection = client.get_collection(collection_name)
        del client
        return collection.query(query_texts=search_query, n_results=n_results)

    def delete_collection(self, pdf_name, username):
        client = self.get_client()
        collection_name = f"{pdf_name}_{username}"
        client.delete_collection(collection_name)

        # Delete the collection from description collection
        description_collection_name = f"description_{username}"

        try:
            description_collection = client.get_collection(description_collection_name)
        except Exception as e:
            print(e)
            del client
            return

        description_collection.delete(ids=[collection_name])
        del client

    def add_to_description_collection(self, username, file_name, description):
        client = self.get_client()
        collection_name = f"description_{username}"
        file_name = f"{file_name}_{username}"

        try:
            collection = client.get_collection(collection_name)
        except Exception as e:
            client.create_collection(collection_name)
            collection = client.get_collection(collection_name)

        collection.add(
            ids=[file_name],
            documents=[description],
        )
        del client

    def check_pdf_name(self, pdf_name, username):
        client = self.get_client()
        collection_name = f"{pdf_name}_{username}"
        try:
            _ = client.get_collection(collection_name)
            del client
            return False
        except Exception as e:
            return True

    def clear_all_collections(self):
        client = self.get_client()
        collections = client.list_collections()
        for collection in collections:
            client.delete_collection(collection.name)
        del client

    def get_all_documents(self, collection_name):
        client = self.get_client()
        collection = client.get_collection(collection_name)
        documents = collection.get(limit=100)
        del client
        return documents



if __name__ == "__main__":
    vdb = VectorDbUtils()

    dummy_files = [
        "pdf1",
        "pdf2",
        "pdf3",
    ]
    dummy_description = [
        "This pdf contains information about operating systems",
        "This pdf contains information about databases",
        "This pdf contains information about programming languages",
    ]

    client = vdb.get_client()
    client.get_or_create_collection("test_berkaybgk")

    collection = client.get_collection("test_berkaybgk")

    collection.add(
        ids = dummy_files,
        documents=dummy_description
    )

    descriptions = collection.get(limit=100)
    files = descriptions.get("ids")
    descriptions = descriptions.get("documents")


    # print(vdb.client.get_settings())

    # print(vdb.get_client().list_collections())
    #
    # try:
    #     vdb.client.get_collection("new_collection")
    # except Exception as e:
    #     vdb.client.create_collection("new_collection")
    #
    # print(vdb.client.list_collections())

    # vdb.client.reset()

    # docs = vdb.get_all_documents("description_berkaybgk")
    # print(docs)



