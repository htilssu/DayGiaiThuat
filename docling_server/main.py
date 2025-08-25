import runpod
from docling.backend.docling_parse_v2_backend import DoclingParseV2DocumentBackend
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

artifacts_path = "/root/.cache/docling/models"
pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
pipeline_options.do_ocr = False
# pipeline_options.do_formula_enrichment = True
# pipeline_options.do_code_enrichment = True


def handler(event):
    input = event["input"]
    url = input.get("url")
    if not url:
        return "No URL provided"
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options, backend=DoclingParseV2DocumentBackend
            )
        }
    )
    return converter.convert(url).document.export_to_text()


# Start the Serverless function when the script is run
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
