# aliasing-checker
Mining Software Repositories tool that checks whether there are some aliases among the contributors.
The path of the repository can also refer to a remote repository.

**NOTE:** the tool do not make use of any remote services direct APIs. It is only based on the information available in the repository.

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