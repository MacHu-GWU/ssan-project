#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
requires:

- boto3
"""

from __future__ import print_function

import os, platform
from pprint import pprint as ppt

import boto3
from boto3.session import Session

if platform.system() == "Windows":
    is_win = True
    

class S3Client(object):
    def __init__(self, aws_access_key_id=None, 
                 aws_secret_access_key=None, 
                 region_name=None):        
        self.session = Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.s3 = self.session.resource("s3")
        
    def use_bucket(self, bucket_name):
        self.bucket = self.s3.Bucket(bucket_name)
    
    #--- Single Object Manipulation ---
    def put_file(self, key, abspath):
        """
        
        **中文文档**
        
        上传一个文件。注意, 如果Key已存在, 则原文件将会被覆盖。
        """
        self.bucket.Object(key=key).put(Body=open(abspath, "rb"))

    def put_object(self, key, content):
        """
        
        **中文文档**
        
        上传一个binary Object。注意, 如果Key已存在, 则原Object将会被覆盖。
        """
        self.bucket.Object(key=key).put(Body=content)
   
    def get_object(self, key):
        """

        **中文文档**
        
        获得一个Object。
        """
        obj = self.bucket.Object(key=key)
        res = obj.get()
        ppt(res)
        content = res["Body"].read()
        return content

    def del_object(self, key):
        """
        
        **中文文档**
        
        删除一个Object。
        """
        obj = self.bucket.Object(key=key)
        res = obj.delete()
        return res
  
    #--- Bulk Operation ---
    def get_all_object(self):
        """
        
        **中文文档**
        
        返回Bucket中的所有对象。对于大型Bucket, 请慎用此方法!
        """
        return self.bucket.objects.all()

    def get_objects_by_prefix(self, prefix):
        """
        
        **中文文档**
        
        返回Bucket中所有前缀匹配的对象的Key和Content。不包括目录对象。
        """
        col = list()
        for obj in self.bucket.objects.filter(Prefix=prefix):
            if not obj.key.endswith("/"):
                key = obj.key
                content = obj.get()["Body"].read()
                col.append((key, content))
        return col
    
    # --- Utility Method ---
    def sync_dir_to_bucket(self, key, abspath):
        """
        
        ***中文文档**
        
        将本地硬盘上的一个目录中的内容同步到Bucket中的一个目录中。
        """
        if not key.endswith("/"):
            key = key + "/"

        if not os.path.isdir(abspath):
            raise ValueError("'%s' is not a directory!" % abspath)

        for obj in self.bucket.objects.filter(Prefix=key):
            obj.delete()
            
        key_list, abspath_list = list(), list()
        for current_dir, folder_list, file_list in os.walk(abspath):
            for filename in file_list:
                path = os.path.join(current_dir, filename)
                relpath = os.path.relpath(path, abspath)
                obj_key = (key + relpath).replace("\\", "/")
                 
                key_list.append(obj_key)
                abspath_list.append(path)
         
        for key_, abspath_ in zip(key_list, abspath_list):
            self.put_file(key_, abspath_)
            
    def sync_bucket_to_dir(self, key, dir_path):
        """

        ***中文文档**
        
        将Bucket中的一个目录同步到本地硬盘上的一个目录中。
        """
        if not key.endswith("/"):
            raise ValueError("'%s' not ends with '/', "
                             "object key has to be a bucket!" % key)

        if not os.path.isdir(dir_path):
            raise ValueError("'%s' is not a directory!" % dir_path)
        
        for fname in os.listdir(dir_path):
            try:
                os.remove(os.path.join(dir_path, fname))
            except Exception as e:
                print(e)
        
        for key_, content in self.get_objects_by_prefix(prefix=key):
            key_ = key_.replace(key, "")
            if is_win:
                key_ = key_.replace("/", "\\")
            abspath = os.path.join(dir_path, key_)
            dirname = os.path.dirname(abspath)
             
            if not os.path.exists(dirname):
                os.mkdir(dirname)
             
            with open(abspath, "wb") as f:
                f.write(content)