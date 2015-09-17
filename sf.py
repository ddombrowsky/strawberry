#!/usr/bin/python
#
# see the README.txt file for
# description of the excercise
#
# $Id: sf.py,v 1.28 2010-07-22 00:53:29 davek Exp $

# usage:
# $ cat rectangles.txt | ./sf.py
#
# To see details, set debug_print to True (in the 
# source code) and run
# $ cat rectangles.txt | ./sf.py > rectangles.out

import sys,re,random;

debug_print=False;
MAX_COMBINES=1024;

class InputReader:
	def __init__(self):
		self.ar_data = [];
		self.ar_max_greenhouses = [];

	def readInput(self):
		num=0;
		grid = [];
		def procgrid(max,num,grid):
			if(debug_print): print "max greenhouses:",max,", grid #",num;
			if(len(grid)>0):
				self.ar_data.append(grid);
				if(debug_print): print "\n".join(grid);
				num+=1;
			return num;

		state=0;
		got_eof=False;
		while(not got_eof):
			if(state==0):
				print "Input max # of greenhouses: ",;

			r=sys.stdin.readline();
			if(len(r)==0):
				got_eof=True;
				continue;

			r=r.rstrip(); # remove newline
			if(len(r)>0): # skip blank lines
				rm=re.match('[0-9]+',r);
				if(rm is None):
					if(state==0):
						print "invalid number";
						continue;
					# load data lines into an array
					grid.append(r);
				else:
					if(state==1):
						# got a new number before a blank
						# line.  Handled by resetting the state
						state=0;
						num=procgrid(
							self.ar_max_greenhouses[len(self.ar_max_greenhouses)-1],
							num,
							grid
						);
						grid=[];

					r=int(r);

					# only limited #s are allows
					if(not ((r>=1) and (r<=10))):
						print "number out of range:",r;
						continue;

					# store the max # of greenhouses
					self.ar_max_greenhouses.append(r);
					state=1;
			else:
				# blank line will reset to initial state
				state=0;
				num=procgrid(
					self.ar_max_greenhouses[len(self.ar_max_greenhouses)-1],
					num,
					grid
				);
				grid=[];

		# if we get EOF before a blank line, don't forget the last grid
		if(state==1):
			procgrid(
				self.ar_max_greenhouses[len(self.ar_max_greenhouses)-1],
				num,
				grid
			);

		return (self.ar_max_greenhouses,self.ar_data);

class ParkSquare:
	'''
		represents a cell in the grid
	'''
	def __init__(self):
		self.occ_list = [];

	def append(self,n):
		self.occ_list.append(n);

	def empty(self):
		return (len(self.occ_list)==0);

	def toString(self):
		'''
			print "." on empty, the value on single, and "X" on multiple
		'''
		if(self.empty()):
			return " . ";
		elif(len(self.occ_list)==1):
			return "{0:3}".format(self.occ_list[0]);
		else:
			return " X ";

