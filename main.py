from bs4 import BeautifulSoup
from datetime import date
# pip install google-search-results
from serpapi import GoogleSearch
# pip install uule-grabber
import requests, uule_grabber, sqlite3, os, re, lxml, json
import pandas as pd
#import pymorphy2
from Constants import LOCATIONS


SERP_API = '<<YOUR_SERP_API_TOKEN HERE>>'

def sql_manipulation():
    """
    This function is made to change your database if you've sent some wrong data
    :return:
    """
    con = sqlite3.connect("database_results.db")
    cur = con.cursor()
    rec = cur.execute('UPDATE google_ads_scrap SET location = "New York,New York,United States" WHERE location = "Istanbul,Istanbul,Turkey"')
    con.commit()


def location_list():
    """
    You can generate different locations uule for a serpApi scraping
    :return:
    """
    answer = []
    city_params = pd.read_csv('geotargets.csv')
    for city in LOCATIONS:
        extract = city_params[city_params['Canonical Name'] == city]
        #answer [('Canonical Name','Country Code','uule'),...]
        answer.append((extract['Canonical Name'].values[0],extract['Country Code'].values[0].lower(), uule_grabber.uule(city)))
    return answer

def scrap_ads_get(keyword='buy'):
    """
    Original code by Dmitriy Zub:
    https://dev.to/dmitryzub/scrape-google-ad-results-with-python-166l
    This function returns you list of Google ads
    :return:
    """
    params = {
        "q": keyword,
        "hl": "en",
        "gl": "au"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }

    html = requests.get("https://www.google.com/search?", params=params, headers=headers)
    soup = BeautifulSoup(html.text, "lxml")

    ad_results = []

    for index, ad_result in enumerate(soup.select(".uEierd"), start=1):
        title = ad_result.select_one(".v0nnCb span").text
        website_link = ad_result.select_one("a.sVXRqc")["data-pcu"]
        ad_link = ad_result.select_one("a.sVXRqc")["href"]
        if ad_result.select_one(".ob9lvb").text:
            displayed_link = ad_result.select_one(".ob9lvb").text
        else:
            displayed_link = None
        tracking_link = ad_result.select_one(".v5yQqb a.sVXRqc")["data-rw"]
        snippet = None if ad_result.select_one(".MUxGbd div").text is None else ad_result.select_one(".MUxGbd div").text
        phone = None if ad_result.select_one("span.fUamLb span") is None else ad_result.select_one(
            "span.fUamLb span").text

        inline_link_text = [title.text for title in ad_result.select("div.bOeY0b a")]
        if len(inline_link_text) < 4:
            while len(inline_link_text) < 4:
                inline_link_text.append('')
        inline_link = [link["href"] for link in ad_result.select("div.bOeY0b a")]
        if len(inline_link) < 4:
            while len(inline_link) < 4:
                inline_link.append('')

        ad_results.append({
            "position": index,
            "title": title,
            "phone": phone,
            "website_link": website_link,
            "displayed_link": displayed_link,
            "ad_link": ad_link,
            "tracking_link": tracking_link,
            "snippet": snippet,
            "sitelinks_title_1": inline_link_text[0],
            "sitelinks_title_2": inline_link_text[1],
            "sitelinks_title_3": inline_link_text[2],
            "sitelinks_title_4": inline_link_text[3],
            "sitelinks_link_1": inline_link[0],
            "sitelinks_link_2": inline_link[1],
            "sitelinks_link_3": inline_link[2],
            "sitelinks_link_4": inline_link[3],
            #enter your current location here
            "location": "Australia, Sydney"
        })
    if ad_results == []:
        print('There are no ads for this search phrase')
        return []
    else:
        return ad_results


def scrap_results_to_sql():
    '''
    Save results in database ("database_results.db") for future manipulations
    :return:
    '''
    keyword = input("Enter your keyword: ").lower()
    while not bool(re.fullmatch('[\w\d\s]+',keyword)):
        keyword = input("Only an alpha-numeric string available.\nEnter your keyword: ").lower()
    df_ads = pd.DataFrame(scrap_ads_get(keyword))
    df_ads['data_scrap'] = date.today()
    df_ads['keyword'] = keyword
    if not os.path.exists("database_results.db"):
        open("database_results.db", 'a').close()
        print('The file "database_results.db" doesn\'t exist, so it have been created')
    con = sqlite3.connect("database_results.db")
    df_ads.to_sql('google_ads_scrap', con=con, if_exists='append', index=False)


