from langchain_text_splitters import RecursiveCharacterTextSplitter


def dividir_en_chunks(texto: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,      
        chunk_overlap=150    
    )

    chunks = splitter.split_text(texto)
    return chunks
