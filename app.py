# doing necessary imports
from flask import Flask, render_template, request
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from dbConnectionLib import db_connection
from csv_file_lib import csv_methods
from visualizatioinLib import data_visualization

app = Flask(__name__)


@app.route('/', methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')


@app.route('/scrap', methods=['POST'])
@cross_origin()
def index():
    csvMethod = csv_methods()
    header = ['SlNo', 'Product', 'ProductName', 'OfferPrice', 'ActualPrice', 'Discount', 'AvailableOffers', 'ProductDescription', 'Name','Rating', 'CommentHead', 'Comment']
    csv_file_name = 'flipkart_scrape_data.csv'

    with open(csv_file_name, 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csvMethod.initialize_csv_writter(csv_file)
        csvMethod.insert_record_in_csv(csv_writer, header)

        if request.method == 'POST':
            searchString = request.form['content'].replace(" ", "")

            # Data Base connection
            dbConnect = db_connection()
            database = dbConnect.connect_mongoDB()
            collection = dbConnect.create_collection(database, searchString)
            is_collection_present = dbConnect.check_existence_collection(database, searchString)

            records = []
            if is_collection_present:
                record_lists = dbConnect.get_records(collection)
                if record_lists.count() > 500:
                    for record in record_lists:
                        records.append(record)
                        db_record = [record['SlNo'], record['Product'], record['ProductName'], record['OfferPrice'], record['ActualPrice'], record['Discount'], record['AvailableOffers'], record['ProductDescription'], record['Name'], record['Rating'], record['CommentHead'], record['Comment']]
                        csvMethod.insert_record_in_csv(csv_writer, db_record)

                    csv_file.close()

                    try:
                        data_Visual = data_visualization()
                        data_Visual.plot_3d_graph(csv_file_name)

                    except:
                        return 'Error while adding graph'

                    return render_template('results_from_db.html', reviews=records)

            try:
                source = requests.get("https://www.flipkart.com/search?q=" + searchString).text
                flipkart_pages = bs(source, 'lxml')
                pagination = flipkart_pages.find_all('a', class_='ge-49M')

                pages_count = len(pagination)
                reviews = []
                slNo = 0
                for n in range(1, pages_count):
                    flipkart_url = f"https://www.flipkart.com/search?q={searchString}&page={n}"
                    uClient = uReq(flipkart_url)
                    flipkartPage = uClient.read()
                    uClient.close()
                    flipkart_html = bs(flipkartPage, "html.parser")
                    bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
                    del bigboxes[0:3]

                    count = 0
                    num = len(bigboxes)
                    for n in range(num - 4):
                        box = bigboxes[n]
                        productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                        prodRes = requests.get(productLink)
                        prod_html = bs(prodRes.text, "html.parser")

                        try:
                            product_name = prod_html.find_all('span', {'class': 'B_NuCI'})[0].text

                        except:
                            product_name = 'No Product Name'

                        try:
                            price_after_offer = prod_html.find_all('div', {'class': "_30jeq3 _16Jk6d"})[0].text

                        except:
                            price_after_offer = 'No Price tag'

                        try:
                            price_before_offer = prod_html.find_all('div', {'class': "_3I9_wc _2p6lqe"})[0].text

                        except:
                            price_before_offer = 'No Price offer'

                        try:
                            discount_in_percent = prod_html.find_all('div', {'class': "_3Ay6Sb _31Dcoz"})[0].text

                        except:
                            discount_in_percent = 'No discount'

                        try:
                            available_offers = prod_html.find_all('div', {'class': "XUp0WS"})[0].text

                        except:
                            available_offers = 'No available offers'

                        try:
                            product_description = prod_html.find_all('div', {'class': "_1mXcCf RmoJUa"})
                            product_description = product_description[0].p.text

                        except:
                            product_description = 'No product description'

                        commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

                        count = count + 1
                        print(count)

                        for commentbox in commentboxes:
                            try:
                                name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                            except:
                                name = 'No Name'

                            try:
                                rating = commentbox.div.div.div.div.text

                            except:
                                rating = 'No Rating'

                            try:
                                commentHead = commentbox.div.div.div.p.text
                            except:
                                commentHead = 'No Comment Heading'
                            try:
                                comtag = commentbox.div.div.find_all('div', {'class': ''})
                                custComment = comtag[0].div.text
                            except:
                                custComment = 'No Customer Comment'

                            slNo += 1
                            mydict = {"SlNo": slNo, "Product": searchString, "ProductName": product_name, "OfferPrice": price_after_offer, "ActualPrice": price_before_offer, "Discount": discount_in_percent, "AvailableOffers": available_offers, "ProductDescription": product_description, "Name": name,"Rating": rating, "CommentHead": commentHead, "Comment": custComment}  # saving that detail to a dictionary

                            dbConnect.insert_single_record_to_db(collection, mydict)

                            record_to_csv = [slNo, searchString, product_name, price_after_offer, price_before_offer, discount_in_percent, available_offers, product_description, name, rating, commentHead, custComment]
                            csvMethod.insert_record_in_csv(csv_writer, record_to_csv)

                            reviews.append(mydict)
                            print(slNo)
                            if (slNo > 505):

                                for data in reviews:
                                    csvMethod.insert_record_in_csv(csv_writer, data)

                                csv_file.close()

                                try:
                                    data_Visual = data_visualization()
                                    data_Visual.plot_3d_graph(csv_file_name)

                                except Exception as e:
                                    print('The Exception message is: ', e)
                                    return 'Error while adding graph'

                                return render_template('results.html', reviews=reviews)
                csv_file.close()
                try:
                    data_Visual = data_visualization()
                    data_Visual.plot_3d_graph(csv_file_name)

                except Exception as e:
                    print('The Exception message is: ', e)
                    return 'Error while adding graph'

                return render_template('results.html', reviews=reviews)

            except Exception as e:
                print('The Exception message is: ', e)
                csv_file.close()
                return 'something is wrong'

if __name__ == "__main__":
    app.run(port=8000, debug=True)
