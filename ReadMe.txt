The dataset contains data scraped from the Zara website (www.zara.com/it, www.zara.com/uk, www.zara.com/es)
the structure is the following:
-images folder: contains all the scraped images.
-dataset file: a csv file containing all the scraped data. 

the dataset file has the following columns:
Language: the selected language of the website for the current item
path: the path to the current item, ex. man\t-shirts
Name: the current name of the item
ID: a unique id to identify each item. It has the following structure: color_code (ex. white_0000-000)
pay attention to the fact that there may be some identical ids for products that belongs to different languages
Price: the price of the item. For uk is expressed in pounds, while for the others in euros.
Description: a detailed description of the item
Composition: the material in which the item is composed. Pay attention to the fact that a lot of items have different 
parts with different materials; in those cases the composition field is referred to the material of the 'main' part of the item.
ID pairing 1/2/3/4: the unique ID of items whit whom the current item is paired with to complete the suggested outfit.

For the images the naming convention is the following: "ID_numberOfTheImage" for example, if for item "white_0000-000" there are
3 images, they will be called "white_0000-000_0" "white_0000-000_1" "white_0000-000_2"