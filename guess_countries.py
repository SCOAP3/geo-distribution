import re
import MySQLdb
from invenio.utils import NATIONS_DEFAULT_MAP

def find_nations(affiliation):
        NATIONS_DEFAULT_MAP['European Organization for Nuclear Research'] = 'CERN'
        NATIONS_DEFAULT_MAP['Centre Europeen de Recherches Nucleaires'] = 'CERN'
        NATIONS_DEFAULT_MAP['High Energy Accelerator Research Organization'] = 'KEK'
        NATIONS_DEFAULT_MAP['KEK'] = 'KEK'
        NATIONS_DEFAULT_MAP['FNAL'] = 'FNAL'
        NATIONS_DEFAULT_MAP['Fermilab'] = 'FNAL'
        NATIONS_DEFAULT_MAP['Fermi'] = 'FNAL'
        NATIONS_DEFAULT_MAP['SLAC'] = 'SLAC'
        NATIONS_DEFAULT_MAP['DESY'] = 'DESY'
        NATIONS_DEFAULT_MAP['Deutsches Elektronen-Synchrotron'] = 'DESY'
        NATIONS_DEFAULT_MAP['JINR'] = 'JINR'
        NATIONS_DEFAULT_MAP['JOINT INSTITUTE FOR NUCLEAR RESEARCH'] = 'JINR'

        values = [y.lower().strip() for y in re.findall(r"[\w']+", affiliation.replace('.', ''))]
        possible_affs = filter(lambda y: y is not None,
                               map(dict((key.lower(), val) for (key, val) in NATIONS_DEFAULT_MAP.iteritems()).get, values))
        if not possible_affs:
            possible_affs = []
            for country in NATIONS_DEFAULT_MAP.iterkeys():
                if country.lower() in affiliation.lower().replace('\n', ' '):
                    possible_affs.append(NATIONS_DEFAULT_MAP[country])
        if not possible_affs:
            possible_affs = ['HUMAN CHECK']
        if 'CERN' in possible_affs and 'Switzerland' in possible_affs:
            # Don't use remove in case of multiple Switzerlands
            possible_affs = [x for x in possible_affs if x != 'Switzerland']
        if 'KEK' in possible_affs and 'Japan' in possible_affs:
            possible_affs = [x for x in possible_affs if x != 'Japan']
        if 'FNAL' in possible_affs and 'USA' in possible_affs:
            possible_affs = [x for x in possible_affs if x != 'USA']
        if 'SLAC' in possible_affs and 'USA' in possible_affs:
            possible_affs = [x for x in possible_affs if x != 'USA']
        if 'DESY' in possible_affs and 'Germany' in possible_affs:
            possible_affs = [x for x in possible_affs if x != 'Germany']
        if 'JINR' in possible_affs and 'Russia' in possible_affs:
            possible_affs = [x for x in possible_affs if x != 'Russia']
        return sorted(list(set(possible_affs)))

impact_db = MySQLdb.connect(host="localhost",
                            user="user",
                            passwd="password",
                            db="impact")
impact_db_c = impact_db.cursor()
impact_db_c.execute("SELECT idaffiliation, aff_name from affiliation where idcountry is NULL")
a = impact_db_c.fetchall()
print len(a)
for id, aff in a:
    b = find_nations(aff)
    if len(b) == 1:
        if b[0] != "HUMAN CHECK":
            impact_db_c.execute("SELECT idcountry from country where country_name = '{0}'".format(b[0]))
            country_id = impact_db_c.fetchone()[0]
            impact_db_c.execute("UPDATE impact.affiliation SET idcountry = {0} WHERE idaffiliation LIKE {1}".format(country_id, id))
