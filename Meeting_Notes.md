##MITRE Notes  

# Jan 29
	- Everyone 
	- Went through attacks
	- Talked about patch options 
	- Assigned chips on the board 
	- Research ways to use them (by Monday)
	- Write some Psuedo-code
	- Continue with things from the previous Week
	- Reach out to eCTF team and ask about extra week (Erin)
	- Come up with a more complete timeline (checking with Profs etc.)
	- Networks prof meeting in ~2 weeks
	- Get Git Setup for those who don't
	- If you write code - post it in the group and ask for review

# Feb 1 
	- Sam, Erin, Victoria, Nick, Emily
	- TPM Keys Discussion (Victoria, Nick)
	- Flags location (Erin)
	- For Friday : Code and Patches (bring something to test)
	- Plan for Friday : Implement and test some patches
	- Get more exp actually running the device and things
	- Keep stuff on Git - allows us to keep tabs on progress
	- Have assigned goals and deadlines each week
	- Nick and Victoria - work on encripting server packets
	- Look at list, prioritize, assign tasks (Sam, Erin, Emily) Mon/Tues

# Feb 5  
	- Mark - RSA & Encription - working on merging w/Nick's stuff 
	- Prevent multiple packets @ once 
	- Kim - JSON, Protect packets - valid data
	- Went through Attacks/Patch doc, status
	- Ran BBB (Mark, Ben, Kim)  tested some of the code
	- For upcoming week - any YELLOW boxes should be tested / merged if posible 
	- Merge MITRE's code into our branch (done)
	- Figure out how to run with the new stuff (Kim)
	- Knowledge transfer (So we all know how to run the BBB, notes about best practices, debug stuff)

#Feb 9th
	-Nick and Victoria: pulling timestamps from BBB, network and formatting the dates 
	-if the timestamps match, then continue forward with connection 		
	-after working on this, we see the need for creating unit testing for our code because it's easy for         
	things to break and hard to pinpoint the source
	-once the timestamp code is working, Nick and Victoria will move forward with encrypting via the ECC   

#Feb 11
	- Victoria and Kim cleaned up timestamps stuff
	- Created unit tests for implementing   

#Feb 12 
	- Erin, Victoria, Nick, Mark, Ben, Kim
	- Review past week work 
	- Discussion about hardware / usage for encryption and signing 
	- Went through new priority list and re-assigned things/ T
	- Planned meeting for Tuesday 315pm  in Wireless
	- Asked to move Monday meeting w/Prof Potter 
	- Ben created Requirements & Tests Document 
	- We set a "System Finished" Deadline Feb17/18 
	- Testing deadline Feb19/20
	- Spend last half week (until 24th handoff) verifying and making sure we meet reqs
	- Week of handoff (2.24) Friday meeting will be focused on coming up with schedule/plan of attack
	- On that week - set a plan of action for the  on-campus visit and timing of that  

#Feb 19
	- Meeting over weekend to do some testing over the weekend in WC
	- Talked about *how* to hand it down 
	- Meeting on Monday 6pm
	- Should be able to do different testing in parallel
	- Handoff list is in the reqs - images, source codes, master PIN, docs
	- This week is about testing the system before handoff Wednesday
	- Monday - go through tests/req Document.  
	- Monday - clean up Branches!!!!  

#Feb 22 AM
	- Everyone 
	- Meeting with Potter, gave updates of last two weeks
	- Should be on track to complete everything before hand-off Wed
	- Sam should reach out about how to hand-off (HW/SW)
	- Meeting at 6pm for extensive testing further discussion
	- Suggested that if this was to be run again, that there should be an assigned "class time"
	- This is crunch time - going to have to work together as a team to get this to go smoothly

#Feb 22 PM
	- Everyone but Mark
	- Meeting in Wireless Club to do testing and go through requirements
	- Verified that tenant PIN can be changed, LED indicates door opened correctly
	- Figured out Master PIN had to be change-able and shouldn't be hard coded 
	- Ben worked on that functionality
	- Some of the team tried to test other things but struggled with the Keys because of their location being hardcoded
	in Mark's code
	- Assigned tasks for the rest of the week.  Decided to meet Tuesday afternoon. 
	- Branch clean moved to Tuesday 
	
