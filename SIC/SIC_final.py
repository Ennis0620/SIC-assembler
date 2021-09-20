#SIC的opcode有26個
opcode_dic={"ADD":"18",
        	"AND":"40",
        	"COMP":"28",
        	"DIV":"24",
        	"J":"3C",
        	"JEQ":"30",
        	"JGT":"34",
        	"JLT":"38",
        	"JSUB":"48",
        	"LDA":"00",
        	"LDCH":"50",
        	"LDL":"08",
        	"LDX":"04",
        	"MUL":"20",
        	"OR":"44",
        	"RD":"D8",
        	"RSUB":"4C",
        	"STA":"0C",
        	"STCH":"54",
        	"STL":"14",
        	"STSW":"E8",
        	"STX":"10",
        	"SUB":"1C",
        	"TD":"E0",
        	"TIX":"2C",
        	"WD":"DC"               
            }

#虛指令判斷
def directive(col):
    if(col=="START"):
        return "START"
    elif(col == "BYTE"):
        return "BYTE"
    elif(col == "WORD"):
        return "WORD"
    elif(col == "RESW"):
        return "RESW"
    elif(col == "RESB"):
        return "RESB"
    elif(col == "END"):
        return "END"
    else:
        return False
#判斷是否為SIC的指令
def opcode(col):
    if(col in opcode_dic):
        return True
    else:
        return False
#檔案讀取
def read_file(data_name,arr = []):
    with open(data_name,"r",encoding="utf-8-sig") as fp:
        row = fp.readlines()
        for index_row,line in enumerate(row):
            line_strip = line.strip("\n")
            line_split = line_strip.split()
            #動態增加行數
            arr.append([])
            #取出分割後一個一個的字串
            for index,row_per in enumerate(line_split):
                #根據所在行數 動態新增 所分割後得到的字串
                arr[index_row].append(row_per)
    fp.close()

#重新整合
def reshape_arr(one_d_arr=[],re_arr=[],arr=[[]]):
    #先將全部的指令存到一個新的1維陣列
    for index_row,row in enumerate(arr):
        #如果row裡面有值 且="." 代表是註解不用理他
        if(len(row)>0):
            if(row[0]=="."):
                continue                  
        for index_col,col in enumerate(row):           
            one_d_arr.append(col)    
            
    
    for index,per in enumerate(one_d_arr):
        
        #如果讀到的字串 是虛指令或是有在opcode_dic中的指令
        if(directive(per)!=False or per in opcode_dic):
            
            now_per = one_d_arr[index]
            next_per = one_d_arr[index+1]
            #如果現在是RSUB，則指將其陣列改為0 ， 因為RSUB沒有運算元
            if(now_per == "RSUB"):
                one_d_arr[index]=0
            #其餘的都有運算元，所以將本身和下一個改成0
            else:
                one_d_arr[index]=0
                one_d_arr[index+1]=0
            
            #當目前的前一個不為0時，代表是symbol
            if(one_d_arr[index-1]!=0):  
                #RSUB因沒運算元 所以 append 0,RSUB,0
                if(now_per == "RSUB"):
                    re_arr.append([0,now_per,0])
                # symbol(上一個)、當前、下一個 一起append
                else:            
                    re_arr.append([one_d_arr[index-1],now_per,next_per])
            #其他代表沒有symbol
            else:
                re_arr.append(["",now_per,next_per])

#計算虛指令要加多少loc
def directive_loc(Loc_int,index_row,index_col,re_arr=[[]]):
    if(re_arr[index_row][index_col]=="BYTE"):
        BYTE_s = re_arr[index_row][index_col+1].split("’")
        if(BYTE_s[0]=="X"):
            Loc_int=1            
            return Loc_int
        elif(BYTE_s[0]=="C"):
            Loc_int = len(BYTE_s[1])
            return Loc_int
    elif(re_arr[index_row][index_col]=="WORD"):
        Loc_int=3
        return Loc_int
    elif(re_arr[index_row][index_col]=="RESW"):
        RESW_add = int(re_arr[index_row][index_col+1])*3
        Loc_int= RESW_add
        return Loc_int
    elif(re_arr[index_row][index_col]=="RESB"):
        RESB_add = int(re_arr[index_row][index_col+1])
        #轉成16進位
        RESB_add_hex = hex(RESB_add)
        #把16進位從str轉成int 讓其可以相加
        Loc_int=int(RESB_add_hex,base=16)
        return Loc_int
    else:
        return False
    

            
           
#計算loc位置
def loc_count(Loc_int,re_arr=[[]]):
    for index_row,row in enumerate(re_arr):
        for index_col,col in enumerate(row):
            #START指令 代表 其後面是程式指令的開始
            if(col=="START"):
                #強制轉成16進位
                Loc = "0x" + re_arr[index_row][index_col+1]
                Loc_int = int(Loc,base=16)
                #例外處理 如果超過4個數字
                loc_overflow(Loc_int,col,index_row)
            elif(directive_loc(Loc_int,index_row,index_col,re_arr)!=False):
                re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
                Loc_int += directive_loc(Loc_int,index_row,index_col,re_arr)
                #例外處理 如果超過4個數字
                loc_overflow(Loc_int,col,index_row)
            #END    
            elif(col=="END"):
                re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
            elif(col in opcode_dic):
                #例外處理 如果超過4個數字
                loc_overflow(Loc_int,col,index_row)
                re_arr[index_row].append(hex(Loc_int)[2:].upper().zfill(4))
                Loc = hex(Loc_int)
                Loc_int += 3

