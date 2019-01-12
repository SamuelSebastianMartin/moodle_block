#! /usr/bin/env python3

import pandas as pd
import os
import html_table_class as table
import re

def main():
    # Get variable names.
    module = input('Which module are you building \nelas, fdps, icc, summer: ')
    year = input('How to display the year? eg 2019-20: ')
    module = module.lower()
    module_title = module.upper() + ' Courses: ' + year
    module_courselist = 'courselist_' + module + '.csv'
    module_saveas = module + '_block.html'
    module_regex = 'regex_names_' + module + '.csv'
    os_instruction = 'epiphany ' + module_saveas
    if module == 'icc':
        bg_color = '#d3f486'
    if module == 'elas':
        bg_color = '#ffc821'
    if module == 'fdps':
        bg_color = '#fdd4ce'

    # Run program.
    df = pd.read_csv(module_courselist)
    add_term(df)
    add_brief_name(df, module_regex)
    add_href(df)
    build_block(df, module_saveas, module_title, bg_color)
    os.system(os_instruction)


def add_term(df):
    "Adds a column with the term number"
    terms = []

    for index, row in df.iterrows():
        name = (row['coursename'])
        term = re.compile(r'\bterm\s+?[123]', re.IGNORECASE).search(name)
        block = re.compile(r'\bblock\s+?[123]', re.IGNORECASE).search(name)
        if term:
            terms.append(term.group()[-1])  # Add term number
        elif block:
            terms.append(block.group()[-1])  # Add block number
        else:
            terms.append(None)  # 'None' if no term or block in coursename.
    df['term/block'] = terms


def add_brief_name(df, module_regex):
    """Adds a column with the shortened coursename that will be displayed
    in the final table."""
    brief_names = []

    for index, row in df.iterrows():
        name = (row['coursename'])
        term = (row['term/block'])
        brief_name = assign_names(name, module_regex)
        if brief_name:
            brief_names.append(brief_name)
        else:
            brief_names.append('No Name')

    df['brief name'] = brief_names
    return brief_names


def assign_names(name, module_regex):
    """Extracts the display name from the coursename.
    The 'regex_names' list is unique for each module (ICC, ELAS etc.), and
    must be hard coded. Each item in the list is a 2-tuple, consisting in
    a regex to identify the course from the official course title, and 
    a display name for the table. Each regex will match only one result,
    except ELAS A1, A2 etc, which reterns the group() of the regex"""

    # Academic English courses: A1, A2 etc.
    ae = re.compile(r'academic\W+english\W+a[1-5]\b',
                    re.IGNORECASE).search(name)
    if ae:
        return ae.group()[-2:]

    else:
        # Other courses: read the list of regex/name pairs.
        regex_names = pd.read_csv(module_regex, sep=';')

        for index, row in regex_names.iterrows():
            regex = row['regex']
            if re.compile(regex, re.IGNORECASE).search(name):  # Check regex search
                return row['name']

    # In the unlikely event of no match found:
    import pdb; pdb.set_trace()#
    return None


def add_href(df):
    """Adds a new column to df, giving the html code that will appear in the
    final table. Whatever is in this code will be placed between the tags
    which define the table cell: <td> and </td>. Therefore the Name and href
    must be included: eg '<a href="https://linkpage">Course Name</a>"""
    hrefs = []

    for index, row in df.iterrows():
        name = (row['brief name'])
        url = (row['url'])
        href = '<a href="' + url + '" target="_blank" >' + name + '</a>'
        hrefs.append(href)
    df['href'] = hrefs
    return hrefs


def build_block(df, module_saveas, module_title, bg_color):
    block = table.HtmlTable()
    block.bg_color = bg_color
    block.table_header(title=module_title)
    if 'elas' in module_saveas or 'summer' in module_saveas:
        #  Only make columns for ELAS and SUMMER.
        block.table_columns()
        block.column_headings(td1='Term 1', td2='Term 2', td3='Term 3')
    add_rows(block, df)

    block.write_page(module_saveas)


def add_rows(block, df):
    courselist = df['href'].tolist()
    while len(courselist) >= 3:
        a, b, c = courselist[0], courselist[1], courselist[2]
        block.add_row(a, b, c)
        for item in (a, b, c):
            courselist.remove(item)
    if len(courselist) == 2:
        a, b, c = courselist[0], courselist[1], ''
        block.add_row(a, b, c)
        return
    elif len(courselist) == 1:
        a, b, c = courselist[0], '', ''
        block.add_row(a, b, c)
        return
    else:
        return


if __name__ == '__main__':
    main()