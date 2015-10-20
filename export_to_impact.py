"""Export of metadata for impact calculation."""

import sys
import re
import MySQLdb
from invenio.search_engine import perform_request_search, get_record
from invenio.bibrecord import record_get_field_value


class ImportCreator:

    def __init__(self, for_aps=False):
        self.for_aps = for_aps
        try:
            self.impact_db = MySQLdb.connect(host="localhost",
                                             user="user",
                                             passwd="password",
                                             db="impact")
            self.impact_db_c = self.impact_db.cursor()
        except Exception as e:
            print("Error - faild to connect to DB")
            raise e

    def find_nations(self, affiliation):
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
        print affiliation
        print values
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

        print possible_affs
        return sorted(list(set(possible_affs)))[0]

    def create_author(self, name, orcid, co_author):
        """Create entry in author table."""
        try:
            if self.impact_db_c.execute("""INSERT INTO
                                   author (author_name, orcid, co_author)
                                   VALUES (%s, %s, %s)""", (name, orcid, co_author)):
                return self.impact_db_c.lastrowid
            else:
                return None
        except Exception:
            print("Error - faild to create author entry")
            raise

    def create_rec_author(self, recid, inserted_id):
        """Create entry in rec_author table."""
        try:
            self.impact_db_c.execute("""INSERT INTO
                                   rec_author (idrecord, idauthor)
                                   VALUES (%s, %s)""", (recid, inserted_id))
        except Exception:
            print("Error - faild to create rec_author entry for recid %s" % (recid,))
            raise

    def get_short_affiliation_inspire(self, short_aff_rec):
        country = record_get_field_value(short_aff_rec, tag='371', code='d')
        if not country:
            country = record_get_field_value(short_aff_rec, tag='371', code='g')
        if '510' in short_aff_rec:
            short_aff_rec = get_record(record_get_field_value(short_aff_rec, tag='510', code='0'))
        institute = record_get_field_value(short_aff_rec, tag='110', code='g')
        ins = ['cern', 'kek', 'fnal', 'slac', 'desy', 'jinr']
        for i in ins:
            if i in institute.lower():
                country = i.upper()

        return country

    def _create_affiliation_entry_aps(self, affiliation):
        country = None
        short_affiliation = perform_request_search(p="110__u:'{affiliation}'".format(affiliation=affiliation), cc="Institutions")
        if short_affiliation:
            short_aff_rec = get_record(short_affiliation[0])
            country = self.get_short_affiliation_inspire(short_aff_rec)
        else:
            print "Can't find this affiliation: %s" % (affiliation,)

        if country and self.impact_db_c.execute("SELECT idcountry FROM country WHERE country_name LIKE %s", (country,)):
            tmp = self.impact_db_c.fetchone()[0]
            # print tmp, affiliation, "[" + self.find_nations(affiliation) + "]"
            if self.impact_db_c.execute("""INSERT INTO affiliation (aff_name, idcountry)
                               VALUES (%s, %s)""", (affiliation, tmp)):
                return self.impact_db_c.lastrowid
            else:
                return None
        else:
            if self.impact_db_c.execute("""INSERT INTO affiliation (aff_name)
                               VALUES (%s)""", (affiliation,)):
                return self.impact_db_c.lastrowid
            else:
                return None

    def _create_affiliation_entry(self, affiliation):
        affiliation = self.find_nations(affiliation)
        if self.impact_db_c.execute("SELECT idcountry FROM country WHERE country_name LIKE %s", (affiliation,)):
            tmp = self.impact_db_c.fetchone()[0]
            # print tmp, affiliation, "[" + self.find_nations(affiliation) + "]"
            if self.impact_db_c.execute("""INSERT INTO affiliation (aff_name, idcountry)
                               VALUES (%s, %s)""", (affiliation, tmp)):
                return self.impact_db_c.lastrowid
            else:
                return None
        else:
            if self.impact_db_c.execute("""INSERT INTO affiliation (aff_name)
                               VALUES (%s)""", (affiliation,)):
                return self.impact_db_c.lastrowid
            else:
                return None

    def create_affiliation(self, aff):
        """Create entry in affiliation table."""
        try:
            if not self.impact_db_c.execute("SELECT idaffiliation FROM affiliation WHERE aff_name LIKE %s", (aff,)):
                if self.for_aps:
                    return self._create_affiliation_entry_aps(aff)
                else:
                    return self._create_affiliation_entry(aff)
            else:
                return self.impact_db_c.fetchone()[0]
        except Exception:
            print("Error - faild to create affiliation entry")
            raise

    def create_auth_affiliation(self, author_id, affiliation_id):
        """Create entry in auth_affiliation table."""
        try:
            self.impact_db_c.execute("""INSERT INTO
                                   auth_affiliation (idauthor, idaffiliation)
                                   VALUES (%s, %s)""", (author_id, affiliation_id))
        except Exception:
            print("Error - faild to create rec_author entry")
            raise

    def insert_author(self, author_tag, recid, co_author):
        """Insert authors and affilaitions."""
        name = sorted(author_tag[0], key=lambda x: 1 if x[0] == 'a' else 2)[0][1]
        orcid = [x[1] for x in author_tag[0] if x[0] == "j"]
        if orcid:
            orcid = orcid[0]
        else:
            orcid = None
        # Inserting first author
        author_id = self.create_author(name, orcid, co_author)
        # Inserting join between author and record
        if author_id:
            self.create_rec_author(recid, author_id)

        affs = [x[1] for x in author_tag[0] if x[0] == "u"]
        if not affs:
            affs = [x[1] for x in author_tag[0] if x[0] == "v"]

        for aff in affs:
            affiliation_id = self.create_affiliation(aff)
            # Inserting join between author and affiliation
            if affiliation_id:
                self.create_auth_affiliation(author_id, affiliation_id)


