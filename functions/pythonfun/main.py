'''
  @description       : 
  @author            : Kishan Kumar
  @group             : 
  @last modified on  : 03-26-2023
  @last modified by  : Kishan Kumar
'''

from typing import Any

from salesforce_functions import Context, InvocationEvent, get_logger
import pdfrw
from base64 import b64decode,b64encode



# The type of the data payload sent with the invocation event.
# Change this to a more specific type matching the expected payload for
# improved IDE auto-completion and linting coverage. For example:
# `EventPayloadType = dict[str, Any]`
EventPayloadType = Any

logger = get_logger()
#Input file in which Salesforce Sent PDF content will be Stored 
Input_file_name = 'Test.pdf'
#Updated Signed PDF will be Stored in this file 
INVOICE_OUTPUT_PATH = 'SignedPdf.pdf'

#Various Annotation in the PDF
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'


async def function(event: InvocationEvent[EventPayloadType], context: Context):
    
    #Preparing a Dictionary (Map) of Acro Field Name with Actual value sent from Salesforce that needs to be Stored in that Field
    data_dict = {
   'Sign1': event.data['sign'],
   'SignDate': event.data['signDate']
        }
    
    #Reading The Encoded PDF Data Sent From Salesforce
    pdfData = event.data['pdfData']
    #Converting the Encoded String to Base64 Decode
    file_64_decode=b64decode(pdfData)
    f = open(Input_file_name, 'wb')
    #Writing the Base64 Content into Input File
    f.write(file_64_decode)
    f.close()
    
    logger.info('reading File')
    #Reading the input file we just created Using pdfrw
    template_pdf = pdfrw.PdfReader(Input_file_name)
    #This Line Says once Acro Fields are Updated Display it even if user is not Focusing on the Acro Field
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true'))) 
    # Finding the Acro Filed on tge PDF which needs to be updated 
    annotations = template_pdf.pages[event.data['pageNumber']][ANNOT_KEY]
    
    #Updating the content of Acro Fiels
    for annotation in annotations:
        if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
            if annotation[ANNOT_FIELD_KEY]:
                key = annotation[ANNOT_FIELD_KEY][1:-1]
                if key in data_dict.keys():
                    annotation.update(
                        pdfrw.PdfDict(V='{}'.format(data_dict[key]))
                    )
    # Writing the Updated File in the Output FIle
    pdfrw.PdfWriter().write(INVOICE_OUTPUT_PATH, template_pdf)
    #Reading the content of Updated File in base64 Encode String to Be Sent Back to Salesforce 
    with open(INVOICE_OUTPUT_PATH, "rb") as pdfFile:
        encodedString = b64encode(pdfFile.read())
  
    
    #Returning the Signed PDF Content in Encoded String to Apex
    return str(encodedString)
