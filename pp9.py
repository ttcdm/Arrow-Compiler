#TODO: wrap the whole thing in a class and maybe with try catches as well
#TODO: allow equivalencies to not mandate calculations, i.e, "y = x" instead of "y = x+0" and "if x = 2" instead of "if x+0 = 2+0"
#TODO: double equal signs for equivalences and single equal signs for variable assignments instead of only using single equal signs for everything
#TODO: incrementing afterc by 2 that many times may cause issues



import os
r = open("arrow.aro", "r")
w = open("6asm.txt", "w")
l = r.readlines()
afterc = 0
elsec = 0
varc = 0x400
varc = int(str(varc).replace("0x", ""))
linec = -1
arrayc = []
arraycin = -1#not sure if this is actually needed cuz arrayc is kinda treated like a stack
barray = []
sarray = []
for i in range(len(l)):
    l[i] = l[i].replace(" ", "").replace("\n", "")
for c in l:
    linec += 1
    print(f"LINE #{linec}")
    afterc += 2
    #c = c.replace(" ", "")
    #c = c.replace("\n", "")
    a = [s for s in c]
    ops = {"+", "-", "*", "/"}
    o = []
    for i in a:
        if i in ops:
            o.append(i)
    def par(var, ar):
        x = "".join(ar[0:ar.index(var)])
        y = "".join(ar[ar.index(var) + 1:len(ar)])
        #print(f"{x} {y}")
        return x, y

    def op(var, x, y):
        if "[" in x:
            numx = "".join(x[x.index("[") + 1:x.index("]")])
            if numx.isnumeric():
                x = x.replace("[", "").replace("]", "")
            elif numx.isalpha():#y is used as the relative address thing
                namex = x[0:x.index("[")]
                w.write(f"LDY {numx}\n")
                x = f"{namex}0,y"
        if "[" in y:
            numy = "".join(y[y.index("[") + 1:y.index("]")])
            if numy.isnumeric():
                numy = y.replace("]", "").replace("[", "")
            elif numy.isalpha():#y is used as the relative address thing
                namey = y[0:y.index("[")]
                w.write(f"LDY {numy}\n")
                y = f"{namey}0,y"

        vx = "#"
        vy = "#"
        if not x.isnumeric():
            vx = ""
        if not y.isnumeric():
            vy = ""
        #w.writeline(f"LDA #00\n")
        if var == "+":
            w.writelines([f"CLC\nCLV\n", f"LDA {vx}{x}\n", f"ADC {vy}{y}\n", f"PHA\n"])
        elif var == "-":
            w.writelines([f"CLC\nCLV\n", f"LDA {vx}{x}\n", f"SBC {vy}{y}\n", f"ADC #0\n",  f"PHA\n"])#always use ADC #0 after every individual calculation i guess
        elif var == "*":
            w.writelines([f"CLC\nCLV\n", f"LDX #$00\n", f"LDA #00\n", f"MULT{afterc}\n", f"ADC {vx}{x}\n", f"INX\n", f"ADC #0\n", f"CPX {vy}{y}\n", f"BNE MULT{afterc}\n", f"PHA\n"])
        elif var == "/":
            w.writelines([f"CLC\nCLV\n", f"LDX #$00\n", f"LDA #00\n", f"DIV{afterc}\n", f"ADC {vy}{y}\n", f"INX\n", f"ADC #0\n", f"CMP {vx}{x}\n", f"BMI DIV{afterc}\n", f"CLC\n", f"DEX\n", f"SBC {vy}{y}\n", f"ADC #0\n", f"STA $10FF\n",  f"LDA {vx}{x}\n", f"SBC $10FF\n", f"ADC #0\n", f"PHA\n",  f"TXA\n", f"PHA\n"])
        w.write("\n")

    def dcvar(var, ad):
        w.writelines([f"{var} = ${ad}\n"])
        w.writelines([f"CLC\nCLV\n", f"PLA\nSTA {var}\n\n"])

    #x, y = par(o)
    #x, y = int(x), int(y)
    #op(o)
    d = []
    def decs(afterc, elsec, varc, arraycin, barray, sarray):
        if "".join(a[0:2]) == "if":
            d = a[2:len(a)]
            first, last = par("=", d)
            #print(f"{first} {last}")
            x, y = par(o[0], first)
            op(o[0], x, y)
            x, y = par(o[1], last)
            op(o[0], x, y)
            w.writelines([f"CLC\nCLV\n", f"PLA\nTAX\nSTX $10FF\nPLA\nCMP $10FF\nBEQ OTHER{afterc+1}\nLDA #$BB\nPHA\nJSR AFTER{afterc}\nOTHER{afterc+1}\nLDA #$AA\nPHA\nAFTER{afterc}\n\n"])#AA is true, BB is false
            afterc += 2
            elsec = afterc#technically elsec isn't needed anymore since we have arrayc
            arraycin += 1
            arrayc.append(elsec)
            w.writelines([f"CLC\nCLV\n", f"PLA\nCMP #$AA\n\nBNE OTHER{afterc+1}\nLDA #$AA\nPHA\n\n"])
            afterc += 2
        elif "".join(a[0:4]) == "else":
            d = a[4:len(a)]
            w.write(f"JSR AFTER{arrayc[arraycin]}\n")
            w.write(f"OTHER{arrayc[arraycin]+1}\n")
        elif "".join(a[0:1]) == ";":
            for i in range(linec, -1, -1):
                if i in sarray:
                    continue
                if "".join(l[i][0:4]) == "else":
                    sarray.append(i)
                    w.write(f"AFTER{arrayc[arraycin]}\n\n")
                    arrayc.pop(arraycin)
                    arraycin -= 1
                    break
                elif "".join(l[i][0:3]) == "for":
                    sarray.append(i)
                    d = l[i][3:len(l[i])]
                    first, last = par(",", d)
                    w.writelines([f"CLC\nCLV\n", f"LDA {first}\nADC #01\nSTA {first}\nCMP #{int(last)}\nBMI AFTER{arrayc[arraycin]}\nLDA {first}\nSBC #01\nSTA {first}\n\n"])#it's branch on minus so it increments till one below the limit. #decrementing it by one after the loop might not be necessary
                    arrayc.pop(arraycin)
                    arraycin -= 1

                    for n in range(linec, i - 1, -1):
                        if "".join(l[n][0:5]) == "break":
                            w.write(f"AFTER{barray[-1]}A\n")#the "A" is there so the numbering doesn't get mixed up with the other subroutines
                            barray.pop()
                            break
                    break

        elif "".join(a[0:3]) == "dec":
            d = a[3:len(a)]
            first, last = par("=", d)
            #first = first.upper()
            #print(f"{first} {last}")
            if len(o) == 0:#if there's no operation then it counts it as an array
                asize = last[last.index("[")+1:last.index("]")]
                first = first.replace("[", "").replace("]", "")
                for i in range(int(asize)):
                    w.writelines([f"{first}{i} = ${str(hex(varc)).replace('0x', '')}\n"])#using single quotes here and the one a few lines below because you can only use single quotes inside doubel quotes or something like that
                    varc += 1
            else:#since there is an operation, it counts it as a variable, because assignments must always have an operator
                x, y = par(o[0], last)
                op(o[0], x, y)
                dcvar(first, varc)#str(hex(varc)).replace('0x', '') in place of varc. if you want to keep it all in $400 and up
                #dcvar(first, str(hex(varc)).replace('0x', ''))#putting only the variables in the 10xx space is just for organizational purposes
                varc += 1

        elif "".join(a[0:3]) == "for":
            """
            loops from 1 to n (inclusive)
            """
            afterc += 2#+= 2 because the loop break afterc's are 1 more than the last element of arrayc
            elsec = afterc
            arraycin += 1
            arrayc.append(elsec)
            d = a[3:len(a)]
            first, last = par(",", d)
            w.writelines([f"{first} = ${str(hex(varc)).replace('0x', '')}\n"])
            varc += 1#varc is always incremented after a variable has been assigned to the address
            w.writelines([f"CLC\nCLV\n", f"LDA #00\nSTA {first}\nAFTER{afterc}\nLDA #00\n"])#LDX #$01 because we're counting from 1 to 5 inclusive to iterate 5 times instead of 6 times from 0-6 because it's a bit more complicated to subtract 1 from 5

        elif "".join(a[0:5]) == "break":
            barray.append(arrayc[arraycin])
            w.write(f"JSR AFTER{barray[-1]}A\n")

        elif a[0].isalpha():#must leave at end because it'll register the first letter as a variable and not part of a keyword
            first, last = par("=", a)
            if "[" in first:
                numa = "".join(a[a.index("[")+1:a.index("]")])
                if numa.isnumeric():
                    first = first.replace("[", "").replace("]", "")
                    #first = first.upper()
                    x, y = par(o[0], last)
                    op(o[0], x, y)
                    w.writelines([f"CLC\nCLV\n", f"PLA\nSTA {first}\n\n"])
                elif numa.isalpha():
                    #first = first.upper()
                    x, y = par(o[0], last)
                    op(o[0], x, y)
                    if "[" in first:
                        namea = first[0:first.index("[")]
                        w.write(f"LDY {numa}\n")
                        rfirst = f"{namea}0,y"
                        w.writelines([f"CLC\nCLV\n", f"PLA\nSTA {rfirst}\n\n"])
            else:#technically this could just be included in the numa.isnumeric() statement with more conditions and some more try catches
                x, y = par(o[0], last)
                op(o[0], x, y)
                w.writelines([f"CLC\nCLV\n", f"PLA\nSTA {first}\n\n"])

        else:
            x, y = par(o[0], a)
            op(o[0], x, y)
        return afterc, elsec, varc, arraycin, barray, sarray
    afterc, elsec, varc, arraycin, barray, sarray = decs(afterc, elsec, varc, arraycin, barray, sarray)
w.close()
r.close()