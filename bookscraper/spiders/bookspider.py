import scrapy


class BookspiderSpider(scrapy.Spider):
    # initial variable setting:
    name = 'bookspider'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']

    # the main function called upon the initiation of the spider:
    def parse(self, response):
        # getting list of html items that fid the identifier for the books:
        books = response.css('article.product_pod')
        # going through the books list
        for book in books:
            #getting the partial url of the books from the main list page:
            partial_url=book.css('h3 a').attrib['href']
            # making sure that the different links are equalized to create the same url:
            if 'catalogue/' in partial_url:
                book_url='https://books.toscrape.com/'+book.css('h3 a').attrib['href']
            else:
                book_url='https://books.toscrape.com/catalogue/'+book.css('h3 a').attrib['href']

            yield scrapy.Request(book_url, callback=self.parse_book_page)
            #    'name': book.css('h3 a::text').get(),
            #    'price': book.css('div.product_price .price_color::text').get(),
            #    'url': book.css('h3 a').attrib['href'],


        ##next page code:
        next_page = response.css('li.next a ::attr(href)').get()
        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    ##parsing the book page that the function parse() gets us to
    def parse_book_page(self, response):
        info=response.css('div.product_main')
        rows=response.css('table tr')

        yield{
            'title': info.css('div.product_main h1::text').get(),
            'price': info.css('p.price_color::text').get(),
            'description': info.xpath("//div[@id='product_description']/following-sibling::p/text()").get(),
            'category': info.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),

            'UPC': rows[0].css('td::text').get(),
            'Product Type': rows[1].css('td::text').get(),
            'Price (excl. tax)': rows[2].css('td::text').get(),
            'Price (incl. tax)': rows[3].css('td::text').get(),
            'Tax': rows[4].css('td::text').get(),
            'Availability': rows[5].css('td::text').get(),
            'Number of reviews': rows[6].css('td::text').get(),

            'Number of stars:': info.css('p.star-rating').attrib['class'].replace('star-rating ',''),
        }