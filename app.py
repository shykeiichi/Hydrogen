from curses.ascii import isalpha
from re import A
from tokenize import Token

L_KEYWORDS = ["switch", "if", "case"]
L_TYPES = ["U8", "U16", "U32", "I8", "I16", "I32", "I64"]
L_SYMBOLS = [";", "{", "}", "(", ")", ":"]
L_OPERATORS = ["=", "==", "!=", ">=", "<=", ">", "<", "+", "++", "+=", "*", "/", "-", "--", "-="]


L_TOKENS = L_KEYWORDS + L_TYPES + L_OPERATORS + L_SYMBOLS

def run(fn):
    text = open(fn, "r").read().replace("\n", "")
    print(text)

    token = ""
    tokens = []
    
    is_string = False
    
    for i, char in enumerate(text):
        if len(text) == i + 1:
            continue    
        
        if char == "\"":
            if i > 0:
                if text[i - 1] != "\\": 
                    is_string = not is_string
        
        token += char
        if len(token) > 1:
            while token[0] == ' ':
                token = token[1:]

        # print(text[i + 1])
        # print(token)
        if is_string:
            continue
        elif token in L_TOKENS and (text[i + 1] == " " or text[i + 1] == ";" or text[i + 1] == ":"):
            token_type = ""
            if(token in L_TYPES):
                token_type = "type"
            elif(token in L_OPERATORS):
                token_type = "operator"
            elif(token in L_KEYWORDS):
                token_type = "keyword"
            elif(token in L_SYMBOLS):
                token_type = "symbol"
            
            tokens.append({
                "value": token,
                "type": token_type
            })
            token = ""
                
        elif char in L_TOKENS and not (char + text[i + 1] in L_TOKENS):
            
            token_type = ""
            if(token in L_TYPES):
                token_type = "type"
            elif(token in L_OPERATORS):
                token_type = "operator"
            elif(token in L_KEYWORDS):
                token_type = "keyword"
            elif(token in L_SYMBOLS):
                token_type = "symbol"
            
            tokens.append({
                "value": token,
                "type": token_type
            })
            token = ""
        
        elif (text[i + 1] == " " or text[i + 1] == ";" or text[i + 1] == ":") and token.replace(".", "").isdigit():
            if token.count('.') > 1:
                print("Number can't have more than one '.'.")
                return
        
            if '.' in token:     
                tokens.append({
                    "value": token,
                    "type": "float"
                })
            else:
                tokens.append({
                    "value": token,
                    "type": "int"
                })
            token = ""
        elif token[0] == "\"" and token[-1] == "\"":
            tokens.append({
                "value": token[1: -1].replace("\\\"", "\""),
                "type": "string"
            })
            token = ""
        elif text[i + 1] == " " or text[i + 1] == ";" or text[i + 1] == "(" or text[i + 1] == ")" or text[i + 1] == ":":
            tokens.append({
                "value": token,
                "type": "id"
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
    
tokens = run("examples/hw.hy")
for i in tokens:
    print("Val: \"{}\", Type: \"{}\"".format(i["value"], i["type"]))
