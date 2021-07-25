#!/usr/bin/env python3

import sys
from html.parser import HTMLParser
from collections import OrderedDict


# TODO: read the whole html file into an OrderedDict before manipulating it
# it will be much easier to manipulate the document this way

# what to modify:
# - insert css at the end of head (A)
# - insert script at the end of body (B)
# - remove ul after <p>These are the available methods:</p> (C)
# - for each <dl class="method">:
#   - track the recursion depth
#   - replace with <button type="button" class="collapsible"> (D)
#   - print the next dt
#   - add these
#     </button>
#     <div class="content">
#     <dl class="method">
#   - look for ending dl (this context), add ending div after that

class MyHTMLParser(HTMLParser):

    css_collapsible = '''<!-- collapsible -->
<style>
.collapsible {
  background-color: aliceblue;
  width: 100%;
  border: none;
  text-align: left;
}
.collapsible:hover {
  background-color: #faf3e8;
}
.active {
  background-color: aliceblue;
}
.content {
  display: none;
}
</style>'''

    js_collapsible = '''<!-- collapsible -->
<script>
var coll = document.getElementsByClassName("collapsible");
for (var i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
</script>'''

    method_collapsible_start = '''<!-- collapsible -->
<button type="button" class="collapsible">'''
    method_collapsible_middle_content = '''</button>
<div class="content">
<dl class="method">'''
    method_collapsible_end = '</div>'

    remove_next_ul = False
    removed_ul_depth = 0

    in_dl_method = False
    dl_method_depth = 0

    convert_function_name = False
    in_dt_method = False


    def handle_starttag(self, tag, attrs):
        # print("handle_starttag: ", tag, attrs)
        # print("starttag_text: ", self.get_starttag_text())
        if self.remove_next_ul and tag == "ul":
            self.removed_ul_depth += 1
        if self.removed_ul_depth > 0:
            return
        if tag == "dl" and attrs == [('class', 'method')]:
            self.in_dl_method = True
            self.convert_function_name = True
            self.dl_method_depth += 1
            print(self.method_collapsible_start, end='')
            return
        if self.in_dl_method and tag == "dl":
            self.dl_method_depth += 1
        if self.in_dl_method and tag == "dt" and self.convert_function_name:
            self.in_dt_method = True
            self.convert_function_name = False
        print(self.get_starttag_text(), end='')

    def handle_endtag(self, tag):
        # print("handle_endtag: ", tag)
        if tag == "head":
            print(self.css_collapsible)
        elif tag == "body":
            print(self.js_collapsible)
        if self.remove_next_ul and tag == "ul":
            self.removed_ul_depth -= 1
            # special case, we just found the ending ul
            if self.removed_ul_depth == 0:
                self.remove_next_ul = False
                return
        if self.removed_ul_depth > 0:
            return
        if self.in_dl_method and tag == "dl":
            self.dl_method_depth -= 1
            if self.dl_method_depth == 0:
                print("</" + tag + ">", end='')
                print()
                print(self.method_collapsible_end, end='')
                self.in_dl_method = False
                return
        if self.in_dt_method and tag == "dt":
            self.in_dt_method = False
            print("</" + tag + ">", end='')
            print()
            print(self.method_collapsible_middle_content, end='')
            return
        print("</" + tag + ">", end='')

    def handle_startendtag(self, tag, attrs):
        # print("handle_startendtag: ", tag, attrs)
        # print("starttag_text: ", self.get_starttag_text())
        print(self.get_starttag_text(), end='')

    def handle_data(self, data):
        # print("handle_data: ", data)
        if self.get_starttag_text() == "<p>":
            if data == "These are the available methods:" \
               or data == "The available paginators are:" \
               or data == "The available waiters are:":
                self.remove_next_ul = True
        if self.removed_ul_depth > 0:
            return
        print(data, end='')

    # if there is an entity inside a string like "hello &amp; goodbye &#x3E; whatever",
    #   then these functions will be called:
    # 1. handle_data("hello ")
    # 2. handle_entityref("amp")
    # 3. handle_data(" goodbye ")
    # 4. handle_charref("x3E")
    # 5. handle_data(" whatever")
    def handle_entityref(self, name):
        # print("handle_entityref: ", name)
        print("&" + name + ";", end='')

    def handle_charref(self, name):
        # print("handle_charref: ", name)
        print("&#" + name + ";", end='')

    def handle_comment(self, data):
        # print("handle_comment: ", data)
        print("<!--" + data + "-->", end='')

    def handle_decl(self, decl):
        # print("handle_decl: ", decl)
        print("<!" + decl + ">", end='')

    def handle_pi(self, data):
        # print("handle_pi: ", data, end='')
        print("<?" + data + ">", end='')

html_parser = MyHTMLParser(convert_charrefs=False)
html_parser.feed(sys.stdin.read())






