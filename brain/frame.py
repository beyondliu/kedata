

from brain.config import *
from brain.storage import *
from brain.snippet import Snippet

class Frame(Snippet):

    primary_key = 'id'
    fields = ('desc', 'vote', 'private', 'title', 'tags', 'attachment', 'children','init_time', 'update_time')       
 


    def __repr__(self):
        return "<Frame: %s>" % Frame.clean_fields(self.__dict__)    

  
            