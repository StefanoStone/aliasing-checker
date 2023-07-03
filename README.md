# aliasing-checker
Mining Software Repositories tool that checks whether there are some aliases among the contributors.
The path of the repository can also refer to a remote repository.

**NOTE:** the tool does not make use of any remote services direct APIs. It is only based on the information available in the repository.

## Installation
Please make sure you install all the dependencies before running the tool. You can do it by running the following command:
```
pip install -r requirements.txt
```

## Usage
Example:
```
python main.py -p /path/to/the/repository -o /path/to/the/output/file
```

Use the following command to see the full list of the available options:
```
python main.py -h
```

## Testing
use the following command to run the tests:
```
pytest test.py
```
to test the functionality based on pydriller, "test_repos" contains all the repositories that can be used in the test functions.
It is a small repository provided by pydriller. The repository is located in the main folder of the project.
