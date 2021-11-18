import re

pattern = 'https://v\.redd\.it/([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'
message = 'https://v.redd.it/d7p8cwap9x171'

match = re.search(pattern, message)
matchedString = match.group(0)

print(matchedString)
