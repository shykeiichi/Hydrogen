import sys, json

L_KEYWORDS = ["switch", "if", "case"]
L_TYPES = ["U8", "U16", "U32", "I8", "I16", "I32", "I64"]
L_SYMBOLS = [";", "{", "}", "(", ")", ":"]
L_COMOP = ["==", "!=", ">=", "<=", ">", "<"]
L_ASOP_SINGLE = ["++", "--"]
L_ASOP_MULTIPLE = ["+=", "-=", "="]
L_ASOP = L_ASOP_SINGLE + L_ASOP_MULTIPLE
L_BINOP = ["+", "*", "/", "-"]

L_TOKENS = L_KEYWORDS + L_TYPES + L_ASOP + L_SYMBOLS + L_COMOP + L_BINOP

def get_type(token: str) -> str:
    token_type = ""
    if(token in L_TYPES):
        token_type = "TYPE"
    elif(token in L_COMOP):
        token_type = "COMOP"
    elif(token in L_ASOP):
        token_type = "ASOP"
    elif(token in L_KEYWORDS):
        token_type = "KEYWORD"
    elif(token in L_SYMBOLS):
        token_type = "SYMBOL"
    elif(token in L_BINOP):
        token_type = "BINARY"
    return token_type

def run(fn):
    text = open(fn, "r").read().replace("\n", "")
    tokens = lexer(text)
    
    ofile = open("output.json", "w")
    ofile.write("")
    ofile.write(json.dumps(gen_prog(tokens), indent=2))
    
def lexer(text):

    token = ""
    tokens = []
    
    is_string = False
    
    for i, char in enumerate(text):
        # print(char)
        
        if char == "\"":
            if i > 0:
                if text[i - 1] != "\\": 
                    is_string = not is_string
    
        token += char
        
        if len(text) == i + 1:
            # print(token)
            if token in L_TOKENS:
                tokens.append({
                    "value": token,
                    "type": get_type(token)
                })
                token = ""
            continue
        
        if len(token) > 1:
            while token[0] == ' ':
                token = token[1:]

        # print(text[i + 1])
        # print("{} {}".format(token, ""))
        if is_string:
            continue
        elif token in L_SYMBOLS:
            tokens.append({
                "value": token,
                "type": get_type(token)
            })
            token = ""
        elif token in L_TOKENS and (text[i + 1] == " " or text[i + 1] == ";" or text[i + 1] == ":"):
            tokens.append({
                "value": token,
                "type": get_type(token)
            })
            token = ""
                
        elif token in L_TOKENS and not (token + text[i + 1] in L_TOKENS) and not text[i + 1].isalnum():
            tokens.append({
                "value": token,
                "type": get_type(token)
            })
            token = ""
        
        elif (text[i + 1] == " " or text[i + 1] == ";" or text[i + 1] == ":") and token.replace(".", "").isdigit():
            if token.count('.') > 1:
                print("Number can't have more than one '.'.")
                return
        
            if '.' in token:     
                tokens.append({
                    "value": token,
                    "type": "FLOAT"
                })
            else:
                tokens.append({
                    "value": token,
                    "type": "INT"
                })
            token = ""
        elif token[0] == "\"" and token[-1] == "\"":
            tokens.append({
                "value": token[1: -1].replace("\\\"", "\""),
                "type": "STRING"
            })
            token = ""
        elif text[i + 1] == " " or text[i + 1] == ";" or text[i + 1] == "(" or text[i + 1] == ")" or text[i + 1] == ":" or (text[i + 1] in L_TOKENS and not (token + text[i + 1] in L_TOKENS)):
            tokens.append({
                "value": token,
                "type": "ID"
            })
            token = ""
            
    if token in L_TOKENS:
        tokens.append({
            "value": token,
            "type": get_type(token)
        })
        token = ""
        
    pop_list = []
    for i, item in enumerate(tokens):
        if(item["value"] == " "):
            pop_list.append(i)
            
    pop_list.sort()
    pop_list.reverse()
    
    for i in pop_list:
        tokens.pop(i)
        
        
    return tokens
    
def gen_prog(tokens):
    parsed_file = []
    
    continue_until_semicolon = False
    
    for i, token in enumerate(tokens):
        if continue_until_semicolon:
            if token["value"] == ";" and token["type"] == "SYMBOL":
                continue_until_semicolon = False
            continue
        
        print(token)
        
        if token["type"] == "TYPE":            
            parsed_file.append({
                "type": "DECLARE",
                "id": tokens[i + 1]["value"],
                "value": token["value"]
            })
            
            if tokens[i + 2]["type"] == "ASOP":
                if tokens[i + 2]["value"] != "=":
                    print("Cannot use dynamic assignment at declaration!")
                    return
                else:
                    parsed_file.append({
                        "type": "ASSIGN",
                        "id": tokens[i + 1]["value"],
                        "value": tokens[i + 3]["value"]
                    })
            elif tokens[i + 2]["type"] == "BINOP":
                print("Can't use binary operator on variable assignment!")
                return
            
            continue_until_semicolon = True
        elif token["type"] == "ID":
            if tokens[i + 1]["type"] == "ASOP":
                continue_until_semicolon = True
                if(tokens[i + 1]["value"] in L_ASOP_SINGLE):
                    parsed_file.append({
                        "type": "ASSIGN",
                        "id": token["value"],
                        "value": {
                            "type": "BINARY",
                            "operator": tokens[i + 1]["value"][0],
                            "left": {
                                "type": "ID",
                                "value": token["value"]
                            },
                            "right": {
                                "type": "I32",
                                "value": "1"
                            }
                        }
                    })
                elif tokens[i + 1]["value"] in L_ASOP_MULTIPLE:
                    if tokens[i + 1]["value"] == "=":
                        parsed_file.append({
                            "type": "ASSIGN",
                            "id": token["value"],
                            "value": tokens[i + 2]["value"]
                        })
                    else:
                        parsed_file.append({
                            "type": "ASSIGN",
                            "id": token["value"],
                            "value": {
                                "type": "BINARY",
                                "operator": tokens[i + 1]["value"][0],
                                "left": {
                                    "type": "ID",
                                    "value": token["value"]
                                },
                                "right": {
                                    "type": "I32",
                                    "value": tokens[i + 2]["value"]
                                }
                            }
                        })
        elif token["type"] == ["KEYWORD"]:
            match token["value"]:
                case "if":
                    parsed_file.append({
                        "type": "CONDITIONAL",
                        "operator": "==", # FIX FIX IFX FIX
                        "id": token["value"],
                        "value": {
                            "type": "BINARY",
                            "operator": tokens[i + 1]["value"][0],
                            "left": {
                                "type": "ID",
                                "value": token["value"]
                            },
                            "right": {
                                "type": "I32",
                                "value": tokens[i + 2]["value"]
                            }
                        }
                    })
                    break
            
            
    return parsed_file
            
    
run(sys.argv[1])
