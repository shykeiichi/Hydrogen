from copy import copy
import enum
import sys, json
from pygments import highlight, lexers, formatters

L_KEYWORDS = ["switch", "if", "case"]
L_TYPES = ["U8", "U16", "U32", "I8", "I16", "I32", "I64"]
L_SYMBOLS = [";", "{", "}", "(", ")", ":"]
L_COMOP = ["==", "!=", ">=", "<=", ">", "<", "&&", "||"]
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
        token_type = "BINOP"
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
        
        elif text[i + 1] == " " or text[i + 1] in L_SYMBOLS and token.replace(".", "").isdigit():
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
                    "type": "I32"
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
    
    # print(json.dumps(tokens, indent=2))
    
    for i, token in enumerate(tokens):
        if continue_until_semicolon:
            if token["value"] == ";" and token["type"] == "SYMBOL":
                continue_until_semicolon = False
            continue

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
        elif token["type"] == "KEYWORD":
            match token["value"]:
                case "if":
                    parsed_file.append({
                        "type": "CONDITIONAL",
                        "value": parse_equation(get_tokens_between_level_parentheses(tokens, i + 2))
                    })
                    formatted_json = json.dumps(parse_equation(get_tokens_between_level_parentheses(tokens, i + 2)), indent=2)    
                    colorful_json = highlight(str(formatted_json), lexers.JsonLexer(), formatters.TerminalFormatter())
                    print(colorful_json)
                    break
            
            
    return parsed_file

def parse_equation(tokens):
    ignore_until_next_bool = False;
    ignore_until_next_level = 0;
    for i, token in enumerate(tokens):
        if ignore_until_next_bool:
            if token["type"] == "SYMBOL":
                if token["value"] == "(":
                    ignore_until_next_level += 1
                if token["value"] == ")":
                    ignore_until_next_level -= 1
                if ignore_until_next_level == -1:
                    ignore_until_next_bool = False
                    continue

        if token["type"] == "SYMBOL":
            if token["value"] == "(":
                result = parse_equation(get_tokens_between_level_parentheses(tokens, i + 1))
                result_range = get_range_between_level_parentheses(tokens, i + 1)
                del tokens[result_range[0] - 1:result_range[1] + 1]
                tokens.insert(result_range[0] - 1, result) 
                ignore_until_next_bool = True
                ignore_until_next_level = 0
            
    # print(json.dumps(tokens, indent=2))
    for i, token in enumerate(tokens):
        if isinstance(token, dict):
            if token["type"] == "BINOP":
                if token["value"] == "*" or token["value"] == "/":
                    new_op = {
                        "type": "BINARY",
                        "operator": token["value"],
                        "left": tokens[i - 1],
                        "right": tokens[i + 1]
                    }
                    del tokens[i + 1]
                    del tokens[i]
                    del tokens[i - 1]
                    tokens.insert(i - 1, new_op) 
                    
    # final_tokens = []
    # for i, token in enumerate(tokens):
    #     if isinstance(token, dict):
    #         if token["type"] == "BINOP":
    #             final_tokens.append({
    #                 "type": "BINARY",
    #                 "operator": token["value"],
    #                 "left": tokens[i - 1],
    #                 "right": tokens[i + 1]
    #             })
    
    return tokens

def get_tokens_between_level_parentheses(tokens, start):
    final_tokens = []
    tokens_level = 0
    
    end = 0
    for i, token in enumerate(tokens):
        if i < start:
            continue
        if token["type"] == "SYMBOL":
            if token["value"] == "(":
                tokens_level += 1
            if token["value"] == ")":
                tokens_level -= 1
            if tokens_level == -1:
                end = i
                break
        final_tokens.append(token)
    # print(json.dumps(final_tokens, indent=2)z

    return final_tokens

def get_range_between_level_parentheses(tokens, start):
    final_tokens = []
    tokens_level = 0
    
    end = 0
    for i, token in enumerate(tokens):
        if i < start:
            continue
        if token["type"] == "SYMBOL":
            if token["value"] == "(":
                tokens_level += 1
            if token["value"] == ")":
                tokens_level -= 1
            if tokens_level == -1:
                end = i
                break
        final_tokens.append(token)
    # print(json.dumps(final_tokens, indent=2))
    return (start, end)
    
run(sys.argv[1])
