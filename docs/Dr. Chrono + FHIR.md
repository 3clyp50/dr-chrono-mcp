
https://support.drchrono.com/home/fhir

---
# Activating your FHIR APIs[](https://support.drchrono.com/home/pdfexport/id/668c73de5487e4c1a7089590 "Download PDF")[](https://support.drchrono.com/home/19063995763867-activating-your-fhir-apis# "Print Article")[](https://support.drchrono.com/home/19063995763867-activating-your-fhir-apis# "Email Article")

Last modified on 03/06/2025 12:02 pm EST

You can set up your FHIR APIs so that you can access your health information.

#### Steps to setup FHIR API

1. Using the link and special key provided by the practice, you’ll be directed to this screen. Once on the site, select **Login**.

![Screenshot 2023-09-25 at 12.51.03 PM.png](https://dyzz9obi78pm5.cloudfront.net/app/image/id/668c73de5487e4c1a7089591/n/.19063990612507)

  

2. Next, select **Click Here to Activate.**

![Screenshot 2023-09-25 at 12.51.46 PM.png](https://dyzz9obi78pm5.cloudfront.net/app/image/id/668c73df5487e4c1a7089592/n/.19064010219163)

3. Enter information as specified:

- First Name (Legal Name)
- Last Name (Legal Name)
- Date of Birth (MM/DD/YY)
- Special key (given to you by the practice in your invitation)
- Submit

![Screenshot 2023-09-25 at 12.52.21 PM.png](https://dyzz9obi78pm5.cloudfront.net/app/image/id/668c73df5487e4c1a7089593/n/.19066335006875)

  

4. After you have activated your account, you will then land on a screen similar to the one below to further explain the setup process following instructions for Postman to configure. Keep your login credentials safe.

![Postman FHIR API.png](https://dyzz9obi78pm5.cloudfront.net/app/image/id/668c73e05487e4c1a7089594/n/.19071675828123)

Below is a sample patient email example of what the invitation looks like.

Subject: Welcome to the **Practice Name** FHIR APIs

Hello,

This email is your invitation to access your personal health data using our practice's FHIR APIs. Accessing your data this way is optional and no additional steps are necessary on your part.

Our FHIR APIs are a modern way to securely interact with and retrieve your health information from our practice. These APIs are one of two options you have to access your health information. For most patients, using [OnPatient.com](https://www.onpatient.com/) to access their personal health information is the easiest and best choice. Reach out to your practice if you have not already set up an [OnPatient.com](https://www.onpatient.com/) account.
```markdown
#### Your API Account Activation Information

#### Steps to Complete

1. To activate your accoun**t**, please access the site by [clicking here](https://identitydemo.dynamicfhir.com:44361/core/localregistration?signin=3400413a451689051270a6691cd6358d "https://stg.isalus-fhirpresentation.everhealthsoftware.com/dhit/dev_most_dev/r4").
2. Select Login
3. An option for Click Here to Activate will be shown below the username and password fields
4. Once selected, you will need to provide your First Name, Last Name, Date of Birth, and Activation Key (myN/MymSf6fxFLT/a)
5. Create a Username and Password. Keep these credentials as you will need them to access your account.

Once activated, keep these details safe:

- Your API ID: **101358**
- Your Activation Key: **myN/MymSf6fxFLT/a**

#### Why am I receiving this?

The Fast Healthcare Interoperability Resources (FHIR) is a standard for exchanging healthcare information electronically. It is designed to facilitate the exchange of electronic health records (EHRs) and other healthcare data between different systems.

The Interoperability and Patient Access final rule requires the use of FHIR by a variety of CMS-regulated payers, including Medicare Advantage organizations, state Medicaid programs, and qualified health plans in the Federally Facilitated Marketplace by 2021.

Specifically, the rule requires FHIR APIs for Patient Access, Provider Directory, and Payer-to-Payer exchange. The primary goal of the rule is to put patients first by giving them access to their health information when they need it most and in a way they can best use it.

Patients and their healthcare providers will have the opportunity to be more informed, which can lead to better care and improved patient outcomes, while at the same time reducing burden.
```

---

https://support.drchrono.com/home/using-health-gorilla-improved-workflow

# Using Health Gorilla (improved workflow)[](https://support.drchrono.com/home/pdfexport/id/6972424bbc7acf9a83001185 "Download PDF")[](https://support.drchrono.com/home/using-health-gorilla-improved-workflow# "Print Article")[](https://support.drchrono.com/home/using-health-gorilla-improved-workflow# "Email Article")

Last modified on 01/22/2026 10:34 am EST

This workflow will begin rolling out February, 2026.

  

Health Gorilla has transitioned its integration to their FHIR API, which introduces changes to how users access and use Health Gorilla within patient charts. This article outlines what users can expect from the update, including changes to workflows, access points, and account migration. We’ll cover the impact on existing users, new users, and mobile users, and explain how to navigate the updated experience.

### [**What's Changed**](https://support.drchrono.com/home/using-health-gorilla-improved-workflow#userimpact)**| [Access Health Gorilla](https://support.drchrono.com/home/using-health-gorilla-improved-workflow#access-health-gorilla) |** [**Place a New Lab Order**](https://support.drchrono.com/home/using-health-gorilla-improved-workflow#place-a-new-order) | [**Frequently Asked Questions**](https://support.drchrono.com/home/using-health-gorilla-improved-workflow#FAQ)

  

New integration requests must be submitted during implementation or through your Account Manager.

## What's Changed

|   |   |   |   |
|---|---|---|---|
|User Type|Impact|Access Changes|Account Migration|
|Existing|- Users must migrate to the new Health Gorilla FHIR API.<br>- The cost of the integration remains unchanged, but the workflow will be different.|- Health Gorilla will no longer be accessible via the App Directory in the patient chart.<br>-  Users will access it through a standalone tab within the patient chart and Clinical Notes.|- Users with existing Health Gorilla accounts do not need to sign up again.<br>- Existing order data will be preserved, and most current order types will continue to be supported in the new embedded view within the patient chart.|
|New|- Customers creating a Health Gorilla account after the migration will follow the new workflow outlined in this article.|- Users will access Health Gorilla through a standalone tab within the patient chart and Clinical Notes.|- Not applicable|
|Mobile|- Mobile users setting up a Health Gorilla account post-migration will also follow the updated workflow.|- Users will access Health Gorilla through a standalone tab within the patient chart and Clinical Notes.|- Not applicable|

  

## Accessing Health Gorilla in DrChrono

### Web

#### **From the Patient Chart**

- From the patient chart, **c**lick Health Gorilla from the menu list on the left
- The recent orders page will display the following :
    - Search bar - search by reference number,  vendor, test or diagnosis code.
    - View in Health Gorilla - clicking the button will open a new table to view details for the order in Health Gorilla's portal 
    - Place Order - click the dropdown to place a new lab order
    - Order ID - hyperlink that redirects to Health Gorilla's portal to view order 
    - Diagnosis -  based on patient problems list
    - Provider - user who ordered the lab
    - Vendor - facility will lab order was sent and will also provide results
    - Test/Services - type of lab order request
    - Date Submitted - date lab order is submitted
    - Status - not sent, sent, canceled, results received or error
    - Pagination - tracks the number of lab order records, with option to choose previous or next page
    

#### ![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/6909272f488c3d825c0ed01e/n/screenshot-2025-11-03-at-50429-pm.png)

#### **From the Clinical Note** 

- Open a new or existing clinical note
- Click the Plan form
- Choose the Health Gorilla tab

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/681cfe6fad802126ed0d7cfa/n/screenshot-2025-05-08-at-25506-pm-c61e79.png)

### Mobile

#### **From the Patient Chart** 

- Tap the patient name to display the dropdown menu
- Tap Health Gorilla from the Patient Column

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/6908bbe22a7e8370c60b0156/n/1762180065840.png)

#### **From the Clinical Note** 

- Open a new or existing clinical note
- Tap the Plan form
- Tap Health Gorilla 

  

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/6908bbed477f9775a802f9ee/n/1762180077190.png)

##  Place New Order

### Web

#### **From the Patient Chart** 

- Navigate to the patient chart
- Click Health Gorilla from the menu list on the left
- Click Place New Order
- Select the applicable order type from the dropdown list (diagnostic laboratories or radiology imaging).
- Enter order details
    - Vendor - search (by distance, office, patient or zip code)  or select vendor from frequently used vendors list > Continue, Cancel or Back to Recent Orders
    - Tests - search or select tests and services for this order (option to choose most used, quick orders or available tests)
        - current order field (optional) - priority level and/or test notes
        - order options (optional) - order notes and/or visit ID
    - Continue, Cancel or Back 
    - Complete - enter the following if applicable, fields with an asterisk (*) are required
        - select (single or multiple) patient diagnoses based on patient problems list
        - ordering physician
        - specimen for the order collected
        - schedule for future date
        - bill to
        - save as quick order
        - current order field (optional) - priority level and/or test notes
        - order options (optional) - order notes and/or visit ID
        - add attachments (optional)
    - Continue, Cancel or Back 
    - Submit - preview order with the following options
        - print requisition form
        - print nearby locations
        - fax requisition form to the service provider
        - skip electronic submission
    - Submit, eSign & Submit, Back  or Cancel
- Once submitted, the user will be redirected to DrChrono's recent order page.

If no options are selected on the preview screen before submitting the order, the order will still be submitted.  The screen will confirm submission, but will not automatically close. To view the order status, the user must go to the Health Gorilla section in the patient chart and click **Back to Recent Orders**.

  

#### **From the Clinical Note**

- Open a new or existing clinical note
- Select H&P 
- Choose the Plan form
- Choose Health Gorilla
- Enter order details (same steps as [Patient Chart](https://support.drchrono.com/home/using-health-gorilla-improved-workflow#patient-chart-steps) ) 
- Once submitted, the user will be redirected to DrChrono's recent orders page.

### Mobile

#### **From the Patient Chart** 

- Tap the patient name to display the dropdown menu
- Tap Health Gorilla from the Patient Column
- Tap the  icon to create a new order
    - Refresh  the page 
    - Option to search and/or view recent orders
    - Tap the icon to launch the Health Gorilla portal in new Safari window.
- Select the applicable order type from the dropdown list 
- Enter order details (same steps as [Patient Chart](https://support.drchrono.com/home/using-health-gorilla-improved-workflow#patient-chart-steps) ) 
- Once submitted, the user will be redirected to DrChrono's recent orders page.

#### **From the Clinical Note** 

- Open a new or existing clinical note
- Tap the Plan form
- Tap Health Gorilla 
- Enter order details (same steps as [Patient Chart](https://support.drchrono.com/home/using-health-gorilla-improved-workflow#patient-chart-steps) ) 
- Once submitted, the user will be redirected to DrChrono's recent orders page.

## Frequently Asked Questions

**Why are "Hospitals" and "Durable Medical Equipment" no longer available in the dropdown menu when placing an order?**  
According to Health Gorilla, these order types have been removed.  Also, DrChrono’s data indicates that a small percentage of users  selected these categories.

**What happens if I choose Imaging Order as my order type?**

 Imaging orders follow the same workflow outlined in the article [above](https://support.drchrono.com/home/using-health-gorilla-improved-workflow#patient-chart-steps).  Once results are received, an entry will automatically be created in the **Imaging Orders** section of the patient chart.

**Are Quest and LabCorp connected to Health Gorilla?**  

Electronic lab orders for Quest and Labcorp are not available through Health Gorilla. In order to place an electronic lab order to Quest or Labcorp, you will need to open an account with each of these labs (if you don’t already have one) and then connect that account to DrChrono. Please see our article for more information on setting up those direct accounts and integrating with DrChrono. In the event that Quest or Labcorp is temporarily unavailable in your account, you are able to order labs for Quest and Labcorp via e-fax as long as you have provided your account numbers to Health Gorilla.

**Are DICOM images for radiology supported?**

No. DICOM image files (the specialized format used in medical imaging) are **not** supported.  
Instead, radiology results are provided **as PDF documents**, which contain the key information extracted from the original DICOM files.

These radiology PDFs typically include:

- **Radiologist’s report** – narrative findings, impressions, and clinical interpretation.
    
- **Key images** – selected representative images taken from the full DICOM study.
    
- **Patient and study details** – such as patient name, imaging date, modality (e.g., CT, MRI, X-ray), and relevant technical information.
    

Click [here](https://developer.healthgorilla.com/docs/list-of-connected-labs) for a list of connected Health Gorilla labs.

---

# Connect Patient Dynamic FHIR API to OnPatient[](https://support.drchrono.com/home/pdfexport/id/66e09adf53699ae34c05ecc5 "Download PDF")[](https://support.drchrono.com/home/how-to-connect-patient-dynamic-fhir-api-to-onpatient# "Print Article")[](https://support.drchrono.com/home/how-to-connect-patient-dynamic-fhir-api-to-onpatient# "Email Article")

Last modified on 06/11/2025 1:07 pm EDT

OnPatient is designed to make managing your healthcare easy and convenient, whether you need to schedule appointments, access clinical records, make payments, or securely communicate with your doctors.

DrChrono has enhanced OnPatient to enable you to connect seamlessly with third-party apps directly from your OnPatient portal account.

#### Steps to activate 

To connect to OnPatient, an existing active DHIT account is necessary.

1. Practice initiates an [onpatient invite](https://support.drchrono.com/home/200027209-onpatient-basics "OnPatient Basics") to the patient.

Patient steps..

        2. Follow the invitation instructions to set up your [OnPatien](https://support.drchrono.com/home/9029997427483-how-do-i-activate-my-onpatient-account "How do I activate my OnPatient account?")t account.

        3.  On the signup screen, there will be a field for entering the Activation Code. You can find the activation

               code in the OnPatient invitation.

        3. Once logged into the OnPatient account, click on your name (top right corner) to access the settings

        5.   Click start connection in the "connect a third-party app to your FHIR R4 API"  box.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/66e9b261417768a07c0ef505/n/screenshot-2024-09-17-at-124458-pm.png)

        6.  Click "activate your FHIR API" under the activation link.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/66e9b4cd9a915d9ebf0b8422/n/screenshot-2024-09-17-at-125613-pm.png)

        7.  The link will take the patient to the DHIT landing page, where they can input their first and last name, date 

               of birth, and activation key and submit. The activation key can be found in the settings of their OnPatient

               account under the "connect a third-party app to your FHIR R4 API" section.

        8.  The DHIT FHIR API account is now connected to the OnPatient account.

       Patients can contact their Practice for any DHIT FHIR support issues.

---

# FHIR API FAQ[](https://support.drchrono.com/home/pdfexport/id/668c7c7c5487e4c1a708b0f3 "Download PDF")[](https://support.drchrono.com/home/19311277515291-fhir-api-faq# "Print Article")[](https://support.drchrono.com/home/19311277515291-fhir-api-faq# "Email Article")

Last modified on 02/06/2025 8:44 am EST

Check out our FAQ for more information about FHIR APIs.

**What is FHIR and do I need it?**

The primary goal of FHIR APIs for patients is to put patients first by giving them access to their health information when they need it most and in a way they can best use it. Patients and their healthcare providers will have the opportunity to be more informed, which can lead to better care and improved patient outcomes, while at the same time reducing burden.

The Fast Healthcare Interoperability Resources (FHIR) is a standard for exchanging healthcare information electronically and are part of the Promoting Interoperability Measure [Provide Patients Electronic Access to Their Health Information](https://support.drchrono.com/help/14839856406555) of the MIPS Quality Payment Program.

It is designed to facilitate the exchange of electronic health records (EHRs) and other healthcare data between different systems. The Interoperability and Patient Access final rule requires the use of FHIR by a variety of CMS-regulated payers, including Medicare Advantage organizations, state Medicaid programs, and qualified health plans in the Federally Facilitated Marketplace by 2021. Specifically, the rule requires FHIR APIs for Patient Access, Provider Directory and Payer-to-Payer exchange.

FHIR setup is **required** If your practice participates in the MIPS program and has chosen the Promoting Interoperability measure. If you do not need to report for MIPS or if you qualify for an exemption, then it is not necessary for you to set up the FHIR APIs.

**What information will patients be able to access using FHIR?**

FHIR requires participating providers to provide their patients with access to their data through an APIs (Application Programming Interface) which software developers use to retrieve patient data. Patients will not be able to view their data directly in plain text without further software development on their part to access the APIs or through the use of third-party solutions obtained by the patient. For information on what they will be able to access, see our article [What data is included in CCDA exports from DrChrono?](https://support.drchrono.com/help/360059776612)

**Will we be charged and if so, how much?**

As part of our commitment to providing you with the best healthcare solutions, the DrChrono team is providing this solution to you at no additional charge.

**What happens if a patient does not have an e-mail address has not shared it with us or it is invalid?**

An e-mail address is required to provide your patients with access to their health information. If a patient does not have an address listed, they will not be able to receive the required information and will not be counted in the numerator for the measure for the reporting period.

**Why do we need to use ConnectEHR and what are the advantages to using it?**

DrChrono has partnered with [ConnectEHR](https://www.dynamichealthit.com/connectehr) to facilitate the FHIR API process and allow your patients to access their health information so that your practice will comply with the FHIR standards in the Promoting Interoperability measure. If you do not participate in MIPS or do not report for the Promoting Interoperability measure, you may not need to use the ConnectEHR platform.

**Is it mandatory for the patient to sign up for ConnectEHR to meet the Provide Patient Access measure or does the email meet the measure?**

No. The patient doesn't need to activate their FHIR API account for you to meet the measure. They only have to receive their invitation, which happens automatically after you lock the clinical note. However, your practice **must be set up with** **ConnectEHR** for this to happen. Please contact [Support](https://support.drchrono.com/hc/en-us/requests/new) if you have any additional questions or if you still need to complete the set-up process.

**What's the difference between checking the health information via the OnPatient portal & ConnectEHR?**

OnPatient allows patients to access their health information from only your practice. Additionally, they can schedule appointments and message their provider. With FHIR APIs, patients can access their health information from all their providers in one place. However, both systems are required if your practice participates in the Promoting Interoperability MIPS measure.

**I didn't mean to sign up for FHIR APIs or I don't need to report. How can I disconnect my account?**

You can disable the connection to ConnectEHR by navigating to **Account** > **API**. Click **Disconnect** under the ConnectEHR tab. Once complete, you will see the green “Connected” status indicator switch to a red “Disconnected” status.


---

# Set Up ConnectEHR for FHIR[](https://support.drchrono.com/home/pdfexport/id/66c76c35dc4f0437fe029115 "Download PDF")[](https://support.drchrono.com/home/set-up-connectehr-for-fhir# "Print Article")[](https://support.drchrono.com/home/set-up-connectehr-for-fhir# "Email Article")

Last modified on 11/21/2025 3:29 pm EST

#### [Set up ConnectEHR](https://support.drchrono.com/home/set-up-connectehr-for-fhir#setup) | [Activate users for ConnectEHR](https://support.drchrono.com/home/set-up-connectehr-for-fhir#activate)

To meet the MIPS Promoting Interoperability measure, [Provide Patients Electronic Access to Their Health Information](https://support.drchrono.com/hc/en-us/articles/22713583772443), your practice must use our ONC Cures Edition FHIR API. To begin, you need to set up ConnectEHR for FHIR.

- Make sure to configure your FHIR APIs before your Promoting Interoperability reporting period begins. This ensures you receive the maximum possible points for the Provide Patients Electronic Access to Their Health Information measure.
- Complete the [MIPS FHIR API Request](https://everhealth.my.site.com/EverHealthSelfService/s/fhir-request) form. An incomplete setup may affect your MIPS reporting.
- Once your setup is finished, you can use your ConnectEHR login credentials to access third-party provider apps.

## Set up ConnectEHR

Practice admin users can access **API Management** and set up users for ConnectEHR.

1. Select **Account** > **API**. 
2. Select the **ConnectEHR Setup for FHIR** tab. 

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/66c777f0fb7742940001a182/n/connectehr-setup-fhir.png)

The **Connect EHR Setup** page opens. 

3. Fill out the form and select **Connect**.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/691673d560227559190dfd66/n/1763079125270.png)

  

Don't refresh your browser during this process. It may take several seconds (up to 20-30 in some cases) for the connected status to appear. 

The status changes to **Connected**. If you are not connected, the status is **Not Connected**. 

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/6916763337d2d85ae00bea58/n/connectehr-setup-connected-88265c.png)

## Activate users for ConnectEHR

It is currently not necessary for individual users to activate ConnectEHR; however, the connection must be established at the practice level.

1. Under **User Management**, search for the user.
2. Select **Activate**

**![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/6916771e53d88319f00b8656/n/1763079965881.png)**

Under **Role**, **Clinician** is selected by default. 

3. Enter a password.
4. Select **Activate**.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/66c77784bba07f24c10c4c99/n/connectehr-setup-activate.png)

The user's status changes to **Active**.

4. Securely provide the password to the user.


---

# SMART on FHIR Application Enhancements[](https://support.drchrono.com/home/pdfexport/id/67c9bb8312a09e9f890ef7bd "Download PDF")[](https://support.drchrono.com/home/smart-on-fhir-application-enhancements# "Print Article")[](https://support.drchrono.com/home/smart-on-fhir-application-enhancements# "Email Article")

Last modified on 04/28/2025 2:37 pm EDT

DrChrono is set to improve the efficiency of SMART on FHIR app launches by allowing users to seamlessly launch both patient apps (EHR app launches) and standalone apps (provider apps) directly from the App Directory tab within a patient’s chart. This enhancement is a transformative approach to patient care. DrChrono ensures a secure, accurate, and user-friendly experience while maintaining compliance with FHIR standards and authentication processes.

To request a new SMART on FHIR integration please fill out [this questionnaire](https://drchronoehr.typeform.com/to/uMK6dCTm).

#### Key Features

1. Admin Configuration

- DrChrono Admins: Can add one or multiple applications for both patient apps and standalone provider apps. They can also manage the enabling or disabling of these applications.

- Practice Group Admins: Can enable or disable the apps for their specific practice in Provider Settings > App Directory once they have been registered by the DrChrono admin.
    

2. Direct Launch from Patient Chart

- Users can launch approved apps directly from the App Directory tab in a patient’s chart.

#### **Admin Setup Instructions**

Application Requirements

- For Patient Apps (EHR Launches): The JTOT token is required, and the practice group must be active with [ConnectEHR](https://support.drchrono.com/home/set-up-connectehr-for-fhir "Set Up ConnectEHR for FHIR").

- For Standalone Apps (Provider Apps): A client secret is required, and the practice must have login credentials (username and password) for [ConnectEHR](https://support.drchrono.com/home/set-up-connectehr-for-fhir "Set Up ConnectEHR for FHIR").
    

Application Management

- DrChrono Admins
    
    - Can add one or multiple applications for EHR app launches and standalone apps, ensuring the necessary tokens and credentials are in place for proper registration.
        
    - Manage enabling or disabling of these applications as needed.
        
- Practice Group Admins
    
    - Can enable or disable apps for their practice from the Provider Settings > App Directory after they have been registered by the DrChrono admin.
        

Launching Apps

- Once the practice admin enables the app, it will appear in the patient’s chart within the App Directory screen. Clinicians or staff can then launch the app directly from the patient’s chart.

  

#### Add Application (internal use)

1. Access the SMART on FHIR Apps Screen

- Navigate to SWORDS in the header under the Global Settings section to access the SMART on FHIR Apps screen.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/67d84867457115fbd90e5edd/n/1742227559629.png)

2. From the SMART on FHIR Management screen, click Add Application.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/67c9fd985b4676d09a05aeba/n/add-application-button-6db888.png)

 3. Fill in applicable data;  fields with an asterisk(*) are required.   

Client ID,  Client Secret, API Launch Point, 0AUth 2.0 Flow and Scope information can be obtained from the users [DHIT](https://support.drchrono.com/home/set-up-connectehr-for-fhir "Set Up ConnectEHR for FHIR") account.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/67c9fdb15a05db28390b9132/n/add-application-page-dec2a1.png)4. Click next; a JWKS Public Key (JTOT token)  screen will appear with a message confirming the successful creation of the application.

To verify that the app has authorization with DrChrono, the JTOT token is required.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/67d846af4303e55c710430fa/n/jtot-token-jwks-public-ket.png)

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/67d8478c4b594a3a03064533/n/screenshot-2025-03-17-at-120159-pm.png)

5. Once the application is added, DrChrono will retrieve the patient data from DHIT and load it into the application.

#### Action Column (internal use) 

**Edit Application**

1. Select the desired application from the SMART on FHIR Management screen.
2. Edit necessary fields.
3. JWKS Public Key - If you choose to generate a new JWKS Public Key,  [ConnectEHR](https://support.drchrono.com/home/set-up-connectehr-for-fhir "Set Up ConnectEHR for FHIR") must be updated with a new key.

An example reason to generate a new key would be to enter in DHIT account to ensure the key matches with DrChrono.

1. Click save application or cancel.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/67c9fd001da46dd9d3029603/n/screenshot-2025-03-06-at-23255-pm-e2253f.png)

- **Manage Practices**

1. Search the practice name.
2. Enable or disable application under the action column for the practice group.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/67d84b530b323b1dde09b24a/n/screenshot-2025-03-17-at-121805-pm.png)

  

#### How can customers view/manage their existing applications?

Customers can view and manage their existing applications within their  DrChrono account by navigating  to Account > App Directory.

![](https://dyzz9obi78pm5.cloudfront.net/app/image/id/67d853e2721e59feec032ad6/n/app-directory.png)

Once an application is enabled for the practice, users are able to view via the App Directory tab in the patient chart.

---

# What is FHIR API?[](https://support.drchrono.com/home/pdfexport/id/668c73e05487e4c1a7089596 "Download PDF")[](https://support.drchrono.com/home/19012428538651-what-is-fhir-api# "Print Article")[](https://support.drchrono.com/home/19012428538651-what-is-fhir-api# "Email Article")

Last modified on 02/06/2025 8:43 am EST

You may have received an email inviting you to access your health data via FHIR APIs from your healthcare provider's office.

The FHIR APIs are a modern way to securely interact with and retrieve your health information from your healthcare provider. Your provider is [required](https://www.healthit.gov/test-method/standardized-api-patient-and-population-services) to set up FHIR APIs in order to deliver your health information to you. Your provider's EHR(electronic health record) software, [DrChrono](https://www.drchrono.com/), has partnered with [ConnectEHR](https://www.dynamichealthit.com/connectehr) to facilitate this process. When your provider completes the clinical documentation for your appointment, it delivers the documentation to ConnectEHR. Once the documentation is delivered, you will receive an email to access it.

Keep in mind, that these APIs are not the only method to access your health information. You can always access your data through [onpatient.com](https://www.onpatient.com/). For most patients, using OnPatient to access their personal health information is the easiest and best choice.

The difference between FHIR API and OnPatient is OnPatient accesses your medical records from a single healthcare organization and FHIR allows access to your medical records from multiple healthcare organizations.

For information on setting up FHIR, see our article for more information.

**What is FHIR?**

The Fast Healthcare Interoperability Resources (FHIR) is a standard for exchanging healthcare information electronically. It is designed to facilitate the exchange of electronic health records (EHRs) and other healthcare data between different systems.

The Interoperability and Patient Access final rule requires the use of FHIR by a variety of CMS-regulated payers, including Medicare Advantage organizations, state Medicaid programs, and qualified health plans in the Federally Facilitated Marketplace by 2021.

Specifically, the rule requires FHIR APIs for Patient Access, Provider Directory and Payer-to-Payer exchange. The primary goal of the rule is to put patients first by giving them access to their health information when they need it most and in a way they can best use it. Patients and their healthcare providers will have the opportunity to be more informed, which can lead to better care and improved patient outcomes, while at the same time reducing burden.


---


# What to Expect with FHIR APIs[](https://support.drchrono.com/home/pdfexport/id/668c7b945487e4c1a708ade1 "Download PDF")[](https://support.drchrono.com/home/19098823939739-what-to-expect-with-fhir-apis# "Print Article")[](https://support.drchrono.com/home/19098823939739-what-to-expect-with-fhir-apis# "Email Article")

Last modified on 02/06/2025 8:43 am EST

FHIR APIs are part of the Promoting Interoperability measure [Provide Patients Electronic Access to Their Health Information](https://support.drchrono.com/help/14839856406555) of the MIPS Quality Payment Program. If you need to report for MIPS, you can set up your FHIR APIs in order to report. If you do not need to report for MIPS, you don't need to set up the FHIR APIs.

Have questions about your reporting status, check our article [Check Your MIPS Participation Status.](https://support.drchrono.com/help/19007330844187)

**What to Expect with FHIR APIs Enabled**

Once we enable FHIR APIs for your practice, your patients will start receiving emails inviting patients to access their clinical data based on their clinical notes via your FHIR API's. See the [example below](https://support.drchrono.com/home/19098823939739-what-to-expect-with-fhir-apis#h_01HB96FPT6Y9JVREYT8VV1KBRR).

In order for this to work for your MIPS reporting there are two requirements:

1. You need to ensure patients are set up with their email address in the Patient Demographics screen in the patient chart.
2. Clinicians also need to ensure they are signing & locking clinical notes within **4 business days** of their appointment. The Sign & Lock process will push a copy of the patient's CCDA in order to populate your FHIR APIs with their clinical data.

Below are some other resources on FHIR APIs

[Set Up ConnectEHR for FHIR](https://support.drchrono.com/home/set-up-connectehr-for-fhir "Set Up ConnectEHR for FHIR")

[Overview of ConnectEHR](https://support.drchrono.com/help/19009575165979)

[FHIR API FAQ](https://support.drchrono.com/help/19311277515291)

Resources for your Patients:

[Activating your FHIR APIs](https://support.drchrono.com/help/19063995763867)

[What is FHIR API?](https://support.drchrono.com/help/19012428538651)

#### **Sample Patient Email**

Subject: Welcome to the **Practice Name** FHIR APIs

Email Body:

Hello,

This email is your invitation to access your personal health data using our practice's FHIR APIs. **Accessing your data this way is optional and no additional steps are necessary on your part.**

Our FHIR APIs are a modern way to securely interact with and retrieve your health information from our practice. These APIs are one of two options you have to access your health information. For most patients, using [OnPatient.com](https://www.onpatient.com/) to access their personal health information is the easiest and best choice. Reach out to your practice if you have not already set up an [OnPatient.com](https://www.onpatient.com/) account.

## Your API Account Activation Information:

### Steps to Complete

1. **To activate your account**, please access the site by [clicking here](https://stg.isalus-fhirpresentation.everhealthsoftware.com/dhit/dev_most_dev/r4 "https://stg.isalus-fhirpresentation.everhealthsoftware.com/dhit/dev_most_dev/r4").
2. Select **Login**
3. An option for **Click Here to Activate** will be shown below the username and password fields
4. Once selected, you will need to provide your **First Name, Last Name, Date of Birth, and Activation Key** (myN/MymSf6fxFLT/a)
5. Create a Username and Password. Keep these credentials as you will need them to access your account.

Once activated, keep these details safe:

- Your API ID: **101358**
- Your Activation Key: **myN/MymSf6fxFLT/a**

## Why am I receiving this?

The Fast Healthcare Interoperability Resources (FHIR) is a standard for exchanging healthcare information electronically. It is designed to facilitate the exchange of electronic health records (EHRs) and other healthcare data between different systems.

The Interoperability and Patient Access final rule requires the use of FHIR by a variety of CMS-regulated payers, including Medicare Advantage organizations, state Medicaid programs, and qualified health plans in the Federally Facilitated Marketplace by 2021.

Specifically, the rule requires FHIR APIs for Patient Access, Provider Directory, and Payer-to-Payer exchange. The primary goal of the rule is to put patients first by giving them access to their health information when they need it most and in a way they can best use it. Patients and their healthcare providers will have the opportunity to be more informed, which can lead to better care and improved patient outcomes, while at the same time reducing burden.

Warm regards,


---
