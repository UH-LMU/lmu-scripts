import sys, subprocess, os, os.path

#
# Modified from:
# http://stackoverflow.com/questions/17123550/extract-and-sort-data-from-mdb-file-using-mdbtools-in-python
#

def mdb_export(database,dir_out):
    subprocess.call(["mdb-schema", database, "mysql"])

    # Get the list of table names with "mdb-tables"
    table_names = subprocess.Popen(["mdb-tables", "-1", database],
                                   stdout=subprocess.PIPE).communicate()[0]
    tables = table_names.splitlines()

    print "BEGIN;" # start a transaction, speeds things up when importing
    #sys.stdout.flush()

    # Dump each table as a CSV file using "mdb-export",
    # converting " " in table names to "_" for the CSV filenames.
    for table in tables:
        if table != '':
            filename = os.path.join(dir_out,table.replace(" ","_") + ".csv")
            file = open(filename, 'w')
            print("Dumping " + table)
            contents = subprocess.Popen(["mdb-export", database, table],
                                        stdout=subprocess.PIPE).communicate()[0]
            file.write(contents)
            file.close()


if __name__=='__main__':

    database = sys.argv[1]
    dir_out = "/tmp"
    if len(sys.argv) > 1:
        dir_out = sys.argv[2]

    mdb_export(database,dir_out)
