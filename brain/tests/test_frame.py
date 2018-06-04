#!/usr/bin/env python

import unittest
import time
from brain.mind import Mind
from brain.snippet import Snippet
from brain.frame import Frame

class TestFrame(unittest.TestCase):

    def setUp(self):
        self.mind = Mind('leon')
        #TODO:test if able to pass init_time and update_time (so far not supported)
        s = self.mind.create_snippet(desc='a test snippet', vote=2, tags=['language'], private=False, title="", attachment=None, url="https://git-scm.com/book/en/v7", children=None, context=None)
        fr = self.mind.create_frame(desc='a frame', private=False, title="a testing frame", attachment=None, children=[s.id])
        pfr = self.mind.create_frame(desc='a parent frame', private=False, title="a testing parent frame", attachment=None, children=[fr.id])
        self.sid = s.id
        self.fid = fr.id
        self.pfid = pfr.id
        self.assertIsInstance(self.fid, int)
        #wait for es to be updated
        time.sleep(6)
    
    def test_get_frame(self):        
        fr = self.mind.get_frame(self.fid)
        self.assertEqual(fr.vote, 2)
        self.assertEqual(fr.desc, 'a frame')
        self.assertFalse(fr.private)
         # self.assertListEqual(fr.tags, ['language'])
        self.assertEqual(fr.title, 'a testing frame')
        self.assertIsNone(fr.attachment)
        self.assertListEqual(fr.children, [self.sid])


    def test_get_frames(self):        
        frs = self.mind.get_frames(all="y")
        frids = [fr.id for fr in frs]
        self.assertIn(str(self.fid), frids)
        self.assertIn(str(self.pfid), frids)

    def test_update_frame(self):
        fr = self.mind.get_frame(self.fid)
        fr.title = 'testing updating the frame'
        fr.desc = 'testing updating the frame'
        fr.vote = 10 #vote shouldn't be modified. Vote should only be computed from the children
        fr.tags = ['play'] #tags also should only be computed from the children
        fr.private = True
        fr.save()
        time.sleep(6)
        updated_fr = self.mind.get_frame(self.fid)
        self.assertEqual(fr.vote, 2)
        self.assertEqual(fr.desc, 'testing updating the frame')
        self.assertTrue(fr.private)
        # self.assertListEqual(fr.tags, ['language'])
        self.assertEqual(fr.title, 'testing updating the frame')
        self.assertIsNone(fr.attachment)
        self.assertListEqual(fr.children, [self.sid])


    def test_add_children(self):
        fr = self.mind.get_frame(self.fid)
        fr.add_children([1,2,3]) #the availbility of children are not verified.         
        time.sleep(6)
        updated_fr = self.mind.get_frame(self.fid)
        self.assertListEqual(fr.children, [self.sid, 1, 2, 3])


    def test_remove_children(self):
        fr = self.mind.get_frame(self.fid)
        fr.remove_children([self.sid]) #can remove one child or a list of children        
        time.sleep(6)
        updated_fr = self.mind.get_frame(self.fid)
        self.assertListEqual(fr.children, [])


    def test_save_children_order(self):
        fr = self.mind.get_frame(self.fid)
        fr.add_children([1,2,3]) #the availbility of children are not verified.         
        time.sleep(6)
        updated_fr = self.mind.get_frame(self.fid)        
        updated_fr.save_children_order([3,2,1,self.sid])        
        time.sleep(6)
        updated_fr = self.mind.get_frame(self.fid)                
        self.assertListEqual(updated_fr.children, [3,2,1,self.sid])


    def test_get_related_frames(self):
        fr2 = self.mind.create_frame(desc='a frame', private=False, title="a testing frame", attachment=None, children=[self.sid])
        time.sleep(6)
        fr1 = self.mind.get_frame(self.fid)
        print('sid:%s, fr1.id: %s, fr2.id: %s' % (self.sid, fr1.id, fr2.id))
        print('fr1.children:', fr1.children)
        print('fr2.children:', fr2.children)
        self.assertIn(str(fr2.id), self.mind.get_related_frames(fr1.id))


    def test_in_frames(self):
        fr = self.mind.get_frame(self.fid)
        print('The frame is in frames:', fr.in_frames)
        self.assertIn(str(self.pfid), fr.in_frames)    

    
    def tearDown(self):
        print('tear down:', self.fid)
        fr = self.mind.get_frame(self.fid)
        fr.discard()
        pfr = self.mind.get_frame(self.pfid)
        pfr.discard()
        s = self.mind.get_snippet(self.sid)
        s.discard()        
        #wait for es to get updated
        time.sleep(6)        
        self.assertRaises(Frame.DoesNotExist, self.mind.get_frame, self.fid)
        self.assertRaises(Frame.DoesNotExist, self.mind.get_frame, self.pfid)
        self.assertRaises(Snippet.DoesNotExist, self.mind.get_snippet, self.sid)

    



if __name__ == "__main__":
    unittest.main()        