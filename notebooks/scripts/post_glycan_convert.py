__author__ = "Chris Barnett"
__version__ = "0.5.2"
__license__ = "MIT"

from BeautifulSoup import BeautifulSoup
import mechanize

class PrettifyHandler(mechanize.BaseHandler):
    def http_response(self, request, response):
        if not hasattr(response, "seek"):
            response = mechanize.response_seek_wrapper(response)
        # only use BeautifulSoup if response is html
        if response.info().dict.has_key('content-type') and ('html' in response.info().dict['content-type']):
            soup = BeautifulSoup(response.get_data())
            response.set_data(soup.prettify())
        return response


def mechanise_glycan_convert(inputstream, format, textformat="json", debug=False):
    """
    Use mechanise to submit input glycan and formats to the new converter tool at RINGS
    :param inputstream: input glycan file stream that is read and then passed to the textarea in web form
    :param format: format to convert to. Options change dependent on input type. ['Glycoct', 'Linearcode', 'Mol', 'Wurcs'])
    :param textformat: output returned in text, json or html. default is text.
    :param debug: print debug info from mechanise
    Can convert to WURCS, mol, Glycoct, Glycoct{condensed}, LinearCode, KCF.
    Does not yet support Linucs as input format. Cannot convert to GLYDE2, IUPAC, Linucs,
    Converts to image when kcf html is returned.

    http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/index.pl
    http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert_index2.pl
    which then directs to http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert_index2.pl
    http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert.pl
    """
    import mechanize
    import cookielib

    if inputstream is None or inputstream == []:
        raise IOError("empty input stream")
        #return None

    if format is None or format == "":
        return inputstream  #

    # create a Browser
    br = mechanize.Browser()
    br.add_handler(PrettifyHandler())

    #  handle cookies - Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    br.set_debug_http(debug)
    br.set_debug_redirects(debug)
    br.set_debug_responses(debug)

    br.addheaders = [('User-agent',
                      'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    # Open site
    page = 'http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/index.pl'
    br.open(page)

    # Show the response headers
    response_info = br.response().info()

    # select the input form
    br.select_form(nr=0)
    # read user glycan and submit
    glycandata = inputstream.read() # read into a variable as I need it later
    br.form["in_data"] = glycandata
    br.submit()

    # the submit redirects to another page which is generated based on the input glycan
    # now submit second form
    br.select_form(nr=0)

    #. bugfix - reinsert data as 7 spaces get prepended to it during the post ?!
    br.form["in_data"] = glycandata
    # look at the convert_to control. These are the options allowed for the particular input as determined by rings
    control = br.form.find_control("convert_to", type="select")
    available_formats =  [item.attrs['value'] for item in control.items]  # should match user selected format .

    # check that the user entered format is in the available formats, if not raise error
    if format not in available_formats:
        raise IOError ("Requested ", format,"  but input glycan can only be converted to the following formats: ",available_formats )

    # set the format
    br.form["convert_to"]=[format,]

    # check and set textformat
    if textformat not in ["json","html","text"]:
        raise IOError ("Requested ", textformat, "  but can only output json, html or text" )
    br.form["type"]=[textformat,]

    #submit conversion and get response
    br.submit()
    #import time
    #time.sleep(5)
    response =  br.response().read()   # the converted file!

    if response is None or str(response.strip()) == '':
        raise IOError("empty response, I recommend using the json format")
        #return None
    return response

def clean_json_response(response):
    """
        # look at json  status has failure status, submitData has original data and result has output with format

    :param response: json from RINGS convert
    :return: a list of glycan structures
    """
    import json
    import re
    import StringIO

    # RINGS bug, additional data returned with JSON format. Clean this up
    jsonoutputasfilehandle = StringIO.StringIO(''.join(response))
    keeplines=[]  # only keep lines that look like JSON
    for line in jsonoutputasfilehandle.readlines():
        if line[0]=="[":
            keeplines.append(line)

    response2=''.join(keeplines)
    # RINGs bug. Now remove junk data appended to the JSON lines for example "}}]GLC "
    p = re.compile( '(}}].*)')
    jsontobeparsed = p.subn( '}}]', response2)

    # load json
    loaded_as_json = json.loads(jsontobeparsed[0])
    structures=[]

    # there could be multiple structures so iterate over, structures are numbered using the No tag.

    # .. matches for  linearcode and eol fixes
    linearcodefix = re.compile( '(;$)')
    eolfix = re.compile( '(\n$)')

    for glycan in loaded_as_json:
        if str(glycan["status"]) == "false":
            raise IOError(glycan["result"]["message"]) # raise error even though not all structures need be broken. It is no use letting through a broken structure. important to let the user know.
        else:
            # bugfix remove ";" from end of LinearCode
            lcfixed = linearcodefix.subn( '\n', str(glycan["result"]["structure"]))[0]
            # now remove all \n at end of each sequence. Some have, some don't, so remove all and add later
            eolfixed = eolfix.subn( '', lcfixed)[0]
            structures.append( eolfixed)

    return structures

def defunct_post_rings_convert(inputstream):
    """
    #impossible to do with urllib2
    posts input glycan stream to the new converter tool at RINGS
    http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/index.pl
    http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert_index2.pl
    which then directs to http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert_index2.pl
    http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert.pl
    :param inputstream: read and then passed to the textarea in web form
    """
    import urllib2, urllib

    if inputstream is None or inputstream == []:
        return []
    # URL to post to
    # changed url to action url found in the form source of the linearcodetokcf page
    url = 'http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert_index2.pl'
    in_data = inputstream.read()
    file = ""
    # values contains all the names of the items in the form and the appropriate data

    values = dict(in_data=in_data, datasetname="default1", submit='SUBMIT')
    response = urllib2.urlopen(url, urllib.urlencode(values))
    the_page = response.read()
    the_url = response.geturl()
    return response, the_page, the_url
    # . page resulting from post is dynamic and I then have to post to this. urllib2 cannot do this easily.


def defunct_automated_glycan_convert(inputstream):
    """
    seems cool but starts a browser there is no strictly headless solution with selenium
    use selenium to input glycan stream to the new converter tool at RINGS
    http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/index.pl
    http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert_index2.pl
    which then directs to http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert_index2.pl
    http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/convert/convert.pl
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import Select
    from selenium.common.exceptions import NoSuchElementException
    from selenium.common.exceptions import NoAlertPresentException
    import time, re

    driver = webdriver.Firefox()
    driver.implicitly_wait(30)
    base_url = "http://rings.t.soka.ac.jp/"
    verificationErrors = []
    accept_next_alert = True
    driver.get(base_url + "/cgi-bin/tools/utilities/convert/index.pl")
    driver.find_element_by_name("datasetname").clear()
    driver.find_element_by_name("datasetname").send_keys("default1")
    driver.find_element_by_name("in_data").clear()
    driver.find_element_by_name("in_data").send_keys(
        "ENTRY      12345     Glycan\nNODE        2\n            1     galnac     0     0\n            2     gal     -8     0\nEDGE        1\n            1     2:1     1\n///")
    driver.find_element_by_css_selector("input[type=\"submit\"]").click()
    Select(driver.find_element_by_name("convert_to")).select_by_visible_text("WURCS")
    # ERROR: Caught exception [Error: Dom locators are not implemented yet!]
    driver.find_element_by_css_selector("input[type=\"submit\"]").click()


def defunct_driver_glycan_convert(inputstream):
    """
    seems cool but starts a browser there is no strictly headless solution with selenium
    """
    from contextlib import closing
    from selenium.webdriver import Firefox  # pip install selenium
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support.ui import Select

    base_url = "http://rings.t.soka.ac.jp/"
    url = base_url + "/cgi-bin/tools/utilities/convert/index.pl"
    # use firefox to get page with javascript generated content
    with closing(Firefox()) as browser:
        browser.get(url)
        browser.find_element_by_name("datasetname").clear()
        browser.find_element_by_name("datasetname").send_keys("default1")
        browser.find_element_by_name("in_data").clear()
        browser.find_element_by_name("in_data").send_keys(
            "ENTRY      12345     Glycan\nNODE        2\n            1     galnac     0     0\n            2     gal     -8     0\nEDGE        1\n            1     2:1     1\n///")
        browser.find_element_by_css_selector("input[type=\"submit\"]").click()
        # wait for the page to load
        WebDriverWait(browser, timeout=10).until(
            lambda x: x.find_element_by_id('convert_to'))
        Select(browser.find_element_by_name("convert_to")).select_by_visible_text("WURCS")
        browser.find_element_by_css_selector("input[type=\"submit\"]").click()

        # store it to string variable
        page_source = browser.page_source
        print(page_source)

if __name__ == "__main__":
    from optparse import OptionParser

    usage = "usage: python %prog [options]\n"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", action="store", type="string", dest="i", default="input",
                      help="input any glycan file (input)")
    parser.add_option("-f", action="store", type="string", dest="f", default="Kcf",
                      help="format to convert to (Kcf)")
    parser.add_option("-t", action="store", type="string", dest="t", default="text",
                      help="format style, text, html or json")
    parser.add_option("-o", action="store", type="string", dest="o", default="output",
                      help="output glycan file (output)")
    parser.add_option("-j", action="store", type="string", dest="j", default="jsonoutput",
                      help="output json output, only if json format is selected (output.json)")
    (options, args) = parser.parse_args()
    try:
        instream = file(options.i, 'r')
    except Exception as e:
        raise IOError(e, "the input file specified does not exist. Use -h flag for help")
    m = mechanise_glycan_convert(instream, options.f, options.t)
    if options.t =="text" or options.t=="html":
        with open(options.o,'w') as f:
            f.write(m)
    elif options.t == "json":
        with open(options.j,'w') as f1:
            f1.write(m)
        with open(options.o,'w') as f:
            f.write("\n".join(clean_json_response(m)))
