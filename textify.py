import re

def remove_bad_chars(str):
    str = re.sub(r'[‘&()\\\-\\\"\\\'\\\[\\\]\\\–\\\,\\\’]', '', str).lower()
    return str

def remove_excluded_words(str_list):
    stopwords = ['radio','edit','ft.','feat.','ms.','with','the','mix','bonus','track']
    new_list= [word for word in str_list if word not in stopwords]
    return new_list

def clean_string(str):
    clean_split = remove_bad_chars(str).split()
    fully_clean = remove_excluded_words(clean_split)
    return fully_clean