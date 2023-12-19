import requests
from bs4 import BeautifulSoup
import difflib
import json

def clean_price(price):
    price = str(price).replace('$', '').replace(' ', '')
    # Convert the price to a float
    try:
        price = float(price)
    except:
        pass
    return price


def get_details(s):  # get attributes from the query entered by the user
    sl = s.lower()
    details = {'bundle':False, 'quantity':False, 'type':False}
    bundles = ['box', 'pack', 'tin']
    for bundle in bundles:
        bundle_of = bundle + ' of'
        if bundle_of in sl:
            details['bundle'] = bundle
            num = sl.split(bundle_of)[1]
    if details['bundle']:
        break_next = False
        for i in num.strip().split():  # extract quantity and type
            if break_next:
                details['type'] = i
                break
            if i.isdigit():
                details['quantity'] = i
                break_next = True
    return details


"""
https://bonitasmokeshop.com/{product_id}/
"""
def get_bonita_smoke_shop_price(product_name):
    details = get_details(product_name)
    product_lower = product_name.lower()
    url = ''
    # Get the page content
    if 'bonitasmokeshop.com' in product_lower:
        if 'http' not in product_lower:
            # add https:// to url
            pass
        url = product_name
    elif '-' in product_name:  # product id provided
        url = f"https://www.bonitasmokeshop.com/{product_name}"
    else:
        # Make the product name URL-friendly
        url = "https://www.bonitasmokeshop.com/" + product_name.strip().replace(' ', '-')
    
    data = {
        'website':'BonitA SMOKE SHOP',
        'title':"-",
        'img':"-",
        'id': "-",
        'msrp': "-",
        'white': "-",
        'error': True,
        'url': url
    }
    
    for i in url.split('?')[0].split('#')[0].split('/')[::-1]:
        if i:
            data['id'] = i
            break
    error = 0
    response = requests.get(url)
    if response.status_code != 200:
        response = requests.get('https://bonitasmokeshop.com/search.php?search_query=' + "+".join(product_name.split()))
        data['url'] = response.text.split("card-title")[1].split('href="')[1].split('"')[0]
        response = requests.get(data['url'])
        
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # extract img
        try:
            target_div = soup.find('div', {'class', 'productImageSlider'})
            data['img'] = target_div.find('img').get('src')
        except:
            error += 1
        try:
            target_h1 = soup.find("h1", {'class':'productView-title'})
            data['title'] = target_h1.text.strip()
        except:
            error += 1
        price_section = soup.find('div', {'class':'msrp-sale-regular-price-section withoutTax'})
        try:
            target_div = price_section.find('span', {'class': 'price price--withoutTax'})
            data['white'] = clean_price(target_div.text.strip())
        except:
            error += 1
        try:
            target_div = price_section.find('span', {'class': 'price price--rrp'})
            data['msrp'] = clean_price(target_div.text.strip())
        except:
            error += 1

        # properties to map from metadata to data dictionary
        props = {
            'product:price:amount': 'price',
            'product:price:currency': 'currency',
            'keywords': 'keywords',
            'og:type': 'type',
            'og:title': 'title',
            'og:description': 'description',
            'og:image': 'img'
        }
        # get all the available properties from the page
        for meta in soup.findAll('meta'):
            attrs = meta.attrs
            prop = attrs.get('property')
            if prop in props:
                content = attrs.get('content')
                if content:
                    data[props[prop]] = content
        data['error'] = False
    return data

