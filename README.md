# aliasing-checker
Mining Software Repositories tool that checks whether there are some aliases among the contributors

## Installation
Please make sure you install all the dependencies before running the tool. You can do it by running the following command:
```
pip install -r requirements.txt
```

## Usage
To run the tool, you need to specify the following parameters:
* `-p` or `--path` - path to the repository
* `-o` or `--output` - path to the output file
If one of the parameters is not specified, the CLI will require the parameter as input before running.
Example:
```
python main.py -p /path/to/the/repository -o /path/to/the/output/file
```

## Output
Two files are generated as the output:
* `list_of_contributors.txt` - contains the list of all the contributors
* `list_of_persons.txt` - contains the list of all the persons filtered by the names that are considered to be aliases