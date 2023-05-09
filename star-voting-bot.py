import discord
from discord.ext import commands

#from discord_interactions import create_interaction

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

messages = []

@bot.command()
async def rankedchoice(ctx):
    #print("starvote")
    """
    Starts a Ranked Choice voting session. Usage: /rankedchoice "Option 1" "Option 2" "Option 3"
    """
    options = ctx.message.content.split('"')[1::2] # extract the options from the command
    if len(options) < 2:
        await ctx.send("You must provide at least two options to vote on.")
        return
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

    question = await ctx.send(f"Score each choice from 1 to 5. Only score choices that you actually want and leave ones you don't blank. Please only score each choice at most once.")
    for option in options:
        message = await ctx.send(option)

        # add reactions to the message
        
        for emoji in emojis:
            await message.add_reaction(emoji)

        # edit the message to include its ID
        #await message.edit(content=f"{message.content}\nMessageID: {message.id}" )
        messages.append(message)
    
    message_ids = " ".join([str(message.id) for message in messages])
    await question.edit(content=f"{question.content}\nTo end voting use the following command:\n/results \"{message_ids}\"" )
        

@bot.command()
async def results(ctx, message_ids):
    message_ids = message_ids.split(" ")
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    tallies = []
    total_votes = []
    options = []
    # Loop through each message ID and tally the reactions
    for message_id in message_ids:
        #print(message_id)
        # get the message object from the message id
        message = await ctx.fetch_message(message_id)
        options.append(message.content)
        total_reactions = 0
        for reaction in message.reactions:
            async for user in reaction.users():
                if not user.bot:
                    total_reactions += 1
        total_votes.append(total_reactions)
        # create a dictionary to store the tally of each reaction for this option
        tally = {}

        # loop through each reaction and update the tally dictionary
        for reaction in message.reactions:
            # get the emoji string for the reaction (e.g. ":thumbsup:")
            emoji = reaction.emoji

            # check if the emoji string is already in the tally dictionary
            if emoji in tally:
                # if it is, increment the count for that emoji
                tally[emoji] += (emojis.index(emoji) + 1) * reaction.count#plus one for base 0 index
            else:
                # if it's not, add the emoji string to the dictionary and set the count to the current reaction count
                tally[emoji] = (emojis.index(emoji) + 1) * reaction.count

        tallies.append(tally)

    # calculate the total score for each option and determine the winner
    scores = {}
    for option_index, tally in enumerate(tallies):
        total_score = 0
        for emoji, count in tally.items():
            total_score += count
        scores[option_index] = total_score - 15

    winner_index = max(scores, key=scores.get)
    winner_score = scores[winner_index]

    # send a message with the tally results and the winner
    result = "Results for message IDs " + ", ".join(message_ids) + ":\n"
    for option_index, tally in enumerate(tallies):
        result += f"\n{options[option_index]}:\n"
        #print(result)
        # for emoji, count in tally.items():
        #     result += str(count) + " " + str(emoji) + "\n"
        #     #print(result)
        result += f"Score: {scores[option_index]}\n"
        #print(result)

    max_value = max(scores.values())
    tied_options =  [key for key, value in scores.items() if value == max_value]
    if len(tied_options) < 2:
        result += f"The winner is \"{options[winner_index]}\" with a total score of {winner_score}"
        #print(result)
        await ctx.send(result)
    else:
        tied_options_array = [f"{options[i]}" for i in tied_options]
        join = ', '.join(tied_options_array)
        result += f"There is a tie between the following options: {join}\nDoing a Runoff"
        total_votes_of_tie = [total_votes[i] for i in tied_options]

        max_index = tied_options[total_votes_of_tie.index(max(total_votes_of_tie))]

        #print(max_index)
        result += f"\nWinner is \"{options[max_index]}\""
        #result += f"{','.join(str(v) for v in total_votes_of_tie)}"
        await ctx.send(result)
        

# # Create an interaction from the command
# interactionRankedChoice = create_interaction(rankedchoice)
# interactionResults = create_interaction(results)
# # Print the generated schema
# print(interactionRankedChoice.to_dict())
# print(interactionResults.to_dict())

bot.run('PLACEHOLDER')
