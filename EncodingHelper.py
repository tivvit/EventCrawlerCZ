__author__ = 'tivvit'

def getEncodedContent(result):
    '''
        bleh
    '''
    content_type = result.headers['Content-Type'] # figure out what you just fetched
    ctype, charset = content_type.split(';')
    encoding = charset[len(' charset='):] # get the encoding
    return result.content.decode(encoding) # now you have unicode