def main(argv):
    for_aps = False

    try:
        for_aps = argv[0] == '--APS'
    except:
        from invenio.utils import NATIONS_DEFAULT_MAP
        print "No argument given. Running for non-APS papers"

    print("Importer starts")
    count = 0
    ic = ImportCreator(for_aps)

    if for_aps:
        ids = perform_request_search(p="773__p:Phys.Rev. 773__v:/d89|d90/")
    else:
        ids = perform_request_search(p="")
    print("Going to import %s records" % (len(ids),))

    for recid in ids:
        if not ic.impact_db_c.execute("SELECT idrecord FROM record WHERE idrecord=%s", (recid,)):
            rec = get_record(recid)
            j_name = sorted(rec['773'][0][0], key=lambda x: 1 if x[0] == 'p' else 2)[0][1]

            if for_aps:
                publ = "APS Phys.Rev.D"
            else:
                publ = sorted(rec['260'][0][0], key=lambda x: 1 if x[0] == 'b' else 2)[0][1]
            year = sorted(rec['773'][0][0], key=lambda x: 1 if x[0] == 'y' else 2)[0][1]
            # Inserting record
            try:
                ic.impact_db_c.execute("""INSERT INTO
                                       record (idrecord, journal_name, publisher, pub_year)
                                       VALUES (%s, %s, %s, %s)""", (recid, j_name, publ, year))
            except Exception as e:
                print("Error - faild to create record entry for recid %s" % (recid,))
                raise e
            if '100' in rec:
                for author in rec['100']:
                    ic.insert_author(author, recid, 0)
            if '700' in rec:
                for coauthor in rec['700']:
                    ic.insert_author(coauthor, recid, 1)
            ic.impact_db.commit()
        else:
            print("Record %s already in Impact DB" % (recid,))
        count += 1
        print("Done %s record out of %s with recid: %s" % (count, len(ids), recid))
    ic.impact_db.close()


if __name__ == "__main__":
    main(sys.argv[1:])

