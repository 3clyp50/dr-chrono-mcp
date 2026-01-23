https://support.drchrono.com/home/app-management
---

# App Management[](https://support.drchrono.com/home/pdfexport/id/682cf897f644203cf40168a8 "Download PDF")[](https://support.drchrono.com/home/app-management# "Print Article")[](https://support.drchrono.com/home/app-management# "Email Article")

Last modified on 05/30/2025 11:56 am EDT

#### [Manage third-party apps](https://support.drchrono.com/home/app-management#manage_apps) | [Access third-party apps](https://support.drchrono.com/home/app-management#access_apps) | [Provider and staff interactions in app management](https://support.drchrono.com/home/app-management#provider_staff) 

Practices rely on various third-party applications to streamline processes, enhance productivity, and improve patient care. App management is crucial to ensure that applications are effectively monitored and maintained to support the practice's goals and objectives.

## Manage third-party apps

- Users with the [**Manage App Directory** permission](https://support.drchrono.com/home/app-management#permission) can deauthorize apps in the **App Directory** (**Account** > **App Directory**).
- To disconnect from an app, select **Deauthorize**. Deauthorizing an app invalidates the current tokens used to connect DrChrono to an external app and removes it from the account.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/682e0a49d2ecb147c20d6475/n/authorized-applications.png)

### Required permission

To manage authorized apps shown in the **App Directory**, you must have the **Manage App Directory** permission turned on in **Permissions Administration** (**Account** > **Staff Permissions**).

## Access third-party apps

Users can access authorized apps from:

-  The **App Directory** tab in the patient chart

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/682fbdb1fd23f494d602c61c/n/patient-chart-sidebar-app-directory.png)

  

- The **APPS** tab in the clinical note

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/682fc55d5e83bcf9600e3369/n/clinical-note-apps-f7e09a.png)

## Provider and staff interactions in app management 

The third-party app connects to a specific user, and the generated token is assigned to this user. The third-party app allows the iframe or the third party’s webpage to be shown in the patient chart or clinical note.

- You can add staff members in **Account** > **Staff Members** > **Staff** tab, and associate the primary provider with the staff member.
- The provider and their associated staff members can view the app.
- When a provider deauthorizes an app, it's removed for the provider and their associated staff members.
- When a staff member deauthorizes an app, it's removed for that staff member. If the integration offers an iframe feature, then when the staff removes the connection, the iframe also removes it for the provider and any associated staff with the same provider.
- If the practice has multiple providers, each provider or their staff must integrate with the third party to view the app.
----
# DrChrono Domains for Application URLs[](https://support.drchrono.com/home/pdfexport/id/68a8f71660a38f50b6019e22 "Download PDF")[](https://support.drchrono.com/home/drchrono-domains-for-application-urls# "Print Article")[](https://support.drchrono.com/home/drchrono-domains-for-application-urls# "Email Article")

Last modified on 10/08/2025 7:46 pm EDT

To maintain the highest standards of resilience, functionality, and security for our APIs, we require API partners and customers to ensure their API traffic is not routed through unsupported subdomains. Specifically, some API partners and customers are routing traffic through www.drchrono.com. 

Ensure that www.drchrono.com isn't used in your integrations **before November 1, 2025**.

- If you are not using www.drchrono.com, no action is required.
- Starting November 1, 2025, we will intermittently reject API traffic on www.drchrono.com as a “brownout” measure to prompt API partners and customers to notice and actively resolve errors. 
- On December 1, 2025, www.drchrono.com will no longer be supported.  
    

We require this change to guarantee that API traffic meets the expected performance and reliability standards, and to clearly separate it from our www.drchrono.com web presence.

#### What's changing?

www.drchrono.com will no longer work for application endpoints. This subdomain was never intended for use with the application, as documentation has previously guided traffic to be routed through drchrono.com or app.drchrono.com.  

#### Which domains will work?  

✅ **Preferred:** app.drchrono.com

✅ **Still supported:** drchrono.com (no subdomain)

❌ **Not supported:** www.drchrono.com  

#### Who’s affected?

Anyone using www.drchrono.com for application routes in integrations, bookmarks, or API calls.

#### When will this change occur?

