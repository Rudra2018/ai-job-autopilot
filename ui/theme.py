import streamlit as st


def apply_theme() -> None:
    """Inject global CSS variables for consistent theming."""
    st.markdown(
        """
        <style>
            :root {
                --primary-color: #667eea;
                --secondary-color: #764ba2;
                --background-color: #f8fafc;
                --secondary-background-color: #ffffff;
                --text-color: #1a202c;
                --font-family: 'Inter', sans-serif;
            }

            .stApp {
                background-color: var(--background-color);
                color: var(--text-color);
                font-family: var(--font-family);
            }

            a, .stMarkdown a {
                color: var(--primary-color);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
