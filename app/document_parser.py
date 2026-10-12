import os
from pathlib import Path
from typing import Dict, Any, Optional
import pypdf
import docx

class DocumentParser:
    """
    Parses and extracts text from various document formats:
    - PDF (.pdf)
    - Microsoft Word (.docx)
    - Plain text (.txt, .md, .rtf)
    """

    @staticmethod
    def extract_text(file_path: Path) -> Dict[str, Any]:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()
        extracted_text = ""
        metadata = {
            "file_name": file_path.name,
            "file_size_bytes": file_path.stat().st_size,
            "file_size_kb": round(file_path.stat().st_size / 1024, 2),
            "file_type": suffix,
            "page_count": 1,
            "word_count": 0,
            "char_count": 0
        }

        try:
            if suffix == ".pdf":
                reader = pypdf.PdfReader(str(file_path))
                metadata["page_count"] = len(reader.pages)
                pages_text = []
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        pages_text.append(f"--- [PAGE {idx + 1}] ---\n{text}")
                extracted_text = "\n\n".join(pages_text)

            elif suffix in (".docx", ".doc"):
                doc = docx.Document(str(file_path))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                # Also extract text from tables
                table_texts = []
                for table in doc.tables:
                    for row in table.rows:
                        row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                        if row_text:
                            table_texts.append(" | ".join(row_text))
                
                extracted_text = "\n\n".join(paragraphs)
                if table_texts:
                    extracted_text += "\n\n--- [TABLES] ---\n" + "\n".join(table_texts)
                metadata["page_count"] = max(1, len(paragraphs) // 15)

            elif suffix in (".txt", ".md", ".json", ".rtf", ".csv"):
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()
                metadata["page_count"] = max(1, len(extracted_text.splitlines()) // 40)

            else:
                # Try generic read
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text = f.read()

        except Exception as e:
            raise RuntimeError(f"Error parsing {file_path.name}: {str(e)}")

        # Clean text
        extracted_text = extracted_text.strip()
        words = extracted_text.split()
        metadata["word_count"] = len(words)
        metadata["char_count"] = len(extracted_text)

        return {
            "text": extracted_text,
            "metadata": metadata
        }

document_parser = DocumentParser()
