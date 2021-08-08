#!/usr/bin/env python3

import sys
from html.parser import HTMLParser
from pprint import pprint
from collections import OrderedDict
from datetime import datetime


class MyHTMLParser(HTMLParser):
    elements = list()
    _current_path = list([elements])

    _SELF_CLOSING_TAGS = ['area', 'base', 'br', 'col', 'command', 'embed', 'hr',
                          'img', 'input', 'keygen', 'link', 'meta', 'param',
                          'source', 'track', 'wbr']

    def handle_starttag(self, tag, attrs):
        if tag in self._SELF_CLOSING_TAGS:
            element = dict()
            element[tag] = attrs
            if str(self.get_starttag_text()).endswith('/>'):
                element['closed'] = True
            else:
                element['closed'] = False

            self._current_path[-1].append(element)
            return

        # OrderedDict() is only useful for debugging and printing with pprint()
        # otherwise it uses more memory than dict() with no other benefit
        # element = OrderedDict()
        element = dict()
        element[tag] = attrs
        element['elements'] = list()
        # print(r'######################################')
        # print("handle_starttag:", tag)
        # # pprint(self._current_path, width=160, depth=None)
        # i = 0
        # for p in self._current_path:
        #     print('self._current_path[{}]:'.format(i))
        #     pprint(p, width=160, depth=None)
        #     i += 1
        # pprint(element, width=160, depth=1)
        # print(r'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        self._current_path[-1].append(element)
        self._current_path.append(element['elements'])

    def handle_endtag(self, tag):
        if tag in self._SELF_CLOSING_TAGS:
            return

        # print(r'######################################')
        # print("handle_endtag:", tag)
        # pprint(self._current_path, width=160, depth=None)
        # print(r'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
        self._current_path.pop()

    def handle_startendtag(self, tag, attrs):
        element = dict()
        element[tag] = attrs
        if str(self.get_starttag_text()).endswith('/>'):
            element['closed'] = True
        else:
            element['closed'] = False

        self._current_path[-1].append(element)

    def handle_data(self, data):
        element = dict()
        element['data'] = data
        self._current_path[-1].append(element)

    # if there is an entity inside a string like "hello &amp; goodbye &#x3E; whatever",
    #   then these functions will be called:
    # 1. handle_data("hello ")
    # 2. handle_entityref("amp")
    # 3. handle_data(" goodbye ")
    # 4. handle_charref("x3E")
    # 5. handle_data(" whatever")

    def handle_entityref(self, name):
        # print("handle_entityref:", name)
        # print("&" + name + ";", end='')
        element = dict()
        element['data'] = "&" + name + ";"
        self._current_path[-1].append(element)

    def handle_charref(self, name):
        # print("handle_charref:", name)
        # print("&#" + name + ";", end='')
        element = dict()
        element['data'] = "&#" + name + ";"
        self._current_path[-1].append(element)

    def handle_comment(self, data):
        element = dict()
        element['comment'] = data
        self._current_path[-1].append(element)

    def handle_decl(self, decl):
        element = dict()
        element['decl'] = decl
        self._current_path[-1].append(element)

    def handle_pi(self, data):
        element = dict()
        element['pi'] = data
        self._current_path[-1].append(element)

    def reconstruct_html(self) -> str:
        return self._reconstruct_html_recursive(self.elements)

    def _reconstruct_html_recursive(self, elements: list) -> str:
        html_string = str()
        for element in elements:
            for item in element.items():
                # item = element.keys()[0]
                if item[0] == 'data':
                    html_string += item[1]
                elif item[0] == 'comment':
                    html_string += "<!--" + item[1] + "-->"
                elif item[0] == 'decl':
                    html_string += "<!" + item[1] + ">"
                elif item[0] == 'pi':
                    html_string += "<?" + item[1] + ">"
                elif item[0] in self._SELF_CLOSING_TAGS:
                    html_string += "<" + item[0]
                    for attr in item[1]:
                        html_string += " " + attr[0] + \
                            "=" + '"' + attr[1] + '"'
                    if element.get('closed', False):
                        html_string += " /"
                    html_string += ">"
                else:  # must be a regular tag
                    html_string += "<" + item[0]
                    for attr in item[1]:
                        html_string += " " + attr[0] + \
                            "=" + '"' + attr[1] + '"'
                    html_string += ">"
                    html_string += self._reconstruct_html_recursive(
                        element['elements'])
                    html_string += "</" + item[0] + ">"
                break

        return html_string


