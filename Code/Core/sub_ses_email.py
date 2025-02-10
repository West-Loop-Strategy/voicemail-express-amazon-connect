current_version = '2024.09.01'
'''
**********************************************************************************************************************
 *  Copyright 2024 Amazon.com, Inc. or its affiliates. All Rights Reserved                                            *
 *                                                                                                                    *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated      *
 *  documentation files (the "Software"), to deal in the Software without restriction, including without limitation   *
 *  the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and  *
 *  to permit persons to whom the Software is furnished to do so.                                                     *
 *                                                                                                                    *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO  *
 *  THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE    *
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF         *
 *  CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS *
 *  IN THE SOFTWARE.                                                                                                  *
 **********************************************************************************************************************
'''

# Import the necessary modules for this function
import json
import boto3
import logging
import os

# Establish logging configuration
logger = logging.getLogger()

def WLSConnectVoicemail3_to_ses_email(writer_payload):
    # Debug lines for troubleshooting
    logger.debug('Code Version: ' + current_version)
    logger.debug('WLSConnectVoicemail3 Package Version: ' + os.environ['package_version'])
    logger.debug(writer_payload)

    # Establish needed clients and resources
    try:
        connect_client = boto3.client('connect')
        ses_client = boto3.client('sesv2')
        logger.debug('********** Clients initialized **********')
    
    except Exception as e:
        logger.error('********** WLSConnectVoicemail Initialization Error: Could not establish needed clients **********')
        logger.error(e)

        return {'status':'complete','result':'ERROR','reason':'Failed to Initialize clients'}
    
    logger.debug('Beginning Voicemail to email')

    # Identify the proper address to send the email FROM
    if 'email_from' in writer_payload['json_attributes']:
        if writer_payload['json_attributes']['email_from']:
            WLSConnectVoicemail3_email_from_address = writer_payload['json_attributes']['email_from']
    else:
        WLSConnectVoicemail3_email_from_address = os.environ['default_email_from']

    logger.debug(WLSConnectVoicemail3_email_from_address)

    # Set destination address
    try:
        WLSConnectVoicemail3_email_target_address = writer_payload['entity_email']

    except:
        WLSConnectVoicemail3_email_target_address = os.environ['default_email_target']

    logger.debug(WLSConnectVoicemail3_email_target_address)

    if '@' in WLSConnectVoicemail3_email_target_address:
        logger.info('Valid email address format')

    else:
        WLSConnectVoicemail3_email_target_address = os.environ['default_email_target']

    logger.debug('Target Email: ' + WLSConnectVoicemail3_email_target_address)

    if 'email_template' in writer_payload['json_attributes']:
        if writer_payload['json_attributes']['email_template']:
            WLSConnectVoicemail3_email_template = writer_payload['json_attributes']['email_template']

    else:
        if writer_payload['entity_type'] == 'agent':
            WLSConnectVoicemail3_email_template = os.environ['default_agent_email_template']

        else:
            WLSConnectVoicemail3_email_template = os.environ['default_queue_email_template']

    WLSConnectVoicemail3_email_data = json.dumps(writer_payload['json_attributes'])

    # Send the email
    try:

        send_email = ses_client.send_email(
            FromEmailAddress=WLSConnectVoicemail3_email_from_address,
            Destination={
                'ToAddresses': [
                    WLSConnectVoicemail3_email_target_address,
                ],
            },
            Content={
                'Template': {
                    'TemplateName': WLSConnectVoicemail3_email_template,
                    'TemplateData': WLSConnectVoicemail3_email_data
                }
            }
        )
        logger.debug('********** Email request sent **********')
        logger.debug(send_email)

        return 'success'

    except Exception as e:
        logger.error('********** Failed to send email **********')
        logger.error(e)

        return 'fail'