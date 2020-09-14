




"""
TO DO:
1) CHANGE THE END OF THE SCRIPT MESSAGE
2) MORE COMMENTS!!

"""














import mysql
from mysql.connector import Error

def rank():
    try:
        conn = mysql.connector.connect(host='127.0.0.1',port = 3307,database='explorer_db',user='root',password = '')
        if conn.is_connected():
            print("Connection successful: ",conn.get_server_info())
        cur = conn.cursor()

        # Find the ids that send out page rank - we only are interested
        # in event in the SCC that have in and out links
        cur.execute('''SELECT DISTINCT from_id FROM links''')
        from_ids = list()
        for row in cur: 
            from_ids.append(row[0])

        # Find the ids that receive page rank 
        to_ids = list()
        links = list()
        cur.execute('''SELECT DISTINCT from_id, to_id FROM links''')
        for row in cur:
            from_id = row[0]
            to_id = row[1]
            if from_id == to_id : continue
            if from_id not in from_ids : continue
            if to_id not in from_ids : continue
            links.append(row)
            if to_id not in to_ids : to_ids.append(to_id)

        # Get latest page ranks for strongly connected component
        prev_ranks = dict()
        for node in from_ids:
            cur.execute('''SELECT new_rank FROM event WHERE event_key = %s''', (node, ))
            row = cur.fetchone()
            prev_ranks[node] = row[0]

        sval = input('How many iterations:')
        many = 1
        if ( len(sval) > 0 ) : many = int(sval)

        # Sanity check
        if len(prev_ranks) < 1 : 
            print("Nothing to page rank.  Check data.")
            quit()

        # Lets do Page Rank in memory so it is really fast
        for i in range(many):
            # print prev_ranks.items()[:5]
            next_ranks = dict();
            total = 0.0
            for (node, old_rank) in list(prev_ranks.items()):
                total = total + old_rank
                next_ranks[node] = 0.0
            # print total

            # Find the number of outbound links and sent the page rank down each
            for (node, old_rank) in list(prev_ranks.items()):
                # print node, old_rank
                give_ids = list()
                for (from_id, to_id) in links:
                    if from_id != node : continue
                   #  print '   ',from_id,to_id

                    if to_id not in to_ids: continue
                    give_ids.append(to_id)
                if ( len(give_ids) < 1 ) : continue
                amount = old_rank / len(give_ids)
                # print node, old_rank,amount, give_ids
            
                for id in give_ids:
                    next_ranks[id] = next_ranks[id] + amount
            
            newtot = 0
            for (node, next_rank) in list(next_ranks.items()):
                newtot = newtot + next_rank
            evap = (total - newtot) / len(next_ranks)

            # print newtot, evap
            for node in next_ranks:
                next_ranks[node] = next_ranks[node] + evap

            newtot = 0
            for (node, next_rank) in list(next_ranks.items()):
                newtot = newtot + next_rank

            # Compute the per-page average change from old rank to new rank
            # As indication of convergence of the algorithm
            totdiff = 0
            for (node, old_rank) in list(prev_ranks.items()):
                new_rank = next_ranks[node]
                diff = abs(old_rank-new_rank)
                totdiff = totdiff + diff

            avediff = totdiff / len(prev_ranks)
            print(i+1, avediff)

            # rotate
            prev_ranks = next_ranks

        # Put the final ranks back into the database
        print(list(next_ranks.items())[:5])
        cur.execute('''UPDATE event SET old_rank=new_rank''')
        for (id, new_rank) in list(next_ranks.items()) :
            cur.execute('''UPDATE event SET new_rank=%s WHERE event_key=%s''', (new_rank, id))
        conn.commit()
        cur.close()
        print("Script successful")
    except Error as e:
        print("Error while connecting to MySQL", e)

