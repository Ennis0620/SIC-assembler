SIC-assembler
===

# Introduction
據System Software，進一步了解Assembler的原理，並予以實作
# Detail
SIC指令格式

|Opcode:8|	x:1	|address:15|

為24bits


暫存器有:A(累加器)、X(索引)、L(連結)、PC(程式計數器)、SW(狀態字組)


SIC 虛指令(directive):

START:指定程式名稱和起始位置(MEM的擺放位址，只有此行是16進位)

END:程式的結尾並指定程式中第一個執行指令

BYTE:分為

C’EOF’= 3 (C表示引號內有多少字元)
    
X’F1’ = 1 (X代表引號中2個16進位為1byte)
    
WORD:定義一個字組的整數常數(固定佔3bytes)

RESB: 保留所示數量位元組

ex. RESB 30(十進位) => 1E(十六進位) 

RESW: 保留所示數量字組(記得乘上3，因為1字組=3bytes)

將指令Loc、Source satement(Symbol、Opcode、Operand)輸入，計算出各行的Object Code

---

### 讀檔:
存取Symbol、Instruction、Operand，不存註解行
### 處理格式
(即使沒有對整齊，也可以順利組譯、偵測Opcode是否都正確)
### 處理Loc

判斷虛指令，計算該行需要+多少Loc

BYTE  X’’  加1

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; C’’  根據引號中的數量 就加多少 

WORD都加3

RESB 將Operand數字轉乘16進位再加上去

RESW 將Operand數字乘3再轉16進位

其他的一般指令都加3

### 處理Object code
一般指令:

Object code:前2碼為參照指令的opcode

後4碼需要根據Operand參照Symbol的Loc位置進行計算

特殊:
RSUB 後4碼Object code通通補0

在Operand有 ,X  直接加8000

虛指令的:

BYTE X’’ 直接填引號中的數值

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;C’’ 引號中數值轉成ASCII的編碼

WORD 要判斷Operand的正負，為負要轉2補數





# Demo
輸入

![](https://i.imgur.com/d9Lcfv2.png)
![](https://i.imgur.com/X1idHTk.png)

輸出

![](https://i.imgur.com/3sYzyRk.png)
![](https://i.imgur.com/UvqgLTB.png)

# Requirement
    None
# Package
    SIC
            SIC.txt         正常格式輸入
            SIC_final.py    主程式
            SIC_space.txt   混亂格式輸入
# Problems

# Solve

