import time
import sys
import argparse
from bs4 import BeautifulSoup
import datetime
from urllib import request
import urllib.parse
import pandas as pd



def clean_date(date):
    return ''.join([i for i in date if i not in ('\r\n\t ')])

def clean_name(offer_name):
    return ''.join([i for i in offer_name if i not in ('\r\n\t')])

def today():
    return datetime.datetime.today().strftime('%d/%m/%Y')


# Search of offers and return dataframe
def find_offer(search_term):
    url = "https://www.tanitjobs.com/jobs/?listing_type%5Bequal%5D=Job&action=search&keywords%5Ball_words%5D="+search_term+"&GooglePlace%5Blocation%5D%5Bvalue%5D=&GooglePlace%5Blocation%5D%5Bradius%5D=50"
    resp = request.urlopen(url=url)
    html = resp.read()
    html_soup = BeautifulSoup(html,'html.parser')

    # get all offers
    offres  = html_soup.find_all('article')
    res = []
    for offre in offres:
        offer_date = clean_date(offre.find('div',{'class':'listing-item__date'}).text)
        # Only process offers for today's date
        if offer_date == today():
            position = clean_name(offre.find('a',{'class':'link'}).text)
            pos_desc =  offre.find('div',{'class':'listing-item__desc visible-sm visible-xs'}).text
            comp_name = clean_name(offre.find('span',{'class':'listing-item__info--item listing-item__info--item-company'}).text)
            detail_link = offre.find('a',{'class':'link'})['href']
            res.append([position,comp_name,pos_desc,detail_link])

    result = pd.DataFrame(res,columns=['Position','Company Name','Pos Description','Link'])
    return result


last_res = pd.DataFrame()
if __name__ == "__main__":
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument("--search", help="Precise keywords")
            parser.add_argument("--cycle",default=100, type=int, help="Cycle time of the bot in ms")
            args = parser.parse_args()

        except : print(" [*] Hint: python search_jobs.py --search engineer --cycle 1000 "); exit(0)

        else:
            print("TanitJobs Bot Started")
            while True:
                now = time.strftime("%c")
                ls = last_res.shape[0]
                new_res = find_offer(args.search)
                # compare the result with last saved one
                ns = new_res.shape[0]
                # if the same dont do anything
                if ls == ns:
                    print("Nothing New  on ",now)
                # Save result to csv and print it to terminal
                else:
                    print("Found {} new offer(s) for today {}".format(ns-ls,now))
                    last_res = new_res
                    new_res.to_csv("result.csv", sep='\t')
                    for row in new_res.iterrows():
                        r = row[1]
                        print("Position:{}\nCompany: {} \nLink:{}".format(r[0],r[1].strip(),r[3]))
                        print("*"*10)

                # bot has to sleep for cycle and go back again
                time.sleep(args.cycle)
