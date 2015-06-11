—Table definitions for the tournament project.

—3 tables to get the tournament application to work have been created. These are:
—Players, Matches and Playerstandings. 

DROP DATABASE if exists tournament;
CREATE DATABASE tournament;
\c tournament

CREATE TABLE players (
playerID SERIAL PRIMARY KEY,
playername VARCHAR(100));

CREATE TABLE matches(
matchID SERIAL PRIMARY KEY,
winnerID INTEGER,
loserID INTEGER);

CREATE TABLE playerstandings(
playerID INTEGER references players(playerid),
playername VARCHAR(100),
wins INTEGER,
matches INTEGER);