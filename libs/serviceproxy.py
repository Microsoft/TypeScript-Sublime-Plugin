import collections
import json

import jsonhelpers
import servicedefs
from nodeclient import CommClient
from servicedefs import Location

class ServiceProxy:
    def __init__(self, comm=CommClient()):
        self.__comm = comm
        self.seq = 1

    def incrSeq(self):
        temp = self.seq
        self.seq += 1
        return temp

    def exit(self):
        req_dict = self.create_req_dict("exit")
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.postCmd(json_str)
        
    def configure(self, hostInfo="Sublime Text", file=None, formatOptions=None):
        args = {"hostInfo": hostInfo, "formatOptions": formatOptions, "file": file}
        req_dict = self.create_req_dict("configure", args)
        json_str = jsonhelpers.encode(req_dict)
        response_dict = self.__comm.sendCmdSync(json_str, req_dict["seq"])
        return response_dict

    def change(self, path, begin_location=Location(1, 1), end_location=Location(1,1), insertString=""):
        args = {
            "file": path, 
            "line": begin_location.line, 
            "offset": begin_location.offset, 
            "endLine": end_location.line, 
            "endOffset": end_location.offset,
            "insertString": insertString
            }
        req_dict = self.create_req_dict("change", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.postCmd(json_str)

    def completions(self, path, location=Location(1, 1), prefix="", on_completed=None):
        args = {"file": path, "line": location.line, "offset": location.offset, "prefix": prefix}
        req_dict = self.create_req_dict("completions", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.sendCmdAsync(
            lambda response_dict: None if on_completed is None else on_completed(response_dict),
            json_str, 
            req_dict["seq"]
            )

    def asyncCompletions(self, path, location=Location(1, 1), prefix="", on_completed=None):
        args = {"file": path, "line": location.line, "offset": location.offset, "prefix": prefix}
        req_dict = self.create_req_dict("completions", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.sendCmdAsync(json_str, req_dict["seq"], on_completed)

    def signatureHelp(self, path, location=Location(1, 1), prefix="", on_completed=None):
        args = {"file": path, "line": location.line, "offset": location.offset, "prefix": prefix}
        req_dict = self.create_req_dict("signatureHelp", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.sendCmd(
            lambda response_dict: None if on_completed is None else on_completed(response_dict), 
            json_str, 
            req_dict["seq"]
            )

    def asyncSignatureHelp(self, path, location=Location(1, 1), prefix="", on_completed=None):
        args = {"file": path, "line": location.line, "offset": location.offset, "prefix": prefix}
        req_dict = self.create_req_dict("signatureHelp", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.sendCmdAsync(json_str, req_dict["seq"], on_completed)

    def definition(self, path, location=Location(1, 1)):
        args = {"file": path, "line": location.line, "offset": location.offset}
        req_dict = self.create_req_dict("definition", args)
        json_str = jsonhelpers.encode(req_dict)
        response_dict = self.__comm.sendCmdSync(json_str, req_dict["seq"])
        return response_dict

    def format(self, path, begin_location=Location(1, 1), end_location=Location(1, 1)):
        args = {
            "file": path, 
            "line": begin_location.line, 
            "offset": begin_location.offset, 
            "endLine": end_location.line, 
            "endOffset": end_location.offset
            }
        req_dict = self.create_req_dict("format", args)
        json_str = jsonhelpers.encode(req_dict)
        response_dict = self.__comm.sendCmdSync(json_str, req_dict["seq"])
        return response_dict

    def formatOnKey(self, path, location=Location(1, 1), key=""):
        args = {"file": path, "line": location.line, "offset": location.offset, "key": key}
        req_dict = self.create_req_dict("formatonkey", args)
        json_str = jsonhelpers.encode(req_dict)
        response_dict = self.__comm.sendCmdSync(json_str, req_dict["seq"])
        return response_dict

    def open(self, path):
        args = {"file": path}
        req_dict = self.create_req_dict("open", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.postCmd(json_str)

    def close(self, path):
        args = {"file": path}
        req_dict = self.create_req_dict("close", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.postCmd(json_str)

    def references(self, path, location=Location(1, 1)):
        args = {"file": path, "line": location.line, "offset": location.offset}
        req_dict = self.create_req_dict("references", args)
        json_str = jsonhelpers.encode(req_dict)
        response_dict = self.__comm.sendCmdSync(json_str, req_dict["seq"])
        return response_dict

    def reload(self, path, alternatePath):
        args = { "file": path, "tmpfile": alternatePath }
        req_dict = self.create_req_dict("reload", args)
        json_str = jsonhelpers.encode(req_dict)
        response_dict = self.__comm.sendCmdSync(json_str, req_dict["seq"])
        return response_dict

    def rename(self, path, location=Location(1, 1)):
        args = { "file": path, "line": location.line, "offset":location.offset }
        req_dict = self.create_req_dict("rename", args)
        json_str = jsonhelpers.encode(req_dict)
        response_dict = self.__comm.sendCmdSync(json_str, req_dict["seq"])
        return response_dict

    def requestGetError(self, delay=0, pathList=[]):
        args = {"files": pathList, "delay": delay}
        req_dict = self.create_req_dict("geterr", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.postCmd(json_str)

    def type(self, path, location=Location(1, 1)):
        args = { "file": path, "line": location.line, "offset":location.offset }
        req_dict = self.create_req_dict("type", args)
        json_str = jsonhelpers.encode(req_dict)
        response_dict = self.__comm.sendCmdSync(json_str, req_dict["seq"])
        return response_dict

    def quickInfo(self, path, location=Location(1, 1), onCompleted=None):
        args = { "file": path, "line": location.line, "offset": location.offset }
        req_dict = self.create_req_dict("quickinfo", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.sendCmd(
            lambda json_dict: None if onCompleted is None else onCompleted(json_dict), 
            json_str, 
            req_dict["seq"]
            )

    def getEvent(self):
        event_json_str = self.__comm.getEvent()
        return jsonhelpers.decode(event_json_str) if event_json_str is not None else None

    def saveto(self, path, alternatePath):
        args = {"file": path, "tmpfile": alternatePath}
        req_dict = self.create_req_dict("saveto", args)
        json_str = jsonhelpers.encode(req_dict)
        self.__comm.postCmd(json_str)

    def navTo(self, search_text, file_name):
        args = { "searchValue": search_text, "file": file_name, "maxResultCount": 20 }
        req_dict = self.create_req_dict("navto", args)
        json_str = jsonhelpers.encode(req_dict)
        response_dict = self.__comm.sendCmdSync(json_str, req_dict["seq"])
        return response_dict

    def create_req_dict(self, command_name, args=None):
        req_dict = {
            "command": command_name,
            "seq": self.incrSeq(),
            "type": "request"
            }
        if args:
            req_dict["arguments"] = args
        return req_dict
