import requests, time, os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from html2image import Html2Image
from io import BytesIO

def scrape_image(element = None, url = "", requests_headers = None):
  for i in range(3):
    try:
      if element != None: url = element["src"]
      response = requests.get(url, headers=requests_headers)
      image_stream = BytesIO(response.content)
      return image_stream
    except Exception as e:
      print(e)
      print(f"Scraping image failed. Attemps: {i+1}")
      time.sleep(0.5)
  image = open("./placeholder.png", "rb")
  image_stream = BytesIO(image.read())
  return image_stream

def news_filter(url, element):
  domain = urlparse(url).netloc

  inner_news = element.find_all("p", {"class": None})
  image_element = None
  if (domain.endswith("cnnindonesia.com")):
    image_element = element.find("img", {"class": "w-full"})
  elif (domain.endswith("kompas.com")):
    image_wrap = element.find("div", {"class": "photo__wrap"})
    if (image_wrap is not None):
      image_element = image_wrap.find("img")
  elif (domain.endswith("detik.com")):
    image_element = element.find("img", {"class": "img-zoomin"})
  elif (domain.endswith("tribunnews.com")):
    image_element = element.find("img", {"class": "imgfull"})
  elif (domain.endswith("kumparan.com")):
    inner_news = element.find_all("span", {"class": "Textweb__StyledText-sc-1ed9ao-0"})
    image_element = element.find("img", {"class": "ImageLoaderweb__StyledImage-sc-zranhd-0"})
  elif (domain.endswith("bola.com")):
    image_element = element.find("img", {"class": "read-page--photo-gallery--item__picture-lazyload"})
  elif (domain.endswith("kincir.com")):
    image_element = element.find("img", {"class": "wp-post-image"})
  elif (domain.endswith("cnn.com")):
    inner_news = element.find_all("p", {"class": "paragraph"})
    image_element = element.find("img", {"class": "image__dam-img"})
  elif (domain.endswith("bbc.com")):
    inner_news = element.find_all("p", {"class": "hxuGS"})
    image_element = element.find("img", {"class": "dvfjxj"})
  elif (domain.endswith("cnbcindonesia.com")):
    image_element = element.find("img", {"class": "w-full object-cover"})
  elif (domain.endswith("liputan6.com")):
    image_element = element.find("img", {"class": "read-page--photo-gallery--item__picture-lazyload"})
  elif (domain.endswith("tempo.co")):
    image_element = element.find("img", {"class": "w-full h-auto"})
  elif (domain.endswith("metrotvnews.com")):
    image_element = element.find("img", {"class": "news-image"})
  elif (domain.endswith("abcnews.go.com")):
    inner_news = element.find_all("p", {"class": "EkqkG"})
    image_element = element.find("img", {"class": "hsDdd"})

  image = scrape_image(element=image_element)

  return {"inner_news": inner_news, "image": image}

def get_news(url, requests_headers):
  res_arr = []
  image = None
  for i in range(3):
    try:
      response = requests.get(url=url, headers=requests_headers)
      element = BeautifulSoup(response.content, "html.parser")
      filtered = news_filter(url=url, element=element)
      image = filtered["image"]
      for e in filtered["inner_news"]:
        text = e.text
        if text != "":
          res_arr.append(text)
      if res_arr == []:
        print(f"Getting news failed. Attemp: {i+1}")
        time.sleep(0.5)
      else:
        break
    except Exception as e:
      print(e)
      print(f"Getting news failed. Attemp: {i+1}")
      time.sleep(0.5)
  return {"news": " ".join(res_arr), "img": image}

def get_classement(url):
  domain = urlparse(url).netloc
  response = requests.get(url)
  element = BeautifulSoup(response.content, "html.parser")

  cache_dir = ".cache/"
  os.makedirs(cache_dir, exist_ok=True)

  hti = Html2Image()
  hti.output_path = cache_dir
  style_file = element.find("link", {"rel": "stylesheet"})
  style_inline = element.find("style")
  table = ""
  if domain.endswith("detik.com"):
    custom_style = "<style>.new_klasemen .klasemen-table > span:nth-of-type(3) { width: 40px; justify-content: center; } .new_klasemen .klasemen-table > span:nth-of-type(2) { width: 350px; justify-content: flex-start; }</style>"
    rows = element.find_all("div", {"class": "klasemen-table"})[:16]
    for row in rows:
      all_spans = row.find_all("span", recursive=False)
      row_class = " ".join(row["class"])
      spans_without_more = "".join(str(x) for x in all_spans[1:])
      new_row = "".join(f"<div class=\"{row_class}\">{spans_without_more}</div>")
      table += new_row
    hti.screenshot(html_str=f"{str(style_file)}{custom_style}<div class=\"new_klasemen\">{table}</div>", size=(895,770))
  elif domain.endswith("mpl.com"):
    custom_style = "<style>table { width: 1000px } thead { background-color: black; color: white !important; } tbody > tr:nth-child(2n) { background-color: #eaeaea } tr * { text-align: center; align-items: center }</style>"
    table = element.find("div", {"id": "standing-regular-season"})
    hti.screenshot(f"{str(style_file)}{str(style_inline)}{custom_style}{table}", size=(1000, 470))