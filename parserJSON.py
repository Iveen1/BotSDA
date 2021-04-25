import json
# def parser(idx): #
#     f = open(r'SDA\maFiles\manifest.json')
#
#     data = json.load(f)
#     filename_first = data['entries'][0]["filename"]
#     steamid_first = data['entries'][0]["steamid"]
#
#     print(data['entries'][0])
#     for i in range(len(data['entries'])):
#         if data['entries'][i]['steamid'] == int(idx):
#
#            data["entries"][0]['filename'] = data['entries'][i]['filename']
#            data["entries"][0]['steamid'] = data['entries'][i]['steamid']
#            data["entries"][i]['filename'] = filename_first
#            data["entries"][i]['steamid'] = steamid_first
#     with open(r'SDA\maFiles\manifest.json', 'w') as f:
#         json.dump(data, f)