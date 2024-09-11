import typing

TRIGGER = r"[^a-z0-9\s@<>#]"
IP_ADDRESS = r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
PORT = r"""(?:
  (?![7-9]\\d\\d\\d\\d) #Ignrore anything above 7....
  (?!6[6-9]\\d\\d\\d)  #Ignore anything abovr 69...
  (?!65[6-9]\\d\\d)   #etc...
  (?!655[4-9]\\d)
  (?!6553[6-9])
  (?!0+)            #ignore complete 0(s)
  (?P<Port>\\d{1,5})
)"""
IMAGE=r"(http)?s?:?(\\/\\/[^\"']*\\.(?:png|jpg|jpeg|gif|png|svg))"
EMOJI_NAME = r"^[a-zA-Z0-9_]+$"
EMOJI_URL = r"(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|jpeg|gif|png)"
