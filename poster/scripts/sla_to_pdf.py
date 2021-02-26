import scribus
scribus.openDoc('poster/template.sla')
pdf = scribus.PDFfile()
pdf.file = 'poster.pdf'
pdf.save()