import requests
from bs4 import BeautifulSoup
import filecmp
import os, sys
import difflib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


root_url = "https://sites.google.com"
index_url = root_url + "/site/csc110winter2015/home"

def get_site_links():
    '''
    Gets links from the website's list items HTML elements.
    '''
    response = requests.get(index_url)
    soup = BeautifulSoup(response.text)
    links =  [a.attrs.get('href') for a in soup.select('li.topLevel a[href^=/site/csc110winter2015/]')]
    return links

def write_links_file():
    '''
    Writes the links.txt file from the website's links 
    '''
    links = get_site_links()
    with open("links.txt", mode='wt', encoding='utf-8') as out_file:
        out_file.write('\n'.join(links))

def write_pages_files():
    '''
    Writes the various page files from the website's links 
    '''
    with open("links.txt") as links:
        for page in links:
            site_page = requests.get(root_url + page)
            soup = BeautifulSoup(site_page.text)
            with open(page.replace("/",".") + ".txt", mode='wt', encoding='utf-8') as out_file:
                out_file.write(str(soup))

def check_links():
    '''
    Checks to see if links have changed since the last time the program was run.
    '''
    if filecmp.cmp("links.txt", "previous_links.txt") == True:
        ## If link data hasn't changed, return false
        pass
    else:
        d = difflib.Differ()
        previous_links = open("previous_links.txt").readlines()
        links =  open("links.txt").readlines()
        diff = d.compare(previous_links, links)
        for difference in diff:
            if '- ' in difference:
                removed = print(difference + "Was a removed page from the CSC110 website since the last time checked.")
                return removed
            elif '+ ' in difference:
                added = print(difference + "Was an added page to the CSC110 website since the last time checked.")
                return added
def check_pages():
    '''
    Checks to see if pages have changed since the last time the program was run.
    '''
    with open("links.txt") as links:
        changed_pages = []
        for page in links:
            page = page.replace("/",".")
            if filecmp.cmp("previous_" + page + ".txt", page + ".txt") == True:
                ## If page data hasn't changed, do nothing
                 pass
            else:
                ## If page data has changed, then write the changed page data to a list
                changed_pages.append(root_url + page.replace(".","/").strip())
        return changed_pages
                
def try_read_links_file():
    '''
    Tries to read the links.txt file; if links.txt is found, then rename links.txt to previous_links.txt
    '''
    try:
        os.rename("links.txt", "previous_links.txt")
        write_links_file()
    except (OSError, IOError):
        print("No links.txt file exists; creating one now.")
        write_links_file()
        try_read_links_file()

def try_read_pages_files():
    '''
    Tries to read the pages .txt files; if pages .txt are found, then rename the pages .txt files to previous_ pages .txt
    '''
    with open("links.txt", mode='r', encoding='utf-8') as pages:
        for page in pages:
            try:
                os.rename(page.replace("/",".") + ".txt", "previous_" + page.replace("/",".") + ".txt")
            except (OSError, IOError,):
                print("No pages .txt file exists; creating them now.")
                write_pages_files()
                try_read_pages_files()
        write_pages_files()

def send_mail():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    ## Say ehlo to my lil' friend!
    server.ehlo()
    ## Start Transport Layer Security for Gmail
    server.starttls()
    server.ehlo()
    if check_pages() or check_links():
        server.login("No email here, either!", "No password for you!")
        fromaddr = "derp."
        toaddr = "herpa"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Incoming CSC110 website changes!"
        if check_pages():
            # Can't return list and concatenate string; implemented here for check_pages()
            changed_pages = str(check_pages()) + " Is/are pages that've changed since last checked.\n\n"
            msg.attach(MIMEText(changed_pages, 'plain'))
        if check_links():
            changed_links = str(check_links())  
            msg.attach(MIMEText(changed_links, 'plain'))
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
    
def main():
    try_read_links_file()
    try_read_pages_files()
    check_links()
    check_pages()
    send_mail()
main()