def scrap_ads_serpapi(keyword='buy', country = 'us', uule='w+CAIQICIGTG9uZG9u'):
    """
    Original code by Dmitriy Zub:
    https://dev.to/dmitryzub/scrape-google-ad-results-with-python-166l
    This function returns you list of Google ads. You should enter your SERP_API earlier to gain access to this feature.
    :return:
    """
    params = {
        "api_key": SERP_API,
        "engine": "google",
        "q": keyword,
        "gl": country,
        "hl": "en",
        "uule": uule
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    ad_results = []
    if results.get("ads", []):
        for ad in results["ads"]:
            try:
                web_link = ad['link']
            except:
                web_link = ad['displayed_link']
            try:
                exten = ' ' + (' ').join(ad['extensions'])
            except:
                exten = ''
            try:
                slt_1 = ad["sitelinks"][0]['title']
            except:
                slt_1 = ''
            try:
                slt_2 = ad["sitelinks"][1]['title']
            except:
                slt_2 = ''
            try:
                slt_3 = ad["sitelinks"][2]['title']
            except:
                slt_3 = ''
            try:
                slt_4 = ad["sitelinks"][3]['title']
            except:
                slt_4 = ''
            try:
                sll_1 = ad["sitelinks"][0]['link']
            except:
                sll_1 = ''
            try:
                sll_2 = ad["sitelinks"][1]['link']
            except:
                sll_2 = ''
            try:
                sll_3 = ad["sitelinks"][2]['link']
            except:
                sll_3 = ''
            try:
                sll_4 = ad["sitelinks"][3]['link']
            except:
                sll_4 = ''
            ad_results.append({
                "position": ad['position'],
                "title": ad['title'],
                "phone": None,
                "website_link": web_link,
                "displayed_link": ad['displayed_link'],
                "ad_link": None,
                "tracking_link": ad['tracking_link'],
                "snippet": ad['description'] + exten,
                "sitelinks_title_1": slt_1,
                "sitelinks_title_2": slt_2,
                "sitelinks_title_3": slt_3,
                "sitelinks_title_4": slt_4,
                "sitelinks_link_1": sll_1,
                "sitelinks_link_2": sll_2,
                "sitelinks_link_3": sll_3,
                "sitelinks_link_4": sll_4
            })
    if ad_results == []:
        print('There are no ads for this search phrase')
        return []
    else:
        return ad_results


def scrap_serapi_results_to_sql(keyword="buy", city = "London,England,United Kingdom", country = 'us', uule='w+CAIQICIGTG9uZG9u'):
    '''
    Save results in database ("database_results.db") for future manipulations
    :return:
    '''
    df_ads = pd.DataFrame(scrap_ads_serpapi(keyword=keyword, country = country, uule=uule))
    df_ads['data_scrap'] = date.today()
    df_ads['keyword'] = keyword
    df_ads['location'] = city
    if not os.path.exists("database_results.db"):
        open("database_results.db", 'a').close()
        print('The file "database_results.db" doesn\'t exist, so it have been created')
    con = sqlite3.connect("database_results.db")
    df_ads.to_sql('google_ads_scrap', con=con, if_exists='append', index=False)


def show_unique_links(cut_params_bool=True):
    '''
    Export "website_link" from "database_results.db" and return unique results list
    :return:
    '''
    keyword = input("Enter your keyword: ").lower()
    while not bool(re.fullmatch('[\w\d\s]+',keyword)):
        keyword = input("Only an alpha-numeric string available.\nEnter your keyword: ").lower()
    con = sqlite3.connect("database_results.db")
    cur = con.cursor()
    rec = cur.execute(
        'SELECT DISTINCT website_link FROM google_ads_scrap WHERE keyword = "{}" AND website_link NOT LIKE "%google%"'.format(
            keyword))
    answer = []
    for i in rec.fetchall():
        if cut_params_bool:
            answer.append(cut_params(i[0]))
        else:
            answer.append(i[0])
    return sorted(answer)


def show_unique_description():
    '''
    Export "snippet" by keyword from "database_results.db" and return unique results list
    :return:
    '''
    keyword = input("Enter your keyword: ").lower()
    while not bool(re.fullmatch('[\w\d\s]+',keyword)):
        keyword = input("Only an alpha-numeric string available.\nEnter your keyword: ").lower()
    con = sqlite3.connect("database_results.db")
    cur = con.cursor()
    rec = cur.execute('SELECT DISTINCT snippet FROM google_ads_scrap WHERE keyword = "{}"'.format(keyword))
    return rec.fetchall()


# def normilize_description():
#     """
#     парсит из текста список слов в 0 форме (им пажед, инфинитив)
#     """
#     sud = ' '.join(show_unique_description())
#     # создает компилятор
#     reg_expr_compiled = re.compile('\w+')
#     # занижает введенную строку
#     raw_text_lower = sud.lower()
#     # формирует из сниженной исходной строки лист из слов
#     text_by_words = reg_expr_compiled.findall(raw_text_lower)
#     # этот класс нужен для приведения формы слова
#     morph = pymorphy2.MorphAnalyzer()
#     normalized_corpus = []
#     for word in text_by_words:
#         parsed_token = morph.parse(word)
#         normal_form = parsed_token[0].normal_form
#         if (not normal_form in STOP_WORDS) and (normal_form.isalpha()):
#             normalized_corpus.append(normal_form)
#     return normalized_corpus


def results_to_csv():
    '''
    It creates "output.csv" to show your current database table (just for a testing)
    :return:
    '''
    con = sqlite3.connect("database_results.db", isolation_level=None,
                          detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query('SELECT DISTINCT * FROM google_ads_scrap', con)
    db_df.to_csv('output.csv', sep=';', index=False)


def scrap_titles():
    '''
    Scrap titles from unique links to print your competitors names
    :return:
    '''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }
    for i in show_unique_links(False):
        try:
            html = requests.get(i, headers=headers)
            content = html.content
            soup = BeautifulSoup(content, "html.parser")
            if soup.findAll("title"):
                print(soup.find("title").string)
        except:
            None


def cut_str(text, chars=100):
    '''
    It cuts strings for a comfort snippets view
    :param text: str
    :param chars: int
    :return:
    '''
    if len(text) > chars:
        answer = text[:text[:chars].rindex(' ')]
        while len(text) > chars:
            text = text[text[:chars].rindex(' ') + 1:]
            if len(text) > chars:
                answer += '\n' + text[:text[:chars].rindex(' ')]
            else:
                answer += '\n' + text
        return answer
    else:
        return text


def cut_params(text):
    """
    It cuts links for a better view
    :return:
    """
    if 'https://' in text:
        text = text.replace('https://', '', 1)
    elif 'http://' in text:
        text = text.replace('https://', '', 1)
    if 'www.' in text[:5]:
        text = text.replace('www.', '', 1)
    if 'index.html' in text:
        text = text.replace('index.html', '', 1)
    if '?' in text:
        text = text[:text.index('?')]
    if '/' == text[-1]:
        text = text[:-1]
    return text


def commander():
    '''
    It's navigation panel for this program
    :return:
    '''
    print('Enter your command')
    print('scrap - Scrap google ads for a search phrase')
    print('tocsv - Import database into a .csv file')
    print('links - Show unique links for a search phrase')
    print('titles - Show unique link titles')
    print('desc - Show unique snippets for a search phrase')
    print('serp - Scrap google ads for a search phrase with SerpApi')
    command = input('Input: ')
    if command.lower() == 'scrap':
        scrap_results_to_sql()
    elif command.lower() == 'links':
        for i in show_unique_links():
            print(i)
    elif command.lower() == 'tocsv':
        results_to_csv()
    elif command.lower() == 'titles':
        scrap_titles()
    elif command.lower() == 'desc':
        for i in show_unique_description():
            print(cut_str(i[0]), '\n')
    elif command.lower() == 'serp':
        keyword = input("Enter your keyword: ").lower()
        while not bool(re.fullmatch('[\w\d\s]+',keyword)):
            keyword = input("Only an alpha-numeric string available.\nEnter your keyword: ").lower()
        for i in location_list():
            scrap_serapi_results_to_sql(keyword=keyword, city = i[0], country = i[1], uule=i[2])
    else:
        print('Nothing happened')


if __name__ == '__main__':
    commander()
    input('Process finished successful. Enter anything: ')
