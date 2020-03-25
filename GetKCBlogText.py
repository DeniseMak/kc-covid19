import requests
import urllib.request
import time
from bs4 import BeautifulSoup

def GetKCBlogText(url):
  kcBlogEntry = requests.get(url)
  if kcBlogEntry.status_code != 200:
    raise Exception(
      "Request failed with {0}: {1}" % (kcBlogEntry.status_code, kcBlogEntry.text))

  kcBlogEntry = kcBlogEntry.text
  soup = BeautifulSoup(kcBlogEntry, "html.parser")
  article = soup.article
  # At command prompt, have issues with printing "\u2014" char; in other
  # contexts it probably doesn't matter, but for the moment replacing here.
  return "\n\n".join(
      p.text.replace("\u2014",'--') for p in article.find_all("p"))


def main():
  blogEntryUrl = "https://www.kingcounty.gov/depts/health/news/2020/March/24-covid.aspx"
  text = GetKCBlogText(blogEntryUrl)
  print(text)  

if ( __name__ == "__main__"):
    main()
