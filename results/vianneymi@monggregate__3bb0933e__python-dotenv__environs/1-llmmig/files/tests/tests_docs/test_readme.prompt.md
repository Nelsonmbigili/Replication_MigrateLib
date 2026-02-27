The following Python code currently uses the library "python-dotenv" version 1.1.0.
Migrate this code to use the library "environs" version 14.1.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "python-dotenv" to "environs".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "python-dotenv" and "environs".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
"""
Module to tests the code snippet in the readme file.

NOTE : Every update on below tests need to be reflected in the readme file.
"""

import pytest

@pytest.mark.skip("Need to authorize the IP address of the machine running the tests.")
@pytest.mark.e2e
def test_basic_pipeline_usage()->None:
    """Tests basic pipeline usage example.
    
    (First code snippet)
    """

    import os

    from dotenv import load_dotenv 
    import pymongo
    from monggregate import Pipeline

    # Creating connexion string securely
    load_dotenv(verbose=True)
    PWD = os.environ["MONGODB_PASSWORD"]
    print("PWD: ", PWD)
    MONGODB_URI = f"mongodb+srv://dev:{PWD}@myserver.xciie.mongodb.net/?retryWrites=true&w=majority"
    print("MONGODB_URI: ", MONGODB_URI)

    # Connect to your MongoDB cluster:
    client = pymongo.MongoClient(MONGODB_URI)

    # Get a reference to the "sample_mflix" database:
    db = client["sample_mflix"]

    # Creating the pipeline
    pipeline = Pipeline()

    # The below pipeline will return the most recent movie with the title "A Star is Born"
    pipeline.match(
        title="A Star Is Born"
    ).sort(
        by="year"
    ).limit(
        value=1
    )

    # Executing the pipeline
    curosr = db["movies"].aggregate(pipeline.export())

    results = list(curosr)
    assert results

@pytest.mark.skip("Need to authorize the IP address of the machine running the tests.")
@pytest.mark.e2e
def test_advanced_usage()->None:
    """Tests more advanced pipeline usage example.
    
    (Second code snippet)
    """

    import os

    from dotenv import load_dotenv 
    import pymongo
    from monggregate import Pipeline, S

    # Creating connexion string securely
    load_dotenv(verbose=True)
    PWD = os.environ["MONGODB_PASSWORD"]
    MONGODB_URI = f"mongodb+srv://dev:{PWD}@myserver.xciie.mongodb.net/?retryWrites=true&w=majority"


    # Connect to your MongoDB cluster:
    client = pymongo.MongoClient(MONGODB_URI)

    # Get a reference to the "sample_mflix" database:
    db = client["sample_mflix"]


    # Creating the pipeline
    pipeline = Pipeline()
    pipeline.match(
        year=S.type_("number") # Filtering out documents where the year field is not a number
    ).group(
        by="year",
        query = {
            "movie_count":S.sum(1), # Aggregating the movies per year
            "movie_titles":S.push("$title")
        }
    ).sort(
        by="_id",
        descending=True
    ).limit(10)

    # Executing the pipeline
    cursor = db["movies"].aggregate(pipeline.export())
    
    # Printing the results
    results = list(cursor)
    #print(results)
    assert results

@pytest.mark.skip("Need to authorize the IP address of the machine running the tests.")
@pytest.mark.e2e
def test_even_more_advanced_usage()->None:
    """Tests even more advanced pipeline usage example.
    
    (Third code snippet)

    """

    import os

    from dotenv import load_dotenv 
    import pymongo
    from monggregate import Pipeline, S

    # Creating connexion string securely
    load_dotenv(verbose=True)
    PWD = os.environ["MONGODB_PASSWORD"]
    MONGODB_URI = f"mongodb+srv://dev:{PWD}@myserver.xciie.mongodb.net/?retryWrites=true&w=majority"


    # Connect to your MongoDB cluster:
    client = pymongo.MongoClient(MONGODB_URI)

    # Get a reference to the "sample_mflix" database:
    db = client["sample_mflix"]

    # Using expressions
    comments_count = S.size(S.comments)


    # Creating the pipeline
    pipeline = Pipeline()
    pipeline.lookup(
        right="comments",
        right_on="movie_id",
        left_on="_id",
        name="comments"
    ).add_fields(
        comments_count=comments_count
    ).match(
        operand=comments_count>2
    ).limit(1)


    # Executing the pipeline
    cursor = db["movies"].aggregate(pipeline.export())

    # Printing the results
    results = list(cursor)
    print(results)
    assert results, results

if __name__ == "__main__":
    test_basic_pipeline_usage()
    test_advanced_usage()
    test_even_more_advanced_usage()
    print("Everything passed")
```