<h1>General discussion forum</h1>
A database project built with Flask and PostgreSQL. Deployed to <a href="http://general-forum.herokuapp.com/">Heroku</a>. In order to post messages or start threads, you need to log in. However you do not need to log in to observe and browse the contents of the site. You can access the login and register pages from every page within the site. These are located in the topside of every page, right below the header. The forum is divided into different discussion areas. Moderators can modify these areas (their rules and topics), remove them and add more of them. Moderators can modify and delete all messages and threads. Users can also delete and modify their own messages and threads. Deleting entries does not actually delete them, it just makes them <i>unlisted</i> so that the app knows not to present that data to anyone.<br>

The site is protected by SQL-injection, XSS and CSRF vulnerabilities. XSS is handled by Flask's own render_template, CSRF is handled by giving a session-based token in form of cookies and SQL-injection is handled with giving variables as parameters to SQL queries.

<br>
You can test the site by registering a new account or using one of these existing accounts:<br>

|username|password|admin|
|user    |user    |False|
|admin   |admin   |True |

<br>
You can test the moderator's features with the admin account.

<h2>Description and features</h2>

- User may register an account and log in to it
- Front page is divided into several different discussion areas, active threads are also shown here
- Moderators can create new areas or modify or delete existing ones
- Areas also show their own active threads and all threads are shown by age (newest first)
- Users may create threads and post replies into these threads
- Users can modify or delete their own messages and threads
- Moderators can modify or delete all messages and threads
- Moderators can delete all images
- Messages can include pictures
- The app only accepts png and jpg images, which are then compressed with Python's Pillow library and does not accept images if their size are over 300kb after compression
- Users can search for all profiles, threads and messages containing a certain string'
- A profile page exists for all users which shows the user's possible profile picture and its posted messages and threads.
- Users can change their profile pictures

<br>
<h2>Database schema</h2>
<img src="/documentation/database-schema.png">
<h2>The state of the app</h2>
The app is almost complete. All of the features I planned are created. At the moment there are no known bugs. The layout and GUI will get some changes in order to make the site more "pleasing" to use. 