|Action|Date|
|---|---|
|Initial communication|September 2, 2025|
|Brownouts start with intermittent rejection of API traffic on www.drchrono.com|November 1, 2025|
|Support for www.drchrono.com ends|December 1, 2025|

#### What do I need to do?

Replace www.drchrono.com with **app.drchrono.com** for application/API endpoints **before November 1, 2025**.

#### What is the API impact?

The APIs are only affected if your API calls use www.drchrono.com. drchrono.com is still supported, but app.drchrono.com is recommended.

---

# Getting Started with DrChrono API with Python and C#[](https://support.drchrono.com/home/pdfexport/id/66e0ae00f50d64fb0b039a95 "Download PDF")[](https://support.drchrono.com/home/getting-started-with-drchrono-api-code-scripts# "Print Article")[](https://support.drchrono.com/home/getting-started-with-drchrono-api-code-scripts# "Email Article")

Last modified on 09/09/2025 7:28 pm EDT

Here are Python and C# scripts created by the DrChrono Engineering team to help you get started with connecting to DrChrono APIs.

### **Python Script**
```python
import datetime
import requests
import json
import threading
import webbrowser
import urllib.parse

from http.server import BaseHTTPRequestHandler, HTTPServer

"""
This python script demonstrates how to implement the OAUTH2 flow where:
1. a user loads a browser url which logs into drchrono.
2. drchrono will prompt the user to authorize a custom web application to operate using their credentials.
3. once the user authorizes the action they will be redirected to the web application with an authorization code.
4. the web application will receive the request containing the authorization code.
5. the web application will exchange the authorization code for an API token.
6. the web application will use the API token to retrieve a list of appointments on behalf of the user.

This script requires python runtime 3.6+ and python "requests" library
Always keep in mind client_secret and access_token are sensitive information and subject to HIPAA least-use policy

Example output:
c:\temp>python.exe thescript.py
Starting web server at http://localhost:8000
https://app.drchrono.com/o/authorize/?scope=calendar%3Aread%20patients%3Aread%20clinical%3Aread&response_type=code&redirect_uri=http://localhost:8000&client_id=XXX
Received GET with URL /?code=YYY
Found auth code YYY
POSTing to token endpoint using client-id/client-secret/auth-code/redirect-uri to get a token
Server responded with {"access_token": "ZZZ", "token_type": "Bearer", "expires_in": 172800, "refresh_token": "AAA", "scope": "calendar:read patients:read clinical:read"}
Token expires at 2024-04-18 09:15:29
Using the token to load appointments
Server responded with {"previous":null,"results":[{...}]}
"""


# this should be a URL to a web server which you control.
# when the user logs in to drchrono they will be redirected to this location with the authorization_code in the querystring.
# this authorization code can be used to log on to the API as the user.
redirect_uri = 'http://localhost:8000'
# you must set up an API application inside drchrono to retrieve these values
client_id = 'DRCHRONO_PROVIDED'
client_secret = 'DRCHRONO_PROVIDED'


class MyWebServer(BaseHTTPRequestHandler):
    """ Replace this with your web application listening on a specific URL """
    def do_GET(self):
        """ listening for a GET request which happens after user logs on and is redirected """
        try:
            print(f'Received GET request with URL {self.path}')
            authorization_code = self.path.split('code=')[1]
            print(f'Found auth code {authorization_code}')
            print(f'POSTing to token endpoint using client-id/client-secret/auth-code/redirect-uri to get a token')
            response = requests.post(f'https://app.drchrono.com/o/token/',
                params={
                    'grant_type': 'authorization_code',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': redirect_uri,
                    'code': authorization_code,
                },
            )
            response.raise_for_status()
            print(f'Server responded with {response.text}')
            token = response.json()
            expires_in = datetime.datetime.now() + datetime.timedelta(seconds=token['expires_in'])
            print(f'Token expires at {expires_in.strftime("%Y-%m-%d %H:%M:%S")}')
            print(f'Using the token to load appointments')
            response = requests.get(
                f'https://app.drchrono.com/api/appointments?since=2024-01-01',
                headers={
                    'Authorization': f'Bearer {token["access_token"]}',
                    'Content-Type': 'application/json',
                },
            )
            response.raise_for_status()
            print(f'Server responded with {response.text}')
        finally:
            raise SystemExit


print(f'Starting disposable web server at {redirect_uri}')
server_thread = threading.Thread(target=lambda: HTTPServer(('localhost', 8000), MyWebServer).serve_forever())
server_thread.start()

# scopes allow you as the client to limit the capabilities the API token will have
permitted_scopes = ['calendar:read', 'patients:read', 'clinical:read']
scope_string = urllib.parse.quote(" ".join(permitted_scopes), safe='')
# this is a url link which the user would click on to initiate the OAUTH2 process
browser_url = f'https://app.drchrono.com/o/authorize/?scope={scope_string}&response_type=code&redirect_uri={redirect_uri}&client_id={client_id}'
webbrowser.open(browser_url, new=2)

# the web server awaits the user to perform the logon process and get redirected back to the web server with the auth token
server_thread.join()
```

