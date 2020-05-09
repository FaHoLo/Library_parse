# Book parser for [tululu.org](http://tululu.org)

The project was created for parse books from [tululu.org](http://tululu.org).

[Russian doc](https://github.com/FaHoLo/Library_parse/blob/master/READMEru.md)

### Installation

1. Python3 should already be installed.

2. It is recommended to use [virtualenv/venv](https://docs.python.org/3/library/venv.html) to isolate the project.

3. Use `pip` (or `pip3`, there is a conflict with Python2) to install the dependencies:
```
pip install -r requirements.txt
```

4. Run the file `parse_tululu_category.py` with or without arguments.

### Arguments

Without arguments script will download all books from all pages of [this category](http://tululu.org/l55/) (it will take much time). There are some arguments that could help to customize this process:
```
--start_page — number of first page for download
--end_page — page number to which books will be downloaded
--dest_folder — choose folder for parsed files: images, books, json
--skip_imgs — don't download book images
--skip_txt — don't download book texts
--json_path — choose folder to *.json file with books info
```
Arguments use example:
```
python3 parse_tululu_category.py --start_page 3 --end_page 5 --skip_imgs --json_path example\path\
```

There are shortcuts for all arguments, to see them use this command:
```
python3 parse_tululu_category.py -h
```
### Project goals

This code is written for educational purposes on the online course for web developers [dvmn.org](https://dvmn.org/).
