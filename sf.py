#!/usr/bin/python
#
# Copyright 2015, David Dombrowsky & 6th Street Software
#
# Distributed under GPLv2.  See LICENSE file for details.
#
# See the README.txt file for description of the excercise.

# usage:
# $ cat rectangles.txt | ./sf.py
#
# To see details, set debug_print to True (in the source code) and run
# $ cat rectangles.txt | ./sf.py > rectangles.out

import sys,re,random;

debug_print=False;
MAX_COMBINES=1000;

class InputReader:
	def __init__(self):
		self.ar_data = [];
		self.ar_max_greenhouses = [];

	def readInput(self):
		num=0;
		grid = [];

		def procgrid(max,num,grid): #{

			if (debug_print): print "max greenhouses:",max,", grid #",num;

			if (len(grid)>0):
				self.ar_data.append(grid);
				if (debug_print): print "\n".join(grid);
				num+=1;

			return num;
		#}

		state=0;
		got_eof=False;

		while (not got_eof): #{
			if (state==0):
				print "Input max # of greenhouses: ",;

			r=sys.stdin.readline();

			if (len(r)==0):
				got_eof=True;
				continue;

			r=r.rstrip(); # remove newline

			if (len(r)>0): # skip blank lines
				rm=re.match('[0-9]+',r);
				if (rm is None):
					if (state==0):
						print "invalid number";
						continue;
					# load data lines into an array
					grid.append(r);
				else:
					if (state==1):
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
					if (not ((r>=1) and (r<=10))):
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
		#}

		# if we get EOF before a blank line, don't forget the last grid
		if (state==1): #{
			procgrid(
				self.ar_max_greenhouses[len(self.ar_max_greenhouses)-1],
				num,
				grid
			);
		#}

		return (self.ar_max_greenhouses,self.ar_data);

