# CovalenSupportBot
A ticketmachine for a covalent support bot

The code is also available at https://replit.com/@KishanHartog/CovalentBot#main.py
In order for it to work a Discord bot token needs to be created and added as a environment variable with the name TOKEN

This code is run on replit.com to run it continuously. 
To keep it alive a UptimeRobot link is created that pings it every five minutes. 

The bot can be run with four commands:
/ticket
  This creates a ticket.
  
/close
  This closes a ticket which is not claimed yet.
  
/claim
  This is for a support staff member to claim tickets.
  The staff member need to have the roll 'Support Staff Member' which is created when the bot joins the server.
  The command creates a private text channel with the staff member and the persons who created the ticket.
  
/end
  This end a claimed ticket. 
  It sends a message in the created text channel and the conversation is saved.
  Any new messages in the text channel will NOT be saved

/information ticketnumber
  This gives all the information of a ticket with a given ticketnumber