# high level
# - Client
#   - remove list of methods
#   - make each method a collapsible section
# - Paginators
#   - remove list of paginators
#   - make each class a collapsible section

# what to modify:
# - insert css at the end of head (A)
# - insert script at the end of body (B)
# - remove: html > body > div class="container-wrapper" > div id="right-column" > div class="document clearer body" > div id="dynamodb" > div id="client" > dl class="class" > dd > ul class="simple"
# - at the same level of <ul class="simple">, for each <dl class="method">,
#   - add class collapsible-title to the dt
#   - add class collapsible-content to the dd

# - client section consists of a single class with multiple methods to fold
# - paginators section consists of multiple classes to fold, consisting of one method each (paginate)
# - waiters section is similar to paginators, with each class having one method (wait)
# - service resource section consists of multiple resource types
#   - Collections resource type contains multiple collections
#     - each collection has 


def get_first_elem(elements: list, elem_name: str, attrs: list):
    if attrs is None:
        attrs = list()
    for elem in elements:
        if elem_name in elem and set(attrs).issubset(elem[elem_name]):
            return elem

    return None


def get_elems(elements: list, elem_name: str, attrs: list):
    if attrs is None:
        attrs = list()
    return [x for x in elements if elem_name in x and set(attrs).issubset(x[elem_name])]


def add_collapsible_css(elements: list):
    search_path = [
        ('html', None),
        ('head', None),
    ]

    CSS_COLLAPSIBLE = '''  <!-- collapsible items -->
    <style>
      /* collapsible functionality */
      .collapsible-title {
        background-color: #f8f8f8;
        width: 100%;
        border: none;
        text-align: left;
        padding-left: 8px;
      }
      .collapsible-title:hover {
        background-color: #faf3e8;
      }
      .collapsible-title-active {
        background-color: aliceblue;
      }
      .collapsible-title-active:hover {
        background-color: antiquewhite;
      }
      .collapsible-content {
        display: none;
      }
      .collapsible-content-show {
        display: block;
      }
      /* remove horizontal lines between methods */
      dl.method {
        border-bottom: none;
      }
      /* move margins from after each item to before the next admonition */
      dl {
        margin-bottom: 0px;
      }
      .admonition-title {
        margin-top: 20px;
      }
      dl dd {
        margin-bottom: 20px;
      }
    </style>
'''

    elements = get_first_element_list(elements, search_path)

    elem = dict()
    elem['data'] = CSS_COLLAPSIBLE
    elements.append(elem)


def add_collapsible_js(elements: list):

    search_path = [('html', None),
                   ('body', None),
                   ]

    JS_COLLAPSIBLE = '''<!-- collapsible content -->
  <script type="text/javascript">
    var collapsibleTitles = document.getElementsByClassName("collapsible-title");
    for (var i = 0; i < collapsibleTitles.length; i++) {
      collapsibleTitles[i].addEventListener("click", function() {
        const nextElement = this.nextElementSibling;
        if (nextElement.classList.contains("collapsible-content")) {
          this.classList.toggle("collapsible-title-active");
          nextElement.classList.toggle("collapsible-content-show");
        }
      });
    }
  </script>
'''

    elements = get_first_element_list(elements, search_path)

    elem = dict()
    elem['data'] = JS_COLLAPSIBLE
    elements.append(elem)


def remove_first_ul_after_label(elements: list, search_label: str):
    idx = 0
    num = len(elements)

    for i in range(num):
        elem = elements[i]
        if 'p' in elem and get_first_p_data(elem).strip() == search_label:
            idx = i
            break

    for i in range(idx, num):
        elem = elements[i]
        if 'ul' in elem and ('class', 'simple') in elem['ul']:
            elements.pop(i)
            break


