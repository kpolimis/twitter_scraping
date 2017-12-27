from utils import *

#https://stackoverflow.com/questions/33712615/using-argparse-with-function-that-takes-kwargs-argument

# edit these three variables
# obama twitter history: https://en.wikipedia.org/wiki/Barack_Obama_on_social_media#
# @barackobama 1st tweet: https://en.wikipedia.org/wiki/Barack_Obama_on_social_media#/media/File:Twitter_activity_of_Barack_Obama.png
# russian interference accounts: (@RT_com, @RT_America, and @ActualidadRT)
# https://blog.twitter.com/official/en_us/topics/company/2017/Update-Russian-Interference-in-2016--Election-Bots-and-Misinformation.html
# russian facebook ads: https://www.politico.com/story/2017/11/01/social-media-ads-russia-wanted-americans-to-see-244423
# russian facebook ads: https://www.axios.com/dems-release-russia-bought-facebook-ads-2505026286.html
def get_all_tweets(screen_name, **kwargs: int):
    if ('start_date' in kwargs):
        #print ('optional parameter found, it is ', kwargs['optional'])
        print ('optional parameter found, it is ', kwargs['start_date'])
        #print(kwargs['start_date'].keys())
        date = kwargs['start_date'].split(',')
        start_date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))

    base_url = "https://twitter.com/"
    #screen_name = "barackobama"
    screen_name = screen_name
    soup_url = base_url+screen_name
    print("screen name is: {0}, soup url is: {1}".format(screen_name,soup_url))
    try:
        shutil.rmtree('../data/'+screen_name)
        os.mkdir('../data/'+screen_name)
        print("created {0} folder in: {1}".format(screen_name, os.getcwd()[:-7]))
    except:
        os.mkdir('../data/'+screen_name)
        print("created {0} folder in: {1}".format(screen_name, os.getcwd()[:-7]))
    soup = BeautifulSoup(urllib.request.urlopen(soup_url), "lxml")
    spans = soup.find_all('span', {'class' : 'ProfileHeaderCard-joinDateText js-tooltip u-dir'})
    soup_date = spans[0]["title"]
    italian_month_dict = {'gen':'jan','mag':'may','giu':'jun','lug':'jul',
                          'ago':'aug','set':'sep','ott':'oct',  'dic':'dec'}
    italian_dates_pattern = re.compile(r'\b(' + '|'.join(italian_month_dict.keys()) + r')\b')
    formatted_soup_date = italian_dates_pattern.sub(lambda x: italian_month_dict[x.group()], soup_date)
    start_date = dt.strptime(dt.strptime(formatted_soup_date, '%I:%M %p -  %d %b %Y').strftime("%Y, %m, %d"), '%Y, %m, %d')
    start_date
    end_date = dt.now()
    end_date
    start = start_date
    end = end_date
    delay = 1  # time to wait on each page load before reading the page
    #driver = webdriver.Chrome()  # options are Chrome() Firefox() Safari()
    driver = webdriver.PhantomJS()

    # don't mess with this stuff
    os.chdir('../data/'+screen_name)
    twitter_ids_filename = 'all_ids.json'
    days = (end - start).days + 1
    id_selector = '.time a.tweet-timestamp'
    tweet_selector = 'li.js-stream-item'
    screen_name = screen_name.lower()
    ids = []

    for day in range(days):
        d1 = format_day(increment_day(start, 0))
        d2 = format_day(increment_day(start, 1))
        url = form_url(screen_name, d1, d2)
        print(url)
        print(d1)
        #reason for next try block:
        # https://stackoverflow.com/questions/40514022/chrome-webdriver-produces-timeout-in-selenium
        try:
            driver.get(url)
            sleep(delay)
        except TimeoutException as ex:
            print(ex.Message)
            driver.navigate().refresh()


        try:
            found_tweets = driver.find_elements_by_css_selector(tweet_selector)
            increment = 10

            while len(found_tweets) >= increment:
                print('scrolling down to load more tweets')
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(delay)
                found_tweets = driver.find_elements_by_css_selector(tweet_selector)
                increment += 10

            print('{} tweets found, {} total'.format(len(found_tweets), len(ids)))

            for tweet in found_tweets:
                try:
                    id = tweet.find_element_by_css_selector(id_selector).get_attribute('href').split('/')[-1]
                    ids.append(id)
                except StaleElementReferenceException as e:
                    print('lost element reference', tweet)

        except NoSuchElementException:
            print('no tweets on this day')

        start = increment_day(start, 1)


    try:
        with open(twitter_ids_filename) as f:
            all_ids = []
            all_ids += ids + json.load(f)
            data_to_write = list(set(all_ids))
            print("\n")
            print('downloaded tweets from: {}'.format(screen_name))
            print('this scrape includes tweets from {} to {}'.format(start_date.date(), end_date.date()))
            print('tweets found on this scrape: ', len(ids))
            print('total tweet count: ', len(data_to_write))
    except FileNotFoundError:
        with open(twitter_ids_filename, 'w') as f:
            all_ids = ids
            data_to_write = list(set(all_ids))
            print("\n")
            print('downloaded tweets from: {}'.format(screen_name))
            print('this scrape includes tweets from {} to {}'.format(start_date.date(), end_date.date()))
            print('tweets found on this scrape: ', len(ids))
            print('total tweet count: ', len(data_to_write))

    with open(twitter_ids_filename, 'w') as outfile:
        json.dump(data_to_write, outfile)

    print('saved {0} in {1}'.format(twitter_ids_filename, os.getcwd()))
    print('all done here')
    driver.close()

if __name__ == '__main__':
	#pass in the username of the account you want to download
  get_all_tweets(sys.argv[1], **dict(arg.split('=') for arg in sys.argv[2:]))
