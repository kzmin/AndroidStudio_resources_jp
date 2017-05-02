#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 11:42:07 2017

@author: kzmin
"""

from db import SessionWrapper, PropertiesFile, Property, Comment
from properties_parser import PropertiesParser
from sqlite3 import OperationalError
from os import listdir
from argparse import ArgumentParser
import re

init = False

def parse(filepath):
    fs = open(filepath, encoding="utf-8")
    properties_comments = PropertiesParser.parse(fs)
    fs.close()
    return properties_comments


argrepatter = re.compile(r"(\{[0-9n]\})")
def getArgNum(string):
    l = argrepatter.findall(string)
    return len(l)

def properties2sqlite(dbpath, inputpath):
    # create session
    session = SessionWrapper(dbpath, encoding='utf-8', echo=False)
    
    try:
        # if init or not, delete comments from db
        session.deleteComments()
        session.commit()

        # init: delete propertiesfiles and properties from db
        if init:
            session.deleteProperties()
            session.deletePropertiesFiles()
            session.commit()
    
            # register PropertiesFile
            repatter = re.compile(r".properties$")
            filenames = [l for l in listdir(inputpath) if repatter.search(l)]
            for filename in filenames:
                pfile = PropertiesFile(name=filename)
                session.add(pfile)
            session.commit()
        
    
        # parse all files into db
        filenames = [f.name for f in session.getAllFiles()]
        print(filenames)
        for filename in filenames:
            
            filerecord = session.queryPropertiesFileByName(filename)
            if not filerecord:
                # filenames written in db should be registered ones
                raise AttributeError
            
            parseresult = parse(inputpath + filename)
            
            # properties: update(or create) key-value item
            for property in parseresult['properties']:
                
                # search from DB
                propertyRecord = session.queryProperty(filename, property['key'])
                if not propertyRecord:
                    propertyRecord = Property(name = property['key'])
                    filerecord.properties.append(propertyRecord)
                    session.add(filerecord)
                
                propertyRecord.line = property['line']
                propertyRecord.value = property['value']
                propertyRecord.hasArgs = getArgNum(propertyRecord.value) > 0
                propertyRecord.isMultiline = property['isMultiLine']
            
            # comments: create comment item(since comments db has already been deleted)
            for comment in parseresult['comments']:
                content = comment['content']
                commentRecord = Comment(
                        content = content,
                        line    = comment['line']
                )
                filerecord.comments.append(commentRecord)
                session.add(filerecord)
        
        session.commit()
    except OperationalError:
        print('Cannot Operate DB')

    # close session
    session.close()

def sqlite2properties(dbpath, outputpath):
    session = SessionWrapper(dbpath, False)
    
    try:    
        all_properties_files = session.getAllFiles()
        for properties_file in all_properties_files:
            try:
                with open(outputpath + properties_file.name, "w", encoding="utf-8") as fs:
                    # Get Properties
                    properties = session.queryProperties(properties_file.name)
                    
                    if (not properties) or (len(properties) == 0):
                        print("{0} has no properties".format(properties_file.name))
                        continue
                    
                    # Format Properties List
                    plist = [(p.line, "{0}={1}".format(p.name, p.value)) 
                        for p in properties]
                    
                    # Get Comments
                    comments = session.queryComments(properties_file.name)
                    
                    if (not comments) or (len(comments) == 0):
                        print("{0} has no comemnts".format(properties_file.name))
                    else:
                        # Format Comments List
                        clist = [(c.line, c.content) for c in comments]
                        
                        # Merge Properties And Comments(if exist)
                        plist.extend(clist)
                    
                    writeList = sorted(plist, key=lambda p:p[0])
                    
                    # Write File
                    write_line = 1
                    for item in writeList:
                        while write_line < item[0]:
                            fs.write('\n')
                            write_line += 1
                        fs.write(item[1] + '\n')
                        write_line += len(re.findall(r'\n', item[1])) + 1

            except IOError:
                print("Not Found File: {0}".format(properties_file.name))
    except OperationalError:
        print('Cannot Operate DB')
    
    session.close()


if __name__ == '__main__':
    # DIr/Pile Paths For Debug
    resourcedirpath = '../resource_ja/'
    ppath = resourcedirpath + 'messages/'
    dpath = resourcedirpath + 'output/properties_ja.sqlite3'
    
    # Parse Argument
    usage = """
python {0} [-init|-reverse] propertiesdir dbfile
    """.format(__file__)

    argparser = ArgumentParser(usage=usage)
    argparser.add_argument('propertiesdir', type=str, help='directory with properties files')
    argparser.add_argument('dbfile', type=str, help='sqlite3 db file')

    group = argparser.add_mutually_exclusive_group()
    group.add_argument('-init', action='store_true', help='clear db')
    group.add_argument('-reverse', action='store_true', help='execute db -> properties')

    args = argparser.parse_args()

    if args.init:
        init = True

    ppath = args.propertiesdir
    dpath = args.dbfile

    if args.reverse:
        sqlite2properties(dpath, ppath)
    else:
        properties2sqlite(dpath, ppath)
        init = False
    
    
    
    

    