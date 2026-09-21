import streamlit as st

from config import ADMIN_PASSWORD, DATA_DIR, PDF_PATH
from ingest import index_documents, load_and_split_pdf
from retriever import build_hybrid_retriever, get_vectorstore

st.set_page_config(page_title="HRBotPolicy Admin", page_icon="🛠️", layout="centered")


# ---------- auth ----------
def check_password():
    if not ADMIN_PASSWORD:
        return True
    if st.session_state.get("admin_ok"):
        return True

    password = st.text_input("Admin password", type="password")
    if password:
        if password == ADMIN_PASSWORD:
            st.session_state.admin_ok = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


# ---------- file handling ----------
def save_uploaded_pdf(uploaded_file):
    """Delete any old PDF in the data folder and save the new one as company_policy.pdf."""
    data = uploaded_file.getvalue()
    if not data.startswith(b"%PDF"):
        raise ValueError("The selected file is not a valid PDF.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for old_file in DATA_DIR.iterdir():
        if old_file.is_file() and old_file.suffix.lower() == ".pdf":
            old_file.unlink()

    PDF_PATH.write_bytes(data)


def reindex_pdf():
    """Re-create the ChromaDB index from the current PDF. Returns the chunk count."""
    chunks = load_and_split_pdf()
    if not chunks:
        raise ValueError(
            "No text could be extracted from this PDF (it may be a scanned image)."
        )

    vectorstore = get_vectorstore()
    index_documents(chunks, vectorstore, replace=True)

    # refresh the BM25 + vector retriever cache in this process
    build_hybrid_retriever.cache_clear()
    return len(chunks)


def current_pdf_info():
    if not PDF_PATH.exists():
        return None
    stat = PDF_PATH.stat()
    return {"name": PDF_PATH.name, "size_kb": stat.st_size / 1024}


# ---------- UI ----------
def render_current_pdf():
    st.subheader("Current policy document")
    info = current_pdf_info()
    if info:
        st.success(f"📄 {info['name']}  ({info['size_kb']:.1f} KB)")
        with open(PDF_PATH, "rb") as f:
            st.download_button("Download current PDF", f, file_name=info["name"])
    else:
        st.warning("No PDF in the data folder yet.")


def render_upload():
    st.subheader("Upload new policy PDF")
    st.caption(
        "The old PDF will be deleted, the new one saved in the data folder, "
        "and the ChromaDB index rebuilt."
    )

    uploaded = st.file_uploader("Choose a PDF file", type=["pdf"])

    if st.button("Upload & Index", type="primary", disabled=uploaded is None):
        try:
            with st.spinner("Saving PDF..."):
                save_uploaded_pdf(uploaded)
        except Exception as e:
            st.error(f"Could not save the PDF: {e}")
            return

        try:
            with st.spinner("Indexing into ChromaDB (this can take a minute)..."):
                total = reindex_pdf()
        except Exception as e:
            st.error(
                "PDF saved, but indexing failed. Is the LM Studio server running "
                f"with the embedding model loaded?\n\n{e}"
            )
            return

        st.success(f"Done! Indexed {total} chunks from '{uploaded.name}'.")


def render_reindex():
    st.subheader("Re-index")
    st.caption("Use this if indexing failed earlier or you changed the embedding model.")

    if st.button("Re-index current PDF", disabled=not PDF_PATH.exists()):
        try:
            with st.spinner("Indexing into ChromaDB..."):
                total = reindex_pdf()
            st.success(f"Done! Indexed {total} chunks.")
        except Exception as e:
            st.error(f"Indexing failed: {e}")


def main():
    st.title("🛠️ HRBotPolicy Admin")

    if not check_password():
        st.stop()

    render_current_pdf()
    st.divider()
    render_upload()
    st.divider()
    render_reindex()


main()