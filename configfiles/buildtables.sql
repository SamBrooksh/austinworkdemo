/* Need to create the database here as well
*/

CREATE TABLE IF NOT EXISTS client (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    email TEXT
);
/*
Need to add all the other possible client details
*/

CREATE TABLE IF NOT EXISTS stage (
    id INTEGER PRIMARY KEY ASC,
    name TEXT
);

/* May not be JSON...
* For now assuming that the details json will hold the functions used and the like
* Not the most efficient way to store everything... Searching through when it gets huge will be incredibly slow
* Should probably have a job table that has a possible id for all the different jobs - and track a one to many for each and so on
* But for this first demo this should be enough
*/
CREATE TABLE IF NOT EXISTS clientrequests (
    id INTEGER PRIMARY KEY ASC,
    details TEXT,
    stage INTEGER NOT NULL,
    client INTEGER NOT NULL, 
    receipt TEXT,
    FOREIGN KEY(client) references client(id),
    FOREIGN KEY(stage) references stage(id)
);
/* I'm assuming that receipt will be the paid for amount - I don't know what is needed for bookkeeping here 
- Should probably make this assign specific values - like starting at 1*/
INSERT INTO stage(id, name) VALUES (1, 'RECEIVED_REQUEST'), (2, 'ACCEPTED'), 
 (3, 'IN_PROGRESS'), (4, 'COMPLETED'), (5, 'PAIDDONE');
