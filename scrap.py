import re

line = "asfasdfasafsf_%4n.%e"

print re.sub( r'%*n', 'hahaha', line)