"""
https://www.neptunecigar.com/cigars/{product_id}
"""
def get_neptune_cigar_price(product_name):
    details = get_details(product_name)
    product_lower = product_name.lower()
    url = ''
    error = 0
    # Get the page content
    if 'neptunecigar.com' in product_lower:
        if 'http' not in product_lower():
            # add https:// to url
            pass
        url = product_name
    elif 'cigars/' in product_lower:
        # build partial link
        if product_name[0] != '/':
            url += '/'
        url = "https://www.neptunecigar.com" + url + product_name
    elif '-' in product_name:  # product id provided
        url = f"https://www.neptunecigar.com/cigars/{product_name}"
    else:
        # Make the product name URL-friendly
        url = "https://www.neptunecigar.com/cigars/" + product_name.replace(' ', '-')
    
    data = {
        'website':'Neptune Cigar',
        'img':"-",
        'title':'title',
        'id': "-",
        'msrp': "-",
        'white': "-",
        'error': True,
        'url': url
    }
    
    for i in url.split('?')[0].split('#')[0].split('/')[::-1]:
        if i:
            data['id'] = i
            break
    
    response = False
    # response = requests.get(url)  # get data from target page
    if response:
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                target_img = soup.find('img', {'class': "pr_img-responsive lazy img_background"})
                data['img'] = target_img.get("data-src")
            except:
                error += 1
            msrp = []
            row = soup.findAll('td',{'class', 'product_table_cells'})
            for i in row:
                child = i.findChild()
                if child:
                    if child.text.strip() == "MSRP:":
                        msrp.append(clean_price(i.text.strip().split(':')[1]))
            white = []
            row = soup.findAll('td', {'class': 'product_table_cells important_price highlightedInfo'})
            for i in row:
                white.append(clean_price(i.find(string=True)))
            if white:
                data['white'] = min(white)
            if msrp:
                data['msrp'] = min(msrp)
            data['error'] = False
    else:  # search product_name from neptunecigar.com/search 
        response = requests.get('https://www.neptunecigar.com/search?text=' + product_name)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            item = soup.find('div', {'class':'product_item'})
            props = {
                'url': 'url',
                'price': 'price',
                'priceCurrency': 'currency',
                'keywords': 'keywords',
                'title': 'title',
                'description': 'description',
                'image': 'img'
            } # ratingValue, ratingCount

            # get metadata from html page
            for meta in item.findAll('meta'):
                attrs = meta.attrs
                prop = attrs.get('itemprop')
                if prop in props:
                    content = attrs.get('content')
                    if content:
                        data[props[prop]] = content
            
            target = None
            targets = []
            bundle = False
            # finding the best match type of product with the given query
            for row in item.findAll('tr')[1:]:  
                bundle = row.findAll('td')[0]
                bundle_lower = bundle.text.lower()
                if 'of' in bundle_lower:
                    bundle = True
                    if details['quantity']:
                        if details['quantity'] in bundle_lower:
                            if details['type']:
                                if details['type'] in bundle_lower:
                                    target = bundle
                            else:
                                price = 10**10
                                # get meta data from target row
                                for meta in item.findAll('meta'):
                                    attrs = meta.attrs
                                    prop = attrs.get('itemprop')
                                    if prop == 'price':
                                        content = attrs.get('content')
                                        if content:
                                            try:
                                                price = float(content)
                                            except:
                                                pass
                                targets.append((price, row))
                    elif details['type']:
                        if details['type'] in bundle_lower:
                            target = bundle
                    else:
                        price = 10**10
                        # get metadata from target row
                        for meta in item.findAll('meta'):
                            attrs = meta.attrs
                            prop = attrs.get('itemprop')
                            if prop == 'price':
                                content = attrs.get('content')
                                if content:
                                    try:
                                        price = float(content)
                                    except:
                                        pass
                        targets.append((price, row))
            if target:
                pass
            elif targets:
                _, target = min(targets, key = lambda t: t[0])
            else:
                target = item.findAll('tr')[-1]
            for meta in target.findAll('meta'):  # update data with target data
                attrs = meta.attrs
                prop = attrs.get('itemprop')
                if prop in props:
                    content = attrs.get('content')
                    if content:
                        data[props[prop]] = content
            row = target.findAll('td')
            try:
                data['msrp'] = clean_price(row[1].text)
            except:
                error += 1
            try:
                data['title'] = item.find('a', {'class':'product_name'}).text.strip()
            except:
                error += 1
            data['error'] = False
    if 'white' not in data or data['white'] == '-':
        data['white'] = data['price']
    return data