```c
### C# Script

using System.Net;
using System.Text.Json;
using System.Web;
using System.Net.Http.Headers;
using System.Text.Json.Nodes;

/*
This C# script demonstrates how to implement the OAUTH2 flow where:
1. a user loads a browser url which logs into drchrono.
2. drchrono will prompt the user to authorize a custom web application to operate using their credentials.
3. once the user authorizes the action they will be redirected to the web application with an authorization code.
4. the web application will receive the request containing the authorization code.
5. the web application will exchange the authorization code for an API token.
6. the web application will use the API token to retrieve a list of appointments on behalf of the user.

This script requires dotnet runtime version 6+. Due to the custom http listener the user must be running with administrator.
Always keep in mind client_secret and access_token are sensitive information and subject to HIPAA least-use policy

Example output:
c:\temp>ConsoleApp1.exe
Starting web server at http://localhost:8000
https://app.drchrono.com/o/authorize/?scope=calendar%3Aread%20patients%3Aread%20clinical%3Aread&response_type=code&redirect_uri=http://localhost:8000&client_id=XXX
Received GET with URL /?code=YYY
Found auth code YYY
POSTing to token endpoint using client-id/client-secret/auth-code/redirect-uri to get a token
Server responded with {"access_token": "ZZZ", "token_type": "Bearer", "expires_in": 172800, "refresh_token": "AAA", "scope": "calendar:read patients:read clinical:read"}
Token expires at 2024-04-18 09:15:29
Using the token to load appointments
Server responded with {"previous":null,"results":[{...}]}
*/

// this should be a URL to a web server which you control.
// when the user logs in to drchrono they will be redirected to this location with the authorization_code in the querystring.
// this authorization code can be used to log on to the API as the user.
string redirect_uri = "http://localhost:8000";
// you must set up an API application inside drchrono to retrieve these values
string client_id = "DRCHRONO_PROVIDED";
string client_secret = "DRCHRONO_PROVIDED";


// this is a disposable web server for the purpose of example which you should replace with your web application
// it will await the user request when they are redirected from login
var listener = new HttpListener();
listener.Prefixes.Add("http://*:8000/");
listener.Start();

// scopes allow you as the client to limit the capabilities the API session will have (HIPAA least-use policy)
// in this example we limit the scopes to read appointment data
var permittedScopes = new[] { "calendar:read", "patients:read", "clinical:read" };
var scopeString = HttpUtility.UrlEncode(string.Join(" ", permittedScopes));
// this is a link which a user would click on to initiate the OAUTH2 process
var browserUrl = $"https://app.drchrono.com/o/authorize/?scope={scopeString}&response_type=code&redirect_uri={redirect_uri}&client_id={client_id}";
// in this example we open the user's default browser to the link
System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo { FileName = browserUrl, UseShellExecute = true });

// wait here for the user to log in and authorize the OAUTH2 session
var context = listener.GetContext();
Console.WriteLine($"Received GET request with URL {context.Request.Url}");
var authorizationCode = HttpUtility.ParseQueryString(context.Request.Url.Query)["code"];
Console.WriteLine($"Found auth code {authorizationCode}");

using (var httpClient = new HttpClient())
{
    Console.WriteLine("POSTing to token resource using client-id/client-secret/auth-code/redirect-uri to get a token");
    var response = httpClient.PostAsync($"https://app.drchrono.com/o/token/", new FormUrlEncodedContent(new[]
    {
        new KeyValuePair<string, string>("grant_type", "authorization_code"),
        new KeyValuePair<string, string>("client_id", client_id),
        new KeyValuePair<string, string>("client_secret", client_secret),
        new KeyValuePair<string, string>("redirect_uri", redirect_uri),
        new KeyValuePair<string, string>("code", authorizationCode)
    })).Result;
    response.EnsureSuccessStatusCode();
    dynamic tokenData = JsonSerializer.Deserialize<JsonNode>(response.Content.ReadAsStringAsync().Result);
    var expiresIn = DateTime.Now.AddSeconds(tokenData["expires_in"].GetValue<int>());
    Console.WriteLine($"Token expires at {expiresIn.ToString("yyyy-MM-dd HH:mm:ss")}");
    
    Console.WriteLine("Using the token to load appointments");
    using (var requestMessage = new HttpRequestMessage(HttpMethod.Get, $"https://app.drchrono.com/api/appointments?since=2024-01-01"))
    {
        requestMessage.Headers.Authorization = new AuthenticationHeaderValue("Bearer", tokenData["access_token"].GetValue<string>());
        response = httpClient.SendAsync(requestMessage).Result;
    }
    response.EnsureSuccessStatusCode();
    Console.WriteLine($"Server responded with {response.Content.ReadAsStringAsync().Result}");
}




```
---

