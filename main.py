import discord
import os
from discord.ext import commands
from discord import FFmpegPCMAudio
import asyncio
import random as rd
from keep_alive import keep_alive
from Ticketmachine import Ticketmachine

# Global
ROLENAME = 'Support Staff Member'
SUPPORT_TITLE = 'Support Text Channel'

# Client
intents = discord.Intents.all()
client = commands.Bot(command_prefix='/', intents=intents)

# Ticketmachine
ticketmachines = dict()  # (server_object : ticketmachine_object)


async def update_staff_members(server, ticketmachine):
	# Find the support staff role
	if ROLENAME in [role.name for role in server.roles]:
		role = [role for role in server.roles if role.name == ROLENAME][0]
	# Create new role if it does not exist
	else:
		role = await server.create_role(name=ROLENAME)
	for member in server.members:
		if role in member.roles:
			ticketmachine.add_staff(member)
		else:
			ticketmachine.delete_staff(member)

@client.event
async def on_ready():
	# Create staffmembers
	for server in client.guilds:
		ticketmachine = Ticketmachine()
		await update_staff_members(server, ticketmachine)
		# Create a ticketmachine
		ticketmachines[server] = ticketmachine
	# Ready
	print(f'{client.user} is ready.')

# Optional Welcome message
@client.event
async def on_member_join(member):
	await member.create_dm()
	await member.dm_channel.send( f'Hi alchemist {member.name}, welcome to the Covalent Discord server!')

# Create a ticket
@client.command(pass_context=True)
async def ticket(ctx):
    await ctx.message.delete()
    # Check if a request is already made
    ticket_in_queue = ticketmachines[ctx.guild].already_in_queue(ctx.author)
    await ctx.author.create_dm()
    if ticket_in_queue == None:
        # Create the ticket
        tn, queue = ticketmachines[ctx.guild].create_ticket(ctx.author)
        # Create embed
        embed = discord.Embed(
        title='Your ticket has been received',
        description=
        f'Hi {ctx.author.name}, you are in queue with ticketnumber {tn}. Please wait for the support staff to help.',
        colour=discord.Colour.blue()
        )
        embed.set_thumbnail( url= 'https://icohigh.net/uploads/posts/2021-04/thumbs/1618468617_covalent_logo.png')
        embed.add_field(name='Position in queue',
            value=f'Your current position is: {queue}.',
            inline=True)
        embed.add_field(
            name='Close ticket',
            value='To close your ticket type "/close" in the guild chat.',
            inline=False
        )
        await ctx.author.dm_channel.send(embed=embed)
        print(f'ticket created: {tn}')
    else:
        tn, queue = ticket_in_queue
        # Send a dm to the author
        await ctx.author.dm_channel.send(
            f'Hi {ctx.author.name}, you cannot make a new request since you are already in queue at position {queue} with ticketnumber {tn}. Please wait for the support staff to help.'
        )


# Close an open ticket
@client.command(pass_context=True)
async def close(ctx):
    await ctx.message.delete()
    ticket_in_queue = ticketmachines[ctx.guild].already_in_queue(ctx.author)
    if ticket_in_queue == None:
        msg = f'Hi {ctx.author.name}, you currently have no open tickets' 
    else:
        tn, queue = ticket_in_queue
        ticketmachines[ctx.guild].close_ticket(tn)
        msg = f'Hi {ctx.author.name}, your ticket request has been closed'
    await ctx.author.create_dm() 
    await ctx.author.dm_channel.send(msg) 
    print(f'ticket closed: {tn}')

@client.command(pass_context=True)
async def claim(ctx):
    await ctx.message.delete()
	# Check if staff member
    role = discord.utils.find(lambda r: r.name == ROLENAME, ctx.message.guild.roles)
    if role in ctx.author.roles:
        # Check if there are tickets in queue
        if ticketmachines[ctx.guild].isEmpty:
            await ctx.author.create_dm()
            await ctx.author.dm_channel.send('Currently no tickets available to claim')
            return
        await update_staff_members(ctx.guild, ticketmachines[ctx.guild])
        # Assign a ticket to a staff member
        values = ticketmachines[ctx.guild].handle_ticket(ctx.author)
        if values == None:
            print('Whaaaatttt?')
            return
        ticketnumber, user = values
        # Create a text channel which is only visible to the user and staff member
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True)
            }
        channel = await ctx.guild.create_text_channel('ticket-' + str(ticketnumber), overwrites=overwrites)
        # Create embed
        embed = discord.Embed(
            title='Support Text Channel',
            description=
            f'Welcome {user.mention}! Feel free to ask any questions to our staff member {ctx.author.mention}. You can ask your questions in this text channel.',
            colour=discord.Colour.blue())
        embed.set_image(url= 'https://www.koncert.com/hubfs/Images/Blog%20Images/ask-blackboard-chalk-board-356079.jpg')
        embed.set_thumbnail(url= 'https://icohigh.net/uploads/posts/2021-04/thumbs/1618468617_covalent_logo.png')
        embed.add_field(
            name='End conversition',
            value= 'Type "/end" to close the conversation. The conversation will be saved afterwards',
            inline=False)
        await channel.send(embed=embed)
        print(f'Ticket claimed: {ticketnumber}')

