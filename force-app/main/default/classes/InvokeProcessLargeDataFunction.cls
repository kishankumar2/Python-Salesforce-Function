/**
 * @description       : 
 * @author            : Kishan Kumar
 * @group             : 
 * @last modified on  : 03-26-2023
 * @last modified by  : Kishan Kumar
**/
public inherited sharing class InvokeProcessLargeDataFunction {
  
  public static void invoke() {
      System.debug('Invoking myfunction');
      //Finding the PDF Stored in Salesforce Where Content will be added by Salesforce Functions
      //TO-Do :- Store the PDF Info etc in Custom Metadata so its configurable
      ContentVersion cv = [SELECT Id, ContentDocumentId, VersionData FROM ContentVersion 
                           where ContentDocumentId = '0692w00000PoiA3AAJ'];
      
        Blob data=cv.VersionData;
      //Encoding the Base64 Content to be passed to Functions  
      String st=EncodingUtil.Base64Encode(data);
      //Preparing Input Wrapper to be Passed to Functions Again It should be Dynamic Values
      input inp = new input(st,'JOHN Doe Returns','03-25-2023',1);
      // Finding the Function running in the Compute Space
      functions.Function myFunction = functions.Function.get('first.pythonfun');
      //Invoking Functions 
      //Recomended Approach will be to call Function Asynchronousaly as PDF generation can take Time
      functions.FunctionInvocation invocation = myFunction.invoke(Json.serialize(inp));
      // Got the Response from Function Here  
      String jsonResponse = invocation.getResponse();

      System.debug('Response from myfunction');
      //Removing Additional Chanracted added in the Return String 
      //TO:Do- Check why extra Characted Returned from Functions
      String correctString = jsonResponse.substring(3, jsonResponse.length()-2);  
      System.debug(correctString); 
      //Creating an File Recored to be Stored in CRM  
      ContentVersion conver = new ContentVersion();
        conver.Title = 'JOHN Doe Returns';
        conver.PathOnClient = 'JOHN Doe Returns' + '.pdf';
      conver.VersionData = EncodingUtil.base64Decode(correctString);//blob.valueOf(response.content);
      insert conver;
      
       Id contentDocumentId = [SELECT ContentDocumentId FROM ContentVersion WHERE Id = :conver.Id].ContentDocumentId;
        
        // Link the content document to sObject record in this case it is account 
        ContentDocumentLink condocLink = new ContentDocumentLink();
        condocLink.ContentDocumentId = contentDocumentId;
      //Link the File to CRM Record  
      condocLink.LinkedEntityId = '0012w00001CqL6H';
        condocLink.ShareType = 'V';
        insert condocLink;
      
    
  }
    //Input Wrapper To Be Passes to Functions
    Public class input{
        Public String pdfData;
        Public String sign;
        Public String signDate;
        Public integer pageNumber;
        
        
        public input(String pdfData,String sign,String signDate,integer pageNumber){
            this.pdfData=pdfData;
            this.sign=sign;
            this.signDate=signDate;
            this.pageNumber=pageNumber;
        }
    }
    
}