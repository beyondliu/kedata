#!/usr/bin/env python

from pytz import timezone
from datetime import datetime
import itertools

from brain.snippet import *
from brain.tag import *
from brain.frame import *
from brain.storage import *


log = getlogger(__name__)

class Mind:
    """
    Mind can be stored on any kind of substance. More type of storage will be supported, for example gitlab hosted project files with search provided with es, 
    or local plain text files managed, with git with searching provided with sqlite, and etc.   
    """

    def __init__(self, username):    
        if not username:
            raise Exception('No username given!')    
        self.username = username
              
        self.storage = GitlabEsStorage(username) 

    # def get_note_cls(self, bookname='snippet'):   
    #     try:     
    #         return getNote(self.username, bookname)       
    #     except:
    #         raise Exception('Invalid username!')     

    
    def create_snippet(self, **kwargs):        
        desc = kwargs.get('desc')
        if not desc:
            raise Exception('desc is required!')                 
        now = timezone(TIME_ZONE).localize(datetime.now()).replace(microsecond=0).isoformat()            
        #TODO: consider case of bulk importing, which probably already have init_time and update_time
        kwargs = Snippet.clean_fields(kwargs)
        # if not kwargs.get('init_time'):    
        kwargs['init_time'] = now
        # if not kwargs.get('update_time'):
        kwargs['update_time'] = now   
        id = self.storage.create_snippet(**kwargs)      
        #Since there will be a delay for es to create this snippet after its creation in gitlab, here we
        # just construct a Snippet to return to user to use, instead of letting user to call get_snippet
        #immediately and get an Snippet.DoesNotExist error
        s = Snippet(self.username, id, **kwargs)        
        s.storage = self.storage
        return s

    def create_frame(self, **kwargs):        
        #TODO:check other fields
        s = self.create_snippet(**Frame.clean_fields(kwargs))
        f = Frame(self.username, s.id, **Frame.clean_fields(s.__dict__.copy()))
        f.storage = self.storage
        return f    
    
    def get_snippet(self, id): 
        """
        Can get a frame as well

        Failing get the snippet from es, will try to get the snippet from
        gitlab and also log the failure. TODO:
        """      
        try: 
            kwargs = self.storage.get_snippet(id)        
        except Storage.NotFoundError:
            raise Snippet.DoesNotExist  
        s = Snippet(self.username, id, **kwargs)        
        s.storage = self.storage
        return s
    
    #TODO:remove?
    def get_frame(self, id):
        return self.get_snippet(id)

    
    #TODO: use GitlabEsStorage as well
    def get_snippets(self, q='', tag_name=None, cache_id=None, order_by="init_date", page_size=50, page_no=1, all=None):
        """
        Can get frames as well
        """
        sns = self.storage.get_snippets(q=q, tag_name=tag_name, cache_id=cache_id, order_by=order_by, page_size=page_size, page_no=page_no, all=all)                            
        log.debug('Snippets found:%s', sns)                         
        snippets = [Snippet(self.username, **sn) for sn in sns]
        return snippets    
        # return SnippetList(snippets)
  
    def get_frames(self,  q='', tag_name=None, cache_id=None, order_by="init_date", page_size=50, page_no=1, all=None):
        frs = self.storage.get_frames(q=q, tag_name=tag_name, cache_id=cache_id, order_by=order_by, page_size=50, page_no=1, all=None)   
        log.debug('Frames found:%s', frs)                         
        frames = [Frame(self.username, **fr) for fr in frs]
        return frames


    @classmethod
    def display_snippets(cls, snippet, template="snippet.html", style="snippet_default.css"):
        pass


    def create_tag(self, **kwargs):
        name = kwargs.get('name')
        #should the logic below goes to Tag? TODO:
        if not name:
            raise Exception('name is required!')                 
        now = timezone(TIME_ZONE).localize(datetime.now()).replace(microsecond=0).isoformat()            
        #TODO: consider case of bulk importing, which probably already have init_time and update_time
        kwargs = Tag.clean_fields(kwargs)
        # if not kwargs.get('init_time'):    
        kwargs['init_time'] = now
        # if not kwargs.get('update_time'):
        kwargs['update_time'] = now   
        self.storage.create_tag(**kwargs)        
        # t = Tag(self.username, **kwargs)        
        # t.storage = self.storage
        return name

    def get_tag(self, name):
        try:
            tag_dict = self.storage.get_tag(name)
        except Storage.NotFoundError:
            raise Tag.DoesNotExist
        t = Tag(self.username, **tag_dict)
        t.storage = self.storage
        return t    

    def get_tags(self):
        tags_dict = self.storage.get_tags()
        tags = []   
        for tag_dict in tags_dict:
            tags.append(Tag(self.username, **tag_dict))
        return tags    

    def update_tag_name(self, name, new_name):
        if self.get_tag(name):                    
            if new_name and new_name != name:
                try:
                    #TODO:
                    self.get_tag(new_name)
                    raise Exception('The new tag name is existing!')
                except Tag.DoesNotExist:    
                    self.storage.update_tag_name(name, new_name)   
            return new_name
        else:
            raise Tag.DoesNotExist               
    
    #TODO:move this into Snippet?
    #TODO: optimize with searching in es directly
    def get_related_frames(self, id):
        fr = self.get_snippet(id)              
        l = list(set(itertools.chain.from_iterable([self.get_snippet(child_id).in_frames for child_id in fr.children])))
        l.remove(str(id))
        log.debug('Found related frames:%s', l)
        return l
                    

    def merge_tag(self, tag_name1, tag_name2, new_tag_name):
        oldnames = [tag_name1, tag_name2]
        if new_tag_name in oldnames:
            oldnames.remove(new_tag_name)
            oldname = oldnames[0]
            self.update_tag_name(oldname, new_tag_name)
        else:
            self.update_tag_name(tag_name1, new_tag_name)
            self.update_tag_name(tag_name2, new_tag_name)
                


    def remove_testing_tags(self):        
        ts = self.get_tags()
        print('tags:', [t.name for t in ts])
        for tag in ts:
            if 'test' in tag.name:
                tag.discard()
        time.sleep(6)        
        ts_new = self.get_tags()    
        print('tags after removing testing tags:', [t.name for t in ts_new])


    



