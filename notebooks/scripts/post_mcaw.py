__license__ = "MIT"
__version__ = "0.2"

def post_rings_mcaw(instream, gap_penalty=-10, sugar=60, anomer=30, nre_carbon=30, re_carbon=30):
    """
    post kcf to MCAW server and return html
    :param instream: instream (kcf or fingerprint) to be placed in the form text area
# Advanced weighting options
#		<input type="text" name="gapPenalty" value="-10" size=3>
#                <td>&nbsp;&nbsp;&nbsp;&nbsp;&emsp;Monosaccharide:
#		<input type="text" name="sugar" value="60" size=3>
#                Linkage information
#		<input type="text" name="anomer" value="30" size=3>
#                <td>&nbsp;&nbsp;&nbsp;&nbsp;&emsp;Non reducing side carbon number:
#		<input type="text" name="nreCarbon" value="30" size=3>
#                <td>&nbsp;&nbsp;&nbsp;&nbsp;&emsp;Reducing side carbon number:
#		<input type="text" name="reCarbon" value="30" size=3>
    """
    import urllib2
    import urllib

    # URL user would navigate to MCAW http://rings.t.soka.ac.jp/cgi-bin/tools/MCAW/mcaw_index.pl
    # URL to post to
    url = 'http://rings.t.soka.ac.jp/cgi-bin/tools/MCAW/mcaw_result_img.pl'

    if instream is None or instream == [] or instream == "":
        raise IOError("input stream is empty")

    kcfdata = instream.read()
    file = ""
    # values contains all the names of the items in the form and the appropriate data
    values = dict(datasetname='default', KCF=kcfdata, KCFfile=file, gapPenalty=gap_penalty, sugar=sugar,
                  anomer=anomer, nreCarbon=nre_carbon, reCarbon=re_carbon, submit='SUBMIT')

    html = urllib2.urlopen(url, urllib.urlencode(values)).readlines()

    if html is None or str(html).strip() == "":
        return None

    for line in list(html):  # hack to remove unable to open file message
        if "<title" in line or "</title" in line:
            html.remove(line)
        elif "<h1" in line or "</h1" in line:
            html.remove(line)
    return ''.join(html[2:])
    # note the image link is /tmp/* /*.png append http://rings.t.soka.ac.jp to this to get the image file


def get_pckf_from_html(html):
    """
     get pkcf related to mcaw html output

    :param html: html from posting to mcaw
    :return: pkcf
    """
    from BeautifulSoup import BeautifulSoup
    import urllib2

    if html is None or html == [] or html == "":
        raise IOError("input stream is empty")
    soup = BeautifulSoup(html)
    pkcf = ""  # set to empty
    for link in soup.findAll('a'):
        if "pkcf" in link.get('href'):
            pkcflink = link.get('href')
            pkcf = urllib2.urlopen(pkcflink).read()
    return pkcf


def get_image_from_html(html):
    """
     get image related to mcaw html output
    :param html: html from posting to mcaw
    :return: png
    """
    from BeautifulSoup import BeautifulSoup
    import urllib2

    if html is None or html == [] or html == "":
        raise IOError("input stream is empty")
    soup = BeautifulSoup(html)
    tags = soup.findAll(name='img')  # have to use explicit name= , as source html is damaged *by me..
    imgsrc = (list(tag['src'] for tag in tags))
    mcawpicsrc = "http://rings.t.soka.ac.jp" + imgsrc[1]

    # now get the img (it is not embedded in the page and must be retrieved from the server
    try:
        img = urllib2.urlopen(mcawpicsrc).read()
        return img
    except urllib2.HTTPError:
        img = ['\x89PNG\r\n', '\x1a\n',
               '\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x03PLTE\x00\x00\x00\xa7z=\xda\x00\x00\x00\x01tRNS\x00@\xe6\xd8f\x00\x00\x00\n',
               'IDAT\x08\x1dc`\x00\x00\x00\x02\x00\x01\xcf\xc85\xe5\x00\x00\x00\x00IEND\xaeB`\x82']

        return "".join(img)


if __name__ == "__main__":
    import urllib2
    from BeautifulSoup import BeautifulSoup
    from optparse import OptionParser

    usage = "usage: python %prog [options]\n"
    parser = OptionParser(usage=usage)
    parser.add_option("-i", action="store", type="string", dest="i", default="input.kcf",
                      help="input kcf file (input)")
    parser.add_option("-o", action="store", type="string", dest="o", default="output.html",
                      help="output html file from mcaw (output)")
    parser.add_option("-p", action="store", type="string", dest="p", default="output.png",
                      help="png output of MCAW")
    parser.add_option("-k", action="store", type="string", dest="k", default="output.pkcf",
                      help="pkcf output from mcaw")
    parser.add_option("-g", action="store", type="int", dest="g", default=-10,
                      help="gap penalty")
    parser.add_option("-s", action="store", type="int", dest="s", default=60,
                      help="sugar")
    parser.add_option("-a", action="store", type="int", dest="a", default=30,
                      help="anomer")
    parser.add_option("-n", action="store", type="int", dest="n", default=30,
                      help="non reducing carbon number")
    parser.add_option("-r", action="store", type="int", dest="r", default=30,
                      help="reducing carbon number")

    (options, args) = parser.parse_args()


    try:
        inputname = options.i
        outputname = options.o
        outputpng = options.p
        outputpkcf = options.k
    except Exception as e:
        raise Exception(e, "Please pass an input (kcf), output html, png and pkcf filename as arguments")
    instream = file(inputname, 'r')

    try:
        html = post_rings_mcaw(instream, gap_penalty=options.g, sugar=options.s, anomer=options.a, nre_carbon=options.n, re_carbon=options.r)
        with open(outputname, "w") as out:
            out.write(html)
        with open(outputpkcf, "w") as f:
            f.write(get_pckf_from_html(html))
        with open(outputpng, "w") as f:
            f.write(get_image_from_html(html))
    except Exception as e:
        raise e
