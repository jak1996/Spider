import shutil
import time
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import requests
import os
from requests.exceptions import ConnectionError


CURRENT_LANGUAGE = 'English'

def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 10)
    return driver


def createDataFrame():
    """
    create a dataframe with all the fields that we need to scrape
    :return: dataframe filled with zeros of the correct dimension
    """
    df = pd.DataFrame(columns=['Language', 'Path', 'Name', 'ID', 'Price', 'Description', 'Composition', 'ID pairing 1', 'ID pairing 2',
                               'ID pairing 3', 'ID pairing 4'])
    return df


def getSubcategoriesLinks(driver, url):
    """
    :param: driver
    :param: url of the page
    extract the links of the subcategories pages
    :return: list of the links
    """
    subCategoriesLinks = []
    driver.get(url)
    try:
        subCategoriesElements = driver.find_elements_by_xpath(
            "//a[@class='category-link _sibling-category-notify _category-link']")
        for element in subCategoriesElements:
            link = element.get_attribute('href')
            subCategoriesLinks.append(link)
    except TimeoutException:
        print("Timeoutexception!")
    return subCategoriesLinks


def getProductsLinks(driver, url):
    """
    :param driver: selenium driver
    :return: a list of all the links to the pages of the single products
    """
    driver.get(url)
    try:
        linksList = []
        try:
            productListElement = driver.find_element_by_xpath("//ul[@class='product-list _productList']")
        except NoSuchElementException:
            productListElement = driver.find_element_by_xpath("//ul[@class='product-list _productList main-components']")
        productList = productListElement.find_elements_by_tag_name('li')
        for element in productList:
            try:
                linkToTheProduct = element.find_element_by_tag_name('a').get_attribute('href')
                queryParameters = element.find_element_by_tag_name('a').get_attribute("data-extraquery")
                if queryParameters is not None:
                    linkToTheProduct = linkToTheProduct + "?" + queryParameters
                linksList.append(linkToTheProduct)
            except NoSuchElementException:
                print("marketing banner")
            except StaleElementReferenceException:
                print("unvalid product")
        return linksList
    except TimeoutException:
        print("Timeoutexception!")


def wait(nSeconds):
    '''
    pause the execution of the program and print the seconds passing
    :param nSeconds: num of seconds to stop
    '''
    print("waiting...")
    for i in range(nSeconds):
        print(str(i + 1))
        time.sleep(1)


def getLinksToImages(driver):
    '''
    :param driver
    :return: list of links to the images of the products
    '''
    # extract the links photos
    imagesListContainer = driver.find_element_by_xpath('//*[@id="main-images"]')
    imagesElementsList = imagesListContainer.find_elements_by_tag_name('div')
    imagesLinksList = []
    for imageElement in imagesElementsList:
        linkToImage = imageElement.find_element_by_tag_name('a').get_attribute('href')
        imagesLinksList.append(linkToImage)
    return imagesLinksList


def getPairingProductsLinks(driver):
    '''
    :param driver
    :return: list of the links to the paired products
    '''
    pairingLinks = []
    try:
        # scroll the page to make elements load
        driver.find_element_by_tag_name('body').send_keys(Keys.END)
        wait(3)
        # extract links to pairing elements
        pairingProductsElement = driver.find_element_by_xpath('//*[@id="product"]/div[3]/div/div[1]/div/ul')
        pairingProductsList = pairingProductsElement.find_elements_by_tag_name("li")
        for product in pairingProductsList:
            linkToPairingProduct = product.find_element_by_tag_name('a').get_attribute('href')
            pairingLinks.append(linkToPairingProduct)
    except NoSuchElementException:
        print("no pairing products for this item")
    return pairingLinks


def getIdsPairedProducts(driver, listOfLinks):
    """
    extract ids of paired products
    :param listOfLinks: list containing the links to the pages of the paired products
    :return: list of ids
    """
    pairedProductsIds = []
    # get codes of pairing products
    for link in listOfLinks:
        driver.get(link)
        wait(8)
        try:
            idPairedProduct = driver.find_element_by_class_name('product-color').text
            idPairedProduct = parseId(idPairedProduct)
            pairedProductsIds.append(idPairedProduct)
        except NoSuchElementException:
            print("no code available for this paired item!")
    return pairedProductsIds


def parseId(id):
    if len(id.split(" - ")) > 1:
        color = id.split(" - ")[0]
        code = id.split(" - ")[1]
        id = color + "_" + code
        id1 = id.split("/")[0]
        id2 = id.split("/")[1]
        id = id1 + "-" + id2
    else:
        id1 = id.split("/")[0]
        id2 = id.split("/")[1]
        id = id1 + "-" + id2
    return id


