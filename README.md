HTTP Status Code Populator

This Python project creates a Semantic Data Collection Changefile that contains
documentation for HTTP status codes. Data is provided by W3C.

To run:

  sudo apt-get install libxml2-dev libxslt-dev python-dev

  pip install -r requirements.txt

  python populate.py

should create the file out/http_status_codes.bz2, which can be uploaded to
Solve for All as a Semantic Data Collection Changefile.

For more documentation on Semantic Data Collections see
https://solveforall.com/docs/developer/semantic_data_collection

