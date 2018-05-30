

from brain.config import *
from brain.storage import *
from brain.snippet import Snippet

class Frame(Snippet):

    primary_key = 'id'
    fields = ('desc', 'vote', 'private', 'title', 'tags', 'attachment', 'children','init_time', 'update_time')
       
    
    # def add_children(self, children):
    #     self.get_storage().add_children(children)

    # def remove_children(self, children):
    #     self.get_storage.remove_children(children)    

    

    # def save_children_order(self):
    #     pass


    def __repr__(self):
        return "<Frame: %s>" % Frame.clean_fields(self.__dict__)    

  
            