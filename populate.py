import json
import re
import os
from subprocess import call
from lxml import etree, html
import requests

def extract_description(h3):
    description_html = ''
    next_element = h3.getnext()

    while (next_element is not None) and (next_element.tag != 'h3'):
        description_html += etree.tostring(next_element)
        next_element = next_element.getnext()

    return description_html.strip()

def extract_location(h3):
    return h3.cssselect('a')[0].get('id')

download_dir = 'downloaded'
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

downloaded_file = os.path.join(download_dir, 'http_status_codes.html')
if not os.path.exists(downloaded_file):
    page = requests.get('http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html')

    with open(downloaded_file, "w") as text_file:
        text_file.write(page.text)

tree = html.parse(downloaded_file)
#doc = etree.tostring(tree, pretty_print=True, method="html")
#print(doc)

root = tree.getroot()

response_code_class_section_header_re = re.compile('\d+\.\d+\s+([^\d]+)\s+(\dxx)$')
response_code_section_header_re = re.compile('\d+\.\d+\.\d+\s+(\d{3})\s+(.+?\w)$')

# first digit of status code => class
response_code_classes = {}
all_response_codes = []
all_response_codes_and_classes = []
last_class = None
output_dir = 'out'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, 'http_status_codes.json')

with open(output_file, "w") as out:
    out.write("""
{
  "metadata" : {
    "mapping" : {
      "_all" : {
        "enabled" : false
      },
      "properties" : {
        "statusCode" : {
          "type" : "string",
          "index" : "not_analyzed"
        },
        "message" : {
          "type" : "string",
          "index" : "analyzed"
        },
        "descriptionHtml" : {
          "type" : "string",
          "index" : "not_analyzed"
        },
        "members": {
          "type" : "object",
          "enabled" : false
        }
      }
    }
  },
  "updates" : [
""")

    for h3 in root.cssselect('h3'):
        line = h3.text_content().strip()

        match = re.match(response_code_section_header_re, line)

        if match:
            response_code = match.group(1)
            response_message = match.group(2)
            description_html = extract_description(h3)
            location = extract_location(h3)
            doc = {'statusCode': response_code, 'message': response_message, 'descriptionHtml': description_html, 'location': location, 'kind': 'status_code' }

            last_class['members'].append(doc)
            all_response_codes.append(doc)
            all_response_codes_and_classes.append(doc)
        else:
            class_match = re.match(response_code_class_section_header_re, line)

            if class_match:
                status_code = class_match.group(2)
                message = class_match.group(1)
                description_html = extract_description(h3)
                location = extract_location(h3)

                last_class = {'statusCode': status_code, 'message': message, 'descriptionHtml': description_html, 'location': location, 'members': [], 'kind': 'status_code_class'}
                response_code_classes[status_code[0]] = last_class
                all_response_codes_and_classes.append(last_class)

    first_doc = True

    for clazz in response_code_classes.values():
        if first_doc:
          first_doc = False
        else:
          out.write(',')

        out.write(json.dumps(clazz))
        del clazz['members']

    for doc in all_response_codes:
        clazz = response_code_classes[doc['statusCode'][0]]
        doc['class'] = clazz
        out.write(',')
        out.write(json.dumps(doc))
        del doc['class']

    all = {'statusCode': 'HTTP Status Codes', 'message': 'HTTP Response Codes', 'members': all_response_codes_and_classes, 'kind': 'all_status_codes'}
    out.write(',')
    out.write(json.dumps(all))
    out.write("]}")

print 'cwd ='
print os.getcwd()
print "output file = " + output_file

call('bzip2 -kf ' + output_file, shell=True)

print('Done!')