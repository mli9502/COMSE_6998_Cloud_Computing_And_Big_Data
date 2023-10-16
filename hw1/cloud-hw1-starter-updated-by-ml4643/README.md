# Chatbot Concierge #

## About ##

Frontend starter repository for HW 1 of the Cloud Computing & Big Data
class at Columbia University and New York University.

## Usage ##

1. Clone the repository.
2. Replace `/assets/js/sdk/apigClient.js` with your own SDK file from API
   Gateway.
3. Open `chat.html` in any browser.
4. Start sending messages to test the chatbot interaction.

---

## Development ##

Followed link: https://docs.aws.amazon.com/AmazonS3/latest/userguide/HostingWebsiteOnS3Setup.html

Endpoint: http://ml4643-coms6998-a1.com.s3-website-us-west-1.amazonaws.com

`ml4643-admin` account id: 416716646862; link to sign-in: https://d-9a670ad251.awsapps.com/start/
Give command line access: https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html
AWS cli is configured as following:
```
mli@DESKTOP-KP02QUO:~$ aws configure sso
SSO session name (Recommended): ml4643
SSO start URL [None]: https://d-9a670ad251.awsapps.com/start#
SSO region [None]: us-east-2
SSO registration scopes [sso:account:access]:
Attempting to automatically open the SSO authorization page in your default browser.
If the browser does not open or you wish to use a different device to authorize this request, open the following URL:

https://device.sso.us-east-2.amazonaws.com/

Then enter the code:

DZJC-RKDB
The only AWS account available to you is: 416716646862
Using the account ID 416716646862
The only role available to you is: AdministratorAccess
Using the role name "AdministratorAccess"
CLI default client Region [None]: us-west-2
CLI default output format [None]: json
CLI profile name [AdministratorAccess-416716646862]:

To use this profile, specify the profile name using --profile, as shown:

aws s3 ls --profile AdministratorAccess-416716646862
```
The default profile is set in `bashrc` following https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html


openapi: https://docs.aws.amazon.com/apigateway/latest/developerguide/getting-started.html
Needs to convert https://github.com/001000001/aics-columbia-s2018/blob/master/aics-swagger.yaml to OpenAPI 3 (https://medium.com/@lawj1100/from-swagger-2-to-openapi-3-6b596d515e93).

Mock response & CORS:
https://stackoverflow.com/questions/43990464/api-gateway-mock-integration-fails-with-500
https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-mock-integration.html#how-to-mock-integration-request-examples
https://enable-cors.org/server_awsapigateway.html

Opensearch:
master username: ml4643-os-master
pw: mz8Xbxh@lz

AWS Lex example:
https://aws.amazon.com/blogs/machine-learning/creating-a-bankingbot-on-amazon-lex-v2-console-with-support-for-english-and-spanish/

LF1: `Oregon`->`Lambda`->`RestaurantsBot`
