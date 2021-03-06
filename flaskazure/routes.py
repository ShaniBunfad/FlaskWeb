from flask import render_template
from flaskazure import app
from flaskazure.forms import PublicFigureForm
#for bing
import requests
import json
#for DB
import string
import azure.common
from azure.storage import CloudStorageAccount
from azure.storage.table import TableService, Entity

#Displaing the recent searched figures from an Azure DataBase, And insert if the user push the submit button
#@param: figurename- The figure to Insert
#isinserted- If the user inserted a figure or we need just to display the recent searched figures 
def dbAzureApp(figurename, isinserted):
    account_name = 'shanistorage'
    account_key = 'j1COI4eq+p/Yl/e8dVCAiaHX/ly1StLuFAlgalNhVI+rjU8YL6wkWlulld4XIZ/5kjnrqkFyGhQsVo68y9NWpg=='
    account = CloudStorageAccount(account_name, account_key)
    table_service = None
    the_figures=[]
    try:
        table_service = account.create_table_service()
        table_name = 'azureFirstStor'
        #insret to a list by order
        by_ord=0
        for entity in table_service.query_entities(table_name):
            the_figures.insert(by_ord,entity['NameFigure'])
            by_ord +=1
	#insert into the DB
        if isinserted is True:
            str_coun= str(by_ord)
            part_key= 'N' + str_coun
            figure_new = {'PartitionKey': part_key, 'RowKey': str_coun, 'NameFigure' : figurename}
            # Insert the entity into the table
            table_service.insert_entity(table_name, figure_new)
            the_figures.insert(by_ord,figurename)   
         # delete an entity if want
         #   table_service.delete_entity(table_name, part_key, str_coun)
    except Exception as e:
        print('Error occurred in the sample. Please make sure the account name and key are correct.', e)
    return the_figures

#Searching the public figure Instagram the user inserted
#@param: figurenameins- the figure name to search
def bingWebSearch(figurenameins):
	subscription_key = "0c8b96989c754e2c80fb0dfd4c5881f9"
	assert subscription_key
	search_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"
	search_term = figurenameins

	headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
	params  = {"q": search_term, "count": 1}
	response = requests.get(search_url, headers=headers, params=params)
	response.raise_for_status()
	search_results = response.json()
	if search_results is None:
		return ""
	the_url=search_results['webPages']['value'][0]['url']
	return the_url


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    form=PublicFigureForm()
    if form.validate_on_submit():
        figurename=form.figurename.data
        figurenameins= figurename + 'Instagram'
        #call the bingSearch
        urlAdress=bingWebSearch(figurenameins)
	#insert into DB
        indic=dbAzureApp(figurename, True)
        return render_template('home.html',form=form, urlNew=urlAdress, thelist=indic)
    indic=dbAzureApp("", False)
    return render_template('home.html', form=form, thelist=indic)
