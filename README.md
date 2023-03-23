# Project BeGreen - Group 17
## ECM2434 Group Software Development

[![Django CI](https://github.com/r-3than/Group17-ECM2434/actions/workflows/django.yml/badge.svg?branch=main)](https://github.com/r-3than/Group17-ECM2434/actions/workflows/django.yml)

## Project Summary

<image src="BeGreen Presentation Poster.png" width="100%">

BeGreen is a django-powered web-based social media app, designed to encorage sustainability on campus through the use of *"eco-challenges"*.
Users are encoraged to submit photos of them completing the sustainable activity, and to interact with submissions of their friends and others on the app.

#### Features
Points are awarded for submissions based on punctuality, and for any upvotes recieved/given.
The app will feature University/friend leaderboards, and a shop for redeeming virtual rewards.
The shop system itself could also be expanded to include, for example, offerings of vouchers for university servicies - this would better incentivise use of the app.

#### Redeployability
This project could be deployed by any universitsy by simply modifying the `MICROSOFT["valid_email_domains"]` list in the [settings](./djangoApp/projectGreen/projectGreen/settings.py) file, as user accounts are verified using Microsoft OAuth.
In the case of multiple domains being present, users not in the primary domain will have their usernames suffixed with the domain to prevent overlap.

#### Influences
We took heavy inspiration from **BeReal** for our main gimmick, thanks to its current relevance.
For the interface, we looked at **Reddit**, due to its ease of portability between desktop and mobile. 

## Process Documents

#### Kanban Board
We have been using a Kanban Board, hosted on **Trello**, to orginise this project, and accomodate an agile aproach. The live board can be found [here](https://trello.com/b/xLFiqGIn/kanban-group-software-dev).
Additionally, an archive of the board (screenshots taken at each group/client meeting) are stored in the Git repositry, in the [Kanban Archive](<./Kanban Archive/>) folder.

#### Meeting Minutes
The discussions during group meetings - as well as feedback from client meetings - are recorded in the form of minutes, which are stored, along with our Policies document, in the [Meeting Minutes](<./Meeting Minutes/>) folder.

## Product Documents
While the interface for the product is still subject to change, our inital mockups for the UI can be found [here](https://trello.com/c/fVn0FVUt/25-prototype-front-end).
We have used the **University of Exeter** colour palette, in order to make our app consitient with the brand - see page 7 of the [brand book](https://brand.exeter.ac.uk/wp-content/uploads/2022/09/University-of-Exeter_Brand-Book.pdf) for reference.

## Technical Notes
Github actions are being utilised in this project to unit tests for the main django app, along with some sub-systems.
Various notes related to running and maintaining the app are listed in [this text file](<./djangoApp/projectGreen/notes.txt>).
The specification for this project is provided below:

https://vle.exeter.ac.uk/pluginfile.php/1800367/mod_label/intro/project-spec-2023.pdf.

### Testing

A comprehensive testing strategy is outlined in [TESTING.md](<./TESTING.md>).

### Dealing with Data Requests

Provided with the database is a data request function. Calling `user_data(fetch=True)` on a profile instance will return a dictionary of all items in our database related to a single user. This includes friend connections, submissions, comments and upvotes.

### Points Economy

The points system is entirely modular, so can be changed globally in [models.py](<./djangoApp/projectGreen/projectGreen/models.py>), but make sure to resynchronize all users points (from the admin panel) if you do this.

## Group Members

+ [Ethan](https://github.com/r-3than) - *<er545@exeter.ac.uk>*
+ [Thomas](https://github.com/tom-newbold) - *<tn337@exeter.ac.uk>*
+ [Oli](https://github.com/olijarrett) - *<omj202@exeter.ac.uk>*
+ [Luc](https://github.com/lbiragnet) - *<lbb203@exeter.ac.uk>*
+ [Steven](https://github.com/StevenXD777) - *<sj546@exeter.ac.uk>*
+ [James](https://github.com/James13524) - *<ja669@exeter.ac.uk>*

## License

This project uses an MIT license, detailed in [LICENCE.MD](LICENSE.MD).