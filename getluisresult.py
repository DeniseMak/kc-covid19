########### Python 3.2 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': '{key}',
}
query = "Staying home is vitally important to King County’s ability to slow the spread of COVID-19 illnesses. Public Health announced 130 new cases today, bringing the official case count in King County to 1170. In addition, twelve new deaths are reported, bringing the total of confirmed deaths in King County to 87. A new local system launched to learn how COVID-19 virus is spreading."

params = urllib.parse.urlencode({
    # Request parameters
    'verbose': 'true',
    'log': 'true',
    'show-all-intents': 'true',
    'q': '{}'.format(query)
})

try:
    conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
    # conn.request("GET",
    #              "/luis/prediction/v3.0/apps/{appId}/slots/{slotName}/predict?query={query}&%s" % params,
    #              "{body}", headers)
    conn.request("GET",
                 "/luis/v2.0/apps/{AppID}?%s" % params,
                 "{body}", headers)
    response = conn.getresponse()
    data = response.read()
    print(data)
    conn.close()
except Exception as e:
    print("[Errno {0}] ".format(e.args))

####################################