#Feb 26
	- Team Name - Comic Sans Intelligence : CSI
	- Moving forward with Nick's stuff (possibly)
	- Short meeting

#Feb 29
	- Got another email from MITRE - things are broken 
	- Kim spent time this weekend - fixing things they said were broken
	- email them - debug in the meantimme
	- Due after Spring Break - paper - what we did for a project - what we did - what *I* did - Reflection (Midterm)
	- Schedule for next section?

#Mar 18
	- Nick reviewed what him and Kim did over break
	- They rewrote a ton of things because our widgets didn't stay saved when the device was powered down
	- Mark will crate new image and submit 
	- Victoria will send email to communicate how much we actually worked
	- Reflected on the first half
	- Got people up to speed with running the system so they can be more useful
	- Coming up with plan 
	- Bought new CC/Keypad - will use BBB from Erin 
	##Priorities 
		- BBB Training Session (tools & understanding)
		- Two Subgroups (another meeting time agreed upon)
		- Regroup on Fridays (discuss and merge)
		- Throughout all - Maintain Communication - Github Issues for Technical Issues 
	- Monday - Skype meeting w/Potter - Erin has WVA Room 
	
#Mar 21 AM
	- Morning: Skype meeting with Prof Potter
	- Everyone but Emily & Sam
	- We chatted with Prof Potter about notes on first half
	- Biggest problem was with communication - we can fix this
	- Moving forward - start meetings with "what can we do better"
	- By tonight (3/21) split up groups for two separate teams
	- Continue to meet Fridays/Mondays, this extra time will be used to get work done
	- Using GitHub Issues moving forward
	- Also discussed the work done by Nick, Kim to get system in to MITRE
	- Basically just waiting for MITRE to send us another system (And confirm ours is fixed)
	
#Mar 21 PM
	- Evening: Organizational meeting
	- Everyone but Sam & Mark
	- Formed 2 subteams with approx times:
		- Monday 6-9pm: Erin, Nick, Kim, Sam
		- Thursday 6-9pm: Victoria, Emily, Mark, Ben
	- Beaglebone training Thursday during meeting - in WVA
	- Github Issues training Friday during meeting?
	- Divided some of the attacks we've come up with (see brainstorm sesh doc)
	- Most issues will need to be found only once we have the opposing team's setup

#Mar 24 PM 
	- BBB training 
	- Notes on Drive
	- Have three BBB, one is missing the Mini-USB connector on the bd

#Mar 25
	- Got system (and we made it to the attack phase!!!!!!!!)
	- Git Issues - for Code/project problems
	- Code problems that need to be fixed or Project 
	- Opened example Issue on Git 
	- Expectations : 
		- Preferred Communication Platform - (is it not fb? what is it?)
		- Be responsive on ^^ 
		- Take this as a learning and teaching opportunity 
		- Don't be afraid to ask the questions if you don't know
		- Be actively involved 
		- Be respectful of people's time (be on time - communicate)
	- Reminder of approx times:
		- Monday 6-9pm: Erin, Nick, Kim, Sam
		- Thursday 6-9pm: Victoria, Emily, Mark, Ben
	- For Monday AM : Look at system(s) and open issues, incl research on attacks (general, specific to the system)

#Apr 1
	- Sent email to MITRE about on campus (tentatively next Fri)
	- Emily Skyped in 
	- Got Master Password from System 2
	- We should be able to read the packet?
	- Make image where we know txt file (Sys2)
	- Sent email to register the widget for sys2
	- Mark "This is going to be so easy"
	- Each group will come up with a write-up during next week's meetings
	- Got some good thoughts and good ideas for both systems
	- Waiting for registration requests to be approved
	- Still can't get the system 1 to flash

#Apr 8 
	- 3 write-ups allowed (no more than 2 pages)
	- got two widgets - giving back one
	- tried to get cloning but they hadn't changed the flag

#Apr 11
	- Prof Potter will proofread stuff 
	- headed into the final week 
	- meeting later

#Apr 11 PM
	- Finished first two writeups
	- Sent off to Prof Potter for proofreading
	- decided on timestamp for 3rd write up
	