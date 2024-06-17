"""
Standing for Kevcore Data Notation
Simliar format to JSON files
"""

# i am SO SURPRISED that i didnt use the internet to make this
# HOW??? ig my own language helped in the process
# obv its not efficient. dont use in production unless u wanna use less disk space...

'''
HOW TO USE:
Here is a VERY easy to way to understand it:
It is a JSON format, but remove colons, quotation marks if the value does not contain any spaces, and commas (replace commas with ; if written in 1 line)
The user writing KDN format can include quotation marks for values that do not contain spaces and it will perform the same.
As of V1, you are unable to put quotation marks inside of values (no \"). Will be changed later
It is more efficient compared to a JSON file in terms of disk usage, but way less efficient in terms of speed.

EXAMPLE USAGE:
# Dumping a dict to a KDN file
import kdn
data = {"hello": "world", "abc": {"a": 1, "b": 2, "c": 3}}
kdn.dumpf(data, "filename.kdn")

# Loading KDN file
kf = kdn.loadf("filename.kdn")

# or loading a KDN formatted string
kdnstr = """parent{yes "some string";yes2 23423;yes3{hello world;some_list [abc];}};parent2{}"""
data = kdn.loads(kdnstr)
'''

'''
EXAMPLE:
parent {
    yes "some string"
    yes2 23423
    yes3 {
        hello world
        "some list" [abc]
    }
}
parent2 { 

}

SHORTENED:
parent{yes "some string";yes2 23423;yes3{hello world;some_list [abc];}};parent2{}
'''

from ast import literal_eval

def loads(data: str) -> dict:
    """Loads a KDN format into a dictionary"""
    dictdata = {}
    trimmed = data.replace("{\n", "{").replace("\n}","}").replace("\n", ";")

    # Temp values
    key = "" 
    value = "" 

    # Whether it is currently on a KEY or VALUE. A space character switches these
    onKey = True

    # How much unclosed brackets ({). Required for iteration 
    unclosed = 0 
    pendingParent = False # Whether a dict inside of dict is detected (uses this function again = recursion)

    parentsTemp = "" # Values of the "inside" dict
    parentName = "" # name of the parent dict

    # Whether it is a string (") or not
    inStr = False

    for t in trimmed:
        match t:
            case "{":               
                unclosed += 1

                if pendingParent:
                    parentsTemp += "{"
                else:
                    pendingParent = True
                    parentName = key
            case '"':
                if not pendingParent:
                    inStr = not inStr
                else:
                    parentsTemp += '"'
            case " ":
                if onKey and key != "" and not pendingParent: 
                    if not inStr:
                        onKey = False
                    else:
                        key += " "
                elif pendingParent:
                    parentsTemp += " "

                if inStr:
                    value += " "

            case ";":
                if not pendingParent:
                    if (key != "" and value != "") or (key != "" and key not in dictdata):
                        try:
                            dictdata[key] = literal_eval(value)
                        except (ValueError, SyntaxError):
                            dictdata[key] = value
                    key, value = "", ""
                    onKey = True
                else:
                    parentsTemp += t

            case "}":
                unclosed -= 1
                if pendingParent and unclosed != 0:
                    parentsTemp += "}"
                if pendingParent and unclosed == 0:
                    dictdata[parentName] = loads(parentsTemp)
                    pendingParent = False
                    onKey = True
                    parentsTemp = ""

            case _:
                if pendingParent:
                    parentsTemp += t
                elif onKey:
                    key += t
                else:
                    if key != "":
                        value += t
    return dictdata

def dumps(data: dict, indent: int = 0, includeEmptyValues: bool = False) -> str:
    """Returns a KDN format of a dictionary"""
    kdndata = []

    for parent in data:
        if isinstance(data[parent], dict):
            kdndata.append( parent + "{" + dumps(data[parent]) + "};" )
        else:
            if isinstance(data[parent], str):
                d = data[parent] if " " not in data[parent] else f'"{data[parent]}"'
            else:
                d = str(data[parent])

            if includeEmptyValues and d == "": d = '""'

            kdndata.append( parent + " " + d + ";" )

    result = "".join(kdndata).replace("};}", "}}")

    if indent > 0:
        return pretty_print(result, indent=indent)
    else:
        return result


def pretty_print(data: str, indent: int = 4, removeBlanks: bool = True) -> str:
    """Pretty prints KDN formats"""

    currentIndent = 0

    newKDN = []
    for t in data:
        if t == "{":           
            currentIndent += 1

            newKDN.append(" {\n" + " " * (currentIndent * indent))
        elif t == "}":            
            currentIndent -= 1

            newKDN.append("\n" + " " * (currentIndent * indent) + "}")
        elif t == ";":
            newKDN.append("\n" + " " * (currentIndent * indent))
        else:
            newKDN.append(t)

    
    # Remove blanks at the cost of performance
    result = "".join(newKDN)
    del newKDN # Free RAM
    if removeBlanks:
        new = []
        for ln in result.splitlines():
            if not (ln.isspace() or ln == ""):
                new.append(ln)

        result = "\n".join(new)
        
                
    return result


def dumpf(data: dict, file: str, indent: int = 0) -> None:
    """Dumps a dictionary to a file in KDN format"""
    with open(file, "w") as file: 
        file.write(dumps(data, indent=indent))

def loadf(file: str) -> dict:
    """Loads a KDN file"""
    with open(file, "r") as file:
        return loads(file.read())

def dump(data: dict, file, indent: int = 0) -> None:
    """Dumps a dictionary to a file in KDN format"""
    file.write(dumps(data, indent=indent))

def load(file) -> dict:
    """Loads a KDN file"""
    return loads(file.read())

def simplifys(data: str) -> str:
    """Simplifes KDN formats by loading and dumping it"""
    return dumps(loads(data))
def simplify(file: str):
    """Simplifes a KDN formatted file by loading and dumping it"""
    return dump(load(file))

