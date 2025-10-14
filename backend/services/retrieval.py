from .vector_db import retrieve_relevant_context

def intelligent_retrieval(query: str):
    context = retrieve_relevant_context(query)
    if context:
        return f"Relevant past context found: {context}\n\nUser query: {query}"
    return query