"""
https://www.cigarsinternational.com/p/anything-here-is-ignored/{product_id}/
"""
def get_cigars_international_price(product_name):  # works with anyone of these: product id, product name, product url, partial url, etc
    url = ''
    error = 0
    details = get_details(product_name)
    data = {
        'website':'Cigars International',
        'img':"-",
        'id': "-",
        'msrp': "-",
        'white': "-",
        'error': 0
    }

    # Make the product name URL-friendly - not required
    # product_name = product_name.replace(' ', '-')

    if product_name.isdigit():  #  work with product_id provided
        url = f"https://www.cigarsinternational.com/p/anything-here-is-ignored/{product_name}/"
        
    elif 'cigarsinternational.com' in product_name.lower():  #  work with URL provided
        if 'http' not in product_name.lower():
            # add https:// to url
            pass
        url = product_name
        
    elif '/' in product_name:  # work with partial link provided
        for i in product_name.strip().split('/')[::-1]:  # extract product id from the end
            if i.isdigit():
                url = f"https://www.cigarsinternational.com/p/anything-here-is-ignored/{i}/"
                break
        
    # now extact the prices
    if not url:
        # work with product_name provided - search query
        url = f"https://www.cigarsinternational.com/shop/?q={'+'.join(product_name.strip().split())}"
   
        # Get the page content
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            url = soup.find('a', {'class':'title'}).get('href')
            if 'cigarsinternational.com' not in url.lower():
                url = "https://www.cigarsinternational.com" + url

    # Get the page content
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        x= soup.findAll('span', {'class': 'offer-text price-msrp'})
        try:
            data['description'] = soup.find('div', {'class':'descrption-div'}).find('div',{'class':'p'}).text
        except Exception as e:
            print(e)
        try:
            data['img'] = soup.findAll('img', {'class': 'img-fluid lazyloaded'})[0].get('src')
        except Exception as e:
            print(e)
        try:
            data['msrp'] = min([clean_price(i.text) for i in x])
        except Exception as e:
            print(e)
        x= soup.findAll('span', {'class': 'price-product cost-text'})
        try:
            data['white'] = min([clean_price(i.text) for i in x])
        except Exception as e:
            print(e)
        
        i = 0
        blind = False
        products = response.text.split('"products":')[1]
        for c in products:
            i+=1
            if c == '}':
                blind = False
            elif c == '{':
                blind = True
            elif not blind and c == ']':
                break
        try:
            products = json.loads(products[:i])
            names = [product['fullName']+' '+product['pack'] for product in products]
            name = difflib.get_close_matches(product_name, names)[0]
        except:
            products = []
            error += 1
        for product in products:
            if product['fullName']+' '+product['pack'] == name:
                try:
                    data['url'] = product['imageUrl']
                except:
                    error += 1
                try:
                    data['price'] = product['price']
                except:
                    error += 1
                try:
                    data['title'] = product['fullName']
                except:
                    error += 1
                try:
                    data['pack'] = product['pack']
                except:
                    error += 1
                id = product.get('skuId')
                if id:
                    try:
                        # get msrp from the id of the product
                        target_div = soup.findAll('div', {'class':"prod-grid-nodeals"})[-1]
                        for i in target_div.findChildren("div" , recursive=False):
                            if id in str(i):
                                data['msrp'] = clean_price(i.find('span', {'class': 'price-product cost-text'}).text)
                                data['white'] = data['price']
                                break
                    except:
                        error += 1
                break
    data['error'] = error
    data['url'] = url
    for i in url.strip().split('/')[::-1]:  # extract product id from the end
        if i.isdigit():
            data['id'] = i
            break

    return data
