#!/usr/bin/python3
# 
# 2021/07/18

from typing import MutableSequence, Sequence, Optional, Final


class TableCharSet :

	def __init__(self, chars: Sequence[str]) :
		assert len(chars) == 11
		self.vertical:     Final[str] = chars[0]
		self.horizontal:   Final[str] = chars[1]
		self.cross:        Final[str] = chars[2]
		self.top:          Final[str] = chars[3]
		self.right:        Final[str] = chars[4]
		self.bottom:       Final[str] = chars[5]
		self.left:         Final[str] = chars[6]
		self.top_left:     Final[str] = chars[7]
		self.top_right:    Final[str] = chars[8]
		self.bottom_right: Final[str] = chars[9]
		self.bottom_left:  Final[str] = chars[10]


UnicodeSet = TableCharSet(['│', '─', '┼', '┬', '┤', '┴', '├', '┌', '┐', '┘', '└'])
AsciiSet   = TableCharSet(['|', '-', '+', '+', '+', '+', '+', '+', '+', '+', '+'])



# Returns a string that corresponds to the string s centered in size characters, padded with c
# (i.e. len(proper_center(s, size)) >= size)
# If size is smaller than len(s), s is returned
# Unlike str.center(), when the total length of the padding is odd, the extra character
# is consistently added at the right : 
# > 'pancake'.center(10)                    > 'pancakes'.center(11)
# ' pancake  '                              '  pancakes '
# > proper_center('pancake', 10)            > proper_center('pancakes', 11)
# ' pancake  '                              ' pancakes  '
def proper_center(s: str, length: int, c: str = ' ') -> str :
	if length <= len(s) :
		return s
	remaining = length - len(s)
	left = remaining // 2
	right = remaining - left
	return (c * left + s + c * right)


class TableSeparator :

	def __init__(self, char: str, lengths: Sequence[int]) :
		self.char = char
		self.lines = [char * (l + 2) for l in lengths]
		self.length = sum(lengths) + 3 * len(lengths) +1
	
	def build(self, left: str, mid: str, right: str) :
		return left + mid.join(self.lines) + right

	def __len__(self) -> int :
		return self.length
		


class TableBuilder :

	def __init__(self, columns: Sequence[str], name: Optional[str] = None, char_set: TableCharSet = AsciiSet) :
		self.char_set  : Final[TableCharSet]  = char_set
		self.col_names : Final[Sequence[str]] = columns
		self.nb_col    : Final[int]           = len(columns)
		self.title     : Final[Optional[str]] = name
		self.rows      : MutableSequence[Sequence[str]] = []
		self.lengths   : Sequence[int] = [len(s) for s in columns]
	
	def add_row(self, row: Sequence[str]) :
		assert len(row) == self.nb_col
		self.rows.append(row)
		for i in range(len(self.lengths)) :
			if len(row[i]) > self.lengths[i] :
				self.lengths[i] = len(row[i])

	def _build_names(self) -> str :
		normalised_row = [
			proper_center(self.col_names[j], self.lengths[j])
			for j in range(self.nb_col)
		]
		joiner = f" {self.char_set.vertical} "
		return f"{self.char_set.vertical} {joiner.join(normalised_row)} {self.char_set.vertical}"

	def _build_row(self, i: int) -> str :
		normalised_row = [
			self.rows[i][j].ljust(self.lengths[j])
			for j in range(self.nb_col)
		]
		joiner = f" {self.char_set.vertical} "
		return f"{self.char_set.vertical} {joiner.join(normalised_row)} {self.char_set.vertical}"
	
	def build_table(self) -> Sequence[str] :
		res: MutableSequence[str]
		sep = TableSeparator(self.char_set.horizontal, self.lengths)
		if self.title is not None :
			res = [
				sep.build(self.char_set.top_left, sep.char, self.char_set.top_right), 
				f"{self.char_set.vertical} {proper_center(self.title, len(sep) - 4)} {self.char_set.vertical}",
				sep.build(self.char_set.left, self.char_set.top, self.char_set.right)
			]
		else :
			res = [sep.build(self.char_set.top_left, self.char_set.top, self.char_set.top_right)]
		middle_sep = sep.build(self.char_set.left, self.char_set.cross, self.char_set.right)
		res.append(self._build_names())
		res.append(middle_sep)
		for i in range(len(self.rows)) :
			# res.append(middle_sep)
			res.append(self._build_row(i))
		res.append(sep.build(self.char_set.bottom_left, self.char_set.bottom, self.char_set.bottom_right))
		return res

	def print(self) :
		for line in self.build_table() :
			print(line)



if __name__ == '__main__' :
	builder = TableBuilder(['id', 'lang', 'hello'], None)
	builder.add_row(['1', 'en', 'hello'  ])
	builder.add_row(['2', 'fr', 'bonjour'])
	builder.add_row(['3', 'es', 'hola'   ])
	builder.add_row(['4', 'de', 'ciao'   ])
	builder.print()
