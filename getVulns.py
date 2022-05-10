#!/usr/bin/python3
import requests
import logging
import json
import pandas as pd
import os
import sys
from time import sleep
import shutil

# Configure logging - Default "WARNING" for production, set to "DEBUG" for development in environment variables
LOGLEVEL = os.environ.get('LOGLEVEL', 'warning').upper()
logging.basicConfig(
    level=LOGLEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

# Get directory path for this file - ensures the output files are saved in the same directory
# scriptPath = os.path.dirname(os.path.abspath(__file__))

# Global variables - change these to match your Nucleus account
project_id = os.environ['NUCLEUS_PROJECT_ID']
asset_group = os.environ['NUCLEUS_PROJECT_GROUP']
apiEndPoint = os.environ['NUCLEUS_API_ENDPOINT']
nucleus_datafolder = os.environ['NUCLEUS_DATAFOLDER']

# dataFolder configuration
# This is the folder where the output files will be saved
# dataFolder = os.environ['NUCLEUS_DATAFOLDER']
dataFolder = '{}/{}'.format(nucleus_datafolder, 'nucleus_data')
vulnFolder = '{}/{}'.format(dataFolder, 'vulnData')

# Delete pre-existing data files and directories if already exist
shutil.rmtree(dataFolder) if os.path.exists(dataFolder) else None
# Create data folders
os.makedirs(vulnFolder, exist_ok=True)

# create .gitinclude if doesn't exist
# gitinclude = '{}/.gitinclude'.format(dataFolder)
# if not os.path.exists(gitinclude):
#     # create a file
#     with open(gitinclude, 'w') as fp:
#         # uncomment if you want empty file
#         fp.write(
#             'DO NOT DELETE - This is required to make sure that the output files are tracked by git')
#         fp.close()

# API Configuration
# Do not store API key in github code. Use environment variables instead.
global_headers = {
    'accept': 'application/json',
    # Add your Nucleus API key in Github environment variables
    'x-apikey': os.environ['NUCLEUS_API_KEY']
}

# Function to get list of assets from Nucleus


def get_assets(projectId, assetGroup):
    url = '{}/projects/{}/assets'.format(apiEndPoint, projectId)
    query = {
        'asset_groups': assetGroup,
        'start': 0,
        'inactive_assets': 'false',  # Only active assets from Nucleus
        'limit': 500  # Default is 100
    }
    r = requests.get(url, headers=global_headers, params=query, verify=False)
    if r.status_code == 200:
        logging.info('Successfully retrieved assets')
        return r.json()
    else:
        logging.error('🚩 Could not get Assets. Exiting...\n\t\t\t...Error Code: {}\n\t\t\t...Reason: {}\n\t\t\t...Error Msg: {}'.format(
            r.status_code, r.reason, r.text))
        sys.exit()

# Function to get list of vulnerabilities for an asset from Nucleus


def get_vulns(projectId, assetId):
    url = '{}/projects/{}/assets/{}/findings'.format(
        apiEndPoint, projectId, assetId)
    r = requests.get(url, headers=global_headers, verify=False)
    if r.status_code == 200:
        logging.info(
            'Successfully retrieved vulnerabilities for asset {}'.format(assetId))
        return r.json()
    else:
        logging.error('🚩Could not get Vulnerability data\n...Error Code: {}\n...Reason: {}\n...Error Msg: {}'.format(
            r.status_code, r.reason, r.text))
        sys.exit()

#######
# Get list of all assets for the group and save as csv and JSON files
#######


# Step 1: Get list of active assets for the group from Nucleus
logging.info(
    'Calling Nucleus API to get list of assets for group {}...'.format(asset_group))
assets = get_assets(project_id, asset_group)

# Save as CSV file
filename = '{}/assets.csv'.format(dataFolder)
# Flatten and convert to a data frame
df = pd.json_normalize(assets, max_level=1, errors='ignore')
df.to_csv(filename, sep=',', encoding='utf-8',
          index=None, header=True)  # Save as csv file
logging.info('Successfully saved assets to {}'.format(filename))

# Save as JSON file
filename = '{}/assets.json'.format(dataFolder)
with open(filename, 'w') as f:
    json.dump(filename, f, indent=4)  # Save as JSON file
logging.info('Successfully saved assets to {}'.format(filename))

# Step 2: Create CSV file for vulnerable hosts
hostList = []  # Create list to store host details
for item in assets:
    # Only include assets with critical, high or medium vulnerabilities
    if item['finding_count_critical'] > '0' or item['finding_count_high'] > '0' or item['finding_count_medium'] > '0':
        logging.info('Adding {} to list of vulnerable hosts'.format(
            item['asset_name']))
        hostDict = {}  # Create empty host dictionary to store asset details
        hostDict['asset_id'] = item.get('asset_id')
        hostDict['asset_type'] = item.get('asset_type')
        hostDict['asset_name'] = item.get('asset_name')
        hostDict['ip_address'] = item.get('ip_address')
        hostDict['application_id'] = item.get(
            'asset_info').get('archer.application_id')
        hostDict['application_short_name'] = item.get(
            'asset_info').get('archer.application_short_name')
        hostDict['archer_criticality'] = item.get(
            'asset_info').get('archer.criticality')
        hostDict['archer.pci'] = item.get('asset_info').get('archer.pci')
        hostDict['tanium.location'] = item.get(
            'asset_info').get('tanium.location')
        hostDict['tanium_model'] = item.get('asset_info').get('tanium.model')
        hostDict['tanium.environment'] = item.get(
            'asset_info').get('tanium.environment')
        hostDict['operating_system_name'] = item.get('operating_system_name')
        hostDict['asset_criticality'] = item.get('asset_criticality')
        hostDict['finding_vulnerability_score'] = item.get(
            'finding_vulnerability_score')
        hostDict['finding_count_critical'] = item.get('finding_count_critical')
        hostDict['finding_count_high'] = item.get('finding_count_high')
        hostDict['finding_count_medium'] = item.get('finding_count_medium')
        hostDict['scan_date'] = item.get('scan_date')
        hostList.append(hostDict)  # Add host dictionary to list
    else:
        logging.info('🚩Skipping asset {} as it does not have any critical, high or medium vulnerabilities'.format(
            item['asset_name']))

# write hostList to csv file
filename = '{}/vulnerable_assets.csv'.format(dataFolder)
df = pd.DataFrame(hostList)
df.to_csv(filename, index=False, header=True)
logging.info('List of vulnerable hosts saved to {}...'.format(filename))

#######
# Get vulnerabilities for each of above assets
#######

# Step 1: Get list of all vulns for each of above assets
for item in assets:
    sleep(5)  # Wait for 5 seconds before calling Nucleus API again
    assetId = item.get('asset_id')
    assetName = item.get('asset_name')
    application = item.get('asset_info').get('archer.application_short_name')
    # Get all vulnerabilities for assetId
    logging.info(
        'Calling Nucleus API to get list of vulnerabilities for asset {}...'.format(assetName))
    assetVulns = get_vulns(project_id, assetId)

    # Only process below if critical or high vulnerabilities exist
    for c in ['Critical', 'High']:
        critType = c
        cCount = 'finding_count_{}'.format(critType.lower())
        if item[cCount] > '0':  # Only include assets with more than 0 critical or high vulnerabilities
            jsonFile = '{}_{}_vulns_{}.json'.format(
                application, assetName, critType.lower())
            csvFile = '{}_{}_vulns_{}.csv'.format(
                application, assetName, critType.lower())

            vulnList = []
            for v in assetVulns:
                vulnhostDict = {}
                vulnhostDict.clear()
                # Only include active vulnerabilities. This step also makes sure to populate different hostDictionary based on criticality type
                if v['finding_status'] == "Active" and v['finding_severity'] == "{}".format(critType):
                    vulnhostDict['vuln_details'] = v
                    vulnhostDict['asset_id'] = assetId
                    vulnhostDict['asset_name'] = assetName
                    vulnhostDict['ip_address'] = item.get('ip_address')
                    vulnList.append(vulnhostDict)
            if len(vulnList) > 0:  # Only write to file if there are vulnerabilities in the list to make sure we don't end up writing empty files
                logging.info('{}_{} - {} vuln: {}'.format(application,
                             assetName, critType, len(vulnList)))
                # convert list to json object
                vulnObj = json.dumps(vulnList, indent=4)
                # save json object to file
                with open(os.path.join(vulnFolder, jsonFile), 'w') as outfile:
                    json.dump(vulnList, outfile)
                logging.info('...✅ Vulnerabilities saved to {}'.format(
                    os.path.join(vulnFolder, jsonFile)))
                # Save list to csv file
                # Flatten and convert list to a data frame
                df = pd.json_normalize(vulnList, max_level=1, errors='ignore')
                df.to_csv(os.path.join(vulnFolder, csvFile), sep=',',
                          encoding='utf-8', index=None, header=True)  # Save as csv file
                logging.info('...✅ Vulnerabilities saved to {}'.format(
                    os.path.join(vulnFolder, csvFile)))
            else:
                logging.warning(
                    "🚩Something went wrong - couldn't find any vulnerabilities")

# pause few seconds
sleep(3)

# Exit program - should be at the end of this script
sys.exit()
