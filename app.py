import streamlit as st

from database import (
    delete_history,
    get_all_history,
    get_history_item,
    init_db,
    save_history,
)
from graph import ask_hr_bot

st.set_page_config(page_title="HRBotPolicy", page_icon="🏢", layout="wide")

PROJECT_HEADING = "🏢 HR Policy Assistant"

init_db()


# ---------- state ----------
def init_state():
    st.session_state.setdefault("question_input", "")
    st.session_state.setdefault("answer", "")
    st.session_state.setdefault("active_id", None)


# ---------- callbacks ----------
def select_history(entry_id):
    item = get_history_item(entry_id)
    if item:
        st.session_state.question_input = item["question"]
        st.session_state.answer = item["answer"]
        st.session_state.active_id = entry_id


def new_question():
    st.session_state.question_input = ""
    st.session_state.answer = ""
    st.session_state.active_id = None


def remove_history(entry_id):
    delete_history(entry_id)
    if st.session_state.active_id == entry_id:
        new_question()


# ---------- helpers ----------
def truncate(text, limit=32):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def handle_submit():
    question = st.session_state.question_input.strip()
    if not question:
        st.warning("Please enter a question.")
        return

    with st.spinner("Searching the company policy..."):
        try:
            answer = ask_hr_bot(question)
        except Exception as e:
            st.error(f"Could not get an answer. Is the LM Studio server running?\n\n{e}")
            return

    entry_id = save_history(question, answer)
    st.session_state.answer = answer
    st.session_state.active_id = entry_id
    st.rerun()


# ---------- UI ----------
def render_sidebar():
    with st.sidebar:
        st.subheader("History")
        st.button("＋ New question", on_click=new_question, width="stretch")
        st.divider()

        history = get_all_history()
        if not history:
            st.caption("No questions yet.")

        for item in history:
            entry_id = item["id"]
            col_q, col_del = st.columns([5, 1], vertical_alignment="center")

            with col_q:
                st.button(
                    truncate(item["question"]),
                    key=f"history_{entry_id}",
                    on_click=select_history,
                    args=(entry_id,),
                    type="primary" if st.session_state.active_id == entry_id else "secondary",
                    width="stretch",
                    help=item["question"],
                )

            with col_del:
                st.button(
                    "✕",
                    key=f"delete_{entry_id}",
                    on_click=remove_history,
                    args=(entry_id,),
                    help="Delete",
                    width="stretch",
                )


def render_main():
    st.title(PROJECT_HEADING)

    with st.form("question_form", border=False):
        st.text_input(
            "Question",
            key="question_input",
            placeholder="Ask anything about the company policy...",
        )
        submitted = st.form_submit_button("Ask")

    if submitted:
        handle_submit()

    with st.container(border=True, height=340):
        if st.session_state.answer:
            st.markdown(st.session_state.answer)
        else:
            st.markdown(
                "<h1 style='text-align:center; color:gray; margin-top:100px;'>Answer</h1>",
                unsafe_allow_html=True,
            )


def main():
    init_state()
    render_sidebar()
    render_main()


main()