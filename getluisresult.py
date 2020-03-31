########### Python 3.7 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64, json, requests, time

with open('luis-config.txt', 'r') as config:
    lines = [line.split() for line in config.readlines()]

key = lines[0][1]
AppID = lines[1][1]

headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': key,
}
# query = "King County hospitals are seeing significant pressures as the number of COVID-19 cases increase. " \
#         "Public Health estimates 82 new cases of COVID-19 today, bringing the estimated case count in King County to 2159. " \
#         "In addition, five new deaths are reported, bringing the estimated total of deaths in King County to 141."

def resolve_number(entities, expr):
    for entity in entities:
        if entity['entity'] == expr:
            return entity['resolution']['value']

def getcaseinfo(result, print_summary=True):
    summary = ''
    caseinfo = {}
    hasnewcases = False
    hastotalcases = False
    hasnewdeaths = False
    hastotaldeaths = False
    if 'compositeEntities' in result:
        for expr in result['compositeEntities']:
            summary += expr['value'] + ", "
            if expr['parentType'] == 'new-case-expression':
                if 'children' in expr and expr['children'][0]['type']=='builtin.number':
                    #caseinfo['new-cases']=expr['children'][0]['value'] #assume it's the first number in the expression
                    value_expr = expr['children'][0]['value']
                    caseinfo['new-cases'] = resolve_number(result['entities'], value_expr)
                    hasnewcases = True
            if expr['parentType'] == 'total-case-expression':
                if 'children' in expr and expr['children'][0]['type']=='builtin.number':
                    #caseinfo['total-cases']=expr['children'][0]['value'] #assume it's the first number in the expression
                    value_expr = expr['children'][0]['value']
                    caseinfo['total-cases'] = resolve_number(result['entities'], value_expr)
                    hastotalcases   = True
            if expr['parentType'] == 'new-death-expression':
                if 'children' in expr and expr['children'][0]['type']=='builtin.number':
                    value_expr = expr['children'][0]['value']
                    caseinfo['new-deaths'] = resolve_number(result['entities'], value_expr)
                    hasnewdeaths = True
            if expr['parentType'] == 'total-death-expression':
                if 'children' in expr and expr['children'][0]['type']=='builtin.number':
                    value_expr = expr['children'][0]['value']
                    caseinfo['total-deaths'] = resolve_number(result['entities'], value_expr)
                    hastotaldeaths = True
    if 'topScoringIntent' in result:
        if result['topScoringIntent']['intent'] == 'None':
            caseinfo['isNone'] = True
    caseinfo['summary'] = summary
    if print_summary:
        print(summary)
    return caseinfo


def getluisresult(query):
    params = urllib.parse.urlencode({
        # Request parameters
        'verbose': 'true',
        'log': 'true',
        'show-all-intents': 'true',
        'q': '{}'.format(query)
    })
    blocked429 = True
    while blocked429:
        try:
            '''conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')'''
            req = requests.get(url="https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/"+AppID+"?%s"%params,
                               headers=headers)
            # conn.request("GET",
            #              "/luis/prediction/v3.0/apps/{appId}/slots/{slotName}/predict?query={query}&%s" % params,
            #              "{body}", headers)
            '''conn.request("GET",
                         "/luis/v2.0/apps/"+AppID+"?%s" % params,
                         "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            # print(data)
            result = json.loads(data)'''
            result = req.json()
            if req.status_code != 429:
                blocked429 = False
                return getcaseinfo(result)
                # summary = ''
                # if 'compositeEntities' in result:
                #     for expr in result['compositeEntities']:
                #         summary += expr['value'] + ", "
                # return summary
            else:
                # wait a second
                print("\tStatus 429: Retrying...")
                time.sleep(2)

            # print(summary)
            # conn.close()
        except Exception as e:
            print("[Exception {}] ".format(type(e)))#.format(e.args))


#getluisresult(query)
####################################