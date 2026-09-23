import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load variables from .env
load_dotenv()


class GeminiDocumentGenerator:
    """
    LegalEase AI Core

    Generates structured legal document drafts using
    Google's Gemini 3.6 Flash model.
    """

    def __init__(self):
        # ---------------------------------------------------------
        # Load API key
        # ---------------------------------------------------------
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from the .env file."
            )

        # ---------------------------------------------------------
        # Gemini model
        # ---------------------------------------------------------
        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        )

        # ---------------------------------------------------------
        # Create Gemini client
        # ---------------------------------------------------------
        self.client = genai.Client(
            api_key=self.api_key
        )

    # =============================================================
    # CREATE LEGAL DOCUMENT PROMPT
    # =============================================================

    def _build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str
    ) -> str:
        """
        Creates the structured prompt used by Gemini.

        The four inputs correspond to the LegalEase project
        requirements:
        - document_type
        - parties
        - terms
        - dates
        """

        prompt = f"""
You are the AI document-generation engine for a system called LegalEase.

Your task is to create a professional legal document draft based ONLY
on the information supplied by the user.

============================================================
DOCUMENT INFORMATION
============================================================

DOCUMENT TYPE:
{document_type}

PARTIES INVOLVED:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE / JURISDICTION:
{dates}

============================================================
DOCUMENT GENERATION REQUIREMENTS
============================================================

1. Start directly with the title of the legal document.

2. Generate a structured and professional legal document.

3. Use clear Markdown formatting.

4. Use numbered sections wherever appropriate.

5. Include the information supplied by the user accurately.

6. Do not invent facts that were not supplied by the user.

7. Never invent:
   - names
   - addresses
   - dates
   - salaries
   - monetary amounts
   - registration numbers
   - identification numbers
   - legal case numbers
   - legal citations
   - company details

8. If information required for a section is missing, use:

[TO BE CONFIRMED]

9. Select sections appropriate to the requested document type.

For example, where relevant, consider:

- Parties
- Purpose
- Scope
- Definitions
- Responsibilities
- Duties and Obligations
- Payment / Compensation
- Confidentiality
- Intellectual Property
- Term
- Termination
- Dispute Resolution
- Governing Law and Jurisdiction
- Notices
- General Provisions
- Signatures

10. Do not add irrelevant clauses merely to make the document longer.

11. Preserve the user's specific terms and conditions.

12. Make the document easy to edit and review.

13. Include signature sections for the relevant parties.

14. Do not claim that the generated document is guaranteed to be
legally valid or enforceable.

15. Do not provide an explanation before the document.

16. Do not provide legal advice outside the document.

17. Keep the document reasonably concise while still being complete.

18. Prefer approximately 700–1200 words unless the requested document
genuinely requires more detail.

============================================================
LEGAL SAFETY NOTICE
============================================================

At the very end of the document, include exactly:

Legal Review Notice: This document is an AI-generated draft intended for informational and drafting assistance. It should be reviewed by a qualified legal professional before signing or relying upon it.
"""

        return prompt

    # =============================================================
    # CHECK WHETHER ERROR IS TEMPORARY
    # =============================================================

    def _is_temporary_error(self, error: Exception) -> bool:
        """
        Detect temporary Gemini availability/rate-limit errors.
        """

        error_text = str(error).lower()

        temporary_error_messages = [
            "503",
            "unavailable",
            "high demand",
            "service unavailable",
            "temporarily",
            "overloaded",
            "resource exhausted",
            "429",
            "too many requests",
        ]

        return any(
            message in error_text
            for message in temporary_error_messages
        )

    # =============================================================
    # GENERATE DOCUMENT
    # =============================================================

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str
    ) -> str:
        """
        Generate a legal document using Gemini 3.6 Flash.
        """

        # ---------------------------------------------------------
        # Build structured prompt
        # ---------------------------------------------------------

        prompt = self._build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            dates=dates,
        )

        # ---------------------------------------------------------
        # Retry configuration
        # ---------------------------------------------------------

        max_attempts = 3

        last_error = None

        # ---------------------------------------------------------
        # Try Gemini
        # ---------------------------------------------------------

        for attempt in range(1, max_attempts + 1):

            try:

                print(
                    f"[LegalEase] Generating document "
                    f"using {self.model_name} "
                    f"(attempt {attempt}/{max_attempts})"
                )

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=5000,
                    ),
                )

                # -------------------------------------------------
                # Validate response
                # -------------------------------------------------

                if response is None:
                    raise RuntimeError(
                        "Gemini returned no response."
                    )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty document."
                    )

                generated_document = response.text.strip()

                if not generated_document:
                    raise RuntimeError(
                        "Gemini returned an empty document."
                    )

                print(
                    f"[LegalEase] Document generated successfully "
                    f"using {self.model_name}"
                )

                return generated_document

            except Exception as error:

                last_error = error

                print(
                    f"[LegalEase] Gemini error "
                    f"(attempt {attempt}/{max_attempts}): "
                    f"{error}"
                )

                # -------------------------------------------------
                # Retry temporary service errors
                # -------------------------------------------------

                if self._is_temporary_error(error):

                    if attempt < max_attempts:

                        wait_seconds = attempt * 5

                        print(
                            f"[LegalEase] Gemini service temporarily "
                            f"unavailable."
                        )

                        print(
                            f"[LegalEase] Retrying in "
                            f"{wait_seconds} seconds..."
                        )

                        time.sleep(wait_seconds)

                        continue

                # -------------------------------------------------
                # Permanent error
                # -------------------------------------------------

                break

        # ---------------------------------------------------------
        # All attempts failed
        # ---------------------------------------------------------

        raise RuntimeError(
            f"Gemini document generation failed using "
            f"{self.model_name}: {last_error}"
        )