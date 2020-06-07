import os
from datetime import datetime
from urllib.request import Request, urlopen
import boto3

SITE = os.environ['site']  # URL of the site to check, stored in the site environment variable
EXPECTED = os.environ['expected']  # String expected to be on the page, stored in the expected environment variable

def send_email(sender, recipient, aws_region, subject):
 
   # Replace sender@example.com with your "From" address.
   # This address must be verified with Amazon SES.
   SENDER = sender
 
   # Replace recipient@example.com with a "To" address. If your account 
   # is still in the sandbox, this address must be verified.
   RECIPIENT = recipient
 
   # Specify a configuration set. If you do not want to use a configuration
   # set, comment the following variable, and the 
   # ConfigurationSetName=CONFIGURATION_SET argument below.
   # CONFIGURATION_SET = "ConfigSet"
 
   # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
   AWS_REGION = aws_region
 
   # The subject line for the email.
   SUBJECT = subject
 
   # The email body for recipients with non-HTML email clients.
   BODY_TEXT = "..."
             
   # The HTML body of the email.
   BODY_HTML = """<html>
   <head></head>
   <body>
     <h1>Checking if gospelmailbox.org is up or down</h1>
     <p>This email was sent with
       <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
       <a href='https://aws.amazon.com/sdk-for-python/'>
         AWS SDK for Python (Boto)</a>.</p>
   </body>
   </html>
             """            
 
   # The character encoding for the email.
   CHARSET = "UTF-8"
 
   # Create a new SES resource and specify a region.
   client = boto3.client('ses',region_name=AWS_REGION)
 
   # Try to send the email.
   try:
       #Provide the contents of the email.
       response = client.send_email(
           Destination={
               'ToAddresses': [
                   RECIPIENT,
               ],
           },
           Message={
               'Body': {
                   'Html': {
                       'Charset': CHARSET,
                       'Data': BODY_HTML,
                   },
                   'Text': {
                       'Charset': CHARSET,
                       'Data': BODY_TEXT,
                   },
               },
               'Subject': {
                   'Charset': CHARSET,
                   'Data': SUBJECT,
               },
           },
           Source=SENDER,
           # If you are not using a configuration set, comment or delete the
           # following line
           # ConfigurationSetName=CONFIGURATION_SET,
     )
   # Display an error if something goes wrong. 
   except ClientError as e:
       return(e.response['Error']['Message'])
   else:
       return("Email sent! Message ID:" + response['MessageId'] )
       

def validate(res):
    '''Return False to trigger the canary

    Currently this simply checks whether the EXPECTED string is present.
    However, you could modify this to perform any number of arbitrary
    checks on the contents of SITE.
    '''
    return EXPECTED in res


def lambda_handler(event, context):
    print('Checking {} at {}...'.format(SITE, event['time']))
    try:
        req = Request(SITE, headers={'User-Agent': 'AWS Lambda'})
        if not validate(str(urlopen(req).read())):
            raise Exception('Validation failed')
    except:
        print('Check failed!')
        send_email('preacher@gospelmailbox.org', 'donniebryson@gmail.com', 'us-east-1', 'gospelmailbox.org is down')
        raise
    else:
        print('Check passed!')
        send_email('preacher@gospelmailbox.org', 'donniebryson@gmail.com', 'us-east-1', 'gospelmailbox.org is up')
        return event['time']
    finally:
        print('Check complete at {}'.format(str(datetime.now())))