if __name__ == '__main__':
    """
    Example:
        * python -m brain.mind remove_testing_tags
        * python -m brain.mind create_tag testupdatetagwork
        * python -m brain.mind update_tag_name testupdatetagwork testupdatetagworking
        * python -m brain.mind remove_testing_tags
        * python -m brain.mind
    """
    import sys
    mind = Mind('leon')
    if len(sys.argv) == 1:
        s = mind.create_snippet(desc='Programming language is similar to spoken language', vote=2, tags=['language'], private=False, title="", attachment=None, url="https://git-scm.com/book/en/v7", chilren=None, context=None)
        time.sleep(6)
        s1 = mind.get_snippet(s.id)
        print('s1:', s1)               
        s1.desc = 'Programming language is similar to spoken language!'
        s1.save()  
        #wait for es to be updated
        import time
        time.sleep(6)
        s2 = mind.get_snippet(s.id)
        print('s2:', s2)  
        snippets = mind.get_snippets()
        print('snippets:', snippets)   
        import random
        tag_name = mind.create_tag(name='testingtag'+str(random.randint(0, 10000)), desc='This is just a random tag for testing', private=False)       
        print('Tag %s created!', tag_name)
        time.sleep(6)
        t = mind.get_tag(tag_name)
        # new_name = 'testingtag'+str(random.randint(0, 10000))
        # t.name = new_name
        t.desc = 'Tagging is ok!'        
        t.private = True        
        t.save()
        #wait for es update
        time.sleep(6)
        updated_t = mind.get_tag(tag_name)        
        print('Tag updated:', updated_t.desc)
        updated_t.discard()
        time.sleep(6)
        mind.remove_testing_tags()
    else:
        command = sys.argv[1]
        if command == 'remove_testing_tags':
            mind.remove_testing_tags()
        elif command == 'create_tag':
            name = sys.argv[2]
            mind.create_tag(name=name)    
        elif command == 'update_tag_name':
            old_name = sys.argv[2]
            new_name = sys.argv[3]
            mind.update_tag_name(old_name, new_name)    
                    
        
        

        
    