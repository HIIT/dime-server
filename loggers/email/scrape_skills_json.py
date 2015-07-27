import requests
import json
f = open("skills_1.txt", "w")

def getSkills(id, type):
    global f
    payload = {'id': id, 'type': type}    
    try:
        resp = requests.get("https://www.itsyourskills.com/skilljson", params=payload)
        d = json.loads(resp.text)
    except Exception as e:
        print 'something wrong'
        return
    for i in d:
        try:
            f.write( i['value'].encode('utf-8').strip())
            print i['value'].encode('utf-8').strip()
            f.write('\n')
        except Exception as e:
            print 'something wrong'
            continue 
        if(i['is_child']):
            getSkills( i['id'], type)
  
  
getSkills('0', 'functionals' )
getSkills('0', 'behavioural' )
f.close()
