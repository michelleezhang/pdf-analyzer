#
# Python program to open and process a PDF file, extracting
# all numeric values from the document. The goal is to tally
# the first significant (non-zero) digit of each numeric
# value, and save the results to a text file. 
#

from configparser import ConfigParser
from pypdf import PdfReader

import json
import string
import os
import pathlib
import boto3
import urllib.parse

#
# execution starts here:
#
def lambda_handler(event, context):
    try:
      print("**STARTED**")
    
      #
      # setup AWS S3 access that we'll need eventually:
      #
      config_file = 'credentials.txt'
      s3_profile = 's3-read-write'
    
      os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
      boto3.setup_default_session(profile_name=s3_profile)
    
      configur = ConfigParser()
      configur.read(config_file)
      bucketname = configur.get('s3', 'bucket_name')
    
      s3 = boto3.resource('s3')
      bucket = s3.Bucket(bucketname)
    
      #
      # file to operate on, and file to output results:
      #
      
      # bucket_name_in_case_you_need_it = event['Records'][0]['s3']['bucket']['name']
      bucketkey = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
      # bucketkey = "SP-4029.pdf"
      
      # issue: bucketkey is "update.pdf" in our test configs, but it's "test/update.pdf" 
      # if we try to use the trigger and upload it to a "folder" object in the bucket
      # workaround: upload them raw, do not put them in folders lmao
      
      bucketkey_results = pathlib.Path(bucketkey).stem + ".txt"
    
      
      # from bucket, download desired file ("test/bucketkey") and save as bucketkey.pdf
      # path = os.path.join(os.getcwd(), bucketkey)
      path = "/tmp/" + bucketkey
      bucket.download_file(bucketkey, path)
      
    
      #
      # open pdf file:
      #
      print("**PROCESSING '", bucketkey, "'**")
    
      reader = PdfReader("/tmp/" + bucketkey)
      number_of_pages = len(reader.pages)
    
      #
      # for each page, extract text, split into words,
      # and see which words are numeric values:
      #
    
      lead_digit_counts = [0 for i in range(10)]
      
      for page_number in range(len(reader.pages)):
        page = reader.pages[page_number]
        
        text = page.extract_text()
        words = text.split()
      
        print("** Page", page_number, ", text length", len(text), ", num words", len(words))
      
        for word in words:
          # remove punctuation from word:
          word = word.translate(str.maketrans('', '', string.punctuation))
          #
          if word.isnumeric():
            word = str(int(word)) # remove leading zeros!
            lead_digit = int(word[0])
            if lead_digit != 0:
              lead_digit_counts[lead_digit] += 1
          # print(word)
    
      #
      # we've analyzed the PDF, so print the results to
      # the console but also to the results .txt file:
      #
    
      print("**RESULTS**")
      print(number_of_pages, "pages")
      
      outfile = open("/tmp/" + bucketkey_results, "w")
      outfile.write("**RESULTS**\n")
      outfile.write(str(number_of_pages) + " pages\n")
      
      for ld in range(len(lead_digit_counts)):
        ld_count = lead_digit_counts[ld]
        print(ld, ld_count)
        outfile.write(str(ld) + " " + str(ld_count) + "\n")
      outfile.close()
      
      # upload results file to S3
      bucket.upload_file("/tmp/" + bucketkey_results, 
                         bucketkey_results, 
                         ExtraArgs={
                           'ACL': 'public-read', 'ContentType': 'text/plain'
                         })
    
      print("**DONE**")
      
      return {
            'statusCode': 200,
            'body': json.dumps('processed')
        }
    
    
    except Exception as err:
      print("**ERROR**")
      print(str(err))
    
      outfile = open("/tmp/" + bucketkey_results, "w")
      outfile.write("**ERROR**\n")
      outfile.write(str(err))
      outfile.write("\n")
      outfile.close()
    
      # upload results file to S3
      bucket.upload_file("/tmp/" + bucketkey_results, 
                         bucketkey_results, 
                         ExtraArgs={
                           'ACL': 'public-read', 'ContentType': 'text/plain'
                         })
      
      print("**DONE**")
      
      return {
            'statusCode': 400,
            'body': json.dumps(str(err))
        }
