
#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2022 Kevin Liu
# Elaina Voice Assistant (single & multi core) 
# MIT License
# Hosted at: https://github.com/ReZeroE/Elaina-Voice-Assistant
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from termcolor import colored

eprint_colors = {
    'dev'   : 'red',        # dev
    'user'  : 'green',      # for user
    'admin' : 'cyan'        # for admin
}

uprint_colors = {
    'dev'   : 'red',        # dev
    'user'  : 'cyan'        # user input
}

def eprint(text, dev=False, user=False, admin=False):
    if dev:
        prefix = colored("Elaina-Dev", eprint_colors['dev'])
    elif user:
        prefix = colored("Elaina", eprint_colors['user'])
    elif admin:
        prefix = colored("Elaina-Admin", eprint_colors['admin'])
    print(f"[{prefix}] {text}") 
        
        
def uprint(text, dev=False):
    if dev:
        prefix = colored("User-Dev", uprint_colors['dev'])
    else:
        prefix = colored("User", uprint_colors['user'])
    print(f"[{prefix}] {text}")
        

# uprint("hello world", dev=False)