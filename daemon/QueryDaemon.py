#!/usr/bin/python3.3
#
#  File:    QueryDaemon.py
#  Author:  Daniel E. Wilson
#
#  This is the Server daemon that holds performs the actual queries
#  once a user has initiated them from the Web interface.
#
#  This program should only be used with Python 2.7 interprester.
#
#  Bonneville Power Adminstration Front-End
#  Copyright (C) 2015 Daniel E. Wilson.
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, US$
#
import sys
import json
import select
import SocketServer
import QueryClient
import DataEngine

def allKeysPresent(dictionary, keyList):
    "Check that all keys are present in the dictionary."
    result = True
    for key in keyList:
        result = result and dictionary.has_key(key)
    return result

def isValidQuery(query):
    "Check to see if the query is valid."
    # Check the query attributes.
    try:
        return allKeysPresent(query['query'],
                              ['query_id', 'Signal_id', 'start', 'end',
                               'analysisFile', 'pmu_channel', 'pmu_company'])
    except KeyError:
        return False


class QueryHandler(SocketServer.StreamRequestHandler):
    "QueryHandler class for the query daemon."

    def readQuery(self):
        "Read the query from the socket."
        response = ''
        while True:
            line = self.rfile.readline()
            if not line.strip():
                break
            else:
                response = response + line
        return response

    def handle(self):
        "Request handler function, each command is terminated by an empty line."
        # Get the query text.
        request = self.readQuery()

        # Get the JSON object from the text.
        query = json.loads(request)

        # Create response object and queue the query.
        if isValidQuery(query):
            queryEngine.putQuery(query)
            a = {'code': 0, 'msg': "SUCCESS"}
        else:
            a = {'code': 1, 'msg': "Not a valid query object."}
        response = {'status': a}

        # Send the data back to the client.
        json.dump(response, self.wfile)
        self.wfile.write('\n\n')

# Start the server.
if __name__ == '__main__':
    # Set the hostname and port numbers.
    host = 'localhost'
    port = 4242

    # Create the DataEngine to hande database Accesses.
    dataEngine = DataEngine.DataEngine()
    dataEngine.start()

    # Create the query engine object and start it.
    queryEngine = QueryClient.QueryEngine(dataEngine)
    queryEngine.start()

    # Create and run the server.
    server = SocketServer.TCPServer((host, port), QueryHandler)
    server.serve_forever()

    # End the program.
    sys.exit(0)
