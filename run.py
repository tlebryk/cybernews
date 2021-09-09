# from cybernews.spiders import articlesspider as AS
# import dailyrunner as DR
# # from cybernews.spiders import art_spider2 as AS2
# from scrapy.utils.project import get_project_settings
# # import json
# from scrapy.crawler import CrawlerRunner
# from sys import stdout
# from twisted.logger import globalLogBeginner, textFileLogObserver
# from twisted.web import server, wsgi
# from twisted.internet import endpoints, reactor
# from zotero import get_meta
# import os
from app import app





if __name__ == "__main__":
    app.run(debug=True)
    
    # # DR.full()
    # # start the logger
    # globalLogBeginner.beginLoggingTo([textFileLogObserver(stdout)])

    # # start the WSGI server
    # root_resource = wsgi.WSGIResource(reactor, reactor.getThreadPool(), app)
    # factory = server.Site(root_resource)
    # http_server = endpoints.TCP4ServerEndpoint(reactor, 5000)
    # http_server.listen(factory)

    # # start event loop
    # reactor.run()

    # # run docker: 
    # # docker run -d -p 1969:1969 --rm --name translation-server zotero/translation-server