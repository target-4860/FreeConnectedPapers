import logging
import re
from typing import Dict, List
import pdfplumber
import spacy


class ReferenceParser:
    def __init__(self):
        """Initialize the reference parser with necessary models and patterns."""
        # Load spaCy model for entity recognition
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("Downloading spaCy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        # Common patterns for reference sections
        self.reference_headers = [
            r"references?$",
            r"bibliography$",
            r"works cited$",
            r"citations?$",
            r"reference list$",
        ]

        # Pattern for common reference formats
        self.reference_patterns = [
            # Author (Year) format
            r"(?P<authors>(?:[A-Z][a-z]+(?:,?\s+(?:and\s+)?[A-Z][a-z]+)*)+)\s*"
            r"\((?P<year>\d{4})\)\s*"
            r"(?P<title>[^\.]+)\.",
            # [1] format
            r"\[(?P<ref_num>\d+)\]\s*" r"(?P<content>.+?)(?=\[\d+\]|\Z)",
            # Numbered format
            r"^\d+\.\s*(?P<content>.+)$",
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            str: Extracted text content
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
            raise

    def find_reference_section(self, text: str) -> str:
        """
        Locate and extract the reference section from the text.

        Args:
            text (str): Full text content

        Returns:
            str: Reference section text
        """
        # Split text into lines for processing
        lines = text.split("\n")
        reference_section = ""
        reference_started = False

        # Combined pattern for reference section headers
        header_pattern = "|".join(self.reference_headers)

        for i, line in enumerate(lines):
            # Check if line matches reference header pattern
            if re.search(header_pattern, line.lower().strip()):
                reference_started = True
                continue

            # Check for next section header (possible end of references)
            if reference_started and re.match(r"^[A-Z][A-Za-z\s]{0,20}$", line.strip()):
                break

            if reference_started:
                reference_section += line + "\n"

        return reference_section.strip()

    def parse_references(self, reference_text: str) -> List[Dict]:
        """
        Parse individual references from the reference section.

        Args:
            reference_text (str): Text containing references

        Returns:
            List[Dict]: List of parsed references with metadata
        """
        references = []
        current_reference = ""

        # Split into individual references
        lines = reference_text.split("\n")

        for line in lines:
            # Check if line starts a new reference
            new_ref_indicators = [
                re.match(r"^\[\d+\]", line),  # [1] format
                re.match(r"^\d+\.", line),  # Numbered format
                re.match(r"^[A-Z]", line),  # Author starting format
            ]

            if any(new_ref_indicators):
                if current_reference:
                    parsed_ref = self._parse_single_reference(current_reference)
                    if parsed_ref:
                        references.append(parsed_ref)
                current_reference = line
            else:
                current_reference += " " + line.strip()

        # Add the last reference
        if current_reference:
            parsed_ref = self._parse_single_reference(current_reference)
            if parsed_ref:
                references.append(parsed_ref)

        return references

    def _parse_single_reference(self, reference: str) -> Dict:
        """
        Parse a single reference string into structured data.

        Args:
            reference (str): Single reference string

        Returns:
            Dict: Structured reference data
        """
        reference = reference.strip()
        parsed_data = {
            "raw_text": reference,
            "authors": [],
            "year": None,
            "title": None,
            "venue": None,
        }

        # Process with spaCy for entity recognition
        doc = self.nlp(reference)

        # Extract potential years
        years = re.findall(r"\d{4}", reference)
        if years:
            parsed_data["year"] = years[0]

        # Extract authors (assuming they're at the start and capitalized)
        author_match = re.match(r"^([A-Z][a-z]+(?:,?\s+(?:and\s+)?[A-Z][a-z]+)*)", reference)
        if author_match:
            authors = author_match.group(1)
            parsed_data["authors"] = [a.strip() for a in re.split(r",|and", authors)]

        # Extract title (assuming it's between author/year and the next period)
        if parsed_data["year"]:
            title_match = re.search(rf"{parsed_data['year']}\)\s*([^\.]+)\.", reference)
            if title_match:
                parsed_data["title"] = title_match.group(1).strip()

        return parsed_data

    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Process a PDF file and extract structured references.

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            List[Dict]: List of parsed references
        """
        try:
            # Extract text from PDF
            full_text = self.extract_text_from_pdf(pdf_path)

            # Find reference section
            reference_section = self.find_reference_section(full_text)

            if not reference_section:
                raise ValueError("No reference section found in the PDF")

            # Parse references
            references = self.parse_references(reference_section)

            return references

        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            raise


def main():
    """Example usage of the ReferenceParser class."""
    logging.basicConfig(level=logging.INFO)

    # Initialize parser
    parser = ReferenceParser()

    # Example usage
    pdf_path = "./data/AudioLM.pdf"
    try:
        references = parser.process_pdf(pdf_path)

        # Print parsed references
        for i, ref in enumerate(references, 1):
            print(f"\nReference {i}:")
            print(f"Authors: {', '.join(ref['authors'])}")
            print(f"Year: {ref['year']}")
            print(f"Title: {ref['title']}")
            print(f"Raw text: {ref['raw_text']}")
            print("-" * 50)

    except Exception as e:
        logging.error(f"Failed to process PDF: {e}")


if __name__ == "__main__":
    main()