# End a ticket
@client.command(pass_context=True)
async def end(ctx):
    await ctx.message.delete()
    # Check if support channel
    if not 'ticket-' in ctx.channel.name : return
    ticketnumber = str(ctx.channel.name).replace('ticket-', '')
    if not ticketnumber.isnumeric(): return
    # Make a list of all the messages
    messages = []
    async for message in ctx.channel.history(limit=1000):
        if message.author.id == client.user.id: continue
        if '/end' in message.content: continue
        messages.insert(0, message)
    values = ticketmachines[ctx.guild].finish_ticket(int(ticketnumber), messages)
    if not values:
        await ctx.channel.send('This ticket does not exists or is not being handled. Cannot save the conversation.')
    else:
        user, staff = values
        await ctx.channel.send('Conversation is succesfully saved and the ticket has been closed. Any new messages will not be saved, for new questions type /ticket to get a new ticket. You can delete the channel if you are done.')
        print(f'ticket ended: {ticketnumber}')
        
async def valid(ctx, ticketnumber):
    # Check if it starts with a ticketnumber
    if not ticketnumber.isnumeric(): return False
    # Check if it may acces this ticket
    information = ticketmachines[ctx.guild].information_ticket(ticketnumber)
    if information == None: return False
    # Check if has access
    role = discord.utils.find(lambda r: r.name == ROLENAME, ctx.message.guild.roles)
    if not role in ctx.author.roles and information['userid'] != ctx.author: return False
    # All the information is correct
    return information # {user, staff, status, date, duration, questions}


# Get the full information of a ticket
@client.command(pass_context=True)
async def information(ctx, ticketnumber):
    # Check if it starts with a ticketnumber
    if not ticketnumber.isnumeric(): 
        await ctx.channel.send('Wrong input. Enter a numeric ticketnumber. Type /information ticketnumber')
        return
    # Check if it may acces this ticket
    information = ticketmachines[ctx.guild].information_ticket(int(ticketnumber))
    if information == None: 
        await ctx.channel.send('Wrong input. Enter a valid ticketnumber. Type /information ticketnumber')
        return
    # Check if has access
    role = discord.utils.find(lambda r: r.name == ROLENAME, ctx.message.guild.roles)
    if not role in ctx.author.roles and information['userid'] != ctx.author: 
        await ctx.channel.send('You don\'t have acces to this ticket.')
        return    
    # Send message with the information of the ticketnumber
    embed = discord.Embed(
        title=f'Information ticket {ticketnumber}',
        description= 'Here is an overview of the ticket.',
        colour=discord.Colour.blue())
    embed.set_thumbnail(url= 'https://icohigh.net/uploads/posts/2021-04/thumbs/1618468617_covalent_logo.png')
    # Make strings for the embed
    general_information = 'Userid: {}'.format(information['user'].mention)
    if information['staff'] != None:
        general_information += '\nStaffid: {}'.format(information['staff'].mention)
    general_information += '\nStatus: {}\nCreated: {}'.format(information['status'], information['date'].strftime("%d %B %Y at %H:%M"))
    if information['duration'] != None: 
        general_information += f'\nDuration: '
        seconds = int(information['duration'].total_seconds())
        minutes = seconds // 60 % 60
        hours = seconds // 3600 % 24
        days = seconds // 86400 
        if days > 0: 
            general_information += f'{days} days, {hours} hours and {minutes} minutes'
        elif hours > 0:
            general_information += f'{hours} hours and {minutes} minutes'
        else: general_information += f'{minutes} minutes and {seconds%60} seconds'

    embed.add_field(
        name='General information',
        value= general_information,
        inline=False)
    if information['status'] == 'Closed': 
        str_question = ''
        for message in information['questions']:
            str_question = str_question + message.author.name + ": " + message.content + '\n'
        embed.add_field(
            name='Conversation',
            value= str_question,
            inline=False)
    await ctx.channel.send(embed=embed)
    print(f'Information ticket: {ticketnumber}')


keep_alive()
client.run(os.environ['TOKEN'])
