# Project Begreen - Testing

## Testing Strategy

The unit tests included in the source code are directed towards the models used by the application, as well as scripts used to enable specific features (such as exracting GPS data from images).

The [models](./djangoApp/projectGreen/projectGreen/models.py) form the core back-end of the application: they are used to manipulate objects such as challenges, submissions,  profiles, etc through helper functions.

Since modifying objects relies on invoking one or more helper functions on them, our strategy specifically targets unit testing these helper functions individually in [test_models.py](./djangoApp/projectGreen/projectGreen/tests/test_models.py).

The [views](./djangoApp/projectGreen/projectGreen/views.py) 