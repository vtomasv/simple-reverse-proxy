from flask import Flask, request, Response, render_template, url_for, make_response
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests
import os, ssl

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)
LOCAL_HOST = 'localhost:8000'
URI_LINK='http://'+LOCAL_HOST+'/proxy?url='

@app.route('/')
def index():
    return 'Tunnel ok'

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    if request.form.get('url')  or request.args.get('url'): 
        url = request.form.get('url')
        if (url ==None):
            url = request.args.get('url')
        response = requests.get(url)
        print(response.headers.get('content-type', ''))

        if response.status_code == 200 and 'text/html' not in response.headers.get('content-type', ''):
            # Si es una imagen, devolver el contenido directamente
            response_ = make_response(response.content)
            response_.headers['Content-Type'] = response.headers['content-type']
            response_.headers['Access-Control-Allow-Origin'] = '*'
            response_.headers['Content-Security-Policy'] = "unsafe-inline' data:" 
            return response_       
        
        if response.status_code == 200 and 'application/javascript' in response.headers.get('content-type', ''):
                # Si es una imagen, devolver el contenido directamente
            response_ = make_response(response.content)
            response_.headers['Content-Type'] = response.headers['content-type']
            response_.headers['Access-Control-Allow-Origin'] = '*'
            response_.headers['Content-Security-Policy'] = "unsafe-inline' data:" 
            return response_              

        headers = dict(response.headers)
        headers.pop('Content-Encoding', None)
        headers.pop('Transfer-Encoding', None)
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Content-Security-Policy'] = "unsafe-inline' data:" 

        
        html = response.content

        # convierte el contenido HTML en un objeto BeautifulSoup para manipulación
        soup = BeautifulSoup(html, "html.parser")

        """ 
        # Reemplazar todos los enlaces en la página web con enlaces de proxy reverso
        for link in soup.find_all(['a', 'link', 'script', 'img']):
            href = link.get('href')
            src = link.get('src')
            url = link.get('url')
            
            if href and not href.startswith(('http', '#')):
                link['href'] = url_for('proxy', url=href)
            elif src and not src.startswith('http'):
                link['src'] = url_for('proxy', url=src)
            elif url and not url.startswith('http'):
                link['url'] = url_for('proxy', url=url)
        """       
        # Convertir los enlaces relativos en absolutos
        for link in soup.find_all(['a', 'link', 'script', 'img']):
            href = link.get('href')
            src = link.get('src')
            url = link.get('url')
           
            if href:
                print (url_for('proxy', url=href))
                link['href'] = url_for('proxy', url=href) #urljoin(url, href)
            elif src:
                print ( url_for('proxy', url=src))
                link['src'] = url_for('proxy', url=src) #urljoin(url, src)
            elif url:
                print (urljoin(url, href))
                link['url'] = url_for('proxy', url=url)     #urljoin(url, url)

        #return response.content, response.status_code, headers
        return str(soup), response.status_code, headers

    return render_template('proxy.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)