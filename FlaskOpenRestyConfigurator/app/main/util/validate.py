import re

ownerRegex = r"([a-z0-9]{30,})"
userKeyUrlRegex = r"^[a-zA-Z0-9]{3,25}$"

upstreamURLRegex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"



def validatePostBackendContent(payload):
    #check owner
    owner = payload['owner']
    if not re.fullmatch(ownerRegex, owner):
        return {"error" : "The owner name can only contain alphabetics and numerics with at least 30 chars. Also no @elixir.org prefix at the end please!"}

    user_key_url = payload['user_key_url']
    if not re.fullmatch(userKeyUrlRegex, user_key_url):
        return {"error" : "The user key url prefix can only contain alphabetics and numerics with at least 3 and a maximum of 25 chars."}

    upstreamURL = payload['upstream_url']
    if not re.fullmatch(upstreamURLRegex, upstreamURL):
        return {"error" : "This is not a valid upstream url. Example: http://129.70.168.5:3000"}

    return {"status" : "okay"}