# Exporting Clinical Data from DrChrono's API[](https://support.drchrono.com/home/pdfexport/id/668c75815487e4c1a7089ae1 "Download PDF")[](https://support.drchrono.com/home/4511847132955-exporting-clinical-data-from-drchrono-s-api# "Print Article")[](https://support.drchrono.com/home/4511847132955-exporting-clinical-data-from-drchrono-s-api# "Email Article")

Last modified on 07/08/2024 7:25 pm EDT

You can use DrChrono's API to export data from your DrChrono account. This article provides an overview of the specific endpoints needed to obtain a copy of clinical records. For more complete information on our API see our [API documentation center](https://www.drchrono.com/api/).

**Note:** This article does not represent a tutorial on the API. In order to use these instructions to the fullest, you should partner with someone who is knowledgeable in consuming REST APIs, like a software engineer. Some partners in DrChrono's Marketplace that can assist in this process can be found under [interoperability](https://partners.drchrono.com/apps/category/X3Lv6Yf/interoperability) and [certified developers](https://partners.drchrono.com/services/category/hj8VE8n/certified-developer).

#### **Data that Makes Up the Patient Record**

Items that make up a patient record:

|   |   |   |
|---|---|---|
|Data Point|Endpoint|Notes|
|Demographics|api/patients||
|Appointments|api/appointments||
|Clinical Notes|api/appointments.clinical_note|PDF-locked version of clinical note|
|Clinical Notes|api/clinical_notes|Unlocked clinical note raw data|
|uploaded documents|api/documents||
|lab results [Manual Entry/Legacy]|api/patient_lab_results||
|communication logs|api/comm_log||
|Medications|api/medications||
|Allergies|api/allergies||
|Problems|api/problems||
|Vaccine Records|api/vaccine_records||
|CCDA Files|api/patients/{patient.id}/ccda|Contain many of the above data items (excluding: Documents, Manual Labs) Integration Lab Result data is included|

**Please Be Aware:**

- Consent Forms (and signatures) are not available via API
- Data provided is segmented (described below in Patient Demographics and the API docs), and must be autonomously iterated upon in order to obtain all results from a data point.

### Overview

**Patient Demographics**

- All data points above are connected to the "patient" object (API/patients) in the API. To export patients, send a GET request to `api\patients`.
- You'll have to loop over the results to get all patients in the set.  
    By default, up to 250 records are returned at a time.

**Patient Insurance, Flags, and Custom Fields**

- Similar to above, except you'll submit the parameter below with your request: -- {"verbose": True}:
- This parameter allows for additional processing and returns primary, secondary, tertiary, auto-accident, and worker's comp insurance data, custom demographics, and attached flags, in addition to the standard demographics.
- Sending this parameter to the API reduces the number of results returned from 250 to 50,  
    in order to obtain the additional fields. Custom Demographic fields and flags do not map 1:1 to accounts outside of the PG from which the data was extracted as the internal identifiers vary between accounts.

**Signed Clinical Notes**

