__author__ = "Chris Barnett"
__version__ = "0.3"
__license__ = "MIT"


def post_rings_kcf_to_image(inputstream):
    """

    posts kcf to the image converter at RINGS
    'http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/KCFtoIMAGE/KCF_to_IMAGE.pl'
    :param inputstream: read and then passed to the textarea in web form
    """
    import urllib

    if inputstream is None or inputstream == []:
        return []
    # URL to post to
    # changed url to action url found in the form source of the linearcodetokcf page
    url = 'http://rings.t.soka.ac.jp/cgi-bin/tools/utilities/KCFtoIMAGE/KCF_to_IMAGE.pl'
    kcfdata = inputstream.read()
    file = ""
    # values contains all the names of the items in the form and the appropriate data
    values = dict(KCF=kcfdata, KCFfile=file, submit='SUBMIT')
    html = urllib.urlopen(url, urllib.urlencode(values)).readlines()
    return ''.join(html[13:])
    # note in this example the images are embedded in the html


def get_first_image_from_html(html):
    from BeautifulSoup import BeautifulSoup

    soup = BeautifulSoup(html)
    tags = soup.findAll(name='img')  # have to use explicit name= , as source html is damaged *by me..
    imgsrc = (list(tag['src'] for tag in tags))
    if len(imgsrc) > 1: # rings logo image and at least one glycan image (thus greater than 1 i.e. 2 or more)
        _, base64img = imgsrc[1].split(",") # get the first glycan image
    else:
        raise IOError("Server did not return an image. Error could be remote or your file.")

    # unfortunately only the first img is saved to png
    # use pillow or just view the html to see everything
    # cool example http://stackoverflow.com/questions/10647311/how-to-merge-images-using-python-pil-library
    return base64img.decode("base64")


if __name__ == "__main__":
    import sys

    try:
        inputname = sys.argv[1]
        pngoutputname = sys.argv[2]
        htmloutputname = sys.argv[3]
    except Exception as e:
        raise Exception(e, "Please pass an input, pngoutput and htmloutput filename as arguments")
    instream = file(inputname, 'r')
    pngoutstream = file(pngoutputname, "wb")
    htmloutstream = file(htmloutputname, "w")
    try:
        html = post_rings_kcf_to_image(instream)
        img = get_first_image_from_html(html)
        htmloutstream.write(html)
        pngoutstream.write(img)
    except Exception as e:
        raise
    finally:
        instream.close()
        pngoutstream.close()
        htmloutstream.close()
