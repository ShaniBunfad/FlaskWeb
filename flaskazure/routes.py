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
        byord=0
        for entity in table_service.query_entities(table_name):
            the_figures.insert(byord,entity['NameFigure'])
            byord +=1
        if isinserted is True:
            str_coun= str(byord)
            partKey= 'N' + str_coun
            figure_new = {'PartitionKey': partKey, 'RowKey': str_coun, 'NameFigure' : figurename}
            # Insert the entity into the table
            table_service.insert_entity(table_name, figure_new)
            the_figures.insert(byord,figurename)   
        #if isinserted is True:
             # delete an entity
         #   table_service.delete_entity(table_name, partKey, str_coun)
    except Exception as e:
        print('Error occurred in the sample. Please make sure the account name and key are correct.', e)
    return the_figures


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
	theUrl=search_results['webPages']['value'][0]['url']
	return theUrl


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    form=PublicFigureForm()
    if form.validate_on_submit():
        figurename=form.figurename.data
        figurenameins= figurename + 'Instagram'
        #added
        urlAdress=bingWebSearch(figurenameins)
        indic=dbAzureApp(figurename, True)
        return render_template('home.html',form=form, urlNew=urlAdress, thelist=indic)
    indic=dbAzureApp("", False)
    return render_template('home.html', form=form, thelist=indic)
