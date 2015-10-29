from __future__ import division
import MySQLdb
from collections import Counter

impact_db=MySQLdb.connect(host="localhost",
                          user="user",
                          passwd="password",
                          db="impact")

impact_db_c=impact_db.cursor()

journals={'NPB':'Nuclear Physics B',
         'JCAP':'JCAP',
         'JHEP':'JHEP',
         'PLB':'Physics letters B',
         'PTEP':'PTEP',
         'AHEP':'Advances in High Energy Physics',
         'APPB':'Acta Physica Polonica B',
         'CPC':'Chinese Phys. C',
         'EPJC':'EPJC',
         'NJP':'New J. Phys.',
         'Phys.Rev.D':'APS Phys.Rev.D',
         'Phys.Rev.C':'APS Phys.Rev.C',
         'Phys.Rev.Lett':'APS Phys.Rev.Lett.'}


for name, search_term in journals.items():
    for rank in range(1,5):
        impact_db_c.execute("select idrecord from record where journal_name = '%s'" % search_term)
        records = impact_db_c.fetchall()
        impact_file = open("impact_factor_"+name+"_rank"+str(rank)+".csv","w")

        for recid in records:
            impact_db_c.execute("select idauthor from rec_author where idrecord = %s", (recid[0],))
            authors_id = impact_db_c.fetchall()
            countries = []
            for author in authors_id:
                impact_db_c.execute("""select country.rank%s
                                   from auth_affiliation
                                   join affiliation
                                       on auth_affiliation.idaffiliation=affiliation.idaffiliation
                                   join country
                                       on affiliation.idcountry=country.idcountry
                                   where auth_affiliation.idauthor = %s
                                   order by country.rank%s""", (rank, author[0],rank))
                ranks = impact_db_c.fetchall()
                if ranks:
                   countries.append(ranks[0][0])
            counter = Counter(countries)
            print "%s: %s" % (recid, counter)
            final = {}
            for key, value in counter.iteritems():
                final[key] = value/len(countries)
            for i in range(-5, 198):
                if i not in final and i != 0:
                    final[i] = 0
            print "%s: %s" % (recid, final)
            result=[]
            for k, v in sorted(final.items(), key=lambda x: x[0]):
                result.extend([str(k), str(v)])
            result=','.join(result)
            print "%s: %s" % (recid, result)
            impact_file.write("%s,%s\n" % (recid[0], result))

        impact_file.close()
