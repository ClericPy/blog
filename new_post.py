from torequests.utils import ttime, re
import os


fname = re.sub(r"\D", "", ttime())
name = f'posts/{fname}.md'
os.system(f'hugo new {name}')