class ParkSquare:
	'''
		represents a cell in the grid
	'''
	def __init__(self):
		self.occ_list = [];
		self.has_berry = False;

	def append(self,n):
		self.occ_list.append(n);

	def empty(self):
		return (len(self.occ_list)==0);

	def toString(self):
		'''
			print "." on empty, the value on single, and "X" on multiple
		'''
		if (self.empty()):
			ch=".";
			if (self.has_berry): ch="@";
			return ch;
		elif (len(self.occ_list)==1):
			# square is occupied by only 1 item,
			# so display with the ascii house ID.
			ch="~";
			m=re.match("[0-9]+",self.occ_list[0]);
			if (m!=None):
				num=int(m.group());
				if (num<(126-33)): # max ascii
					ch=chr(ord('!')+num);
					if ((ch==".") or (ch=="@")): # reserved
						ch="~";
			return ch;
		else:
			# conflict
			return "X";

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
				self.grid[i][j].has_berry=other_park.grid[i][j].has_berry;


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
				if (
					(not cell.empty()) and
					(cell.occ_list[0]==hname)
				):
					if (i<top): top=i;
					if (i>bottom): bottom=i;
					if (j<left): left=j;
					if (j>right): right=j;
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
		if (len(houses)==1):
			combolist.append((houses[0],houses[0]));
		else:
			for a in houses:
				for b in houses:
					if (a!=b): combolist.append((a,b));

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
				if (len(self.grid[i][j].occ_list)>0):
					if (self.grid[i][j].occ_list.count(hname)>0):
						self.grid[i][j].occ_list.remove(hname);
						assert(not (len(self.grid[i][j].occ_list)==0 and
									self.grid[i][j].has_berry));

	def allHouseNames(self):
		res=dict();
		for i in range(len(self.grid)):
			for j in range(len(self.grid[i])):
				for r in self.grid[i][j].occ_list:
					res[r]=1;
		return res.keys();

	def totalPrice(self):
		names=self.allHouseNames();
		price=0;
		for n in names:
			price+=10; # 10 points per house
			(t,l,b,r) = self.getHouseCoors(n);
			# plus 1 per covered square
			height=(b-t)+1;
			width=(r-l)+1;
			price+=(height*width);
		return price;

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
				if (len(self.grid[i][j].occ_list)>1):
					# store the conflicting coordinates
					if (i<conf_t): conf_t=i;
					if (j<conf_l): conf_l=j;
					if (i>conf_b): conf_b=i;
					if (j>conf_r): conf_r=j;

		if (debug_print): print "conflict",(conf_t,conf_l,conf_b,conf_r);

		# for empty blocks previously occupied
		# by the conflicting house, place one
		# of two new houses based on the split type
		# and the conflicting corner
		new_t=[0,0];
		new_l=[0,0];
		new_b=[0,0];
		new_r=[0,0];
		if (con_corner==1):
			# A is existing (to be split), B is new

			# 1 = bottom-right corner
			if (split_type==1):
				#
				# AAA      CCC
				# AAXBB -> DDBBB
				#   BBB      BBB
				#
				# C:
				new_t[0]=cur_t;
				new_l[0]=cur_l;
				new_b[0]=conf_t-1;
				new_r[0]=cur_r;
				# D:
				new_t[1]=conf_t;
				new_l[1]=cur_l;
				new_b[1]=cur_b;
				new_r[1]=conf_l-1;
			else:
				#
				# AAA      CCD
				# AAXBB -> CCBBB
				#   BBB      BBB
				#
				# C:
				new_t[0]=cur_t;
				new_l[0]=cur_l;
				new_b[0]=cur_b;
				new_r[0]=conf_l-1;
				# D:
				new_t[1]=cur_t;
				new_l[1]=conf_l;
				new_b[1]=conf_t-1;
				new_r[1]=cur_r;
		elif (con_corner==2):
			# 2 = top-right corner
			if (split_type==1):
				#
				#   BBB      BBB
				# AAXBB -> CCBBB
				# AAA      DDD
				#
				# C:
				new_t[0]=cur_t;
				new_l[0]=cur_l;
				new_b[0]=conf_b;
				new_r[0]=conf_l-1;
				# D:
				new_t[1]=conf_b+1;
				new_l[1]=cur_l;
				new_b[1]=cur_b;
				new_r[1]=cur_r;
			else:
				#
				#   BBB      BBB
				# AAXBB -> CCBBB
				# AAA      CCD
				#
				# C:
				new_t[0]=cur_t;
				new_l[0]=cur_l;
				new_b[0]=cur_b;
				new_r[0]=conf_l-1;
				# D:
				new_t[1]=conf_b+1;
				new_l[1]=conf_l;
				new_b[1]=cur_b;
				new_r[1]=cur_r;
		elif (con_corner==3):
			# 3 = bottom-left corner
			if (split_type==1):
				#
				#   AAA      CCC
				# BBXAA -> BBBDD
				# BBB      BBB
				#
				# C:
				new_t[0]=cur_t;
				new_l[0]=cur_l;
				new_b[0]=conf_t-1;
				new_r[0]=cur_r;
				# D:
				new_t[1]=conf_t;
				new_l[1]=conf_r+1;
				new_b[1]=cur_b;
				new_r[1]=cur_r;
			else:
				#
				#   AAA      CDD
				# BBXAA -> BBBDD
				# BBB      BBB
				#
				# C:
				new_t[0]=cur_t;
				new_l[0]=cur_l;
				new_b[0]=conf_t-1;
				new_r[0]=conf_r;
				# D:
				new_t[1]=cur_t;
				new_l[1]=conf_r+1;
				new_b[1]=cur_b;
				new_r[1]=cur_r;
		elif (con_corner==4):
			# 4 = top-left corner
			if (split_type==1):
				#
				# BBB      BBB
				# BBXAA -> BBBCC
				#   AAA      DDD
				#
				new_t[0]=cur_t;
				new_l[0]=conf_r+1;
				new_b[0]=conf_b;
				new_r[0]=cur_r;
				new_t[1]=conf_b+1;
				new_l[1]=cur_l;
				new_b[1]=cur_b;
				new_r[1]=cur_r;
			else:
				#
				# BBB      BBB
				# BBXAA -> BBBCC
				#   AAA      DCC
				#
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


		# create the two new houses
		for n in range(2):
			if (debug_print):
				print("New house, {0},{1} to {2},{3}".
				      format(new_t[n],new_l[n],new_b[n]+1,new_r[n]+1));

			for i in range(new_t[n],new_b[n]+1):
				for j in range(new_l[n],new_r[n]+1):
					if (len(self.grid[i][j].occ_list)>1):
						sys.stderr.write("ERROR: attempting to add conflict\n");
						sys.exit(-1);
					self.grid[i][j].occ_list.append(sname[n]);

		# remove the original
		if (debug_print):
			print("Removing house {0}".format(hname));
			self.display()

		self.deleteHouse(hname);


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
				if (
					(not cell.empty()) and (
						(cell.occ_list[0]==gh1) or
						(cell.occ_list[0]==gh2)
					)
				):
					if (i<top): top=i;
					if (i>bottom): bottom=i;
					if (j<left): left=j;
					if (j>right): right=j;
				j+=1;
			i+=1;

		if (debug_print): print gh1,"+",gh2,"=",top,left,bottom,right;

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
				if (len(cell.occ_list)>1):
					conflict[cell.occ_list[0]]=1;

		nhcoord = self.getHouseCoors(newhouse);
		for s in conflict.iterkeys():
			curcoord = self.getHouseCoors(s);
			if (debug_print): print s,curcoord,"overlaps",newhouse,nhcoord;
			(cur_t,cur_l,cur_b,cur_r) = curcoord;
			(new_t,new_l,new_b,new_r) = nhcoord;

			# easiest case: old house is completely
			# contained within the new.  old can simply
			# be eliminated
			if (
				(cur_t>=new_t) and
				(cur_l>=new_l) and
				(cur_b<=new_b) and
				(cur_r<=new_r)
			):
				self.deleteHouse(s);
				if (debug_print): print "REMOVED";
				continue;

			# kinda easy case: one side of the house
			# can be truncated
			if (
				(cur_t>=new_t) and
				(cur_b<=new_b)
			): #{
				if (cur_l>=new_l):
					if (debug_print): print "TRUNC (left)";
					for i in range(cur_t,cur_b+1):
						for j in range(cur_l,new_r+1):
							self.grid[i][j].occ_list.remove(s);
					continue;

				if (cur_r<=new_r):
					if (debug_print): print "TRUNC (right)";
					for i in range(cur_t,cur_b+1):
						for j in range(new_l,cur_r+1):
							self.grid[i][j].occ_list.remove(s);
					continue;
			#}

			if (
				(cur_l>=new_l) and
				(cur_r<=new_r)
			): #{
				if (cur_t<=new_t):
					if (debug_print): print "TRUNC (bottom)";
					for i in range(new_t,cur_b+1):
						for j in range(cur_l,cur_r+1):
							self.grid[i][j].occ_list.remove(s);
					continue;

				if (cur_b>=new_b):
					if (debug_print): print "TRUNC (top)";
					for i in range(cur_t,new_b+1):
						for j in range(cur_l,cur_r+1):
							self.grid[i][j].occ_list.remove(s);
					continue;
			#}


			# the hard case: a house is split by the new house
			if (
				(cur_l<=new_l) and
				(cur_r>=new_r) and
				(cur_t> new_t) and
				(cur_b< new_b)
			):
				if (debug_print): print "SPLIT (horizontal)";
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

			if (
				(cur_l> new_l) and
				(cur_r< new_r) and
				(cur_t<=new_t) and
				(cur_b>=new_b)
			):
				if (debug_print): print "SPLIT (vertical)";
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
			if (
				(cur_l<new_l) and
				(cur_t<new_t) and
				(cur_r>=new_l) and
				(cur_b>=new_t)
			):
				if (debug_print): print "SPLIT (bottom-right corner)";
				self.splitAndRemove(s,1,1);
				p.splitAndRemove(s,2,1);
				p.reduce(newhouse);
				reduce_result.append(p);
				continue;

			if (
				(cur_l<new_l) and
				(cur_t>new_t) and
				(cur_b>=new_b) and
				(cur_r>=new_l)
			):
				if (debug_print): print "SPLIT (top-right corner)";
				self.splitAndRemove(s,1,2);
				p.splitAndRemove(s,2,2);
				p.reduce(newhouse);
				reduce_result.append(p);
				continue;

			if (
				(cur_l<=new_r) and
				(cur_t<new_t) and
				(cur_b>=new_t) and
				(cur_r>new_r)
			):
				if (debug_print): print "SPLIT (bottom-left corner)";
				self.splitAndRemove(s,1,3);
				p.splitAndRemove(s,2,3);
				p.reduce(newhouse);
				reduce_result.append(p);
				continue;

			if (
				(cur_l<=new_r) and
				(cur_t<=new_b) and
				(cur_b>new_b) and
				(cur_r>new_r)
			):
				if (debug_print): print "SPLIT (top-left corner)";
				self.splitAndRemove(s,1,4);
				p.splitAndRemove(s,2,4);
				p.reduce(newhouse);
				reduce_result.append(p);
				continue;


			# if we get here, then we have an unresolved conflict
			# and we must die
			sys.stderr.write("ERROR: unresolved conflict\n");
			if (debug_print): self.display();
			sys.exit(-1);



		if (debug_print): self.display();
		reduce_result.append(self);

		return reduce_result;


				
