L_KEYWORDS = ["switch", "if", "case"]
L_TYPES = ["U8", "U16", "U32", "I8", "I16", "I32", "I64"]
L_SYMBOLS = [";", "{", "}", "(", ")", ":"]
L_COMOP = ["==", "!=", ">=", "<=", ">", "<"]
L_ASOP = ["+", "++", "+=", "*", "/", "-", "--", "-=", "="]

L_TOKENS = L_KEYWORDS + L_TYPES + L_ASOP + L_SYMBOLS + L_COMOP

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
    return token_type

def run(fn):
    text = open(fn, "r").read().replace("\n", "")
    print(text)

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
        print("{} {}".format(token, ""))
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
    
tokens = run("examples/hw.hy")
for i in tokens:
    print(i)