#找symbol
def symbol_lookup(re_arr=[[]]):
    for index_row,row in enumerate(re_arr):
        #找一行的長度>=4 (避免第一行進去)
        if(len(re_arr[index_row])>=4 and re_arr[index_row][0]!=""):
            #symbol
            key = re_arr[index_row][0]
            #loction值
            value = re_arr[index_row][3]
            symbol.setdefault(key,value)

#填上剩餘程式碼
def object_code(re_arr=[[]]):
    #,X 目的碼要加8000(16進位的)
    add_8000 = "0x8000"
    add_8000 = int(add_8000,base=16)
    
    #剩餘的目的碼
    for index_row,row in enumerate(re_arr):
        for index_col,col in enumerate(row):
            if(col=="RSUB"):
                re_arr[index_row].append("4C0000")
            else:
                if(directive(re_arr[index_row][index_col])!=False):
                    if(re_arr[index_row][index_col]=="BYTE"):
                            BYTE_s = re_arr[index_row][index_col+1].split("’")
                            if(BYTE_s[0]=="X"):
                                re_arr[index_row].append(BYTE_s[1])
                            elif(BYTE_s[0]=="C"):
                                sumstr=""
                                for i in BYTE_s[1]:
                                    ten_ = ord(i)
                                    hex_ = hex(ten_)
                                    sumstr+=hex_[2:].upper()
                                re_arr[index_row].append(sumstr.upper()) 
                    elif(re_arr[index_row][index_col]=="WORD"):
                        ten_WORD = int(re_arr[index_row][index_col+1])
                        if(ten_WORD<0):
                             #利用補數
                             over_7_digit = "0x"+"1000000"
                             #先轉成10進位的int
                             over_7_digit_hex = int(over_7_digit,base=16)
                             #相加後再轉乘16進位
                             two_plus = over_7_digit_hex + ten_WORD
                             two_plus_hex = hex(two_plus)[2:].upper()
                             re_arr[index_row].append(two_plus_hex)
                        #如果WORD是>0     
                        else:
                            #轉成16進位
                            hex_WORD = hex(ten_WORD)[2:]
                            sumstr_word=""
                            #如果字串長度不等於6 要補0
                            if(len(hex_WORD)!=6):
                                for i in range(6-len(hex_WORD)):
                                    sumstr_word+="0"
                            re_arr[index_row].append((sumstr_word+hex_WORD).upper())                           
                                               
                elif(re_arr[index_row][index_col] in opcode_dic):
                    value = opcode_dic[re_arr[index_row][index_col]]
                    str_split = re_arr[index_row][index_col+1].split(",")
                    if(len(str_split)>=2):
                        loc = symbol[str_split[0]]
                        #loc轉成16進位
                        loc = "0x" + loc
                        #再轉成10進位
                        loc_hex_int = int(loc,base=16)
                        loc_hex_int  += add_8000
                        loc_hex = hex(loc_hex_int)[2:].upper()
                        re_arr[index_row].append(value+loc_hex)
                    else:
                        #例外處理symbol錯誤
                        symbol_not_found(index_row,index_col,symbol,re_arr)
                        
                        loc = symbol[re_arr[index_row][index_col+1]]
                        
                        #例外處理 如果loc>7FFF代表錯誤 因為addr只有15bits 最大到7FFF
                        object_overflow(index_row,re_arr[index_row][index_col+2])
                        
                        sum_value_loc = value + loc
                        re_arr[index_row].append(sum_value_loc)

#印出來
def print_re_arr(re_arr=[[]]):
    for index_row,row in enumerate(re_arr):
        for index_col,col in enumerate(row):     
            if(index_col==len(re_arr[index_row])-1):   
                print('%-13s' % re_arr[index_row][index_col])
            else:
                print('%-13s' % re_arr[index_row][index_col],end="")

#例外處理
#位址超出4個數
class locERROR(Exception):
    pass
def loc_overflow(loc,col,index_row):
    loc = hex(loc)[2:]
    if(len(loc)>4):
        raise locERROR("locERROR 第"+str(index_row)+"行 "+ str(col) +"出錯") 

class objectERROR(Exception):
    pass
def object_overflow(index_row,obj):
    obj = "0x"+obj
    obj = int(obj,base=16)
    limit = "0x7FFF"
    limit = int(limit,base=16)
    if(obj>limit):
        raise objectERROR("objectERROR 第"+str(index_row)+"行"+str(hex(obj))+"出錯")
class symbolERROR(Exception):
    pass
def symbol_not_found(index_row,index_col,symbol,re_arr):
    if(re_arr[index_row][index_col+1] not in symbol):
        raise symbolERROR("symbolERROR 第"+str(index_row)+"行"+str(re_arr[index_row][index_col+1])+"出錯")
    
''' 主程式 '''
Loc = 0
arr = []
symbol={}
data_name = "SIC_space.txt"
read_file(data_name,arr)
one_d_arr=[]
re_arr = []
reshape_arr(one_d_arr,re_arr,arr)

try:    
    loc_count(Loc,re_arr)
    symbol_lookup(re_arr)
    object_code(re_arr)
    print_re_arr(re_arr)
except locERROR as e:
    print(e)
except objectERROR as o:
    print(o)
except symbolERROR as s:
    print(s)
