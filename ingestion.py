import json
import sys
import traceback
from typing import List

from langchain_core.documents import Document
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

from llm import invoke_llm


def partition_document(file_path: str):
    """Extract elements from PDF using unstructured"""
    try:
        print(f"📄 Partitioning document: {file_path}")

        elements = partition_pdf(
            filename=file_path,
            strategy="hi_res",
            infer_table_structure=True,
            extract_image_block_types=["Image"],
            extract_image_block_to_payload=True
        )

        print(f"✅ Extracted {len(elements)} elements")
        return elements
    except FileNotFoundError:
        print(f"[ERROR] PDF file not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Document partitioning failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def create_chunks_by_title(elements):
    """Create intelligent chunks using title-based strategy"""
    try:
        print("🔨 Creating smart chunks...")

        chunks = chunk_by_title(
            elements,
            max_characters=3000,
            new_after_n_chars=2400,
            combine_text_under_n_chars=500
        )

        print(f"✅ Created {len(chunks)} chunks")
        return chunks
    except Exception as e:
        print(f"[ERROR] Chunking failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def separate_content_types(chunk):
    """Analyze what types of content are in a chunk"""
    try:
        content_data = {
            'text': chunk.text,
            'tables': [],
            'images': [],
            'types': ['text']
        }

        if hasattr(chunk, 'metadata') and hasattr(chunk.metadata, 'orig_elements'):
            for element in chunk.metadata.orig_elements:
                element_type = type(element).__name__

                if element_type == 'Table':
                    content_data['types'].append('table')
                    table_html = getattr(element.metadata, 'text_as_html', element.text)
                    content_data['tables'].append(table_html)

                elif element_type == 'Image':
                    if hasattr(element, 'metadata') and hasattr(element.metadata, 'image_base64'):
                        content_data['types'].append('image')
                        content_data['images'].append(element.metadata.image_base64)

        content_data['types'] = list(set(content_data['types']))
        return content_data
    except Exception as e:
        print(f"[ERROR] Content type separation failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def create_ai_enhanced_summary(text: str, tables: List[str], images: List[str]) -> str:
    try:
        prompt_text = f"""You are creating a searchable description for document retrieval.

            CONTENT TO ANALYZE:
            TEXT:
            {text}
        """

        if tables:
            prompt_text += "\nTABLES:\n"
            for i, table in enumerate(tables):
                prompt_text += f"\nTable {i+1}:\n{table}\n"

        if images:
            prompt_text += "\nIMAGES PRESENT: Describe visual data such as charts, patterns, trends.\n"

        prompt_text += """

            YOUR TASK:
            Generate a comprehensive, searchable description that includes:

            1. Key facts and numbers
            2. Important entities and topics
            3. Questions this content could answer
            4. Alternative search terms

            Make it detailed and optimized for semantic search.

            SEARCHABLE DESCRIPTION:
        """

        return invoke_llm(prompt_text)

    except Exception as e:
        print(f"     ❌ AI summary failed: {e}")

        summary = f"{text[:300]}..."
        if tables:
            summary += f" [Contains {len(tables)} table(s)]"
        if images:
            summary += f" [Contains {len(images)} image(s)]"

        return summary


def summarize_chunks(chunks, file_id: str = None):
    """Process all chunks with AI Summaries"""
    try:
        print("🧠 Processing chunks with AI Summaries...")

        langchain_documents = []
        total_chunks = len(chunks)

        for i, chunk in enumerate(chunks):
            current_chunk = i + 1
            print(f"   Processing chunk {current_chunk}/{total_chunks}")

            content_data = separate_content_types(chunk)

            print(f"     Types found: {content_data['types']}")
            print(f"     Tables: {len(content_data['tables'])}, Images: {len(content_data['images'])}")

            if content_data['tables'] or content_data['images']:
                print(f"     → Creating AI summary for mixed content...")
                try:
                    enhanced_content = create_ai_enhanced_summary(
                        content_data['text'],
                        content_data['tables'],
                        content_data['images']
                    )
                    print(f"     → AI summary created successfully")
                    print(f"     → Enhanced content preview: {enhanced_content[:200]}...")
                except Exception as e:
                    print(f"     ❌ AI summary failed: {e}")
                    enhanced_content = content_data['text']
            else:
                print(f"     → Using raw text (no tables/images)")
                enhanced_content = content_data['text']

            doc = Document(
                page_content=enhanced_content,
                metadata={
                    "original_content": json.dumps({
                        "raw_text": content_data['text'],
                        "tables_html": content_data['tables'],
                        "images_base64": content_data['images']
                    }),
                    "file_id": file_id if file_id else None
                }
            )

            langchain_documents.append(doc)

        print(f"✅ Processed {len(langchain_documents)} chunks")
        return langchain_documents
    except SystemExit:
        raise
    except Exception as e:
        print(f"[ERROR] Chunk summarization failed: {e}")
        traceback.print_exc()
        sys.exit(1)


def export_chunks_to_json(chunks, filename="chunks_export.json"):
    """Export processed chunks to clean JSON format"""
    try:
        export_data = []

        for i, doc in enumerate(chunks):
            chunk_data = {
                "chunk_id": i + 1,
                "enhanced_content": doc.page_content,
                "metadata": {
                    "original_content": json.loads(doc.metadata.get("original_content", "{}"))
                }
            }
            export_data.append(chunk_data)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported {len(export_data)} chunks to {filename}")
        return export_data
    except Exception as e:
        print(f"[ERROR] JSON export failed: {e}")
        traceback.print_exc()
        sys.exit(1)
