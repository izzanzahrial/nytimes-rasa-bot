# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.forms import FormValidationAction
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

        if tracker.get_slot("time") != "skip":
            category = tracker.get_slot("category")
            time = tracker.get_slot("time")

            url = f"https://api.nytimes.com/svc/books/v3/lists/{time}/{category}.json?&api-key="+api_key

            response = requests.get(url)
            data = response.json()

            if data["status"] == "ERROR":
                dispacther.utter_message(response="utter_doesnt_exist")
            elif data["results"]:
                
                data_range = data["num_results"]

                if data_range == 0:
                    dispacther.utter_message(response="utter_doesnt_exist")
                else:
                    if data_range > 18:
                        data_range = 18

                    dispacther.utter_message(text=f"Here's a list of best seller {category}\n")

                    for i in range(data_range):
                        amazon_url = data["results"]["books"][i]["amazon_product_url"]
                        title = data["results"]["books"][i]["title"]
                        author = data["results"]["books"][i]["author"]
                        book_image = data["results"]["books"][i]["book_image"]
                        dispacther.utter_message(text=f"{i+1}. Title = {title}\nAuthor = {author}\nWhere to buy = {amazon_url}\n")
                        dispacther.utter_message(image=f"{book_image}")
            else:
                dispacther.utter_message(response="utter_doesnt_exist")
                    
        elif tracker.get_slot("time") == "skip":
            category = tracker.get_slot("category")

            url = f"https://api.nytimes.com/svc/books/v3/lists/current/{category}.json?&api-key="+api_key

            response = requests.get(url)
            data = response.json()
            
            if data["status"] == "ERROR":
                dispacther.utter_message(response="utter_doesnt_exist")
            elif data["results"]:
                
                data_range = data["num_results"]

                if data_range == 0:
                    dispacther.utter_message(response="utter_doesnt_exist")
                else:
                    if data_range > 18:
                        data_range = 18

                    dispacther.utter_message(text=f"Here's a list of best seller {category}\n")

                    for i in range(data_range):
                        amazon_url = data["results"]["books"][i]["amazon_product_url"]
                        title = data["results"]["books"][i]["title"]
                        author = data["results"]["books"][i]["author"]
                        book_image = data["results"]["books"][i]["book_image"]
                        dispacther.utter_message(text=f"{i+1}. Title = {title}\nAuthor = {author}\nWhere to buy = {amazon_url}\n")
                        dispacther.utter_message(image=f"{book_image}")
            else:
                dispacther.utter_message(response="utter_failed")
        else:
            dispacther.utter_message(response="utter_can't_skip_all")

        return [AllSlotsReset()]

