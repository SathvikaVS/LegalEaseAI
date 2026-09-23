import os
import sys
import inspect
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# PROJECT SETUP
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

CSS_FILE = ROOT_DIR / "frontend" / "static" / "style.css"


# ============================================================
# DOCUMENT FORMATTERS
# ============================================================

try:

    from utils.formatter import (
        sanitize_text,
        format_document_output,
        format_docx,
        format_pdf,
    )

except ImportError:

    sanitize_text = lambda text: text

    format_document_output = lambda text: text

    def format_docx(text, *args, **kwargs):
        return text.encode("utf-8")

    def format_pdf(text, *args, **kwargs):
        return text.encode("utf-8")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# LOAD CSS
# ============================================================

if CSS_FILE.exists():

    css = CSS_FILE.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )


# ============================================================
# SESSION STATE
# ============================================================

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False


# ============================================================
# BACKEND HEALTH
# ============================================================

def check_backend():

    try:

        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=5
        )

        if response.status_code == 200:
            return True, response.json()

        return False, {}

    except Exception:

        return False, {}


# ============================================================
# GENERATE DOCUMENT
# ============================================================

def generate_document(
    document_type,
    parties,
    terms,
    effective_date
):

    payload = {
        "document_type": document_type,
        "parties": parties,
        "terms": terms,
        "dates": effective_date,
    }

    response = requests.post(
        f"{BACKEND_URL}/generate",
        json=payload,
        timeout=180,
    )

    if response.status_code >= 400:

        try:

            error_data = response.json()

            detail = error_data.get(
                "detail",
                "Unknown backend error."
            )

        except Exception:

            detail = (
                response.text
                or "Unknown backend error."
            )

        raise RuntimeError(
            f"Backend returned HTTP "
            f"{response.status_code}: {detail}"
        )

    data = response.json()

    if data.get("status") != "success":

        raise RuntimeError(
            data.get(
                "detail",
                "Document generation failed."
            )
        )

    return data.get("document", "")


# ============================================================
# DOCX
# ============================================================

def create_docx(text):

    try:

        signature = inspect.signature(
            format_docx
        )

        if len(signature.parameters) == 1:

            return format_docx(text)

        return format_docx(
            text,
            title="LegalEase Document"
        )

    except Exception:

        return format_docx(text)


# ============================================================
# PDF
# ============================================================

def create_pdf(text):

    try:

        signature = inspect.signature(
            format_pdf
        )

        if len(signature.parameters) == 1:

            return format_pdf(text)

        return format_pdf(
            text,
            title="LegalEase Document"
        )

    except Exception:

        return format_pdf(text)


# ============================================================
# BACKEND STATUS
# ============================================================

backend_online, health_data = check_backend()

if backend_online:

    model_name = health_data.get(
        "model",
        GEMINI_MODEL
    )

else:

    model_name = GEMINI_MODEL


# ============================================================
# BRAND
# ============================================================

