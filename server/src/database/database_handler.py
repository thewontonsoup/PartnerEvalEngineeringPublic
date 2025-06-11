"""
chromadb setup and wrapper methods with relevant docstrings

Reference:
    https://docs.trychroma.com/docs/overview/introduction

Dependencies:
    1. chromadb
        pip install chromadb
    2. openai
        pip install openai

Notes:
    Find more embedding models:
        SentenceTransformers models here https://www.sbert.net/docs/sentence_transformer/pretrained_models.html
        OpenAI models here https://platform.openai.com/docs/guides/embeddings#embedding-models
    For metadata filtering:
        https://docs.trychroma.com/docs/querying-collections/metadata-filtering
    For text filtering:
        https://docs.trychroma.com/docs/querying-collections/full-text-search
        
"""

import chromadb
from chromadb import QueryResult


####################
# DATABASE METHODS #
####################

def database_add(collection: chromadb.Collection, *, doc_list: list[str], metadata_list: list[dict[str, str]], id_list: list[str]) -> None:
    """Adds one or more document(s) to the database along with the assoicated metadata(s) and id(s)

    Args:
        collection: the collection to operate on
        docs_list: The documents to be embedded and stored
        metadata_list: The metadatas to be associated with each document
        id_list: The unique specifiers to be associated with each document

    Returns:
        None
    
    Example Arg Formatting:
        doc_list = [
            "123 Test Street is occupied by a non-profit organization specializing in AI",
            "86 Street NE is a multifamily apartment building"
        ]
        metadata_list = [
            {"document_name": "27183_om.pdf", "address": "123 Test Street", "page": "7"},
            {"document_name": "6432_mf.pdf", "address": "86 Street NE", "page": "2"}
        ]
        id_list = ["id1", "id2"]
    """
    # add text documents to the collection
    collection.add(
        documents = doc_list, 
        metadatas = metadata_list,
        ids = id_list
    )

def database_query(collection: chromadb.Collection, *, texts: list[str], results: int = 10, where_dict: dict[str, str] = None, where_docs_dict: dict[str, str] = None) -> QueryResult:
    """Queries the database for the results amount of documents closest to the embedded query text(s)

    Args:
        collection: the collection to operate on
        texts: The queries to be embedded and searched with (can be just one str)
        results: number of results (documents) to return (default = 10)
        where_dict: optional dict to specify the presence of certain metadata assoicated with the document
        where_docs_dict: optional dict to specify the presence of certain text in the document

    Returns:
        QueryResult: a dict like object with relevant keys such as:
            ids, embeddings, documents, uris, data, metadatas, distances, included
            values in the dict are lists of size = results
    
    Example Arg Formatting:
        texts = ["multifamily", "query2"]
        results = 5
        where_dict = {"metadata_field": "value"}
        where_docs_dict = {"$contains": "string"}
    """
    return collection.query(
        query_texts = texts,
        n_results = results,
        where = where_dict,
        where_document = where_docs_dict
    )

def database_update(collection: chromadb.Collection, *, id_list: list[str], metadata_list: list[str] = None, document_list: list[str] = None) -> None:
    """Updates the documents and metadatas for each of the given ids

    Args:
        collection: the collection to operate on
        id_list: The list of ids to have their assoicated information updated
        metadata_list: The new metadatas to be associated with the ids
        document_list: The new documents to be updated with the ids
    
    Returns:
        None
    
    Example Arg Formatting:
        id_list = ["id1", "id2"]
        metadata_list = [
            {"document_name": "27183_om.pdf", "address": "987 Fake Avenue", "page": "3"},
            {"document_name": "6432_mf.pdf", "address": "33 Court SW", "page": "18"}
        ]
        document_list = [
            "987 Fake Avenue is occupied by a for-profit organization specializing in bread baking",
            "33 Court SW is a commercial shopping mall"
        ]
    """
    collection.update(
        ids = id_list,
        metadatas = metadata_list,
        documents = document_list
    )

def database_delete(collection: chromadb.Collection, *, id_list: list[str], where_list: dict[str, str] = None, where_docs_list: dict[str, str] = None) -> None:
    """Queries the database for the results amount of documents closest to the embedded query text(s). This process cannot be undone.

    Args:
        collection: the collection to operate on
        id_list: list of ids to delete
        where_dict: optional dict to specify the presence of certain metadata assoicated with the id
        where_docs_dict: optional dict to specify the presence of certain text in the document assoicated with the id

    Returns:
        None
    
    Example Arg Formatting:
        id_list = ["id1", "id2"]
        where_dict = {"metadata_field": "value"}
        where_docs_dict = {"$contains": "string"}
    """
    collection.delete(
        id_list,
        where = where_list,
        where_document = where_docs_list
    )

def database_delete_collection(chroma_client: chromadb.Client, collection_name: str) -> None:
    """Deletes the collection from the database. This process cannot be undone.

    Args:
        chroma_client: the client connected to the database
        collection_name: name of the collection to be deleted

    Returns:
        None
    
    Example Arg Formatting:
        collection_name = "test_collection"
    """
    chroma_client.delete_collection(name = collection_name)

def main():
    from . import settings
    
    # setup the chromadb client (persistent allows data to be stored on disk)
    chroma_client = chromadb.PersistentClient(path=settings.PATH_TO_DATA)
    # create the collection
    coll_name = "test_collection"
    collection = chroma_client.get_or_create_collection(name=coll_name, embedding_function=settings.EMBEDDING_FUNCTION)

    # PERFORM OPERATIONS #
    database_add(
        collection,
        doc_list = [
            "123 Test Street is occupied by a non-profit organization specializing in AI",
            "86 Street NE is a multifamily apartment building"
        ],
        metadata_list = [
            {"document_name": "27183_om.pdf", "address": "123 Test Street", "page": "7"},
            {"document_name": "6432_mf.pdf", "address": "86 Street NE", "page": "2"}
        ],
        id_list = ["id1", "id2"]
    )

    query_results = database_query(
        collection,
        texts = ["What type of apartment building?"],
        results = 2
    )
    print(query_results, end="\n\n")

    database_update(
        collection,
        id_list = ["id1", "id2"],
        metadata_list = [
            {"document_name": "27183_om.pdf", "address": "987 Fake Avenue", "page": "3"},
            {"document_name": "6432_mf.pdf", "address": "33 Court SW", "page": "18"}
        ],
        document_list = [
            "987 Fake Avenue is occupied by a for-profit organization specializing in bread baking",
            "33 Court SW is a commercial shopping mall"
        ]
    )

    query_results = database_query(
        collection,
        texts = ["What type of organization occupies 987 Fake Avenue?"],
        results = 2
    )
    print(query_results, end="\n\n")

    database_delete(
        collection,
        id_list = ["id1"],
        where_list = {"address": "987 Fake Avenue"},
        where_docs_list = {"$contains": "organization"}
    )

    query_results = database_query(
        collection,
        texts = ["organization"],
        results = 2
    )
    print(query_results, end="\n\n")

    database_delete_collection(chroma_client, coll_name)

if __name__ == "__main__":
    main()
