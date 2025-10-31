from py5paisa import FivePaisaClient
cred={
    "APP_NAME":"5P53420117",
    "APP_SOURCE":"25774",
    "USER_ID":"EiQjGoK1oL5",
    "PASSWORD":"bM70U1eUchW",
    "USER_KEY":"j1XFKr6kUg0DAHgty85BLtZ1zCwxOr3B",
    "ENCRYPTION_KEY":"rqj6zhHtpX8iFG5KXDvyDerQAIXNw8ro"
    }

#This function will automatically take care of generating and sending access token for all your API's

client = FivePaisaClient(cred=cred)

# OAUTH Approach
# First get a token by logging in to -> https://dev-openapi.5paisa.com/WebVendorLogin/VLogin/Index?VendorKey=j1XFKr6kUg0DAHgty85BLtZ1zCwxOr3B&ResponseURL=https://Openapi.5paisa.com/VendorsAPI/Service1.svc/GetAccessToken
# VendorKey is UesrKey for individuals user
# for e.g. you can use ResponseURL as https://www.5paisa.com/technology/developer-apis
# Pass the token received in the response url after successful login to get an access token (this also sets the token for all the APIs you use)-

# Please note that you need to copy the request token from URL and paste in this code and start the code within 30s.

client.get_oauth_session('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IjUzNDIwMTE3Iiwicm9sZSI6ImoxWEZLcjZrVWcwREFIZ3R5ODVCTHRaMXpDd3hPcjNCIiwibmJmIjoxNzU2ODIyMzgxLCJleHAiOjE3NTY4MjU5ODEsImlhdCI6MTc1NjgyMjM4MX0.h1DktnA8uYLKAi_rjBD1zV3tAlbF3FrK6dxWRseBmd0')

#After successful authentication, you should get a Logged in!! message in console

#Function to fetch access token after successful login
print(client.get_access_token())

#Login with Access Token
client.set_access_token('accessToken','clientCode')