class Park:
	'''
		represents a park
	'''
	def __init__(self,rows,cols):
		self.rows = rows;
		self.cols = cols;
		self.grid=[];
		for i in range(rows):
			self.grid.append([]);
			for j in range(cols):
				self.grid[i].append(ParkSquare());

	def copyFrom(self,other_park):
		# NOTE: this object must have been created with the 
		# same size parameters.
		for i in range(len(other_park.grid)):
			for j in range(len(other_park.grid[i])):
				self.grid[i][j].occ_list.extend(other_park.grid[i][j].occ_list);


	def display(self):
		'''
			print the contents of the park
		'''
		for i in range(len(self.grid)):
			for j in range(len(self.grid[i])):
				# print without trailing space...
				sys.stdout.write(self.grid[i][j].toString());
			print;

	def getHouseCoors(self,hname):
		'''
			return a set containing the house
			coordinates in the format
			(top,left,bottom,right)
		'''
		top=len(self.grid);
		left=len(self.grid[0]);
		bottom=0;
		right=0;
		i=0;
		for row in self.grid:
			j=0;
			for cell in row:
				if(
					(not cell.empty()) and 
					(cell.occ_list[0]==hname)
				):
					if(i<top): top=i;
					if(i>bottom): bottom=i;
					if(j<left): left=j;
					if(j>right): right=j;
				j+=1;
			i+=1;
		return (top,left,bottom,right);

	def randomizeComboList(self):
		'''
			generate a shuffled list of all 
			combinations of 2 greenhouses
		'''
		houses=self.allHouseNames();

		# generate list of all combinations of two houses
		combolist=[];

		# if we only have one house, then 
		# return an illogical answer and the
		# processing loop will exit.
		if(len(houses)==1):
			combolist.append((houses[0],houses[0]));
		else:
			for a in houses:
				for b in houses:
					if(a!=b): combolist.append((a,b));

			# shuffle the list
			for i in range(10000):
				n1=random.randint(0,len(combolist)-1);
				n2=random.randint(0,len(combolist)-1);
				a = combolist[n1];
				combolist[n1] = combolist[n2];
				combolist[n2] = a;

		return combolist;

	def deleteHouse(self,hname):
		'''
			remove a house from the park
		'''
		for i in range(len(self.grid)):
			for j in range(len(self.grid[i])): 
				if(len(self.grid[i][j].occ_list)>0):
					if(self.grid[i][j].occ_list.count(hname)>0):
						self.grid[i][j].occ_list.remove(hname);

	def allHouseNames(self):
		res=dict();
		for i in range(len(self.grid)):
			for j in range(len(self.grid[i])):
				for r in self.grid[i][j].occ_list:
					res[r]=1;
		return res.keys();

	def totalScore(self):
		names=self.allHouseNames();
		score=0;
		for n in names:
			score+=10; # 10 points per house
			(t,l,b,r) = self.getHouseCoors(n);
			# plus 1 per covered square
			height=(b-t)+1;
			width=(r-l)+1;
			score+=(height*width);
		return score;

	def splitAndRemove(self,hname,split_type,con_corner):
		'''
			remove house <hname> where it conflicts 
			with any other house, and split the
			remainder into two new houses based
			on the <split_type> parameter.
			<con_corner> determines the conflicting corner:
			1 = bottom-right corner
			2 = top-right corner
			3 = bottom-left corner
			4 = top-left corner

		'''
		sname=[];
		sname.append(hname+"a");
		sname.append(hname+"b");
		(cur_t,cur_l,cur_b,cur_r)=self.getHouseCoors(hname);
		conf_t=cur_b;
		conf_l=cur_r;
		conf_b=cur_t;
		conf_r=cur_l;
		for i in range(cur_t,cur_b+1):
			for j in range(cur_l,cur_r+1):
				self.grid[i][j].occ_list.remove(hname);
				if(len(self.grid[i][j].occ_list)>0):
					# store the conflicting coordinates
					if(i<conf_t): conf_t=i;
					if(j<conf_l): conf_l=j;
					if(i>conf_b): conf_b=i;
					if(j>conf_r): conf_r=j;

		if(debug_print): print "conflict",(conf_t,conf_l,conf_b,conf_r);

		# for empty blocks previously occupied
		# by the conflicting house, place one
		# of two new houses based on the split type
		# and the conflicting corner
		new_t=[2,(0,0)];
		new_l=[2,(0,0)];
		new_b=[2,(0,0)];
		new_r=[2,(0,0)];
		if(con_corner==1):
			# 1 = bottom-right corner
			if(split_type==1):
				new_t[0]=cur_t; 
				new_l[0]=cur_l;
				new_b[0]=conf_t-1;
				new_r[0]=cur_r;
				new_t[1]=conf_t;
				new_l[1]=cur_l;
				new_b[1]=cur_b;
				new_r[1]=conf_l-1;
			else:
				new_t[0]=cur_t; 
				new_l[0]=cur_l;
				new_b[0]=cur_b;
				new_r[0]=conf_l-1;
				new_t[1]=cur_t;
				new_l[1]=conf_l;
				new_b[1]=conf_t-1;
				new_r[1]=cur_r;
		elif(con_corner==2):
			# 2 = top-right corner
			if(split_type==1):
				new_t[0]=cur_t; 
				new_l[0]=cur_l;
				new_b[0]=conf_b;
				new_r[0]=conf_l-1;
				new_t[1]=conf_b+1;
				new_l[1]=cur_l;
				new_b[1]=cur_b;
				new_r[1]=cur_r;
			else:
				new_t[0]=cur_t; 
				new_l[0]=cur_l;
				new_b[0]=cur_b;
				new_r[0]=conf_l-1;
				new_t[1]=conf_b+1;
				new_l[1]=conf_l;
				new_b[1]=cur_b;
				new_r[1]=cur_l;
		elif(con_corner==3):
			# 3 = bottom-left corner
			if(split_type==1):
				new_t[0]=cur_t; 
				new_l[0]=cur_l;
				new_b[0]=conf_t-1;
				new_r[0]=cur_r;
				new_t[1]=conf_t;
				new_l[1]=conf_r+1;
				new_b[1]=cur_b;
				new_r[1]=cur_r;
			else:
				new_t[0]=cur_t; 
				new_l[0]=cur_l;
				new_b[0]=conf_t-1;
				new_r[0]=cur_r;
				new_t[1]=conf_t;
				new_l[1]=conf_r+1;
				new_b[1]=cur_b;
				new_r[1]=cur_r;
		elif(con_corner==4):
			# 4 = top-left corner
			if(split_type==1):
				new_t[0]=conf_t;
				new_l[0]=conf_r+1;
				new_b[0]=conf_b;
				new_r[0]=cur_r;
				new_t[1]=conf_b+1;
				new_l[1]=cur_l;
				new_b[1]=cur_b;
				new_r[1]=cur_r;
			else:
				new_t[0]=cur_t;
				new_l[0]=conf_r+1;
				new_b[0]=cur_b;
				new_r[0]=cur_r;
				new_t[1]=conf_b+1;
				new_l[1]=cur_l;
				new_b[1]=cur_b;
				new_r[1]=conf_r;
		else:
			print "invalid corner";
			sys.exit(-1);


		# finally, create the two new houses
		for n in range(2):
			for i in range(new_t[n],new_b[n]+1):
				for j in range(new_l[n],new_r[n]+1):
					if(len(self.grid[i][j].occ_list)>0):
						sys.stderr.write("ERROR: attempting to add conflict\n");
						sys.exit(-1);
					self.grid[i][j].occ_list.append(sname[n]);




	def combineAndReduce(self,gh1,gh2):
		'''
			combine two greenhouses together, and
			subtract the overlap from the remaining
			greenhouses.  The result is a list
			containing 1 item if no splits were
			required, and >1 item if there were.
		'''
		# NOTE: this function returns a new park
		# and does not affect itself
		res=Park(self.rows,self.cols);
		res.copyFrom(self);

		# find the maximum area top-left,bottom-right 
		# coordinates from the greenhouse numbers given
		top=len(self.grid);
		left=len(self.grid[0]);
		bottom=0;
		right=0;
		i=0;
		for row in res.grid:
			j=0;
			for cell in row:
				if(
					(not cell.empty()) and (
						(cell.occ_list[0]==gh1) or
						(cell.occ_list[0]==gh2)
					)
				):
					if(i<top): top=i;
					if(i>bottom): bottom=i;
					if(j<left): left=j;
					if(j>right): right=j;
				j+=1;
			i+=1;

		if(debug_print): print gh1,"+",gh2,"=",top,left,bottom,right;

		# the new greenhouse is named <gh1>_.  Fill in
		# the squares with the new combined house.  
		# remove the original house
		newhouse=gh1+'_';
		for i in range(top,bottom+1):
			for j in range(left,right+1):
				res.grid[i][j].append(newhouse);

		res.deleteHouse(gh1);
		res.deleteHouse(gh2);

		# the "reduce" function returns a list of
		# additional options if it needed to split,
		# including itself
		new_parks = res.reduce(newhouse);
		new_parks.append(res);

		return new_parks;
		
	def reduce(self,newhouse):
		#
		# REDUCE
		# resolve squares that have overlapping houses
		reduce_result = [];

		# first find the list of conflicting houses
		conflict=dict();
		i=0;
		for row in self.grid:
			j=0;
			for cell in row:
				if(len(cell.occ_list)>1):
					conflict[cell.occ_list[0]]=1;

		nhcoord = self.getHouseCoors(newhouse);
		for s in conflict.iterkeys():
			curcoord = self.getHouseCoors(s);
			if(debug_print): print s,curcoord,"overlaps",newhouse,nhcoord;
			(cur_t,cur_l,cur_b,cur_r) = curcoord;
			(new_t,new_l,new_b,new_r) = nhcoord;

			# easiest case: old house is completely
			# contained within the new.  old can simply
			# be eliminated
			if(
				(cur_t>=new_t) and
				(cur_l>=new_l) and
				(cur_b<=new_b) and
				(cur_r<=new_r)
			):
				self.deleteHouse(s);
				if(debug_print): print "REMOVED";
				continue;

			# kinda easy case: one side of the house
			# can be truncated
			if(
				(cur_t>=new_t) and
				(cur_b<=new_b)
			):
				if(cur_l>=new_l):
					if(debug_print): print "TRUNC (left)";
					for i in range(cur_t,cur_b+1):
						for j in range(cur_l,new_r+1):
							self.grid[i][j].occ_list.remove(s);
					continue;

				if(cur_r<=new_r):
					if(debug_print): print "TRUNC (right)";
					for i in range(cur_t,cur_b+1):
						for j in range(new_l,cur_r+1):
							self.grid[i][j].occ_list.remove(s);
					continue;

			if(
				(cur_l>=new_l) and
				(cur_r<=new_r)
			):
				if(cur_t<=new_t):
					if(debug_print): print "TRUNC (bottom)";
					for i in range(new_t,cur_b+1):
						for j in range(cur_l,cur_r+1):
							self.grid[i][j].occ_list.remove(s);
					continue;

				if(cur_b>=new_b):
					if(debug_print): print "TRUNC (top)";
					for i in range(cur_t,new_b+1):
						for j in range(cur_l,cur_r+1):
							self.grid[i][j].occ_list.remove(s);
					continue;


			# the hard case: a house is split by the
			# new house
			if(
				(cur_l<=new_l) and
				(cur_r>=new_r) and
				(cur_t> new_t) and
				(cur_b< new_b)
			):
				if(debug_print): print "SPLIT (horizontal)";
				self.deleteHouse(s);

				# new left side
				for i in range(cur_t,cur_b+1):
					for j in range(cur_l,new_l):
						self.grid[i][j].occ_list.append(s+"y");

				# new right side
				for i in range(cur_t,cur_b+1):
					for j in range(new_r+1,cur_r):
						self.grid[i][j].occ_list.append(s+"z");

				continue;

			if(
				(cur_l> new_l) and
				(cur_r< new_r) and
				(cur_t<=new_t) and
				(cur_b>=new_b)
			):
				if(debug_print): print "SPLIT (vertical)";
				self.deleteHouse(s);

				# new top side
				for i in range(cur_t,new_t):
					for j in range(cur_l,new_l):
						self.grid[i][j].occ_list.append(s+"y");

				# new bottom
				for i in range(new_t+1,cur_b+1):
					for j in range(new_l+1,cur_r):
						self.grid[i][j].occ_list.append(s+"z");

				continue;

			# the really hard case: one corner of the
			# house is conflicting.
			p=Park(self.rows,self.cols);
			p.copyFrom(self);
			if(
				(cur_l<new_l) and
				(cur_t<new_t) and
				(cur_r>=new_l) and
				(cur_b>=new_t)
			):
				if(debug_print): print "SPLIT (bottom-right corner)";
				self.splitAndRemove(s,1,1);
				p.splitAndRemove(s,2,1);
				p.reduce(newhouse);
				reduce_result.append(p);
				continue;

			if(
				(cur_l<new_l) and
				(cur_t>new_t) and
				(cur_b>=new_b) and
				(cur_r>=new_l)
			):
				if(debug_print): print "SPLIT (top-right corner)";
				self.splitAndRemove(s,1,2);
				p.splitAndRemove(s,2,2);
				p.reduce(newhouse);
				reduce_result.append(p);
				continue;

			if(
				(cur_l<=new_r) and
				(cur_t<new_t) and
				(cur_b>=new_t) and
				(cur_r>new_r)
			):
				if(debug_print): print "SPLIT (bottom-left corner)";
				self.splitAndRemove(s,1,3);
				p.splitAndRemove(s,2,3);
				p.reduce(newhouse);
				reduce_result.append(p);
				continue;

			if(
				(cur_l<=new_r) and
				(cur_t<=new_b) and
				(cur_b>new_b) and
				(cur_r>new_r)
			):
				if(debug_print): print "SPLIT (top-left corner)";
				self.splitAndRemove(s,1,4);
				p.splitAndRemove(s,2,4);
				p.reduce(newhouse);
				reduce_result.append(p);
				continue;


			# if we get here, then we have an unresolved conflict
			# and we must die
			sys.stderr.write("ERROR: unresolved conflict\n");
			if(debug_print): self.display();
			sys.exit(-1);



		if(debug_print): self.display();
		reduce_result.append(self);

		return reduce_result;


				
