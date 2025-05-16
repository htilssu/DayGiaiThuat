from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

source = "https://arxiv.org/pdf/2505.09525"  # PDF path or URL
pipeline_options = PdfPipelineOptions()
pipeline_options.do_code_enrichment = True
pipeline_options.do_formula_enrichment = True
pipeline_options.do_ocr = True
converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "### Docling Technical Report[...]"