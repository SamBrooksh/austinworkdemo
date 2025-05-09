
buildtables.sql is for the results being saved and the like
information.json is the various variables and the like (I could try putting it in a sql, but I think it is going to be simpler for others to modify if it's stored this way)
functions.config is to define the various functions as a string - the variables will reference user input with UPPERCASE and the name in information.json for the value from that
There will also be variables with constants that may change (like the 1.66)
So if you wanted cost with rebar size and estimated labor days for concrete foundation it would be 
concrete-foundation-cost: CONCRETE-FOUNDATION-ESTIMATED-LABOR * foundation-rebarsize


Going to be making a template for each of the "jobs" that each extend the base

Added some shell scripts for quick use during testing as well - remaking the tables and starting the server up

### Known Bugs
In the equations/functions the code does a test for x in y (with python) which returns true if there are variables that are just the partial of the function. Could change this, but for now ignoring it 