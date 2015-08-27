import requests
import json
f = open("skills.txt", "w")

def getSkills(id, type, level):
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
            t = '-' * level + i['value'].encode('utf-8').strip()
            f.write( t)
            print t
            f.write('\n')
        except Exception as e:
            print 'something wrong'
            continue 
        if(i['is_child']):
            getSkills( i['id'], type, level+1)
  
  
getSkills('0', 'functionals', 0 )
getSkills('0', 'behavioural', 0 )
f.close()