- Obtained from API/appointments as a URL (appointment.clinical_note.pdf).
- The token appended to the URL is valid for one hour from the time it is obtained.
- You must download the file within this time. Raw Clinical Notes: - send GET to API/clinical_notes.
- Raw clinical notes will not map 1:1 with DrChrono accounts outside of the source practice group. This data will have to be matched to a compatible element in the new account.

**Medications, Allergies, Problems, Lab Results, Vaccine Records, Communication Logs**

- No special processing required for these data points.
- Pull the data via the API and save to local storage.

**Uploaded Documents**

- GET requests will provide a JSON object containing a URL (the `document` field).
- The token embedded within the URL is valid for one hour. Within such time, you must download the linked file and save to local storage, or a server.

Once the information is collected locally, you may push the data in any manner of your choosing through the API of the target account.

All data exported from DrChrono's API, cannot be inserted via the API. Please review the API documentation regarding the data types, and allowed values for each endpoint.

---

# Creating an API application[](https://support.drchrono.com/home/pdfexport/id/68dede19c7fec33d620ac00b "Download PDF")[](https://support.drchrono.com/home/creating-an-api-application# "Print Article")[](https://support.drchrono.com/home/creating-an-api-application# "Email Article")

Last modified on 10/02/2025 4:19 pm EDT

DrChrono Restful APIs allow your practice to connect to other services and leverage your data.

Sign in to your DrChrono account and navigate to Account > API. Create a new application by selecting "New Application".

(To note, the staff permission "**Settings**" will need to be enabled to access the API Page)

