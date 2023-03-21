# Project Begreen - Testing

## Testing Strategy

The unit tests included in the source code are directed towards the models used by the application, as well as scripts used to enable specific features (such as exracting GPS data from images).

The [models](./djangoApp/projectGreen/projectGreen/models.py) form the core back-end of the application: they are used to manipulate objects such as challenges, submissions,  profiles, etc through helper functions.

Since modifying objects relies on invoking one or more helper functions on them, our strategy specifically targets unit testing these helper functions individually in [test_models.py](./djangoApp/projectGreen/projectGreen/tests/test_models.py).

A script for [metadata extraction](./djangoApp/projectGreen/projectGreen/imageMetadata/extract_metadata.py) is provided in the source code, along with [unit tests](./djangoApp/projectGreen/projectGreen/imageMetadata/tests/test_extract_metadata.py) for its various functions. It is kept separate from models and their respective unit tests since it essentially acts as an external module, and does not require access to model fields or functions.

The [views](./djangoApp/projectGreen/projectGreen/views.py) essentially allow users to call certain model helper functions through the application interface. Since these are already unit tested, the views themselves along with the templates that they use are tested by running the application locally, navigating through the different pages, and trying out the different features.

To make this effective, it is possible to manipulate objects through the admin page, which can be accessed at [localhost:8000/admin](http://localhost:8000/admin) if hosting locally, or alternatively [projectgreen.grayitsolutions.com/admin](https://projectgreen.grayitsolutions.com/admin/) if using the deployed application. The admin page is defined by [admin.py](./djangoApp/projectGreen/projectGreen/admin.py), and gives an administrator the ability to manually create, edit and delete objects by invoking model helper functions (which are all individually tested as mentionned).

Therefore the testing strategy for the application relies on unit tests for model and metadata-processing functions, as well as integration tests by manually altering objects through the admin page and using the features of the application through the interface.


## Running Unit Tests
The majority of unit tests are aimed at model helper functions. They can be executed from the outer [/projectGreen/](./djangoApp/projectGreen/) folder, if all required modules from [requirements.txt](./djangoApp/projectGreen/requirements.txt) are installed. If this is not the case, we recommend starting a Python virtual environment and running:

    $ pip install -r requirements.txt

The unit tests can then be run using:

    $ python manage.py test

Additionally, more unit tests are provided for functions used to extract and process GPS metadata from images. Provided the required modules are installed, these can be run from the [/imageMetadata/](./djangoApp/projectGreen/projectGreen/imageMetadata/) folder using:

    $ python -m pytest