"""
Created on Sun ‎Jun ‎14 ‎2020 ‏‎12:16:01

@author: name
"""

# Get UK Parliament data via API: 
# House of Commons - Written questions

import json
from urllib.request import urlopen
import time

csv_sep = "|"

def get_data(res_item):
    """
    Parse one item of the API response
    
    Parameters:
    -----------
    res_item: dict
        one entry (question) of the response dictionary

    Returns:
    -----------
    A string with the relevant data of the res_item
    
    """
    
    # print(res_item)
    uri = res_item.get("_about")
    answer_date = res_item.get("AnswerDate").get("_value")
    answering_body = res_item.get("AnsweringBody")[0].get("_value") # Note: there may be multiple entries here, only take the first one!
    date_tabled = res_item.get("dateTabled").get("_value")
    question_text = res_item.get("questionText")
    tabling_member_label = res_item.get("tablingMember").get("label").get("_value")
    tabling_member_print = res_item.get("tablingMemberPrinted")[0].get("_value")
    title = res_item.get("title")
    uin = res_item.get("uin")
    
    return csv_sep.join([uri, answer_date, answering_body, date_tabled, question_text, tabling_member_label, tabling_member_print, title, uin])

def parse_json_response(response_json):
    """
    Parse the JSON response items
    
    Parameters:
    -----------
    response_json: dict
        JSON response as Python dictionary
        
    Returns:
    -----------
    List of items (questions and details) as strings
    
    """

    # print(responseJson)
    items = response_json.get("result").get('items')
    print("Found {} items".format(len(items)))
    parsed_data = [get_data(item) for item in items]
    
    return parsed_data

def getApiRes(itemsPerPage, res_filename):
    """
    Get written questions data via API and save details to csv
    
    Parameters:
    -----------
    itemsPerPage: int
        number of items per page requested by each API call
    res_filename: str
        name of csv file with results 
    
    Note: result columns are separated by | instead of comma or semicolon!!!
    
    Returns:
    -----------
    """

    # First API call
    response = urlopen('http://lda.data.parliament.uk/commonswrittenquestions.json?_pageSize={0}'.format(itemsPerPage)).read().decode('utf-8')
    # parse json
    responseJson = json.loads(response)
    parsed_res = parse_json_response(responseJson)
    
    # write parsed data to file
    res_file = open(res_filename, 'w', encoding = 'utf-8')
    # write header
    res_file.write(csv_sep.join(["uri","answer date","answering body","date tabled","question text","tabling member > label","tabling member printed","title","uin"]) + "\n")
    # write result of first page
    res_file.write("\n".join(parsed_res) + "\n")
    # delay before requesting next page
    time.sleep(10)
    
    has_next = True
    while has_next:
        # API call for the remaining pages
        nextpage = responseJson.get("result").get("next")
        # print(nextpage)
        # read the next page of results, if it exists
        if nextpage:
            response = urlopen(nextpage + '&_pageSize={0}'.format(itemsPerPage) ).read().decode('utf-8')
            responseJson = json.loads(response)
            parsed_res = parse_json_response(responseJson)
            # write parsed data to file
            res_file.write("\n".join(parsed_res) + "\n")
        else:
            has_next = False
    
    res_file.close()


if __name__ == '__main__':
    # get details about written questions, reading 500 entries per page
    getApiRes(500, "results.csv")
