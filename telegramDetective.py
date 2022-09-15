# -*- coding: utf-8 -*-
"""
Author: psjs97 (https://github.com/psjs97)
"""

# Libraries
import argparse
import os, requests
from datetime import datetime
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
import requests

# Arguments
parser = argparse.ArgumentParser(description="Telegram Detective script: get messages from specific Telegram's channel or group according to customizable wordlist.",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--directory", help="Input directory with HTML messages from Telegram's channel", required=True)
parser.add_argument("-w", "--wordlist", help="Wordlist to detect Telegram's messages that match with any word.", required=True)
args = parser.parse_args()


# Generic functions
def get_current_datetime():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("Script execution datetime: ", dt_string)	

def banner():
    # Script banner
    os.system('color')
    print('\033[92m' + '\033[01m' + """
|''||''|        '||`                                         '||'''|.          ||                   ||                       
   ||            ||                                           ||   ||          ||                   ||     ''                
   ||    .|''|,  ||  .|''|, .|''|, '||''|  '''|.  '||),,(|,   ||   || .|''|, ''||''  .|''|, .|'', ''||''   ||  \\  // .|''|, 
   ||    ||..||  ||  ||..|| ||  ||  ||    .|''||   || || ||   ||   || ||..||   ||    ||..|| ||      ||     ||   \\//  ||..|| 
  .||.   `|...  .||. `|...  `|..|| .||.   `|..||. .||    ||. .||...|' `|...    `|..' `|...  `|..'   `|..' .||.   \/   `|...  
                                ||                                                                                           
                             `..|'                                                                                           
    """ + '\033[0m')
    print('\033[93m' + '\033[01m' +"[ Author: psjs97 ] | https://github.com/psjs97\n" + '\033[0m')

# Script functions
def read_whitelist(whitelist_file):
    with open(whitelist_file) as file:
        whitelist = file.readlines()
        whitelist = [word.rstrip() for word in whitelist]
        whitelist = [word.lower() for word in whitelist]
    return whitelist


def read_html_files(html_path):
    html_files_dict = {}
    n = 0
    for file in os.listdir(html_path):
        if not file.endswith('.html'):
            continue
        n += 1
        with open(os.path.join(html_path, file), 'r', encoding = "utf8") as f:
            lines = f.readlines()
            hmtl_page_str = '\t'.join([line.strip() for line in lines])
            html_files_dict[n] = hmtl_page_str
    return html_files_dict


def get_wordlist_messages(html_files_dict, wordlist):
    msgs_list = []
    first_file = True
    channel_group_title = ''
    for i in html_files_dict:
        soup = BeautifulSoup(html_files_dict[i], features="lxml")

        channel_group_title = soup.find_all("div", class_="text bold")[0].text.strip() # Channel or group title
        aux_list = soup.find_all("div", class_="text") # Filtered by div class="text"
        
        if len(aux_list) > 0:
            if first_file:
                channel_group_title = aux_list.pop(0) # Set first element (channel's title)
                first_file = False
            else:
                aux_list.pop(0) # Set first element (channel's title)
        
        msgs_list.extend(aux_list)

    msgs_list = list(set(msgs_list)) # Remove duplicated msgs
    return channel_group_title, msgs_list

def get_match_messages(msgs_list, wordlist):
    # Filter messages that match with 'wordlist'
    msg_match_result_dict = {}
    for msg in msgs_list:
        if msg is None:
            pass
        match_word_list = []
        for word in wordlist:
            if str(word).lower() in str(msg).lower():
                match_word_list.append(word)
        if len(match_word_list) > 0:
             msg_match_result_dict[msg] = match_word_list
    
    return msg_match_result_dict
    

def create_html_page_results(msg_match_result_dict, channel_group_title):
    with open(os.path.join('resources', 'html_template_report.html'), "r", encoding='utf-8') as f:
        html_model= f.read()
    html_model = html_model.replace('GROUP', channel_group_title)
    soup = BeautifulSoup(html_model, features="lxml")
    headTag = soup.find('h1')
    headTag = soup.body
    for msg in msg_match_result_dict.keys():
        headTag.append(msg)
        new_tag = soup.new_tag("hr")
        headTag.append(new_tag)
    filename = channel_group_title + '_report.html'
    with open(os.path.join('.', filename), "wb") as file:
        file.write(soup.encode('utf-8'))
    print('Report html with matched messages: ' + os.path.join('.', filename))


# Main function
def main():
    banner()
    get_current_datetime()
    wordlist = read_whitelist(args.wordlist)
    html_files_dict = read_html_files(args.directory)
    channel_group_title, msgs_list = get_wordlist_messages(html_files_dict, wordlist)
    print("Channel/group name: " + '\033[92m' + '\033[01m' + channel_group_title + '\033[0m')
    print("Total messages in channel/group: " + '\033[92m' + '\033[01m' + str(len(msgs_list)) + '\033[0m')
    msg_match_result_dict = get_match_messages(msgs_list, wordlist)
    print("Total messages found that match with any word: " + '\033[93m' + '\033[01m' + str(len(msg_match_result_dict.keys())) + '\033[0m' + '/' + '\033[92m' + '\033[01m' + str(len(msgs_list)) + '\033[0m')
    soup = create_html_page_results(msg_match_result_dict, channel_group_title)
    
    
if __name__=='__main__':
    main()

