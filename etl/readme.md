# ETL

Contains source code for performing the ETL processes required to populate the data for the service to use.

1. db package has the SQL scripts to make the database
2. Transforms have the core business logic in it. This makes the project engine agnostic.
3. Driver package has the scripts that co-ordinates all the jobs and calls the transformations. Basically handles the
   DAG.
4. Lookup is just a bunch of useful data used in the transformations.