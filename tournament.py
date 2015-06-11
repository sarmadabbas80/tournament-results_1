#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE matches;")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE players;")
    conn.commit()
    cursor.execute("TRUNCATE playerstandings;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) as count from players;")
    result = cursor.fetchone()
    numberofrows = result[0]
    conn.close()
    return numberofrows


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT into players(playername) values (%s)", (name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""INSERT into playerstandings(playerid,playername)
                  (SELECT p.playerID, p.playername from players p
                  GROUP BY p.playerid,p.playername);""")
    conn.commit()
    cursor.execute("""UPDATE playerstandings SET wins = (SELECT count(winnerID)
                    from matches
                    where matches.winnerID  = playerstandings.playerid);""")
    conn.commit()
    cursor.execute("""UPDATE playerstandings SET matches = (SELECT count(matchID)
                    from matches
                    where matches.winnerID  = playerstandings.playerid
                    or matches.loserID  = playerstandings.playerid);""")
    conn.commit()
    cursor.execute("SELECT * from playerstandings order by wins desc;")
    result = cursor.fetchall()
    standings = result
    conn.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""INSERT into matches(winnerID, loserID)
                   values (%s,%s)""", (winner, loser))
    cursor.execute("""UPDATE playerstandings SET wins = (SELECT count(winnerID)
                from matches
                where matches.winnerID  = playerstandings.playerid);""")
    conn.commit()
    cursor.execute("""UPDATE playerstandings SET matches = (SELECT count(matchID)
                    from matches
                    where matches.winnerID  = playerstandings.playerid
                    or matches.loserID  = playerstandings.playerid);""")
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    cursor = conn.cursor()
    results = []
    cursor.execute("""SELECT playerid, playername from playerstandings
                    order by wins;""")
    results = cursor.fetchall()
    final_pairings = []
    for i in range(0, len(results), 2):
        player1_id = results[i][0]
        player1_name = results[i][1]
        player2_id = results[i + 1][0]
        player2_name = results[i + 1][1]
        pairing = (player1_id, player1_name, player2_id, player2_name)
        final_pairings.append(pairing)
    conn.close()
    return final_pairings
