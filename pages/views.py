from django.shortcuts import redirect, render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests
import random
import urllib.parse
import pymongo
from pymongo import MongoClient


print("------BASLADI-------")

a= "12345"
client = MongoClient("mongodb+srv://melekmbbal:"+a+"@datas.ws7ckaq.mongodb.net/?retryWrites=true&w=majority&appName=datas")
db = client["Yazlab_Project"] # database
collection = db["datas"] # collection

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    
url = "https://dergipark.org.tr/tr/search?q=deep+learning&section=articles"

search_query = None

arama_url = urllib.parse.quote_plus("deep learning")

url1 = f"https://dergipark.org.tr/tr/search?q={arama_url}"



def get_data(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    return soup

soup = get_data(url1)

def find_links(soup):
    links = soup.find_all('h5', class_='card-title')
    link_result = []
    for link in links[:10]:
        link_result.append(link.a['href'])
        
    return link_result

links = find_links(soup)

def get_title(soup):
    titles = soup.find_all('h5', class_='card-title')
    title_result = []
    for title in titles[:10]:  
        title_result.append(title.a.text.strip())
        
    return title_result
        
def get_authours(soup):
    authors_result = []    
    for i in range(len(find_links(soup))):
        soup1 = get_data(find_links(soup)[i]) 
        authors = soup1.find_all('p', class_='article-authors') 
        for a in authors[:1]:  
            authors_result.append(' '.join(a.text.strip().split()))
            
    return authors_result
                
def get_dates(soup):   
    dates = soup.find_all('small', class_='article-meta')   
    date_result = []
    for date in dates[:20]:
        text = date.get_text(strip=True)
        if '(' in text and ')' in text:
            year = text[text.find('(') + 1: text.find(')')]
            date_result.append(year)
            
    return date_result
            
def get_types(soup):    
    type = soup.find_all('span', class_='badge badge-secondary')
    type_result = []
    for t in type[:10]:
        type_result.append(t.text.strip())
        
    return type_result

def get_publishers(soup):    
    publisher_result = []  
    for i in range(len(find_links(soup))):
        soup1 = get_data(find_links(soup)[i]) 
        publisher = soup1.find_all('h1', id='journal-title') 
        for p in publisher[:10]:  
            publisher_result.append(p.text.strip())  
            
    return publisher_result

def get_keywords(soup):
    keywords_result = []    
    for i in range(len(find_links(soup))):
        soup1 = get_data(find_links(soup)[i]) 
        keywords = soup1.find_all('div', class_='article-keywords data-section')
        for k in keywords[:9]:  
            if k.p:
                keywords_result.append(k.p.text.strip()) 
                
    return keywords_result

def get_sums(soup):
    sums_result = []    
    for i in range(len(find_links(soup))):
        soup1 = get_data(find_links(soup)[i]) 
        sums = soup1.find_all('div', class_='article-abstract data-section') 
        for a in sums:  
            summary = a.p.text.strip()
            if summary:  # Boş özetlerin eklenmemesi için kontrol
                sums_result.append(summary)
                

    if len(sums_result) < 10:
            i = len(sums_result)
            for i in range(10):
                sums_result.append("Özet bulunamadı")
                
            
    return sums_result
            
def get_id():
    id = []
    for _ in range(10):
        rastgele_sayi = random.randint(1, 999999)        
        while rastgele_sayi in id:
            rastgele_sayi = random.randint(1, 999999)
        id.append(rastgele_sayi)
    
    return id

def pdf_links(soup):
        pdf_links_result = []
        for i in range(len(find_links(soup))):
                soup1 = get_data(find_links(soup)[i])
                links = soup1.find_all('div', id='article-toolbar')
                
                for link in links[:10]:
                        pdf_links_result.append("https://dergipark.org.tr"+link.a['href'])
                        
        return pdf_links_result
            
pdf_url = pdf_links(soup)

print(pdf_url)

def save_datas(soup):
        soup1 = soup
        for i in range(10):
                data = {
                "id": get_id()[i],
                "title": get_title(soup1)[i],
                "author": get_authours(soup1)[i],
                "date": get_dates(soup1)[i],
                "type": get_types(soup1)[i],
                "publisher": get_publishers(soup1)[i],
                "keyword": get_keywords(soup1)[i],
                "summary": get_sums(soup1)[i],
                "pdf_url": pdf_links(soup1)[i]
                }
                collection.insert_one(data)
                print(i+1, ". data saved to MongoDB")
                
title = get_title(soup)

def download_pdf(pdf_url):
        for i in range(len(pdf_url)):
                save_path = "C:/Users/90546/OneDrive/Masaüstü/Yazlab/pdf_indir/" + str(i) + ".pdf"  # Yolun ters eğik çizgilerle belirtilmesi
                try:
                        response = requests.get(pdf_url[i])
                        # HTTP isteği başarılı mı diye kontrol edelim
                        if response.status_code == 200:
                        # Dosyayı binary modda yazıp indirelim
                                with open(save_path, 'wb') as pdf_file:
                                        pdf_file.write(response.content)
                                print("PDF başarıyla indirildi.")
                        else:
                                print(f"HTTP hatası: {response.status_code}")
                except Exception as e:
                        print(f"Hata: {e}")

def pull_datas():
        cursor = collection.find({})

        id_list = []
        title_list = []
        author_list = []
        date_list = []
        type_list = []
        publisher_list = []
        keyword_list = []
        summary_list = []
        pdf_url_list = []

        for document in cursor:
                id_list.append(document["id"])
                title_list.append(document["title"])
                author_list.append(document["author"])
                date_list.append(document["date"])
                type_list.append(document["type"])
                publisher_list.append(document["publisher"])
                keyword_list.append(document["keyword"])
                summary_list.append(document["summary"])
                pdf_url_list.append(document["pdf_url"])
                
        zip_list = zip(id_list, title_list, author_list, date_list, type_list, publisher_list, keyword_list, summary_list, pdf_url_list)
                
        return zip_list

def index(request):
    zip_list = pull_datas()
    context = {
                'zip_list': zip_list
        }

    #print (pull_datas())
        
    return render(request, 'pages/index.html', context)


def search(request):
    if request.method == 'POST':
        search_input = request.POST.get('search_input', '')  # Formdan gelen veriyi al

        arama_url1 = urllib.parse.quote_plus(search_input)
        url2 = f"https://dergipark.org.tr/tr/search?q={arama_url1}"
        soup2 = get_data(url2)
        
        collection.delete_many({}) 
        save_datas(soup2)
        pull_datas()
        download_pdf(pdf_url)

        zip_list = pull_datas()
        context = {
                    'zip_list': zip_list
            }
        
        return render(request, 'pages/search.html', context)
    else:
        return HttpResponse("HATA")  # İsteğin POST olmadığı durumu işle


def detail(request):
    title = request.GET.get('title', '')
    author = request.GET.get('author', '')
    date = request.GET.get('date', '')
    type = request.GET.get('type', '')
    publisher = request.GET.get('publisher', '')
    keyword = request.GET.get('keyword', '')
    summary = request.GET.get('summary', '')
    pdf_url = request.GET.get('pdf_url', '')
    
    # Veriyi oturumda saklayın
    request.session['pdf_url'] = pdf_url
    
    return render(request, 'pages/detail.html', {
        'title': title,
        'author': author,
        'date': date,
        'type': type,
        'publisher': publisher,
        'keyword': keyword,
        'summary': summary
    })
    
def open_pdf(request):
    # Oturumdan pdf_url'yi alın
    pdf_url = request.session.get('pdf_url', '')
    if pdf_url:
        return redirect(pdf_url)
    else:
        # Eğer pdf_url oturumda yoksa başka bir yere yönlendirin veya hata mesajı gösterin
        # Örneğin:
        return HttpResponse("PDF URL not found in session.")


print("------BİTTİ-------")