def downloadPhotos(imagesLinksList, subpath, id):
    """
    download all the photos in the list and save them into the path specified
    :param imagesLinksList: list of urls of the images
    :param subpath folder path name where to save images
    """
    index = 0
    for imageLink in imagesLinksList:
        wait(2)
        r = requests.get(imageLink, stream=True)
        if r.status_code == 200:
            fileNamePath = 'Data\images\\' + subpath + "\\"
            fileNameSuffix = str(id) + '_' + str(index) + ".jpg"
            fileName = fileNamePath + fileNameSuffix
            os.makedirs(os.path.dirname(fileName), exist_ok=True)
            with open(fileName, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        index += 1


def getComposition(driver):
    try:
        try:
            compositionButton = driver.find_element_by_xpath(
                '//*[@id="product"]/div[1]/div/div[2]/div[4]/ul/li[1]/a')
        except NoSuchElementException:
            # different name of the button in the html
            compositionButton = driver.find_element_by_xpath('//*[@id="product"]/div[1]/div/div[2]/div[3]/ul/li[1]/a')
        driver.execute_script("arguments[0].click();", compositionButton)
        wait(2)
        composition = driver.find_element_by_class_name('zonasPrenda').text
    except NoSuchElementException:
        # no compisition available
        composition = np.NaN
    return composition


def parsePath(url):
    pathFirstPart = url.split("-")[0]
    pathFirstPart = pathFirstPart.split("/")[-1]
    pathSecondPart = url.split("-")[1]
    path = pathFirstPart + "\\" + pathSecondPart
    return path


def scrapeData(productsLinks, path):
    """
    :param productsLinks: list of links to the pages of all the products of the category
    :param path
    :return:
    """
    counter = 0
    print(str(len(productsLinks)))
    df = createDataFrame()
    for link in productsLinks:
        wait(7)
        try:
            driver.get(link)
            productName = driver.find_element_by_class_name('product-name').text
            try:
                price = driver.find_element_by_class_name('main-price').text
            except NoSuchElementException:
                # In case of discounted prices, where the price is not indicated directly
                price = driver.find_element_by_class_name('line-through').text
            price = price.split(" ")[0]
            id = driver.find_element_by_class_name('product-color').text
            id = parseId(id)
            DescriptionElement = driver.find_element_by_class_name('description').text
            description = DescriptionElement.split('\n')[0]

            composition = getComposition(driver)

            imagesLinksList = getLinksToImages(driver)

            downloadPhotos(imagesLinksList, path, id)

            pairingProductsLinksList = getPairingProductsLinks(driver)
            pairedProductsIds = getIdsPairedProducts(driver, pairingProductsLinksList)

            # fill the dataframe
            missingPairings = 4 - len(pairedProductsIds)
            for i in range(missingPairings):
                pairedProductsIds.append(np.NaN)
            df = df.append({'Language': CURRENT_LANGUAGE, 'Path': path, 'Name': productName, 'ID': id, 'Price': price,
                            'Description': description, 'Composition': composition,
                            'ID pairing 1': pairedProductsIds[0], 'ID pairing 2': pairedProductsIds[1],
                            'ID pairing 3': pairedProductsIds[2], 'ID pairing 4': pairedProductsIds[3]},
                           ignore_index=True)
            counter += 1
        except TimeoutException:
            print("Timeoutexception!")
        except NoSuchElementException:
            print("unvalid product page!")
        except ConnectionError:
            print("connection aborted")
            f = open("errors.txt", "a")
            f.write(path + "=> scraped " + str(counter) + "/" + str(len(productsLinks)) + "\n")
            f.close()
            return df
    return df


if __name__ == "__main__":
    driver = init_driver()
    file = open('URLs.txt', mode="r")
    for url in file:
        wait(3)
        path = parsePath(url)
        # path = 'pantalones shorts'
        fileName = path.split("\\")[0] + "-" + path.split("\\")[1] + ".csv"
        # fileName = 'mujer-pantalones shorts.csv'
        dataFrameCategory = createDataFrame()
        subcategoriesLinks = getSubcategoriesLinks(driver, url)
        if len(subcategoriesLinks) > 0:
            for link in subcategoriesLinks:
                # if link is not subcategoriesLinks[-1]:
                wait(8)
                productsLinks = getProductsLinks(driver, link)
                dataFrameSubCategory = scrapeData(productsLinks, path)
                dataFrameCategory = dataFrameCategory.append(dataFrameSubCategory)
            dataFrameCategory.to_csv(index=False, path_or_buf='Data\\' + fileName, na_rep='Null')
        else:
            wait(8)
            productsLinks = getProductsLinks(driver, url)
            dataFrameCategory = scrapeData(productsLinks, path)
            dataFrameCategory.to_csv(index=False, path_or_buf='Data\\' + fileName, na_rep='Null')
    file.close()
    driver.close()
