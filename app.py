import streamlit as st
import pandas as pd
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieAPI
from config import GENIE_SPACES, GENIE_SPACE_MAP

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Genie Agent",
    page_icon="🧞",
    layout="wide"
)

st.title("🧞 Databricks Genie Agent")

st.markdown(
    """
Ask questions about your Databricks Genie Space using natural language.
"""
)

# =========================================================
# INITIALIZE DATABRICKS CLIENT
# =========================================================

# Uses Databricks native authentication automatically
# when running inside Databricks Apps

w = WorkspaceClient()

# =========================================================
# SIDEBAR - SPACE SELECTION
# =========================================================

space_names = [space.name for space in GENIE_SPACES]

selected_space_name = st.sidebar.selectbox(
    "Select Genie Space",
    space_names
)

selected_space = GENIE_SPACE_MAP[selected_space_name]

st.sidebar.markdown("### Description")

st.sidebar.write(selected_space.description)

# =========================================================
# CHAT HISTORY
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# =========================================================
# USER INPUT
# =========================================================

user_prompt = st.chat_input(
    "Ask your Genie Agent..."
)

# =========================================================
# PROCESS QUESTION
# =========================================================

if user_prompt:

    # ---------------------------------------------
    # Add user message
    # ---------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(user_prompt)

    # ---------------------------------------------
    # Assistant response
    # ---------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                # =====================================
                # CREATE GENIE CONVERSATION
                # =====================================

                conversation = w.genie.start_conversation_and_wait(
                    space_id=selected_space.space_id,
                    content=user_prompt
                )

                # =====================================
                # EXTRACT RESPONSE
                # =====================================

                assistant_response = ""

                if hasattr(conversation, "messages"):

                    for msg in conversation.messages:

                        if msg.role == "assistant":

                            assistant_response = msg.content

                if not assistant_response:

                    assistant_response = (
                        "No response returned from Genie."
                    )

                # =====================================
                # DISPLAY RESPONSE
                # =====================================

                st.markdown(assistant_response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_response
                    }
                )

                # =====================================
                # OPTIONAL SQL DISPLAY
                # =====================================

                if hasattr(conversation, "sql_query"):

                    with st.expander(
                        "Generated SQL"
                    ):

                        st.code(
                            conversation.sql_query,
                            language="sql"
                        )

                # =====================================
                # OPTIONAL TABLE RESULTS
                # =====================================

                if hasattr(conversation, "data"):

                    data = conversation.data

                    if data:

                        df = pd.DataFrame(data)

                        st.subheader("Query Results")

                        st.dataframe(
                            df,
                            use_container_width=True
                        )

                        # Download CSV
                        csv = df.to_csv(index=False)

                        st.download_button(
                            label="Download CSV",
                            data=csv,
                            file_name="genie_results.csv",
                            mime="text/csv"
                        )

                        # Visualization
                        numeric_cols = df.select_dtypes(
                            include="number"
                        ).columns

                        if len(numeric_cols) > 0:

                            st.subheader("Visualization")

                            st.bar_chart(
                                df[numeric_cols[0]]
                            )

            except Exception as e:

                st.error(f"Error: {str(e)}")

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": str(e)
                    }
                )


    