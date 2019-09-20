from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "" # TODO put account_sid here
# Your Auth Token from twilio.com/console
auth_token  = "" # TODO put auth_token here

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="", # TODO put receiving phone number here
    from_="", # TODO put sender phone number here (yours)
    body="Put text here")

print(message.sid)
