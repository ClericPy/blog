import subprocess


fname = input('Input the title:\n')
name = f'posts/{fname}.md'
subprocess.Popen(['hugo', 'new', name]).wait()