class ValidateListBestSellerForm(FormValidationAction):
    """Validates Slots of the list_best_seller_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_list_best_seller_form"

    async def validate_category(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'category' slot"""
        if slot_value.lower() == "skip":
            return {"category": "skip"}
        
        if type(slot_value) is str:
            category = tracker.get_slot("category")
            return {"category": category}
        else: 
            dispatcher.utter_message(response="utter_wrong_type")
            return {"category": None}
        
        return {"category": None}

    async def validate_time(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'time' slot"""
        if type(slot_value) is str:
            if slot_value.lower() == "skip":
                return {"time": "skip"}
            time = tracker.get_slot("time")
            return {"time": time}
            
        dispatcher.utter_message(response="utter_wrong_type")
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

        if tracker.get_slot("time") != 'skip':
            time = tracker.get_slot("time")
                
            url = f"https://api.nytimes.com/svc/books/v3/lists/overview.json"

            parameters = {
                'api-key': api_key,
                'published_date': time
            }

            response = requests.get(url, params=parameters)
            data = response.json()

            data_range = data["num_results"]
            if data_range > 18:
                data_range = 18

            if data["results"]:
                dispacther.utter_message(text=f"Here's a list of list best seller at {time} \n")

                for i in range(data_range):
                    list_name = data["results"]["lists"][i]["list_name"]
                    book_image = data["results"]["lists"][i]["books"][0]["book_image"]
                    author = data["results"]["lists"][i]["books"][0]["author"]
                    title = data["results"]["lists"][i]["books"][0]["title"]
                    description = data["results"]["lists"][i]["books"][0]["description"]
                    amazon = data["results"]["lists"][i]["books"][0]["buy_links"][0]["url"]
                    dispacther.utter_message(text=f"{i+1}. List name: {list_name}\nTitle: {title}\nAuthor: {author}\nDescription: {description}\nWhere to buy: {amazon}")
                    dispacther.utter_message(image=f"{book_image}")
            else:
                dispacther.utter_message(response="utter_doesnt_exist")

        elif tracker.get_slot("time") == 'skip':

            url = f"https://api.nytimes.com/svc/books/v3/lists/overview.json?&api-key={api_key}"

            parameters = {
                'api-key': api_key,
            }

            response = requests.get(url, params=parameters)
            data = response.json()
            today = datetime.date.today()

            data_range = data["num_results"]
            if data_range > 18:
                data_range = 18

            if data["results"]:
                dispacther.utter_message(text=f"Here's a list of list best seller at {today} \n")

                for i in range(data_range):
                    list_name = data["results"]["lists"][i]["list_name"]
                    book_image = data["results"]["lists"][i]["books"][0]["book_image"]
                    author = data["results"]["lists"][i]["books"][0]["author"]
                    title = data["results"]["lists"][i]["books"][0]["title"]
                    description = data["results"]["lists"][i]["books"][0]["description"]
                    amazon = data["results"]["lists"][i]["books"][0]["buy_links"][0]["url"]
                    dispacther.utter_message(text=f"{i+1}. List name: {list_name}\nTitle: {title}\nAuthor: {author}\nDescription: {description}\nWhere to buy: {amazon}")
                    dispacther.utter_message(image=f"{book_image}")
            else:
                dispacther.utter_message(response="utter_doesnt_exist")

        else:
            dispacther.utter_message(response="utter_can't_skip_all")

        return [AllSlotsReset()]

class ValidateBestSellerListOverview(FormValidationAction):
    """Validates Slots of the list_best_seller_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_list_best_seller_overview_form"

    async def validate_time(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'time' slot"""
        if type(slot_value) is str:
            if slot_value.lower() == "skip":
                return {"time": "skip"}
            time = tracker.get_slot("time")
            return {"time": time}
            
        dispatcher.utter_message(response="utter_wrong_type")
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

        param = [number, title, author]
        param = checkParam(param)

        if param is not None:

            url = f"https://api.nytimes.com/svc/books/v3/reviews.json"

            parameters = {
                'api-key': api_key,
                'isbn': param[0],
                'title': param[1],
                'author': param[2],
            }

            response = requests.get(url, params=parameters)
            data = response.json()

            data_range = data["num_results"]
            if data_range > 18:
                data_range = 18

            if data["status"] == "ERROR":
                dispacther.utter_message(text="This requires at least one parameter")
            elif data["results"]:
                dispacther.utter_message(text=f"Here's a list of review \n")

                for i in range(data_range):
                    review_url = data["results"][i]["url"]
                    publication_dt = data["results"][i]["publication_dt"]
                    review_by = data["results"][i]["byline"]
                    book_title = data["results"][i]["book_title"]
                    book_author = data["results"][i]["book_author"]
                    dispacther.utter_message(text=f"{i+1}. Book title: {book_title}\nBook author: {book_author}\nReview by: {review_by}\nPublication date: {publication_dt}\nReview link: {review_url}\n")
            else:
                dispacther.utter_message(response="utter_failed")
        
        else:
            dispacther.utter_message(response="utter_can't_skip_all")

        return [AllSlotsReset()]

class ValidateBookReview(FormValidationAction):
    """Validates Slots of the book_review_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_book_review_form"

    async def validate_number(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'number' slot"""
        if slot_value:
            slot_value = str(slot_value)

            if slot_value.lower() == "skip":
                return {"number": "skip"}

            number = tracker.get_slot("number")
            number = str(number)
            
            if len(number) == 10 or len(number) == 13:
                return {"number": number}
            else:
                dispatcher.utter_message(response="utter_wrong_amount")
                return {"number": None}
        
        dispatcher.utter_message(response="utter_wrong_type")
        return {"number": None}

    async def validate_title(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'title' slot"""
        if type(slot_value) is str:
            if slot_value.lower() == "skip":
                return {"title": "skip"}
            else:
                return {"title": slot_value}            
        
        dispatcher.utter_message(response="utter_wrong_type")
        return {"title": None}

    async def validate_PERSON(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'PERSON' slot"""
        if slot_value.lower() == "skip":
            return {"PERSON": "skip"}
        
        if type(slot_value) is str:
            author = tracker.get_slot("PERSON")
            return {"PERSON": author}
        
        dispatcher.utter_message(response="utter_wrong_type")
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

        param = [age_group, author, contributor, number, amount_of_money, publisher, title]
        param = checkParam(param)

        if param is not None:

            for idx, val in enumerate(param):
                if val == "skip":
                    param[idx] = None
            
            url = f"https://api.nytimes.com/svc/books/v3/lists/best-sellers/history.json"

            parameters = {
                'api-key': api_key,
                'age-group': param[0],
                'author': param[1],
                'contributor': param[2],
                'isbn': param[3],
                'price': param[4],
                'publisher': param[5],
                'title': param[6],
            }

            response = requests.get(url, params=parameters)
            data = response.json()

            data_range = data["num_results"]
            if data_range > 18:
                data_range = 18

            if data["status"] == "ERROR":
                dispacther.utter_message(text="This requires at least one parameter")
            elif data["results"]:
                dispacther.utter_message(text="Here's a list of book's detail \n")

                for i in range(data_range):
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
                    dispacther.utter_message(text=f"{i+1}.Title: {title}\nDescription: {description}\nContributor: {contributor}\nAuthor: {author}\nPrice: {price} $\nAge-group: {age_group}\nPublisher: {publisher}\nIsbn's : {isbn10}, {isbn13}\nReview link: {review_url}\n")
            else:
                dispacther.utter_message(response="utter_failed")

        else:
            dispacther.utter_message(response="utter_can't_skip_all")

        return [AllSlotsReset()]

class ValidateBookDetail(FormValidationAction):
    """Validates Slots of the book_detail_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_book_detail_form"

    async def validate_age_group(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'age_group' slot"""
        if slot_value:
            slot_value = str(slot_value)

            if slot_value.lower() == "skip":
                return {"age_group": "skip"}

            age_group = tracker.get_slot("age_group")
            age_group = int(age_group)
            
            if age_group > 0:
                age_group = str(age_group)
                return {"number": age_group}
            else:
                dispatcher.utter_message(response="utter_wrong_amount")
                return {"number": None}
        
        dispatcher.utter_message(response="utter_wrong_type")
        return {"number": None}

    async def validate_PERSON(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'PERSON' slot"""
        if slot_value.lower() == "skip":
            return {"PERSON": "skip"}

        if type(slot_value) is str:
            author = tracker.get_slot("PERSON")
            return {"PERSON": author}
        
        dispatcher.utter_message(response="utter_wrong_type")
        return {"PERSON": None}

    async def validate_number(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'number' slot"""
        if slot_value:
            slot_value = str(slot_value)

            if slot_value.lower() == "skip":
                return {"number": "skip"}

            number = tracker.get_slot("number")
            number = str(number)
            
            if len(number) == 10 or len(number) == 13:
                return {"number": number}
            else:
                dispatcher.utter_message(response="utter_wrong_amount")
                return {"number": None}
        
        dispatcher.utter_message(response="utter_wrong_type")
        return {"number": None}

    async def validate_amount_of_money(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'amount-of-money' slot"""
        if slot_value.lower() == "skip":
            return {"amount-of-money": "skip"}

        if type(slot_value) is str:
            amount_of_money = tracker.get_slot("amount-of-money")
            if int(amount_of_money) <= 0:
                dispatcher.utter_message(text= "The price can't be 0 or bellow 0")
                return {"amount-of-money": None}
            return {"amount-of-money": amount_of_money}
        
        dispatcher.utter_message(response="utter_wrong_type")
        return {"amount-of-money": amount_of_money}

    async def validate_publisher(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'publisher' slot"""
        if slot_value.lower() == "skip":
            return {"publisher": "skip"}

        if type(slot_value) is str:
            publisher = tracker.get_slot("publisher")
            return {"publisher": publisher}
        
        dispatcher.utter_message(response="utter_wrong_type")
        return {"publisher": publisher}

    async def validate_title(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'title' slot"""
        if type(slot_value) is str:
            if slot_value.lower() == "skip":
                return {"title": "skip"}
            else:
                return {"title": slot_value}
        
        dispatcher.utter_message(response="utter_wrong_type")
        return {"title": title}

    async def validate_contributor(
        self, 
        slot_value: Any,
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate value of 'contributor' slot"""
        if slot_value.lower() == "skip":
            return {"contributor": "skip"}

        if type(slot_value) is str:
            contributor = tracker.get_slot("contributor")
            return {"contributor": contributor}
        
        dispatcher.utter_message(response="utter_wrong_type")
        return {"contributor": None}


def checkParam(param):
    return [None if val == "skip" else val for val in param]