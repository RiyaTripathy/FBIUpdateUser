# import python modules

import csv
import configparser
import requests
import urllib3
import pandas as pd


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Read the config file to retrieve url, token and filename
config = configparser.ConfigParser()
config.read('okta-config.txt')
url = config.get('General', 'url')
token = config.get('General', 'token')




# function to update FBI user/admin profile in Okta with required attributes

def updateFBIUser ( Company, Division, Roundtable, userid, login ):

    # Stripping whitespaces from Company , Division and Roundtable values and removing duplicate values

    Company = [x.strip(' ') for x in Company]
    CompanySet = set(Company)
    UniqueCompany=list(CompanySet)
    Division = [x.strip(' ') for x in Division]
    DivisionSet = set(Division)
    UniqueDivision = list(DivisionSet)
    Roundtable = [x.strip(' ') for x in Roundtable]
    RoundtableSet = set(Roundtable)
    UniqueRoundtable = list(RoundtableSet)


    # preparing the Update User JSON BODY
    jsonTosend = {"profile": {"company": UniqueCompany, "divisions": UniqueDivision, "roundtable_group": UniqueRoundtable}}

    # Call the update user Okta API
    res = requests.post(url+'/api/v1/users/'+userid, headers={'Accept': 'application/json', 'Content-Type':'application/json', 'Authorization': 'SSWS '+token}, json=jsonTosend, verify=False)

    response = res.json()

    # Check the status code of the response for success and failure
    if res.status_code == 200:

        # Add the login of the updated user to a file for record
        with open('UserUpdated.txt', 'a') as f:
            f.write(login.lstrip().rstrip() + '\n')

    # Add the login and error summary of the users not updated to a csv file for record
    else:
      with open('UserNotUpdated.csv', mode='a') as f:
          error = str(response['errorCauses'])
          writer = csv.writer(f, delimiter=',')
          writer.writerow([login.lstrip().rstrip(), error[19:-3]])
    return res.status_code

# Get All FBI Member and FBI Member Admin user list from Okta
# provide the id in the api below (FBI Member and FBI Member Admin )
apiurl= url + '/api/v1/users?search=type.id eq "otyucrvn8uCPSpgZ10h7" or type.id eq "otyucrapejSRr1Is90h7"'

res1 = requests.get(apiurl,

                                headers={'Accept': 'application/json', 'Content-Type': 'application/json',
                                         'Authorization': 'SSWS ' + token},verify=False)
result=res1.json()


if res1.status_code == 200:
# Retrieve the id,login,division,company and roundtable attributes of all the users to pass it to the Update user API JSON body
    for attributes in result:
        userid=attributes['id']
        login=attributes['profile']['login']
        company=attributes['profile']['company']
        division = attributes['profile']['divisions']
        roundtable = attributes['profile']['roundtable_group']

        # Call user update function
        updateFBIUser(company, division, roundtable, userid, login)

else:
    print('Okta connection failed')