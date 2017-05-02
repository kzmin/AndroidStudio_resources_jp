# -*- coding: utf-8 -*-
import io

class PropertiesParser(object):
    @staticmethod
    def parse(stream):
        lines = stream.readlines()
        # print("lines = " + str(lines) + ", len = " + str(len(lines)))
        
        properties = []
        comments = []
        linecount = 0
        lines_iter = iter(lines)
        for line in lines_iter:
            linecount += 1
            # print(result)
            # print("line No." + str(linecount) + " = " + line.encode('utf-8'))
            
            # Blank Line: ignore
            if PropertiesParser.isBlankLine(line):
                continue


            if PropertiesParser.isCommentLine(line):
                content = line.rstrip('\n')
                
                # Append Comment
                dics = {
                    'content': content,
                    'line': linecount,
                    'isMultiLine': False
                }
                
                # If continue to next line, concatinate
                while PropertiesParser.isMiddleInMultiLine(dics['content']):
                    nextline = next(lines_iter)
                    if not nextline:
                        break
                    dics['content'] += '\n' + nextline.rstrip('\n')
                    dics['isMultiLine'] = True
                    linecount += 1
                
                comments.append(dics)
                
            else:
                # print("line No." + str(linecount) + " = " + line.encode('utf-8'))
                
                splitlist     = line.split('=', 1)
            
                # Not Key-Value: ignore
                if not len(splitlist) == 2:
                    continue
                
                splitlist[1] = splitlist[1].rstrip('\n')
                
                # Append Key-Value
                dics = {
                    'key': splitlist[0],
                    'value': splitlist[1],
                    'line': linecount,
                    'isMultiLine': False
                }
                
                # If continue to next line, concatinate
                while PropertiesParser.isMiddleInMultiLine(dics['value']):
                    nextline = next(lines_iter)
                    if not nextline:
                        break
                    dics['value'] += '\n' + nextline.rstrip('\n')
                    dics['isMultiLine'] = True
                    linecount += 1
                
                properties.append(dics)
        
        return {'comments': comments, 'properties': properties}

    @staticmethod
    def isCommentLine(line):
        return line[0] == '#'

    @staticmethod
    def isBlankLine(line):
        return line[0] == '\n'
    
    @staticmethod
    def isMiddleInMultiLine(string):
        return string[-1] == '\\' if len(string) > 0 else False

def parsertest():
    string = """
# comment1

abc.def=1
ghi.000.j=2
# comment2
klm=3\
4

# comment3
"""
    s = io.StringIO(string)
    result = PropertiesParser.parse(s)
    #print(result)

if __name__ == '__main__':
    parsertest()