st.markdown(
    '<div class="brand">'
    '<div class="brand-icon">⚖</div>'
    '<div class="brand-name">LegalEase</div>'
    '<div class="brand-tagline">'
    'AI Legal Document Generator'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# AI STATUS
# ============================================================

if backend_online:

    st.markdown(
        '<div class="status-online">'
        '<span class="status-dot"></span>'
        f'<span>{model_name}</span>'
        '<span class="status-muted">Online</span>'
        '</div>',
        unsafe_allow_html=True
    )

else:

    st.markdown(
        '<div class="status-offline">'
        '<span class="status-dot"></span>'
        '<span>Backend Offline</span>'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# CREATE DOCUMENT
# ============================================================

st.markdown(
    '<div class="section-heading">'
    '<h2>Create Your Document</h2>'
    '<p>'
    'Enter the essential details and generate a concise '
    'professional first draft.'
    '</p>'
    '</div>',
    unsafe_allow_html=True
)


document_type = st.text_input(
    "Document Type / Title",
    placeholder="e.g. Employment Contract",
)


parties = st.text_area(
    "Parties Involved",
    placeholder=(
        "Party A: ABC Technologies Pvt. Ltd. (Employer)\n"
        "Party B: Priya Sharma (Employee)"
    ),
    height=100,
)


terms = st.text_area(
    "Key Terms & Specific Clauses",
    placeholder=(
        "Salary: ₹35,000/month\n"
        "Term: 1 year\n"
        "Notice period: 30 days\n"
        "Confidentiality required"
    ),
    height=135,
)


effective_date = st.text_input(
    "Effective Date & Jurisdiction",
    placeholder="e.g. 1 October 2026 | Tamil Nadu, India",
)


# ============================================================
# GENERATE BUTTON
# ============================================================

generate_clicked = st.button(
    "✨  Generate Legal Document",
    type="primary",
    use_container_width=True,
)


if generate_clicked:

    if not backend_online:

        st.error(
            "Backend is offline. "
            "Start the LegalEase API first."
        )

    elif not document_type.strip():

        st.error(
            "Please enter the document type."
        )

    elif not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter the key terms."
        )

    elif not effective_date.strip():

        st.error(
            "Please enter the effective date "
            "and jurisdiction."
        )

    else:

        with st.spinner(
            f"Creating your document with "
            f"{model_name}..."
        ):

            try:

                generated = generate_document(
                    document_type=document_type.strip(),
                    parties=parties.strip(),
                    terms=terms.strip(),
                    effective_date=effective_date.strip(),
                )

                if not generated:

                    raise RuntimeError(
                        "Gemini returned an empty document."
                    )

                # ---------------------------------------------
                # Clean generated document
                # ---------------------------------------------

                try:

                    generated = format_document_output(
                        generated
                    )

                except Exception:

                    pass

                try:

                    generated = sanitize_text(
                        generated
                    )

                except Exception:

                    pass

                # ---------------------------------------------
                # Store document
                # ---------------------------------------------

                st.session_state.generated_text = generated

                # IMPORTANT:
                # Do NOT create/change the document_editor
                # widget state here.
                #
                # Edit mode will initialize its own widget
                # from generated_text.

                st.session_state.edit_mode = False

                st.success(
                    "Legal document generated successfully."
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request took too long. "
                    "Please try again."
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Cannot connect to the LegalEase backend. "
                    "Make sure FastAPI is running."
                )

            except Exception as error:

                st.error(
                    f"Document generation failed: {error}"
                )


# ============================================================
# GENERATED DOCUMENT
# ============================================================

if st.session_state.generated_text:

    st.markdown(
        '<div class="document-section"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="document-heading">'
        '<div>'
        '<h2>Generated Document</h2>'
        '<p>Review and customize your AI-generated draft.</p>'
        '</div>'
        '<div class="document-badge">AI DRAFT</div>'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # EDIT MODE
    # ========================================================

    if st.session_state.edit_mode:

        # ----------------------------------------------------
        # IMPORTANT FIX
        #
        # Do not use:
        # value=st.session_state.document_editor
        #
        # and then modify document_editor after the widget
        # is created.
        #
        # Instead, use a temporary widget key.
        # ----------------------------------------------------

        edited_document = st.text_area(
            "Edit Document",
            value=st.session_state.generated_text,
            height=620,
            label_visibility="collapsed",
            key="document_editor_widget",
        )


        edit_col1, edit_col2 = st.columns(2)


        with edit_col1:

            save_clicked = st.button(
                "💾 Save Changes",
                type="primary",
                use_container_width=True,
            )


        with edit_col2:

            cancel_clicked = st.button(
                "Cancel",
                use_container_width=True,
            )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        if save_clicked:

            # Save the edited content as the actual document.
            st.session_state.generated_text = edited_document

            # Leave edit mode.
            st.session_state.edit_mode = False

            st.rerun()


        # ----------------------------------------------------
        # CANCEL
        # ----------------------------------------------------

        if cancel_clicked:

            # Do NOT modify the text-area widget state.
            # Simply leave edit mode.
            st.session_state.edit_mode = False

            st.rerun()


    # ========================================================
    # PREVIEW MODE
    # ========================================================

    else:

        st.markdown(
            '<div class="document-paper">',
            unsafe_allow_html=True
        )

        st.markdown(
            st.session_state.generated_text
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        # ====================================================
        # DOCUMENT ACTIONS
        # ====================================================

        action_col1, action_col2 = st.columns(2)


        with action_col1:

            edit_clicked = st.button(
                "✏️ Edit Document",
                use_container_width=True,
            )


        with action_col2:

            new_clicked = st.button(
                "＋ New Document",
                use_container_width=True,
            )


        # ----------------------------------------------------
        # EDIT DOCUMENT
        # ----------------------------------------------------

        if edit_clicked:

            st.session_state.edit_mode = True

            st.rerun()


        # ----------------------------------------------------
        # NEW DOCUMENT
        # ----------------------------------------------------

        if new_clicked:

            st.session_state.generated_text = ""

            st.session_state.edit_mode = False

            st.rerun()


        # ====================================================
        # EXPORT
        # ====================================================

        st.markdown(
            '<div class="export-heading">'
            'Export Document'
            '</div>',
            unsafe_allow_html=True
        )


        export_col1, export_col2, export_col3 = st.columns(3)


        # ----------------------------------------------------
        # TXT
        # ----------------------------------------------------

        with export_col1:

            st.download_button(
                label="📄 TXT",
                data=st.session_state.generated_text,
                file_name="LegalEase_Document.txt",
                mime="text/plain",
                use_container_width=True,
            )


        # ----------------------------------------------------
        # DOCX
        # ----------------------------------------------------

        with export_col2:

            try:

                docx_data = create_docx(
                    st.session_state.generated_text
                )

                st.download_button(
                    label="📝 DOCX",
                    data=docx_data,
                    file_name="LegalEase_Document.docx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),
                    use_container_width=True,
                )

            except Exception:

                st.button(
                    "📝 DOCX",
                    disabled=True,
                    use_container_width=True,
                )


        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        with export_col3:

            try:

                pdf_data = create_pdf(
                    st.session_state.generated_text
                )

                st.download_button(
                    label="📑 PDF",
                    data=pdf_data,
                    file_name="LegalEase_Document.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            except Exception:

                st.button(
                    "📑 PDF",
                    disabled=True,
                    use_container_width=True,
                )


        # ====================================================
        # LEGAL NOTICE
        # ====================================================

        st.markdown(
            '<div class="legal-notice">'
            '<strong>⚖️ AI-assisted drafting notice</strong><br>'
            'This document is an AI-generated draft for '
            'informational and drafting assistance. Review and '
            'customize it with a qualified legal professional '
            'before signing or relying on it.'
            '</div>',
            unsafe_allow_html=True
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'LegalEase &nbsp;•&nbsp; AI-assisted legal drafting'
    f'&nbsp;•&nbsp; {model_name}'
    '</div>',
    unsafe_allow_html=True
)