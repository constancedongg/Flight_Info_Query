# Flight Information Query System

##
##
##
#### Description
There are 5 navigation tabs on our web page, and we basically cover all the functions we mentioned at Part 1. 

Historical Queries (Returned Users) tab is for returned users to get their historical requests on the website which uses the simulated data to demonstrate the many-to-many relationship on our ER diagram. Flight Information tab is for new users to search historical flight information by inputting departure airport, arrival airport, date and sorting preference. Recommendation tab provides airline recommendations according to flight routes and date. The last Interesting Facts tab incorporates the SQL queries for Part 2. Therefore, we covered all functions.

One thing to mention is that we intend to cover all flights information through the year 2018. But due to the large data set (over 500,000 records for Jan. 2018), we just demonstrate our web application uses the data of Jan. 2018, but it won't affect the functionality of our application. 

#### Interesting operations
1.  Flight Information
    It is in "Flight Information" Tab. This function provides the search function. Users can input departure airport, arrival airport, select date and sorting preferences, and then they will get historical flight information in this sorting order. E.g. If we input 'JFK' in "From", 'ATL' in "To", '01-10-2018' in "Date", and 'Fastest' in "Sort results by:", we will get all flight information from 'JFK' to 'ATL' on Jan. 1, 2018 with the fatest flights (shortest flying duation) at the first place. If we input 'JFK' in "From", 'EWR' in "To", '01-10-2018' in "Date", and 'Default' in "Sort results by:", we will be redirected to "No results!" page since no flight flying from JFK to EWR. 
2. Recommend
    It is in "Recommendation" Tab. This function provides the recommendation function. Users can input departure airport, arrival airport and date. We will return Top 10 airlines by their final scores sorting from highest to lowest. The final scores of airlines use 3 criteria, which are: 1. Shortest average delay 2. Highest manager ratio (no. of managers/no.of employees) 3. Shortest average durations. By combining the ranks of these 3 criteria, the airline with smallest rank (highest rank) will appear at the first place.
    utorial/java/concepts/interface.html).

 
