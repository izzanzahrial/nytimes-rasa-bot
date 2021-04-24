# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
from rasa_sdk import Tracker, Action, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from dotenv import load_dotenv
import os
import requests
import datetime

load_dotenv()

api_key = os.getenv('KEY')

class ActionListCategory(Action):
    """List best seller category."""
    
    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_list_best_seller_category"

    async def run(
        self, 
        dispacther: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        url = "https://api.nytimes.com/svc/books/v3/lists/names.json"

        parameters = {
            'api-key': api_key,
        }

        response = requests.get(url, params=parameters)
        data = response.json()

        for count,value in enumerate(data["results"]):
            output = value["list_name"]
            dispacther.utter_message(text=f'''{count+1}.{output}''')  

        return []

class ActionListBestSeller(Action):
    """List best seller book."""
    
    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_list_best_seller"

    async def run(
        self, 
        dispacther: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        if tracker.get_slot("time") != None:
            category = tracker.get_slot("category")
            time = tracker.get_slot("time")

            url = f"https://api.nytimes.com/svc/books/v3/lists/{time}/{category}.json?&api-key="+api_key

            response = requests.get(url)
            data = response.json()

            if data["status"] == "ERROR":
                dispacther.utter_message(text="This requires at least one parameter")
            elif data["results"] is None:
                dispacther.utter_message(template="utter_doesnt_exist")
            else:
                dispacther.utter_message(text=f"Here's a list of best seller {category} \n")

                for i in range(9):
                    amazon_url = data["results"]["books"][i]["amazon_product_url"]
                    title = data["results"]["books"][i]["title"]
                    author = data["results"]["books"][i]["author"]
                    book_image = data["results"]["books"][i]["book_image"]
                    dispacther.utter_message(text=f"{i+1}. Title = {title} \n Author = {author} \n Amazon link = {amazon_url} \n")
                    dispacther.utter_message(image=f"{book_image} \n")
                    dispacther.utter_message(text="\n")
                    
        elif tracker.get_slot("time") == None:
            category = tracker.get_slot("category")

            url = f"https://api.nytimes.com/svc/books/v3/lists/current/{category}.json?&api-key="+api_key

            response = requests.get(url)
            data = response.json()

            if data["status"] == "ERROR":
                dispacther.utter_message(text="This requires at least one parameter")
            elif data["results"] is None:
                dispacther.utter_message(template="utter_failed")
            else:
                dispacther.utter_message(text=f"Here's a list of best seller {category} \n")

                for i in range(9):
                    amazon_url = data["results"]["books"][i]["amazon_product_url"]
                    title = data["results"]["books"][i]["title"]
                    author = data["results"]["books"][i]["author"]
                    book_image = data["results"]["books"][i]["book_image"]
                    dispacther.utter_message(text=f"{i+1}. Title = {title} \n Author = {author} \n Amazon link = {amazon_url} \n")
                    dispacther.utter_message(image=f"{book_image} \n")
                    dispacther.utter_message(text="\n")

        else:
            dispacther.utter_message(template="utter_failed")

        return []

class ValidateListBestSellerForm(FormValidationAction):
    """Validates Slots of the list_best_seller_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_list_best_seller_form"

    async def validate_category(
        self, 
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'category' slot"""
        if not value:
            return {"category": None}
        
        if type(value) is str:
            category = tracker.get_slot("category")
            if category.lower() == 'none':
                return {"category": None}
            return {"category": category}
        else: 
            dispatcher.utter_message(template="utter_wrong_type")
            return {"category": None}
        
        return {"category": None}

    async def validate_time(
        self, 
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'time' slot"""

        if not value:
            return {"time": None}
        
        if type(value) is str:
            time = tracker.get_slot("time")
            if time.lower() == 'none':
                return {"time": None}
            dateformat = '%Y-%m-%d'
            try:
                output_time = datetime.date.strptime(time, dateformat)
                return {"time": output_time}
            except ValueError:
                dispatcher.utter_message(template="utter_wrong_type")
                return {"time": None}
        
        return {"time": None}

class ActionListBestSellerListOverview(Action):
    """List Best Seller Overview by time"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_list_best_seller_overview"

    async def run(
        self, 
        dispacther: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        if tracker.get_slot("time") != None:
            time = tracker.get_slot("time")
                
            url = f"https://api.nytimes.com/svc/books/v3/lists/overview.json"

            parameters = {
                'api-key': api_key,
                'published_date': time
            }

            response = requests.get(url, params=parameters)
            data = response.json()

            if data["results"] is None:
                dispacther.utter_message(template="utter_doesnt_exist")
            else:
                dispacther.utter_message(text=f"Here's a list of list best seller at {time} \n")

                for i in range(9):
                    list_name = data["results"]["lists"][i]["list_name"]
                    dispacther.utter_message(text=f"{i+1}. {list_name} \n")
                    dispacther.utter_message(text="\n")

        elif tracker.get_slot("time") == None:

            url = f"https://api.nytimes.com/svc/books/v3/lists/overview.json?&api-key={api_key}"

            parameters = {
                'api-key': api_key,
            }

            response = requests.get(url, params=parameters)
            data = response.json()
            today = datetime.date.now()

            if data["results"] is None:
                dispacther.utter_message(template="utter_doesnt_exist")
            else:
                dispacther.utter_message(text=f"Here's a list of list best seller at {today} \n")

                for i in range(9):
                    list_name = data["results"]["lists"][i]["list_name"]
                    dispacther.utter_message(text=f"{i+1}. {list_name} \n")
                    dispacther.utter_message(text="\n")

        else:
            dispacther.utter_message(template="utter_failed")

        return []

class ValidateBestSellerListOverview(FormValidationAction):
    """Validates Slots of the list_best_seller_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_list_best_seller_overview_form"

    async def validate_time(
        self, 
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'time' slot"""
        if not value:
            return {"time": None}
        
        if type(value) is str:
            time = tracker.get_slot("time")
            if time.lower() == 'none':
                return {"time": None}
            dateformat = '%Y-%m-%d'
            try:
                output_time = datetime.date.strftime(time, dateformat)
                return {"time": output_time}
            except ValueError:
                dispatcher.utter_message(template="utter_wrong_type")
                return {"time": None}
        
        return {"time": None}


class ActionBookReview(Action):
    """List of review"""

    def name(self) -> Text:
        """Unique indentifier of the action"""
        return "action_book_review"
    
    async def run(
        self, 
        dispacther: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        number = tracker.get_slot("number")
        title = tracker.get_slot("title")
        author = tracker.get_slot("PERSON")
    
        if number is not None or title is not None or author is not None:

            url = f"https://api.nytimes.com/svc/books/v3/reviews.json"

            parameters = {
                'api-key': api_key,
                'isbn': number,
                'title': title,
                'author': author,
            }

            response = requests.get(url, params=parameters)
            data = response.json()

            if data["status"] == "ERROR":
                dispacther.utter_message(text="This requires at least one parameter")
            elif data["results"] is None:
                dispacther.utter_message(template="utter_doesnt_exist")
            else:
                dispacther.utter_message(text=f"Here's a list of review \n")

                for i in range(9):
                    review_url = data["results"][i]["url"]
                    publication_dt = data["results"][i]["publication_dt"]
                    review_by = data["results"][i]["byline"]
                    book_title = data["results"][i]["book_title"]
                    book_author = data["results"][i]["book_author"]
                    dispacther.utter_message(text=f"{i+1}. Book title: {book_title} \n  Book author: {book_author} \n  Review by: {review_by} \n  Publication date: {publication_dt} \n Review link: {review_url}")
                    dispacther.utter_message(text="\n")
        
        else:
            dispacther.utter_message(template="utter_failed")

        return []

class ValidateBookReview(FormValidationAction):
    """Validates Slots of the book_review_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_book_review_form"

    async def validate_number(
        self, 
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'number' slot"""
        if not value:
            return {"number": None}
        
        if type(value) is str:
            number = tracker.get_slot("number")
            if number.lower() == 'none':
                return {"number": None}
            if len(number) == 10 or len(number) == 13:
                return {"number": number}
            else:
                dispatcher.utter_message(template="utter_wrong_number")
                return {"number": None}
        
        dispatcher.utter_message(template="utter_wrong_type")
        return {"number": None}

    async def validate_title(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'title' slot"""
        if not value:
            return {"title": None}

        if type(value) is str:
            title = tracker.get_slot("title")
            if title.lower() == 'none':
                return {"title": None}
            return {"title": title}
        
        dispatcher.utter_message(template="utter_wrong_type")
        return {"title": None}

    async def validate_PERSON(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'PERSON' slot"""
        if not value:
            return {"PERSON": None}
        
        if type(value) is str:
            author = tracker.get_slot("PERSON")
            if author.lower() == 'none':
                return {"PERSON": None}
            return {"PERSON": author}
        
        dispatcher.utter_message(template="utter_wrong_type")
        return {"PERSON": None}

class ActionBookDetail(Action):
    """List of detail"""

    def name(self) -> Text:
        """Unique indentifier of the action"""
        return "action_book_detail"
    
    async def run(
        self, 
        dispacther: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
    
        age_group = tracker.get_slot("age_group")
        author = tracker.get_slot("PERSON")
        contributor = tracker.get_slot("contributor")
        number = tracker.get_slot("number")
        amount_of_money = tracker.get_slot("amount-of-money")
        publisher = tracker.get_slot("publisher")
        title = tracker.get_slot("title")

        if age_group is not None or author is not None or contributor is not None or number is not None or amount_of_money is not None or publisher is not None or title is not None:
            
            url = f"https://api.nytimes.com/svc/books/v3/lists/best-sellers/history.json"

            parameters = {
                'api-key': api_key,
                'age-group': age_group,
                'author': author,
                'contributor': contributor,
                'isbn': number,
                'price': amount_of_money,
                'publisher': publisher,
                'title': title,
            }

            response = requests.get(url, params=parameters)
            data = response.json()

            if data["status"] == "ERROR":
                dispacther.utter_message(text="This requires at least one parameter")
            elif data["results"] is None:
                dispacther.utter_message(template="utter_doesnt_exist")
            else:
                dispacther.utter_message(text="Here's a list of book's detail \n")

                for i in range(9):
                    title = data["results"][i]["title"]
                    description = data["results"][i]["description"]
                    contributor = data["results"][i]["contributor"]
                    author = data["results"][i]["author"]
                    price = data["results"][i]["price"]
                    age_group = data["results"][i]["age_group"]
                    publisher = data["results"][i]["publisher"]
                    isbn10 = data["results"][i]["isbns"][0]["isbn10"]
                    isbn13 = data["results"][i]["isbns"][0]["isbn13"]
                    review_url = data["results"][i]["reviews"][0]["book_review_link"]
                    dispacther.utter_message(text=f"{i+1}.Title: {title} \n Description: {description} \n Contributor: {contributor} \n  Author: {author} \n Price: {price} $ \n Age-group: {age_group} \n Publisher: {publisher} \n Isbn's : {isbn10}, {isbn13} \n Review link: {review_url}")
                    dispacther.utter_message(text="\n")

        else:
            dispacther.utter_message(template="utter_failed")

        return []

class ValidateBookDetail(FormValidationAction):
    """Validates Slots of the book_detail_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_book_detail_form"

    async def validate_age_group(
        self, 
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'age_group' slot"""

        if not value:
            return {"age_group": None}

        if type(value) is str:
            age_group = tracker.get_slot("age_group")
            if age_group.lower() == 'none':
                return {"age_group": None}
            return {"age_group": age_group}
        
        dispatcher.utter_message(template="utter_wrong_type")
        return {"age_group": None}

    async def validate_PERSON(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'PERSON' slot"""

        if not value:
            return {"PERSON": None}

        if type(value) is str:
            author = tracker.get_slot("PERSON")
            if author.lower() == 'none':
                return {"author": None}
            return {"PERSON": author}
        
        dispatcher.utter_message(template="utter_wrong_type")
        return {"PERSON": None}

    async def validate_number(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'number' slot"""
        
        if not value:
            return {"number": None}

        if type(value) is str:
            number = tracker.get_slot("number")
            if number.lower() == 'none':
                return {"number": None}
            if len(number) == 10 or len(number) == 13:
                return {"number": number}
            else:
                dispatcher.utter_message(template="utter_wrong_amount")
                return {"number": None}
        
        dispatcher.utter_message(template="utter_wrong_type")
        return {"number": None}

    async def validate_amount_of_money(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'amount-of-money' slot"""

        if not value:
            return {"amount-of-money": None}

        if type(value) is str:
            amount_of_money = tracker.get_slot("amount-of-money")
            if amount_of_money.lower() == 'none':
                return {"amount-of-money": None}
            if int(amount_of_money) <= 0:
                dispatcher.utter_message(text= "The price can't be 0 or bellow 0")
                return {"amount-of-money": None}
            return {"amount-of-money": amount_of_money}
        
        dispatcher.utter_message(template="utter_wrong_type")
        return {"amount-of-money": amount_of_money}

    async def validate_publisher(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'publisher' slot"""

        if not value:
            return {"publisher": None}

        if type(value) is str:
            publisher = tracker.get_slot("publisher")
            if publisher.lower() == 'none':
                return {"publisher": None}
            return {"publisher": publisher}
        
        dispatcher.utter_message(template="utter_wrong_type")
        return {"publisher": publisher}

    async def validate_title(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate value of 'title' slot"""

        if not value:
            return {"title": None}

        if type(value) is str:
            title = tracker.get_slot("title")
            if title.lower() == 'none':
                return {"title": None}
            return {"title": title}
        
        dispatcher.utter_message(template="utter_wrong_type")
        return {"title": title}