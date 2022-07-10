import re

with open('/users/yumoto/Desktop/chk.txt','r') as f:
    lines = f.readlines()

koumoku = []
for line in lines:
    line = line.replace('\n','')
    elms = line.split(',')
    for j in elms:
        j = j.strip()
        koumoku.append(j)

koumoku = sorted(set(koumoku))

with open('/users/yumoto/Desktop/chk2.txt','w') as f:
    for i in koumoku:
        ii = i.lower()
        if 'dept ' in ii or 'univ' in ii or ' dept' in ii:
            #print(i)
            pass
        elif 'co ltd' in ii or ' ltd'in ii or 'hosp' in ii:
            pass
        elif 'adv ' in ii or 'ctr' in ii or 'dev' in ii or 'res ' in ii:
            pass
        elif 'div' in ii or 'lab' in ii or 'fac' in ii:
            pass
        elif 'grad' in ii or 'inst' in ii or 'sch' in ii:
            pass
        elif 'grp' in ii or 'corp' in ii or 'inc' in ii:
            pass
        elif 'japan' in ii or 'world' in ii or 'technol' in ii:
            pass
        elif 'nippon' in ii or 'aist' in ii or 'appl' in ii:
            pass
        elif 'chem' in ii or 'coll' in ii or 'engn' in ii:
            pass
        elif 'comp' in ii or 'global' in ii or 'high' in ii:
            pass
        elif 'innovat' in ii or 'jst' in ii or 'mat ' in ii:
            pass
        elif 'nims' in ii or 'natl' in ii or 'org ' in ii:
            pass
        elif 'platform' in ii or 'quantum' in ii or 'riken' in ii:
            pass
        elif 'sect ' in ii or 'synchrotron' in ii or ' kk' in ii:
            pass
        elif 'unit ' in ii in 'wpi' in ii or 'erato' in ii:
            pass
        elif 'elyt' in ii or 'element' in ii or 'energy' in ii:
            pass
        elif 'environm' in ii or 'agcy' in ii or 'acad' in ii:
            pass
        elif 'elect' in ii or 'int ' in ii or 'interdiscip' in ii:
            pass
        elif 'jfe' in ii or 'minist' in ii or 'govt' in ii:
            pass
        elif 'clin' in ii or 'oral' in ii or 'course' in ii:
            pass
        elif 'dent ' in ii or 'degree' in ii or 'integrat' in ii:
            pass
        elif 'intel' in ii or 'cnrs' in ii or 'liberal' in ii:
            pass
        elif ' unit' in ii or 'museum' in ii or 'new ' in ii:
            pass
        elif 'nat ' in ii or 'r&d' in ii:
            pass
        elif re.search('^[A-Z]+$', i) or re.search(' [Cc]o$', i):
            pass
        elif re.search('S[Pp]ring',i):
            pass
        else:
            i = i + '\n'
            f.write(i)
