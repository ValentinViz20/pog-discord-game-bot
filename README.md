# New Discord Game Bot
A huge discord game bot project I did long ago, but I abandoned. 

## Info
Back in September 2022, I started working on this new discord game that I was
thinking about for a few months, however turns out that game development is 
not all about writing code, that's the easy part, this also requires lots of good 
ides and thinking, especially how you are going to balance certain aspects of the
game, for example the hunt command, you have many enemies, weapons, armors, etc, all
of which require their own stats to be correctly balanced. Besides this the game
also needs tons of sprites for the equipment, and these take time making.

## Why I abandoned the project?
- The main reason was lack of time, I thought that in about one month I will be able to make
something I cal release for people, however I started adding way too many features that delayed
the release.
- Too big complexity: I started adding too many features, some of which were way too difficult to
to implement, I should have made a smaller game first, and then add the complicated stuff
- The need of art: The game has many items, and all of them need an emoji in discord, making
them is pretty difficult and time-consuming, I ended up spending days just creating the emojis
for a new zone.
- Lack of motivation: Working daily 10h on the project quickly make me dislike it, and start
to work on other projects I didn't give much attention to.

## What could I have done better?
- Use an async database driver (right now all databases calls stop the whole bot from working)
- Better project structure, now all the commands are in one file, all the resources in another file and so on
- To use Git, I realized too late how valuable this would have been
- To not add so much complexity to the game, I should have released something smaller and then work towards my goals.

## Features

> Each feature goes very in-depth, this is just a list of commands. 

**Progress:**  
[ `mine` ] - mine for resources using your pickaxe  
[ `seek` ] - seek enemies to kill and obtain loot and xp  
[ `battle` ] - battle strong enemies for better rewards  
[ `progress` ] - advance to higher zones  

**Help:**  
[ `help [anything]` ] - Check help about anything in the game  
[ `recipes` ] - shows all recipes in the game  

**Commands:**  
[ `profile` ] - shows your profile  
[ `inventory` ] - displays your current items  
[ `house` ] - shows your current home and crafting stations  
[ `traits` ] - view and assigin your trait points  
[ `crates` ] - view info about the available crates  
[ `build` ] - make a house and crafting stations  
[ `explore` ] - explore the zone you are in  
[ `craft` ] - craft armors and tools  
[ `heal` ] - heal yourself after fights  
[ `use` ] - use an item  

**Small guide:**
- `mine` to get resources  
- `seek` enemies to kill and use Fruit found in mine to   
- gather resources and craft better pickaxes and armors  
- smelt bricks, leather or pies into your furnace  