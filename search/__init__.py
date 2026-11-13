# Searches the text of PDF, Word, spreadsheet, JSON and plain-text files.
#
#   readers/   turn each kind of file into (pageNumber, text) blocks
#   text.py    cleanText, shared by the readers and the search prompt
#   terms.py   parse what the user typed and build the regex for it
#   matching   run the regex over the blocks of one file or a folder
#   report.py  print the readable report or write JSON
#   prompts.py the questions asked on the terminal
