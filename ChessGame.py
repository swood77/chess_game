#!/usr/bin/python -d

#Author:  Scott Wood
import sqlite3
import sys
import re

#R=rook, Q=Queen, K=King, B=Bishop, N=Knight, P=Pawn E=Empty
#W= White, B= Black


class ChessGame:
	def __init__(self, sqlitedb):
		self.database_file = sqlitedb 
		conn = sqlite3.connect(self.database_file)
		db = conn.cursor()
		try:
		 	db.execute('''create table chess (row number, column number, color text, piece text)''')
			db.execute('''create table status (colorx text)''')
			db.execute("""insert into status values ('W')""")
			conn.commit()
			x = 0		
			y = 0
			for y in range(8):
				for x in range(8):
					chess_list = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
					px = (chess_list[x])
					if y == 0: db.execute("""insert into chess values (?, ?, 'W', ?)""", (x, y, px))
					if y == 7: db.execute("""insert into chess values (?, ?, 'B', ?)""", (x, y, px))
					if y == 1: db.execute("""insert into chess values (?, ?, 'W', ?)""", (x, y, 'P'))
					if y == 6: db.execute("""insert into chess values (?, ?, 'B', ?)""", (x, y, 'P'))
					if y == 2: db.execute("""insert into chess values (?, ?, 'E', ?)""", (x, y, 'E'))
					if y == 5: db.execute("""insert into chess values (?, ?, 'E', ?)""", (x, y, 'E'))
					if y == 4: db.execute("""insert into chess values (?, ?, 'E', ?)""", (x, y, 'E'))
					if y == 3: db.execute("""insert into chess values (?, ?, 'E', ?)""", (x, y, 'E'))
					conn.commit()
		except:
			print "sql file already has chess table"

		#dictionary to be used to parse all moves
		db.execute("""select colorx from status""")
		t = db.fetchone()
		db.close()
		#MAKE NOT OF HOW THIS WAS DONE WHEN RETRIEVING FROM DATABASE YOU ARE GIVEN A TUPLE NOTE THE NEXT LINE
		self.current_color = t[0]
		self.board = {}
		for x in range(8):
			for y in range(8):
				db.execute("""select color,piece from chess where row = ? and column = ?""", (x, y))
				z = db.fetchone()
				self.board[x,y] = z


	def _updatedb(self, x1, y1, x2, y2):
                #Update the database with the latest move
                #Update the status table also
                conn = sqlite3.connect(self.database_file)
                db = conn.cursor()
		color,piece = self.board[x1,y1]
		self._changecolor()
                try:
                        db.execute("""update chess set color=?, piece=? where row=? and column=?""", ('E', 'E', x1, y1))
                        db.execute("""update chess set color=?, piece=? where row=? and column=?""", (color, piece, x2, y2))
			db.execute("""update status set colorx=?""", (self.current_color))
                        conn.commit()
                except:
                        print "can't update database"

                db.close()



	def _diag(self, xaxis, yaxis, xaxis2, yaxis2, bishop_legal_moves, valid_move):

	#lower left hand side

		xpos = xaxis - 1
		ypos = yaxis - 1
		for x in range(0, 8):
			if xpos != -1:
				if ypos != -1:
					bishop_legal_moves += [[xpos, ypos]]
					ypos = ypos - 1
					xpos = xpos - 1
	#upper left hand side moves

		xpos = xaxis - 1
		ypos = yaxis + 1
		for x in range(0, 8):
                        if xpos != -1:
                                if ypos != 8:
                                        bishop_legal_moves += [[xpos, ypos]]
                                        ypos = ypos + 1
                                        xpos = xpos - 1

	#lower right hand side
		xpos = xaxis + 1
                ypos = yaxis - 1
                for x in range(0, 8):
                        if xpos != 8:
                                if ypos != -1:
                                        bishop_legal_moves += [[xpos, ypos]]
                                        ypos = ypos - 1
                                        xpos = xpos + 1

	#upper right hand side
 		xpos = xaxis + 1
                ypos = yaxis + 1
                for x in range(0, 8):
                        if xpos != 8:
                                if ypos != 8:
                                        bishop_legal_moves += [[xpos, ypos]]
                                        ypos = ypos + 1
                                        xpos = xpos + 1

	#Lets check if there are any pieces between the two
		if xaxis > xaxis2 and yaxis < yaxis2:
			print "upper lift"
			for z in bishop_legal_moves:
				xx,yy = z
                                if xx < xaxis and yy > yaxis:
                                        color,piece = self.board[xx,yy]
                                        if piece not in ('E'):
                                                valid_move[0]=1

		if xaxis < xaxis2 and yaxis < yaxis2:
			print "upper right"
			for z in bishop_legal_moves:
				xx,yy = z
				if xx > xaxis and yy > yaxis:
					color,piece = self.board[xx,yy] 
					if piece not in ('E'):
						valid_move[0]=1
						
					
		if xaxis > xaxis2 and yaxis > yaxis2:
			print "lower left"
			for z in bishop_legal_moves:
				xx,yy = z
                                if xx < xaxis and yy < yaxis:
                                        color,piece = self.board[xx,yy]
                                        if piece not in ('E'):
                                                valid_move[0]=1

		if xaxis < xaxis2 and yaxis > yaxis2:
			print "lower right" 
			for z in bishop_legal_moves:
				xx,yy = z
                                if xx > xaxis and yy < yaxis:
                                        color,piece = self.board[xx,yy]
                                        if piece not in ('E'):
                                                valid_move[0]=1


	def _movebishop(self, x1, y1, x2, y2):
		bvalid=[]
		bvalid=[0]
		legal_moves=[]
		#bvalid is whether there are any pieces between the moves, true means there are pieces
		self._diag(x1, y1, x2, y2, legal_moves, bvalid)
		if [x2, y2] in legal_moves:
			if bvalid[0] == 0:
				#color,piece = self.board[x1,y1]
				#self.board[x2,y2] = color,piece
				self._updatedb(x1, y1, x2, y2)
				self.board[x2,y2] = self.board[x1,y1]
				#Is the line below legal?
				self.board[x1,y1] = 'E','E'

	def _movepawn(self, x1, y1, x2, y2):
		#Need to check if the pieces are on the last row or out of bound
		#Is the piece at x2, y2 empty?
		#color2,piece2 is the square that is between the two square pawn move
		colorx,piecex = self.board[x1,y1]
		colorz=self.current_color
		if colorz == 'W':
			color2,piece2 = self.board[x1,y1+1]
		else:
			color2,piece2 = self.board[x1,y1-1]

		color,piece = self.board[x2,y2]
		if color == 'E':
			if y1 + 2 == y2 or y1 - 2 == y2:
				if colorx == 'W' and y1 + 2 == y2 and x1 == x2:
					if color2 == 'E':
					#Will need to check if the move puts King in Check eventually
						self._updatedb(x1, y1, x2, y2)
						self.board[x1,y1] = 'E','E'
						self.board[x2,y2] = colorx,piecex

				if colorx == 'B' and y1 - 2 == y2 and x1 == x2:
					if color2 == 'E':
						self._updatedb(x1, y1, x2, y2)
						self.board[x1,y1] = 'E','E'
                                                self.board[x2,y2] = colorx,piecex
			else:
				if y1 + 1 == y2 or y1 - 1 == y2 and x1 == x2:
					if colorx == 'W' and y1 + 1 == y2:
                                        	if color2 == 'E':
                                        #Will need to check if the move puts King in Check eventually
							 self._updatedb(x1, y1, x2, y2)
                                               		 self.board[x1,y1] = 'E','E'
                                                	 self.board[x2,y2] = colorx,piecex
                                	if colorx == 'B' and y1 - 1 == y2 and x1 == x2:
                                       		 if color2 == 'E':
							 self._updatedb(x1, y1, x2, y2)
                                               		 self.board[x1,y1] = 'E','E'
                                               		 self.board[x2,y2] = colorx,piecex
		#This is for a capture
		elif x1 - 1 == x2 or x1 + 1 == x2:
			if colorx == 'W' and color == 'B':
				 print "white pawn capturing"
			         self._updatedb(x1, y1, x2, y2)
				 self.board[x1,y1] = 'E','E'
                                 self.board[x2,y2] = colorx,piecex
			elif colorx == 'B' and color == 'W':
				 print "black pawn capturing"
			         self._updatedb(x1, y1, x2, y2)
				 self.board[x1,y1] = 'E','E'
                                 self.board[x2,y2] = colorx,piecex


	def _moverook(self, x1, y1, x2, y2):
		#Lets check if there any pieces between the two squares
		valid_move=True
		if x1 == x2 and y1 < y2:
			ya = y1
			yb = y2
			while ya != yb and ya <=7:
				ya += 1
				color,piece = self.board[x1,ya]
				if ya == yb:
                                        if color != self.current_color:
                                                continue
				elif piece != 'E':
				 	valid_move=False	

		if y1 == y2 and x1 < x2:
			xa = x1
			xb = x2
			while xa != xb and xa <=7:
                                xa += 1
                                color,piece = self.board[xa,y1]
				if xa == xb:
                                        if color != self.current_color:
                                                continue
				elif piece != 'E':
                                        valid_move=False

		if x1 == x2 and y1 > y2:
                        ya = y1
                        yb = y2
                        while ya != yb and ya >=0:
                                ya = ya - 1
                                color,piece = self.board[x1,ya]
				if ya == yb:
                                        if color != self.current_color:
                                                continue
				elif piece != 'E':
                                        valid_move=False

                if y1 == y2 and x1 > x2:
                        xa = x1
                        xb = x2
                        while xa != xb and xa >=0:
                                xa = xa - 1
                                color,piece = self.board[xa,y1]
				if xa == xb:
                                        if color != self.current_color:
                                                continue
                                elif piece != 'E':
                                        valid_move=False

		if valid_move == True: 
			self._updatedb(x1, y1, x2, y2)
			self.board[x2,y2] = self.board[x1,y1]
			self.board[x1,y1] = 'E','E';



		#now is the piece capturing a piece?
		if x1 + 1 == x2	or x1 - 1 == x2:
			if colorx == 'W' and color2 == 'B':
				if y1 + 1 == y2:
					self._updatedb(x1, y1, x2, y2)
					self.board[x1,y1] = 'E','E'
					self.board[x2,y2] = colorx,piecex
			if colorx == 'B' and color2 == 'W':
                                if y1 - 1 == y2:
					self._updatedb(x1, y1, x2, y2)
                                        self.board[x1,y1] = 'E','E'
                                        self.board[x2,y2] = colorx,piecex


	def _movequeen(self, x1, y1, x2, y2):
		if x1 == x2 or y1 == y2:
			self._moverook(x1, y1, x2, y2)
		else:
			self._movebishop(x1, y1, x2, y2)

	def _moveknight(self, x1, y1, x2, y2):
		color,piece = self.board[x1,y1]
		color2,piece2 = self.board[x2,y2]
		if x1 + 2 == x2:
			if y1 +1 == y2 or y1 -1 == y2:
				if color != color2:
					self._updatedb(x1, y1, x2, y2)
					self.board[x1,y1] = 'E','E'
					self.board[x2,y2] = color,piece

		if x1 - 2 == x2:
			if y1 + 1 == y2 or y1 -1 == y2:
                                if color != color2:
					self._updatedb(x1, y1, x2, y2)
                                        self.board[x1,y1] = 'E','E'
                                        self.board[x2,y2] = color,piece

		if y1 + 2 ==y2:
			if x1 + 1 == x2 or x1 - 1 == x2:
                                if color != color2:
					self._updatedb(x1, y1, x2, y2)
                                        self.board[x1,y1] = 'E','E'
                                        self.board[x2,y2] = color,piece

		if y1 - 2 == y2:
			if x1 + 1 == x2 or x1 - 1 == x2:
                                if color != color2:
					self._updatedb(x1, y1, x2, y2)
                                        self.board[x1,y1] = 'E','E'
                                        self.board[x2,y2] = color,piece

	def _moveking(self, x1, y1, x2, y2):
		color,piece = self.board[x1,y1]
		color2,piece2 = self.board[x2,y2]
		if x1 == x2:
			if y1 - 1 == y2 or y1 + 1 == y2:
				if color != color2:
					self._updatedb(x1, y1, x2, y2)
                                        self.board[x1,y1] = 'E','E'
                                        self.board[x2,y2] = color,piece

		elif x1 + 1 == x2 or x1 - 1 == x2:
			if y1 == y2 or y1 + 1 == y2 or y1 - 1 == y2:
				if color != color2:
					self._updatedb(x1, y1, x2, y2)
                                        self.board[x1,y1] = 'E','E'
                                        self.board[x2,y2] = color,piece


	def _changecolor(self):
		#Need to change the status table
		if self.current_color == 'W':
			self.current_color = 'B'
		else:
			self.current_color = 'W'




	def move(self, x1, y1, x2, y2):
		color,piece = self.board[x1,y1]
		if color == self.current_color:
			if piece == 'B':
				self._movebishop(x1, y1, x2, y2)
				print "moving bishop"
			elif piece =='P':
				self._movepawn(x1, y1, x2, y2)
				print "moving pawn"
			elif piece =='R':
				self._moverook(x1, y1, x2, y2)
				print "moving rook"
			elif piece =='Q':
				print "moving queen"
				self._movequeen(x1, y1, x2, y2)
			elif piece =='N':
				print "moving knight"
				self._moveknight(x1, y1, x2, y2)
			elif piece =='K':
				print "moving king"
				self._moveking(x1, y1, x2, y2)
		else:
			print "illegal move"	
	
	def GenerateBoard(self):
		colorb=['W','B']
		self.displayboard={}
		x=0
		y=0
		z=0
		for y in range(8):
                        for x in range(8):
				
				if x!=8 or y!=8:
					if x==0:
						if z==0: 
							z=1
						elif z==1: 
							z=0
					color,piece=self.board[x,y]
					d1 = color+piece+colorb[z]
					d1 = d1.lower()+'.gif'
					self.displayboard[x,y]=d1
					if z==0: 
						z=1
					elif z==1:	
						z=0


if __name__=="__main__":
	mygame = ChessGame(sys.argv[1])
	mygame.GenerateBoard()
