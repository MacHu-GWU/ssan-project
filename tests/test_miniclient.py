#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ssan.s3client import S3Client
import os
import config


client = S3Client(aws_access_key_id=config.aws_access_key_id,
                  aws_secret_access_key=config.aws_secret_access_key,
                  region_name=config.region_name)
client.use_bucket("eni.e5")

def test_put():
    client.put_file(key="e5SanheDataScience/S3Demo/test1.txt", abspath="test1.txt")
    client.put_object(key="e5SanheDataScience/S3Demo/test2.txt", content="test2")

# test_put()

def test_get():
    content = client.get_object(key="e5SanheDataScience/S3Demo/test1.txt")
    print(content)
    
# test_get()

def test_del():
    client.del_object(key="e5SanheDataScience/S3Demo/test1.txt")
    
# test_del()

def test_get_all_object():
    for obj in client.get_all_object():
        print(obj)

# test_get_all_object()

def test_get_objects_by_prefix():
    prefix="e5SanheDataScience/S3Demo/"
    for key, content in client.get_objects_by_prefix(prefix=prefix):
        print(key, content)

# test_get_objects_by_prefix()

dir_path = os.path.dirname(os.getcwd())
s3_key = "e5SanheDataScience/S3Demo/ssan-project/"

def test_sync_dir_to_bucket():
    client.sync_dir_to_bucket(key=s3_key, dir_path=dir_path)
    
# test_sync_dir_to_bucket()

def test_sync_bucket_to_dir():
    dir_path = os.path.abspath("downloaded")
    client.sync_bucket_to_dir(key=s3_key, dir_path=dir_path)
    
# test_sync_bucket_to_dir()