# the logic for is as follows:
# Begin with one 1x1 greenhouse covering every
# strawberry.  Then, 
# a) iterate through combinations
# of two existing greenhouses, merge the selected two,
# and subtract the overlap from any of the remaining houses.
# The total number of combinations to check is set as a 
# constant from within the program (MAX_COMBINES).
#
# b) after a new set of parts is calculated, the best is
# selected using this logic
# * variation is calculated with: # of houses in new park - # of houses in original park
# * if the variation is negative AND the current park has more than the max # of houses, 
#   then select always new park 
# * if variation is positive, select the park with the smallest variation
# * select park with lowest price
# if more than one new park is selected, one with lowest score is chosen 
#
# c) if the park selected in B has a lower price than the current
# park, then it is selected as the current and the program returns
# to step (a).  If not, the current park is selected as the solution.
# 
#
# optimizations not done: 1) the initial park can be guessed
# at without starting from the minimal state of 1x1 greenhouses.

class InputProcessor:
	def __init__(self,max_array,data_array):
		self.max_array = max_array;
		self.data_array = data_array;
	def do_run(self):
		print "\n";
		grid_index=0;
		for max_gh_count in self.max_array:
			rows=len(self.data_array[grid_index]);
			cols=len(self.data_array[grid_index][0]);
			if(debug_print): print "creating new park with (rows,cols) = (",rows,",",cols,")";
			p=Park(rows,cols);

			# load the park object with the input data
			# i.e. the location of the strawberries
			j=0;
			for row in self.data_array[grid_index]:
				k=0;
				for c in row:
					if(c=='@'):
						p.grid[j][k].append(c);
					k+=1;
				j+=1;

			# display the park, per the test requirements
			print max_gh_count;
			p.display();
			print;

			# INITIAL PARK:
			#
			# convert all strawberries to 1x1 greenhouses
			j=0;
			gh_num=0;
			for row in self.data_array[grid_index]:
				k=0;
				for c in row:
					if((len(p.grid[j][k].occ_list)>0) and (p.grid[j][k].occ_list[0]=='@')):
						p.grid[j][k].occ_list[0]="{0}".format(gh_num);
						gh_num+=1;
					k+=1;
				j+=1;
			if(debug_print): p.display();

			solution_found=False;
			round=0;
			while(not solution_found):
				round+=1;
				if(debug_print): sys.stderr.write("\nStarting round {0}\n".format(round));

				cur_num_houses = len(p.allHouseNames());
				cur_score = p.totalScore();
				if(debug_print): print "*****************";
				if(debug_print): p.display();
				if(debug_print): print "CUR: # of houses:",cur_num_houses;
				if(debug_print): print "CUR: price:",cur_score;

				# generate list of greenhouses to combine
				# NOTE: the loop only does MAX_COMBINES number of
				# combinations in this list
				clist = p.randomizeComboList();
				i=0;
				selected=[];

				min_variation=sys.maxint;
				min_score=sys.maxint;
				min_score_l=[];

				for cmb in clist:
					if(i>=MAX_COMBINES): break;
					if(debug_print): sys.stderr.write("\rtesting combination {0}".format(i));
					i+=1;

					(gh1,gh2) = cmb;

					# take the union of two greenhouses, and then
					# reduce (subtract from) all other
					# greenhouses except the two we just
					# combined
					new_park_list=p.combineAndReduce(gh1,gh2);

					for np in new_park_list:
						num_houses = len(np.allHouseNames());
						score = np.totalScore();
						if(debug_print): print "# of houses:",num_houses;
						if(debug_print): print "price:",score;

						variation=num_houses-cur_num_houses;
						# if the number of greenhouses went down, and 
						# we have too many in the current one, then select
						# only if variation is -1.
						# otherwise, take the one with the smallest absolute
						# variation.
						if(cur_num_houses>max_gh_count):
							if(variation==-1): selected.append(np);
						else:
							v=abs(variation);
							if(v==0): v=1; # variation of 0 and 1 are considered equal
							if(v<min_variation):
								selected=[];
								selected.append(np);
								min_variation=v;
							elif(v==min_variation):
								selected.append(np);

						# also select those with the lowest score
						# NOTE: ignored because it always selects the
						# single house to cover all the strawberries
						#if(score<min_score):
						#	min_score_l=[];
						#	min_score_l.append(np);
						#	min_score=score;
						#elif(score==min_score):
						#	min_score_l.append(np);

				if(debug_print): print "min_var",min_variation;
				if(debug_print): print "min_score",min_score;
				if(debug_print): print "total selected: ",len(selected);

				# append the min_score list to the selected
				# list.  This will weight lower scores
				# higher in probability.
				selected.extend(min_score_l);

				# pick the next candidate from the selection list
				# with the lowest score
				MAX_SCORE_SEARCH = 16;
				selidx=-1;
				min_score=sys.maxint;
				for i in range(len(selected)):
					if(selected[i].totalScore()<min_score): selidx=i;

				candidate=selected[selidx];
				num_houses=len(candidate.allHouseNames());
				score=candidate.totalScore();

				# if we need to reduce houses, then choose 
				# it and goto next round
				if(
					(cur_num_houses>max_gh_count) and
					(num_houses<cur_num_houses)
				):
					p=candidate;
				elif(
					(cur_score>score) or
					((cur_score==score) and (num_houses<cur_num_houses))
				):
					p=candidate;
				else:
					# optimized park cannot beat current park, so
					# we select the current as the solution
					solution_found=True;

			if(debug_print): sys.stderr.write("\n\nprocessing finished in round {0}\n".format(round));
			if(debug_print): print "SOLUTION:";
			print p.totalScore();
			p.display();

			grid_index+=1;

		print "done";


print "Starting...";

reader = InputReader();
(max_ar,data_ar) = reader.readInput();
proc = InputProcessor(max_ar,data_ar);
proc.do_run();