![Screenshot 2024-03-29 at 5.03.36 PM.png](https://dyzz9obi78pm5.cloudfront.net/app/image/id/668c72f95487e4c1a7089315/n/.24324592220315)

We require two pieces of information highlighted in red (Name and Redirect URIs). Ensure that your application is named for its intended service. Input a valid URI, for example -- https://myapp.com. Save changes to complete the application.

You are now ready to use our APIs. To get started, feel free to review our article "[Getting started with our APIs via Postman](https://support.drchrono.com/home/23701475632923-getting-started-with-our-apis-via-postman)".

---
DrChrono APIs have endpoints to grab data in bulk. Normally, our API response has a page size limit of 250, but our bulk APIs can obtain up to 1000 results.

**Our current list of bulk APIs**.

[Appointments](https://app.drchrono.com/api-docs/#tag/Clinical/operation/appointments_list_create)

[Patients](https://app.drchrono.com/api-docs/#tag/Clinical/operation/patients_list_create)

[Line Item](https://app.drchrono.com/api-docs/#tag/Billing/operation/line_items_list_create)

[Transactions](https://app.drchrono.com/api-docs/#tag/Billing/operation/transactions_list_create)

[Prescription Messages](https://app.drchrono.com/api-docs/#tag/Clinical/operation/prescription_messages_list_create)

[Eligibility Checks](https://app.drchrono.com/api-docs/#tag/Clinical/operation/eligibility_checks_list_create)

[Clinical Notes](https://app.drchrono.com/api-docs/#tag/Clinical/operation/clinical_notes_list_create)

[Clinical Note Field Values](https://app.drchrono.com/api-docs/#tag/Billing/operation/clinical_note_field_values_list_create)

### Steps to perform request 

1. POST a request with the filter and pagination options
2. Make a GET request with the "uuid" field from the POST response to fetch the results list once available  
    -> While the list is being generated, the GET response will have "status": "In progress"  
      
    **_Note: Higher page sizes will take longer to generate._**

The list generated is cached in DrChrono for 1 hour. If the list is expired, the UUID will return an invalid message. The POST request will need to be sent to generate a new list.

### Example

In this example, we will use the Appointments API. The response includes a "uuid" value that will be used in the GET request to retrieve the result list. 

POST REQUEST:

```sh
POST https://app.drchrono.com/api/appointments_list?verbose=true&since=2024-02-01&page=1&page_size=1000&order_by=updated_at
```

```json

RESPONSE:

HTTP Status 201

{
"status": "In progress",
"uuid": "dfeb7fa2-13dd-4b73-902d-c86ffd8d7f54",
"description": "Call https://app.drchrono.com/api/appointments_list?uuid=dfeb7fa2-13dd-4b73-902d-c86ffd8d7f54 to get the list"
}
```

  
GET REQUEST:
```json
GET https://app.drchrono.com/api/appointments_list?uuid=dfeb7fa2-13dd-4b73-902d-c86ffd8d7f54
```

```json
RESPONSE:

{
"status": "Complete",
"pagination": {
"count": 4428,
"pages": 5,
"page_size": 1000,
"page": 1
},
"uuid": "dfeb7fa2-13dd-4b73-902d-c86ffd8d7f54",
"results": [
{...}
]
}
```

To paginate to the next page you will need to make another POST request using the query parameter, "page=integer" [1 .. 1000].

EXPIRED RESULT RESPONSE

If the requested UUID is expired, the detail will specify the error.

```json
{
"detail": "Invalid uuid specified"
} 
```

### Python Example Code

This script can be used for any of our bulk API endpoints. The goal is to obtain all the data by iterating through all the pages.

```python
import json
import time
import requests
import textwrap

token = '6pxCIEj162QS80Ae6btWniZihkHHJv'
patient_data = []
mode='appointments'

def print_roundtrip(response, *args, **kwargs):
""" print full req and resp """
format_headers = lambda d: '\n'.join(f'{k}: {v}' for k, v in d.items())
print(textwrap.dedent('''
---------------- request ----------------
{req.method} {req.url}
{reqhdrs}
{req.body}
---------------- response ----------------
{res.status_code} {res.reason} {res.url}
{reshdrs}
{res.text}
''').format(
req=response.request,
res=response,
reqhdrs=format_headers(response.request.headers),
reshdrs=format_headers(response.headers),
))

hooks = { 'response': print_roundtrip }

def get_page(page=1, page_size=1000, since='2023-06-01'):
""" call the {records}_list asynchronously to POST a batch request and poll for results """
response = requests.post(
f'https://app.drchrono.com/api/{mode}_list?page_size={page_size}&page={page}&since={since}&verbose=true',
headers={
'Authorization': f'Bearer {token}',
'Content-Type': 'application/json'},
hooks=hooks,
)
response.raise_for_status()
handle = response.json()['uuid']
# await the request to be complete. check periodically.
while response.json()['status'] != 'Complete':
time.sleep(10)
response = requests.get(f'https://app.drchrono.com/api/{mode}_list?uuid={handle}',
headers={f'Authorization': f'Bearer {token}'},hooks=hooks,
)
response.raise_for_status()
return response

print('fetching page 1 of UNKNOWN')
response = get_page(1)
print('initial submission complete. record counts: ' + json.dumps(response.json()['pagination']))
patient_data.extend(response.json()['results'])
total_records = int(response.json()['pagination']['count'])
total_pages = int(response.json()['pagination']['pages'])
current_page = int(response.json()['pagination']['page']) + 1
print(f'gathered {[x["id"] for x in response.json()["results"]]}')

while current_page <= total_pages:
print(f'fetching page {current_page} of {total_pages}')
response = get_page(current_page)
patient_data.extend(response.json()['results'])
print(f'gathered {[x["id"] for x in response.json()["results"]]}')
current_page = current_page + 1

print(f'total records gathered: {len(patient_data)}. records reported by api: {total_records}')
print(f'{[x["id"] for x in patient_data]}')
```

---

# API Lab Interface Capabilities[](https://support.drchrono.com/home/pdfexport/id/679be1ffd12d5089f50a69f3 "Download PDF")[](https://support.drchrono.com/home/api-lab-interface-capabilities# "Print Article")[](https://support.drchrono.com/home/api-lab-interface-capabilities# "Email Article")

Last modified on 01/30/2025 6:03 pm EST

DrChrono offers open APIs and webhooks for custom lab interfaces designed to streamline lab order management. Our lab APIs and webhooks can be reviewed [**here**](https://support.drchrono.com/home/drchrono-lab-api-and-webhook). 

While DrChrono does not have the ability to directly send lab orders to vendors, we provide alternative solutions to ensure smooth lab order processing.

### Lab Ordering Methods

[_IMPORTANT: These methods have to be paired with our Lab APIs to reflect the order -> result progression via patient chart_]

###### Iframe Integration

Users can embed a **lab vendor’s portal** directly into the patient chart and clinical note pages using an iFrame. This method allows providers to place lab orders within DrChrono without needing to switch platforms, maintaining a seamless user experience.

When a doctor views your iFrame, the source URL will include various query parameters appended to it. For example, for the patient page, the `src` parameter of the iFrame will be:

```javascript
<iframe_url>?doctor_id=<doctor_id>&patient_id=<patient_id>&practice_id=<practice_id>&iat=<iat>&jwt=<jwt>
```

These IDs can be used to enhance the user experience by making API calls to retrieve relevant data and prepopulate most of the lab order fields automatically.

**Security Considerations for iFrame Integration:**

- **X-Frame-Options: same-origin** – Allows a page to be rendered in an iFrame only if the origin of the iFrame matches that of the page.
    
- **Referrer Policy: origin-when-cross-origin** – For same-origin requests, the browser sends the full URL (origin, path, and query string). For cross-origin requests, only the document’s origin is sent.
    
- **Mixed Content Restrictions** – If any resource from the lab vendor is served over HTTP instead of HTTPS, the browser will block the iFrame due to mixed content security policies.
    

###### Utilizing Task Center

DrChrono’s Tasks Center can be leveraged to track and manage lab orders efficiently. We offer both API and Webhooks.

Users can perform the following:

- Create a category in the task center. Example: Lab Orders  
    ![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/679bef1dff760daf17007dae/n/screenshot-2025-01-30-at-30309-pm.png)
- Create a manual task entry for lab orders  
    -> You can programmatically create a script or cron job to poll for tasks OR listen to the Task_Create webhook. For example:`GET /api/tasks?since=yyyy-mm-dd&category=id`  
    -> A list of categories can be found in `GET /api/task_categories`  
    -> Once the new order is obtained, push the order details back into DrChrono via POST /api/lab_orders. This will allow the doctor to view the order in the patient chart > Lab Orders.

This initial step can help begin the ordering process. You can create a 'Lab Results' category to inform the doctor or staff that the results are in. However, once you POST the lab_documents + lab_results on the same day we automatically send out a message to the provider from the Message Center. 

###### Faxing

DrChrono Faxing feature can be utilized to directly send to a lab vendor if the vendor allows faxes. It is a great alternative for minimal development work.

However, faxing directly from DrChrono comes with limitations as we do not support composing and sending messages through our fax line. Faxes have to be sent through the patient chart or referral. You can, however, compose a message, upload or scan it into DrChrono as a PDF document, and then send that as a fax.

For example, a lab order sheet is filled on a computer. You can upload it into the patient's chart > Documents. You can then fax the document to the vendor.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/679bf67659138322db0a2e74/n/screenshot-2025-01-30-at-35925-pm.png)

With the 'Faxing' alternative, you can keep it simple by bypassing the API and using the practice's fax number to send results.

Alternatively, instead of following the lab API sequence, you can post the lab results into the 'uploaded documents'. An example flow of this method can be.

- The doctor sends out a fax
- Once the fax is received, you can utilize the patient's name and other identifiers to prepare for the final results pdf.
- Make a call to `GET /api/patients?first_name=Joe&last_name=Turner&date_of_birth=yyyy-mm-dd`  
    -> A complete list of patient query parameters can be found [here](https://app.drchrono.com/api-docs/#tag/Clinical/operation/patients_list).
- POST final result document

```
curl --location '<a data-fr-linked="true" href="https://app.drchrono.com/api/documents">https://app.drchrono.com/api/documents</a>' \
```

### References

[https://app.drchrono.com/api-docs/#section/iframe-integration](https://app.drchrono.com/api-docs/#section/iframe-integration)

[https://app.drchrono.com/api-docs-old/v4/documentation#iframe-integration](https://app.drchrono.com/api-docs-old/v4/documentation#iframe-integration)

[https://app.drchrono.com/api-docs/#tag/Practice-Management/operation/tasks_list](https://app.drchrono.com/api-docs/#tag/Practice-Management/operation/tasks_list)

[https://app.drchrono.com/api-docs/#tag/Practice-Management/operation/task_categories_list](https://app.drchrono.com/api-docs/#tag/Practice-Management/operation/task_categories_list)

[https://app.drchrono.com/api-docs/#tag/Clinical/operation/documents_create](https://app.drchrono.com/api-docs/#tag/Clinical/operation/documents_create)