# The logic for is as follows:
#
# Begin with one 1x1 greenhouse covering every strawberry.  Then,
#
# a) iterate through combinations of two existing greenhouses,
#    merge the selected two, and subtract the overlap from any of the
#    remaining houses.  The total number of combinations to check is
#    set as a constant from within the program (MAX_COMBINES).
#
# b) after a new set of parts is calculated, the best is
#    selected using this logic
#    * variation is calculated with: # of houses in new park - # of
#      houses in original park
#    * if the variation is negative AND the current park has more than the
#      max # of houses, then select always new park
#    * if variation is positive, select the park with the smallest variation
#    * of the remaining, select park with lowest price
#
# c) if the park selected in (b) has a lower price than the current
#    park, then it is selected as the current and the program returns
#    to step (a).  If not, the current park is selected as the solution.
#
#
# optimizations not done: 1) the initial park can be guessed
# at without starting from the minimal state of 1x1 greenhouses.

class InputProcessor:
	def __init__(self,max_array,data_array):
		# FIXME: this should not take multiple problems at once
		self.max_array = max_array;
		self.data_array = data_array;
		self.best = None;

	def do_single_run(self):
		print "\n";
		grid_index=0;
		p=None;
		for max_gh_count in self.max_array: #{
			rows=len(self.data_array[grid_index]);
			cols=len(self.data_array[grid_index][0]);

			if (debug_print):
				print("creating new park with (rows,cols) = ({0},{1})".
				      format(rows,cols));
			p=Park(rows,cols);

			# load the park object with the input data
			# i.e. the location of the strawberries
			j=0;
			for row in self.data_array[grid_index]:
				k=0;
				for c in row:
					if (c=='@'):
						p.grid[j][k].has_berry = True;
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
			for row in self.data_array[grid_index]: #{
				k=0;
				for c in row: #{
					if (p.grid[j][k].has_berry): #{
						p.grid[j][k].occ_list.append("{0}".format(gh_num));
						gh_num+=1;
					#}
					k+=1;
				#}
				j+=1;
			#}

			if (debug_print): p.display();

			solution_found=False;
			round=0;
			while (not solution_found):
				round+=1;

				print("Starting round {0}".format(round));

				cur_num_houses = len(p.allHouseNames());
				cur_price = p.totalPrice();
				if (debug_print): print "*****************";
				if (debug_print): p.display();
				if (debug_print): print "CUR: # of houses:",cur_num_houses;
				if (debug_print): print "CUR: price:",cur_price;

				# generate list of greenhouses to combine
				# NOTE: the loop only does MAX_COMBINES number of
				# combinations in this list
				clist = p.randomizeComboList();
				i=0;
				selected=[];

				min_variation=sys.maxint;
				min_price=sys.maxint;
				min_price_l=[];

				for cmb in clist: #{
					if (i>=MAX_COMBINES): break;

					if (debug_print):
						sys.stdout.write("\ntesting combination #{0}\n".
						                 format(i));

					i+=1;

					(gh1,gh2) = cmb;

					# take the union of two greenhouses, and then
					# reduce (subtract from) all other greenhouses
					# except the two we just combined
					new_park_list=p.combineAndReduce(gh1,gh2);

					for np in new_park_list: #{
						num_houses = len(np.allHouseNames());
						price = np.totalPrice();

						variation=num_houses-cur_num_houses;

						if (debug_print):
							print "# of houses:",num_houses;
							print "price:",price;
							print "house count variation:",variation;

						# if the number of greenhouses went down, and
						# we have too many in the current one, then
						# select only if variation is -1.  otherwise,
						# take the one with the smallest absolute
						# variation.
						if (cur_num_houses>max_gh_count): #{
							if (variation==-1):
								selected.append(np);
							else: #{
								v=abs(variation);

								# variation of 0 and 1 are considered equal
								if (v==0): v=1;

								if (v<min_variation):
									# found a new minimum, blank
									# the list and start over
									selected=[];
									selected.append(np);
									min_variation=v;
								elif (v==min_variation):
									selected.append(np);
							#}
						else:
							# We're at or below the max number of
							# houses.  Keep this configuration
							# by default.
							selected.append(np);
						#}

						# In later rounds, also select those with
						# the lowest price.  If we included this
						# in early rounds, it would most often select
						# one house over all berries and iteration
						# would stop.
						if (round>10): #{
							if (price<min_price):
								min_price_l=[];
								min_price_l.append(np);
								min_price=price;
							elif (price==min_price):
								min_price_l.append(np);
						#}
					#}
				#}

				if (debug_print):
					print "min_var",min_variation;
					print "min_price",min_price;

				print("Selecting best price of {0} configurations".
				      format(len(selected)));

				# append the min_price list to the selected list.
				# This will weight lower prices higher in probability.
				selected.extend(min_price_l);

				assert(len(selected) > 0);

				# pick the next candidate from the selection list
				# with the lowest price
				MAX_SCORE_SEARCH = 16;
				selidx=-1;
				min_price=sys.maxint;
				for i in range(len(selected)):
					if (selected[i].totalPrice()<min_price): selidx=i;

				candidate=selected[selidx];
				num_houses=len(candidate.allHouseNames());
				price=candidate.totalPrice();

				# if we need to reduce houses, then choose
				# it and goto next round
				if (
					(cur_num_houses>max_gh_count) and
					(num_houses<cur_num_houses)
				):
					p=candidate;
				elif (
					(cur_price>price) or
					((cur_price==price) and (num_houses<cur_num_houses))
				):
					p=candidate;
				else:
					# optimized park cannot beat current park, so
					# we select the current as the solution
					solution_found=True;

			if (debug_print):
				sys.stdout.write("\n\nprocessing finished in round {0}\n".
				                 format(round));
				print "SOLUTION:";
			print p.totalPrice();
			p.display();

			grid_index+=1;
		#}

		self.best = p;
		print "done";

	def do_run(self):
		best_overall=None;
		done=False;

		# Number of times we will try to beat our current best
		# before accepting the solution:
		retry=4;

		while (not done): #{
			self.do_single_run();
			if (best_overall==None or
			    self.best.totalPrice() < best_overall.totalPrice()):

				if (best_overall!=None):
					prevbest=best_overall.totalPrice();
				else:
					prevbest=-1;

				best_overall=self.best;

				print("NEW BEST: price down from {0} to {1}".
				      format(prevbest,
					         best_overall.totalPrice()));
			else: #{
				retry-=1;
				print("can't beat previous best of {0}, retries {1}".
				      format(best_overall.totalPrice(),retry));
			#}

			if (retry<=0): done=True;

			best_overall.display();
			print("\n------------------------------");
		#}



print "Starting...";

reader = InputReader();

# TODO: this should probably read each count+grid input
# individually, and process each as we go along.
(max_ar,data_ar) = reader.readInput();
proc = InputProcessor(max_ar,data_ar);

proc.do_run();

# vim:ts=4:noet
