# Project BeGreen - Testing

## Testing Strategy

The unit tests included in the source code are directed towards the models used by the application, as well as scripts used to enable specific features (such as exracting GPS data from images).

The [models](./djangoApp/projectGreen/projectGreen/models.py) form the core back-end of the application; they are used to manipulate objects such as challenges, submissions,  profiles, etc through the provided helper functions.

Since modifying objects relies on invoking one or more of these functions on each instance, our strategy specifically targets unit testing them individually. in [test_models.py](./djangoApp/projectGreen/projectGreen/tests/test_models.py).

A script for [metadata extraction](./djangoApp/projectGreen/projectGreen/imageMetadata/extract_metadata.py) is provided in the source code, along with associated [unit tests](./djangoApp/projectGreen/projectGreen/imageMetadata/tests/test_extract_metadata.py) for its component functions. It is kept separate from models and their respective unit tests, since it essentially acts as an external module, and does not require access to either model fields or functions.

The [views](./djangoApp/projectGreen/projectGreen/views.py) essentially allow users to call certain sequences of model helper functions through the application interface. Since these are already unit tested, the views themselves - along with the templates that they use - are tested by running the application locally, navigating through the different pages, and trying out the different features.

To improve the effectiveness of this strategy, it is possible to manipulate objects through the admin page, which can be accessed at [localhost:8000/admin](http://localhost:8000/admin) if hosting locally, or alternatively [projectgreen.grayitsolutions.com/admin](https://projectgreen.grayitsolutions.com/admin/) if using the deployed application. The admin page is defined by [admin.py](./djangoApp/projectGreen/projectGreen/admin.py), and gives an administrator account the ability to manually create, modify and delete objects by invoking a range of defined actions. These actions are composed of the model helper functions which are all individually tested, as mentioned) above.

In summary, the testing strategy for this application relies on unit tests for model and metadata-processing functions, as well as integration tests on the interface by manually altering objects through the admin page and using the features of the application as a user would.


## Running Unit Tests
The django-based unit tests are aimed at model helper functions. They can be executed from the outer [/projectGreen/](./djangoApp/projectGreen/) folder, if all required modules from [requirements.txt](./djangoApp/projectGreen/requirements.txt) are installed. If this is not the case, we recommend starting a Python virtual environment and running:

    $ pip install -r requirements.txt

The unit tests can then be run using:

    $ python manage.py test

Additionally, more unit tests are provided for functions used to extract and process GPS metadata from images. Provided the required modules are installed, these can be run from the [/imageMetadata/](./djangoApp/projectGreen/projectGreen/imageMetadata/) folder using:

    $ python -m pytest
