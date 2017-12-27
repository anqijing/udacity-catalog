# UDACITY catalog item project
A web application that provides a list of items within a variety of categories and integrate third party user registration and authentication.  developing a web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users should have the ability to post, edit, and delete their own items.
## Installation
1. Install Vagrant and VirtualBox
2. Clone the fullstack-nanodegree-vm
3. Launch the Vagrant VM (vagrant up) and go to the catalog folder and replace it with the contents of this respository.
## Usage
Create database by running
```
python database_setup.py
```
Populate database with:
```
python populatemovies.py
```
Run the app:
```
python app.py
```
Then browse the application at this URL:
```
http://localhost:5050
```
## JSON endpoint
View category and item information at the url
```
http://localhost:5000/catalog
```
