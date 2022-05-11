# Nucleus v1

This action is used to retrieve list of security vulnerabilities from [Nucleus platform](https://nucleussec.com/). You can store the vulnerabilities in a particular folder in your repository or store in a more secured location, such as Azure or AWS storage account with restricted access.

🚩If you are storing data into your repository, please make sure to keep repo private. This will ensure that the data is not accessible to the public or any unauthorized person.

## Prerequisites

You need following information to retrieve the data from Nucleus platform.

1. Nucleus API key: You can get it from Nucleus webapp or work with your security team who manages this platform. 

   - Save this key in github - `Settings/Actions/New Repository Secret`

   - Follow these directions to create a new secret 👉[How to create repository secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets#about-encrypted-secret)

2. Nucleus Asset Group Name: This is the group name that you use to filter your assets in Nucleus webapp. Example: `/Product Name/...`
3. Nucleus Project ID: This is the project ID for your project in Nucleus webapp. You can get it from the URL of your project. This normally remains same for all assets for your company/organization.

   - Example: If the URL looks like this - `https://nucleus-us3.nucleussec.com/nucleus/public/app/index.php#bc/13000008/...`, then the project ID is `13000008`.

4. Nucleus API Endpoint - This is the endpoint that you use to retrieve the data from Nucleus platform.

   - Default: `https://nucleus-us3.nucleussec.com/nucleus/api`

5. Logging Level: Use "warning" to make sure you don't see sensitive records in github actions logs. To see more details, set it to "info"
6. Nucleus data folder: This is the folder where resulted data is stored, such as list of vulnerabilities. Provide full path in yoru repository. This action will create all necessary files and folders within this path and save data in there.

## Usage

Example of a new workflow in github

```yaml
on: 
  workflow_dispatch: # Allows to run this workflow manually
  schedule:  # every day at 08:00CDT (13:00UTC) Monday through Friday
    - cron: '0 13 * * 1,2,3,4,5'
jobs:
  retrieve-nucleus-vulns:
    name: Nucleus_Vulnerability_Report
    runs-on: ubuntu-latest
    continue-on-error: false # If true, the job will continue to run even if there is an error
    permissions:
      contents: write # Allows the workflow to write to the repository
    env: 
        NUCLEUS_API_KEY: ${{ secrets.NUCLEUS_API_KEY }} # Save this key in github - `Settings/Actions/New Repository Secret`
        NUCLEUS_ASSET_GROUP: '/Product Name/Cybersecurity Incident Response' # Change this to your asset group within Nucleus
        NUCLEUS_PROJECT_ID: '13000008'
        LOGLEVEL: 'WARNING' # Change to "INFO" to see more details in action logs
        NUCLEUS_API_ENDPOINT: "https://nucleus-us3.nucleussec.com/nucleus/api"
        NUCLEUS_DATAFOLDER: "data" # Change this folder per your needs. This folder should already exist in your repository.
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Get Vulnerabilities
        uses: samkshah/nucleus@v1.32 # Used to retrieve vulnerabilities from Nucleus platform

      - name: Commit results to Github # Save retrieved data to your repository
        run: |
          cd $NUCLEUS_DATAFOLDER
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add --force .
          git commit -m "🤖 [Github Action]: Saved vulnerabilities details in $NUCLEUS_DATAFOLDER"
          git push origin main
```

## Vulnerability Data

If you are storing data in your repository, here's how the data will be structured within `NUCLEUS_DATAFOLDER` folder mentioned in above github workflow.
```text
.
├── assets.csv
├── assets.json
├── vulnData
│   ├── ServerName_vulns_critical.csv
│   ├── ServerName_vulns_critical.json
.
.
└── vulnerable_assets.csv

```

- assets.csv: This is the list of all assets in the asset group mentioned in github action
- assets.json: Same data with another format
- vulnData/...: This is the folder that has detailed vulnerabilities data for each asset
- vulnerable_assets.csv: This is the list of all assets that have vulnerabilities