def make_dl_collapsible(dl: dict):
    sub_elems = dl.get('elements', [])

    # there is one dt and one dd under the dl
    # - to the <dt>: add class="collapsible-title"
    # - to the <dd>: add class="collapsible-content"
    dt = get_first_elem(sub_elems, 'dt', [])
    dd = get_first_elem(sub_elems, 'dd', [])
    if dt is not None and dd is not None:
        if dt['dt'] is None:
            dt['dt'] = [('class', 'collapsible-title')]
        else:
            if not set([('class', 'collapsible-title')]).issubset(dt['dt']):
                dt['dt'].append(('class', 'collapsible-title'))

        if dd['dd'] is None:
            dd['dd'] = [('class', 'collapsible-content')]
        else:
            if not set([('class', 'collapsible-content')]).issubset(dd['dd']):
                dd['dd'].append(('class', 'collapsible-content'))


def get_first_p_data(element: dict) -> str:
    if 'p' not in element or 'elements' not in element:
        return ''

    sub_elements = element['elements']
    if len(sub_elements) < 1:
        return ''

    first_sub_element = sub_elements[0]
    if not 'data' in first_sub_element:
        return ''

    return first_sub_element['data']


def get_first_element_list(elements: list, path_to_search: list) -> list:
    for pathinfo in path_to_search:
        elem = get_first_elem(elements, pathinfo[0], pathinfo[1])
        if elem is not None:
            elements = elem.get('elements', [])

    return elements


def remove_label(elements: list, label: str):
    for i in range(len(elements)):
        elem = elements[i]
        if 'p' in elem and get_first_p_data(elem).strip() == label:
            elements.pop(i)
            break


def process_client(elements: list):
    path_to_search = [
        ('html', None),
        ('body', None),
        ('div', [('class', 'container-wrapper')]),
        ('div', [('id', 'right-column')]),
        ('div', [('class', 'document clearer body')]),
        ('div', [('class', 'section')]),
        ('div', [('id', 'client')]),
        ('dl', [('class', 'class')]),
        ('dd', None),
    ]

    classes_to_fold = [
        'method',
        'attribute',
    ]

    elements = get_first_element_list(elements, path_to_search)

    remove_first_ul_after_label(elements, "These are the available methods:")

    for search_class in classes_to_fold:
        for elem in elements:
            if 'dl' in elem and set([('class', search_class)]).issubset(elem['dl']):
                make_dl_collapsible(elem)


def process_paginator(elements: list):
    path_to_search = [
        ('html', None),
        ('body', None),
        ('div', [('class', 'container-wrapper')]),
        ('div', [('id', 'right-column')]),
        ('div', [('class', 'document clearer body')]),
        ('div', [('class', 'section')]),
        ('div', [('id', 'paginators')]),
    ]

    classes_to_fold = [
        'class',
    ]

    elements = get_first_element_list(elements, path_to_search)

    remove_first_ul_after_label(elements, "The available paginators are:")

    for search_class in classes_to_fold:
        for elem in elements:
            if 'dl' in elem and set([('class', search_class)]).issubset(elem['dl']):
                make_dl_collapsible(elem)


def process_waiter(elements: list):
    path_to_search = [
        ('html', None),
        ('body', None),
        ('div', [('class', 'container-wrapper')]),
        ('div', [('id', 'right-column')]),
        ('div', [('class', 'document clearer body')]),
        ('div', [('class', 'section')]),
        ('div', [('id', 'waiters')]),
    ]

    classes_to_fold = [
        'class',
    ]

    elements = get_first_element_list(elements, path_to_search)

    remove_first_ul_after_label(elements, "The available waiters are:")

    for search_class in classes_to_fold:
        for elem in elements:
            if 'dl' in elem and set([('class', search_class)]).issubset(elem['dl']):
                make_dl_collapsible(elem)


def get_dl_list_for_admonition(elements: list, admonition: str):
    dl_list = list()

    admonition_found = False
    for elem in elements:
        if not admonition_found:
            if 'p' in elem and get_first_p_data(elem).strip() == admonition:
                admonition_found = True
        else:
            # after the admonition-title, there is usually a short description inside <p>
            # so when we look for the next admonition, we should also match the class
            if 'p' in elem and ('class', 'admonition-title') in elem['p']:
                break

            if 'dl' in elem and ('class', 'attribute') in elem['dl']:
                dl_list.append(elem)

    return dl_list


