Recipe App API
This is a recipe app API built using Django REST framework and Test Driven Development (TDD). The app allows users to create, retrieve, update, and delete recipes, as well as create tags and ingredients associated with those recipes.

Installation
To install the necessary dependencies for this app, run the following command:


pip install -r requirements.txt


To run the app, use the following command:

python manage.py runserver

Once the app is running, you can access the API via http://localhost:8000/api/.

To create a new user, make a POST request to http://localhost:8000/api/user/create/, providing the following information in the request body:


{
    "email": "user@example.com",
    "password": "testpass",
    "name": "Test User"
}

To authenticate a user, make a POST request to http://localhost:8000/api/user/token/, providing the user's email and password in the request body:


{
    "email": "user@example.com",
    "password": "testpass"
}

This will return a token that can be used to access protected endpoints.

To create a new recipe, make a POST request to http://localhost:8000/api/recipe/recipes/, providing the following information in the request body:

json

{
    "title": "Test Recipe",
    "time_minutes": 10,
    "price": 5.00
}

To add tags and ingredients to a recipe, make POST requests to http://localhost:8000/api/recipe/tags/ and http://localhost:8000/api/recipe/ingredients/, respectively, providing the appropriate information in the request body.


To retrieve a list of all recipes, make a GET request to http://localhost:8000/api/recipe/recipes/.


For more detailed information on available endpoints and their usage, see the API documentation at http://localhost:8000/api/docs/.

Running tests

To run the automated tests for this app, use the following command:

python manage.py test

This will run all tests in the tests directory and output the results.


Recipe App API Images:

<img width="1512" alt="Screenshot 2023-02-20 at 8 51 11 PM" src="https://user-images.githubusercontent.com/45141940/220228166-156b9c97-6f30-40b8-99ce-e435a74b371e.png">
<img width="1512" alt="Screenshot 2023-02-20 at 8 51 27 PM" src="https://user-images.githubusercontent.com/45141940/220228241-23cf4f26-d892-41ca-b2fb-3bf9721a32ad.png">
<img width="1512" alt="Screenshot 2023-02-20 at 8 51 44 PM" src="https://user-images.githubusercontent.com/45141940/220228257-6f88ccba-ad56-4f50-af99-e89d69551e8b.png">
<img width="1512" alt="Screenshot 2023-02-20 at 8 51 51 PM" src="https://user-images.githubusercontent.com/45141940/220228269-7d228bde-59c0-492d-b605-b92334a7926e.png">
<img width="1512" alt="Screenshot 2023-02-20 at 8 52 48 PM" src="https://user-images.githubusercontent.com/45141940/220228291-f379d527-807a-4812-a269-98066a278923.png">
<img width="1512" alt="Screenshot 2023-02-20 at 8 53 33 PM" src="https://user-images.githubusercontent.com/45141940/220228316-1375b2f4-983e-4043-a1a6-6e8df7b91a74.png">
<img width="1512" alt="Screenshot 2023-02-20 at 8 54 48 PM" src="https://user-images.githubusercontent.com/45141940/220228330-31f70a10-35f1-4ea7-9f61-c3f6f87c3a81.png">
<img width="1512" alt="Screenshot 2023-02-20 at 8 55 28 PM" src="https://user-images.githubusercontent.com/45141940/220228357-00356fa9-e205-40b4-9c98-7bd605f63e58.png">
<img width="1512" alt="Screenshot 2023-02-20 at 8 56 33 PM" src="https://user-images.githubusercontent.com/45141940/220228376-d5206c7d-7db1-4a89-bd4b-0e67db47e007.png">



Contributing

If you would like to contribute to this project, please fork the repository and make a pull request with your changes. Any contributions are welcome!
