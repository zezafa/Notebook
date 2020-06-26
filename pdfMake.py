#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""
Collects BW note images and compiles them into a pdf ready to be shared
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import mm
import datetime, glob
import re

########################################################################
class MCLine(Flowable):
    def __init__(self, width, height=0):
        Flowable.__init__(self)
        self.width = width
        self.height = height
 
    def __repr__(self):
        return "Line(w=%s)" % self.width
 
    def draw(self):
        self.canv.line(0, self.height, self.width, self.height)

#----------------------------------------------------------------------
class PageNumCanvas(canvas.Canvas):
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = [] 
    
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage() 
    
    def save(self):
        page_count = len(self.pages) 
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self) 
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
	DTUlogo = 'etc/logo_dtu.jpg'
	#A4: 210mm x 297mm
        self.drawImage(DTUlogo, 140*mm, 275*mm,55*mm,14*mm)
        page = "Side %s af %s" % (self._pageNumber, page_count)
        self.setFont("Helvetica", 9)
        self.drawRightString(190*mm, 15*mm, page)
 
#----------------------------------------------------------------------
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

#----------------------------------------------------------------------
def createMultiPage():
    doc = SimpleDocTemplate(docName,pagesize=A4,
                            rightMargin=15*mm,leftMargin=15*mm,
                            topMargin=20*mm,bottomMargin=25*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
 
    Story = []
    now = datetime.datetime.now()
    #now.strftime("%Y-%m-%d (Uge: %W)")
    #title = "Noterne om Kompelekse Tal"

    #General information
    ptext = '<font size=16>%s</font>' % title
    Story.append(Paragraph(ptext, styles["Center"]))
    Story.append(Spacer(1, 5*mm))
    for part in info_parts:
        ptext = '<font size=8>%s</font>' % part.strip()
        Story.append(Paragraph(ptext, styles["Normal"]))
    Story.append(Spacer(1, 5*mm))
    line = MCLine(176*mm)
    Story.append(line)
    Story.append(Spacer(1, 4*mm))

    count = 1
    pageBreak = 1
    totalCount = len(glob.glob(folderName+'/*.jpg'))
    for filename in sorted(glob.iglob(folderName+'/*.jpg'),key=numericalSort):
        if pageBreak > 3:
            Story.append(PageBreak())
            pageBreak = 1
        pageBreak = pageBreak + 1
        ptext = '<font size=8>Tavle %s ud af %s</font>' % (count, totalCount)
        Story.append(Paragraph(ptext, styles["Center"]))
        Story.append(Spacer(1, 1*mm))
        count = count + 1
        im = Image(filename,160*mm,62*mm)
        Story.append(im)
        Story.append(Spacer(1, 5*mm))

    Story.append(Spacer(1, 5*mm))
    Story.append(line)
    Story.append(Spacer(1, 5*mm))
    ptext = '<font size=10>Alle rettigheder til billederne tilhører Danmarks Tekniske Universitet. Vedrørende spørgsmål, kontakt Jurgis Vosylius og Jens Wilsby.</font>'
    Story.append(Paragraph(ptext, styles["Justify"]))
        

    doc.build(Story, canvasmaker=PageNumCanvas)
 
#----------------------------------------------------------------------

if __name__ == "__main__":
    now = datetime.datetime.now()
    info_parts = ["Kursus: 01005-TEST", "Forlæser: Ingen", "Dato: %s" % date]
    folderName = now.strftime("NOTE_%Y_%m_%d")
    docName = "%s.pdf" % now.strftime("NOTE_%Y_%m_%d")
    title = "%s" % now.strftime("Test %d-%m-%Y")
    date = now.strftime("%d/%m/%Y (Uge: %W)")
    createMultiPage()