def fold_dd_dl(elements: list):
    path_to_search = [
        ('dd', None),
    ]

    elements = get_first_element_list(elements, path_to_search)

    classes_to_fold = [
        'method',
    ]

    elements = get_first_element_list(elements, path_to_search)

    for search_class in classes_to_fold:
        for elem in elements:
            if 'dl' in elem and set([('class', search_class)]).issubset(elem['dl']):
                make_dl_collapsible(elem)


def process_service_resource(elements: list):
    path_to_search = [
        ('html', None),
        ('body', None),
        ('div', [('class', 'container-wrapper')]),
        ('div', [('id', 'right-column')]),
        ('div', [('class', 'document clearer body')]),
        ('div', [('class', 'section')]),
        ('div', [('id', 'service-resource')]),
        ('dl', [('class', 'class')]),
        ('dd', None),
    ]

    labels_to_remove = [
        "These are the resource's available actions:",
        "These are the resource's available sub-resources:",
        "These are the resource's available collections:",
    ]

    classes_to_fold = [
        'method',
        'attribute',
    ]

    elements = get_first_element_list(elements, path_to_search)

    for label in labels_to_remove:
        remove_first_ul_after_label(elements, label)
        remove_label(elements, label)

    for search_class in classes_to_fold:
        for elem in elements:
            if 'dl' in elem and set([('class', search_class)]).issubset(elem['dl']):
                make_dl_collapsible(elem)

    collections = get_dl_list_for_admonition(elements, "Collections")

    for collection in collections:
        if 'elements' in collection:
            fold_dd_dl(collection['elements'])


def process_each_sub_resource(elements: list):
    path_to_search = [
        ('dl', [('class', 'class')]),
        ('dd', None),
    ]

    labels_to_remove = [
        "These are the resource's available identifiers:",
        "These are the resource's available attributes:",
        "These are the resource's available references:",
        "These are the resource's available actions:",
        "These are the resource's available sub-resources:",
        "These are the resource's available collections:",
        "These are the resource's available waiters:",
    ]

    classes_to_fold = [
        'method',
        'attribute',
    ]

    elements = get_first_element_list(elements, path_to_search)

    for label in labels_to_remove:
        remove_first_ul_after_label(elements, label)
        remove_label(elements, label)

    for search_class in classes_to_fold:
        for elem in elements:
            if 'dl' in elem and set([('class', search_class)]).issubset(elem['dl']):
                make_dl_collapsible(elem)

    collections = get_dl_list_for_admonition(elements, "Collections")

    for collection in collections:
        if 'elements' in collection:
            fold_dd_dl(collection['elements'])


def process_sub_resources(elements: list):
    path_to_search = [
        ('html', None),
        ('body', None),
        ('div', [('class', 'container-wrapper')]),
        ('div', [('id', 'right-column')]),
        ('div', [('class', 'document clearer body')]),
        ('div', [('class', 'section')]),
    ]

    sections_to_skip = [
        'client',
        'paginators',
        'waiters',
        'service-resource',
    ]

    elements = get_first_element_list(elements, path_to_search)

    for div_section in elements:
        if 'div' in div_section:
            attrs = div_section['div']
            if ('class', 'section') in attrs:
                for attr in attrs:
                    if attr[0] == 'id' and attr[1] not in sections_to_skip:
                        process_each_sub_resource(div_section['elements'])
                        break


# print(datetime.now(), file=sys.stderr)
parsed_html = MyHTMLParser(convert_charrefs=False)
# print(datetime.now(), file=sys.stderr)
parsed_html.feed(sys.stdin.read())
# print(datetime.now(), file=sys.stderr)
# pprint(parsed_html.elements, width=16000)

add_collapsible_css(parsed_html.elements)
add_collapsible_js(parsed_html.elements)

# fold client, paginators, waiters
# fold service resource
# fold sub resources

# sub_resources = get_sub_resources(parsed_html.elements)

process_client(parsed_html.elements)
process_paginator(parsed_html.elements)
process_waiter(parsed_html.elements)
process_service_resource(parsed_html.elements)

process_sub_resources(parsed_html.elements)

# pprint(parsed_html.elements, width=16000)
# print(datetime.now(), file=sys.stderr)
print(parsed_html.reconstruct_html(), end='')
# print(datetime.now(), file=sys.stderr)
