The current boto3 HTML documentation is very long and it's not easy to read. From my personal experience, when I was learning DynamoDB, the reference documentation is very long. Each function's documentation is also very long, and it's quite difficult to find my way around.

For example, when I wanted to learn how to query a DynamoDB table, I opened up the [API reference for that function](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.query). It's quite a long section, and if I wanted to go to the end of the section to see the Response Syntax, I either had to scroll down, potentially missing the section altogether, or I had to go back to the table of contents, pick the next function, and then scroll up a little bit from there. It was not a pleasant experience. The extremely verbose syntax of `KeyConditionExpression` didn't help, either.

When the documentation is hard to read, people won't use it. Most people would just google their problem and apply the first accepted answer on sites like Stackoverflow, not knowing that those answers might not be applicable to their situation. I have seen this problem firsthand, so I know.

I had a couple of different ideas on how to solve this problem:
- split each service reference into multiple HTML files, each describing a function
- convert each function into a collapsible section, but keeping the single large HTML file

With this project, I'm implementing the second idea. This project reformats boto3 HTML docs, specifically the available services section inside the API reference, so that it is easier to read. After the HTML docs have been reformatted, we put it up on GitHub Pages.

## Conversion mechanism

Currently, I first have to generate the HTML docs from boto3. It's something like this:

```console
$ git clone boto3
$ cd boto3
$ echo 'docutils<0.16' >> requirements-docs.txt # keep this until bug is fixed upstream
$ virtualenv venv
$ . venv/bin/actvate
$ pip3 install -r requirements-docs.txt
$ cd docs
$ make html
```

After all that, we will have the HTML documentation inside `boto3:docs/build/html`. This should give us the exact same documentation as the [official one](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html). Then we use `boto3-html-reformat.py` to convert each service documentation.

## Bugs

It's currently a simple hack and slash. I'm planning to rewrite the script, to read the HTML file into memory as a nested OrderedDict, and then manipulate the tags there. I don't want to have to resort to a 3rd party library, so I would just have to do this myself.

Also, currently everything has to be done by hand, and all these can actually be automated:
- the html docs need to be copied over
- the python script has to be executed manually
- the documentation has to be published manually to GitHub Pages

## Licensing status

This project is just a simple python script that modifies boto3's documentation. Therefore I just went with boto3's license, which is Apache License 2.0. You can read the license in its entirety, in the file [LICENSE](LICENSE).