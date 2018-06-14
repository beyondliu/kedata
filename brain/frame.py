

from brain.config import *
from brain.storage import *
from brain.snippet import Snippet

class Frame(Snippet):

    primary_key = 'id'
    fields = ('desc', 'vote', 'private', 'title', 'tags', 'attachment', 'children','init_time', 'update_time')       
 


    def __repr__(self):
        return "<Frame: %s>" % Frame.clean_fields(self.__dict__)    

  
    

    @property
    def vote(self):
        return self._vote 
   
    @vote.setter
    def vote(self, vote):
        pass
        # if hasattr(self, '_vote'):
        #     raise AttributeError("Can't set the vote of a frame! It has to be computed from its children!")
        # self._vote = vote
         

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, children):
        self._children = children

        
        # functools.reduce(sum, self.storage.get_snippet(child_id)['vote'] for child_id in children)
            

        self._vote = self._sum_of_vote(children)         


    def _sum_of_vote(self, children):
        sum_of_vote = 0
        for child_id in children:
            sn = self.get_storage().get_snippet(child_id)
            vote = sn.get('vote')
            if not vote:
                if sn.get('children'):
                    vote = self._sum_of_vote(sn.get('children'))
                else:
                    raise ValueError("Not a strictly valid snippet! No children and no vote at the same time!")    
            sum_of_vote += vote
        return sum_of_vote    

           

            