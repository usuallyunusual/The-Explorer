
HOW TO UTILIZE THESE SCRIPTS TO IMPORT DATA FROM XML FILE


1. Drop database from xampp dashboard (If exists)
2. Create a new database with the name "explorer_db"
3. Run "make_db.py" in preferred console/terminal or IDE 
    (No output will be shown except connection successful)
4. Make sure the "explorer_db.xml" file is in the same directory / folder as script "make_db_xml.py"
5. Run "make_db_xml.py" in preferred console/terminal or IDE.
    Note: This will take a lot of time but is a considerable improvement over other methods
    NOTE : Do not quit midway, or you will have to repeat the whole process.

6. To verify (Sort-of, bcs you cant really verify so much data easily):
    6.1 Go to xampp dashboard --> explorer_db -->SQL
    6.2 Execute command
        "SELECT COUNT(*) FROM event"
        Return value should be : 113942
    6.3 Execute command
        "SELECT COUNT(*) FROM links"
        Return value should be : 206151
    6.4 The "genre" table has to have 9 records

Congratulations. Phew