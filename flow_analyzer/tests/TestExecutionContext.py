import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.ExecutionContext import ExecutionContext
from model.Frame import Frame

class TestExecutionContext(unittest.TestCase):

    def test_insert_topframe(self):
        """
        top
        """
        ctx = ExecutionContext()
        frame = Frame()
        ctx.insert_frame("top", frame)

        self.assertIsNotNone(ctx.topframe)
        self.assertEqual(ctx.topframe.hierarchy(), "top")

    def test_insert_iframe(self):
        """
        top
            -> frames[0]
        """
        ctx = ExecutionContext()
        frame = Frame()
        ctx.insert_frame("top.frames[0]", frame)

        self.assertIsNotNone(ctx.topframe)
        self.assertEqual(ctx.topframe.hierarchy(), "top")
        self.assertIsNotNone(ctx.topframe.frames[0])
        self.assertEqual(ctx.topframe.frames[0].hierarchy(), "top.frames[0]")

    def test_insert_two_iframes(self):
        """
        top
            -> frames[0]
            -> frames[1]
        """
        ctx = ExecutionContext()
        frame0 = Frame()
        frame1 = Frame()
        ctx.insert_frame("top.frames[0]", frame0)
        ctx.insert_frame("top.frames[1]", frame1)

        self.assertIsNotNone(ctx.topframe)
        self.assertEqual(ctx.topframe.hierarchy(), "top")
        self.assertIsNotNone(ctx.topframe.frames[0])
        self.assertIsNotNone(ctx.topframe.frames[1])
        self.assertEqual(ctx.topframe.frames[0].hierarchy(), "top.frames[0]")
        self.assertEqual(ctx.topframe.frames[1].hierarchy(), "top.frames[1]")
    
    def test_insert_popup(self):
        """
        top
            -> popups[0]
        """
        ctx = ExecutionContext()
        frame = Frame()
        ctx.insert_frame("top.popups[0]", frame)

        self.assertIsNotNone(ctx.topframe)
        self.assertEqual(ctx.topframe.hierarchy(), "top")
        self.assertIsNotNone(ctx.topframe.popups[0])
        self.assertEqual(ctx.topframe.popups[0].hierarchy(), "top.popups[0]")
    
    def test_insert_two_popups(self):
        """
        top
            -> popups[0]
            -> popups[1]
        """
        ctx = ExecutionContext()
        frame0 = Frame()
        frame1 = Frame()
        ctx.insert_frame("top.popups[0]", frame0)
        ctx.insert_frame("top.popups[1]", frame1)

        self.assertIsNotNone(ctx.topframe)
        self.assertEqual(ctx.topframe.hierarchy(), "top")
        self.assertIsNotNone(ctx.topframe.popups[0])
        self.assertIsNotNone(ctx.topframe.popups[1])
        self.assertEqual(ctx.topframe.popups[0].hierarchy(), "top.popups[0]")
        self.assertEqual(ctx.topframe.popups[1].hierarchy(), "top.popups[1]")
    
    def test_insert_remove_multiple(self):
        """
        top
            -> popups[0]
                -> frames[0]
                    -> frames[0]
                        -> popups[0]
                    -> frames[1]
            -> popups[1]
                -> frames[0]
                -> frames[1]
            -> frames[0]
            -> frames[1]
            -> frames[2]
        """
        ctx = ExecutionContext()
        frame0 = Frame()
        frame1 = Frame()
        frame2 = Frame()
        frame3 = Frame()
        frame4 = Frame()
        frame5 = Frame()
        frame6 = Frame()
        ctx.insert_frame("top.popups[0].frames[0].frames[0].popups[0]", frame0)
        ctx.insert_frame("top.popups[0].frames[0].frames[1]", frame1)
        ctx.insert_frame("top.popups[1].frames[0]", frame2)
        ctx.insert_frame("top.popups[1].frames[1]", frame3)
        ctx.insert_frame("top.frames[0]", frame4)
        ctx.insert_frame("top.frames[1]", frame5)
        ctx.insert_frame("top.frames[2]", frame6)

        self.assertIsNotNone(ctx.topframe)
        self.assertIsNotNone(ctx.topframe.popups[0])
        self.assertIsNotNone(ctx.topframe.popups[0].frames[0])
        self.assertIsNotNone(ctx.topframe.popups[0].frames[0].frames[0])
        self.assertIsNotNone(ctx.topframe.popups[0].frames[0].frames[0].popups[0])
        self.assertIsNotNone(ctx.topframe.popups[0].frames[0].frames[1])
        self.assertIsNotNone(ctx.topframe.popups[1])
        self.assertIsNotNone(ctx.topframe.popups[1].frames[0])
        self.assertIsNotNone(ctx.topframe.popups[1].frames[1])
        self.assertIsNotNone(ctx.topframe.frames[0])
        self.assertIsNotNone(ctx.topframe.frames[1])
        self.assertIsNotNone(ctx.topframe.frames[2])
        
        self.assertEqual(ctx.topframe.hierarchy(), "top")
        self.assertEqual(ctx.topframe.popups[0].hierarchy(), "top.popups[0]")
        self.assertEqual(ctx.topframe.popups[0].frames[0].hierarchy(), "top.popups[0].frames[0]")
        self.assertEqual(ctx.topframe.popups[0].frames[0].frames[0].hierarchy(), "top.popups[0].frames[0].frames[0]")
        self.assertEqual(ctx.topframe.popups[0].frames[0].frames[0].popups[0].hierarchy(), "top.popups[0].frames[0].frames[0].popups[0]")
        self.assertEqual(ctx.topframe.popups[0].frames[0].frames[1].hierarchy(), "top.popups[0].frames[0].frames[1]")
        self.assertEqual(ctx.topframe.popups[1].hierarchy(), "top.popups[1]")
        self.assertEqual(ctx.topframe.popups[1].frames[0].hierarchy(), "top.popups[1].frames[0]")
        self.assertEqual(ctx.topframe.popups[1].frames[1].hierarchy(), "top.popups[1].frames[1]")
        self.assertEqual(ctx.topframe.frames[0].hierarchy(), "top.frames[0]")
        self.assertEqual(ctx.topframe.frames[1].hierarchy(), "top.frames[1]")
        self.assertEqual(ctx.topframe.frames[2].hierarchy(), "top.frames[2]")

        ctx.remove_frame("top.popups[0].frames[0]") # frame 0 and 1 should be deleted
        ctx.remove_frame("top.popups[1].frames[0]") # frame 2 should be deleted
        ctx.remove_frame("top.frames[1]") # frame 5 should be deleted

        self.assertListEqual(ctx.topframe.popups[0].frames, [])
        
        self.assertListEqual(ctx.topframe.popups[1].frames, [frame3])
        self.assertEqual(ctx.topframe.popups[1].frames[0], frame3)
        self.assertEqual(ctx.topframe.popups[1].frames[0].hierarchy(), "top.popups[1].frames[0]")

        self.assertListEqual(ctx.topframe.frames, [frame4, frame6])

        ctx.remove_frame("top.popups[0]")
        self.assertNotIn(0, ctx.topframe.popups)

        ctx.remove_frame("top.popups[1]")
        self.assertNotIn(1, ctx.topframe.popups)

        self.assertDictEqual(ctx.topframe.popups, {})

    def test_overwrite_iframe(self):
        ctx = ExecutionContext()
        
        frame0 = Frame()
        ctx.insert_frame("top.popups[0].frames[0]", frame0)
        self.assertIsNotNone(ctx.topframe.popups[0].frames[0])
        self.assertEqual(ctx.topframe.popups[0].frames[0].hierarchy(), "top.popups[0].frames[0]")
        self.assertIsNone(ctx.topframe.popups[0].frames[0].href)
        self.assertIsNone(ctx.topframe.popups[0].frames[0].html)

        frame0_new = Frame(href="http://frame0.com", html="<html>frame0</html>")
        ctx.insert_frame("top.popups[0].frames[0]", frame0_new)
        self.assertIsNotNone(ctx.topframe.popups[0].frames[0])
        self.assertEqual(ctx.topframe.popups[0].frames[0].hierarchy(), "top.popups[0].frames[0]")
        self.assertEqual(ctx.topframe.popups[0].frames[0].href, "http://frame0.com")
        self.assertEqual(ctx.topframe.popups[0].frames[0].html, "<html>frame0</html>")

    def test_overwrite_popup(self):
        ctx = ExecutionContext()
        
        popup0 = Frame()
        ctx.insert_frame("top.popups[0]", popup0)
        self.assertIsNotNone(ctx.topframe.popups[0])
        self.assertEqual(ctx.topframe.popups[0].hierarchy(), "top.popups[0]")
        self.assertIsNone(ctx.topframe.popups[0].href)
        self.assertIsNone(ctx.topframe.popups[0].html)

        popup0_new = Frame(href="http://popup0.com", html="<html>popup0</html>")
        ctx.insert_frame("top.popups[0]", popup0_new)
        self.assertIsNotNone(ctx.topframe.popups[0])
        self.assertEqual(ctx.topframe.popups[0].hierarchy(), "top.popups[0]")
        self.assertEqual(ctx.topframe.popups[0].href, "http://popup0.com")
        self.assertEqual(ctx.topframe.popups[0].html, "<html>popup0</html>")

    def test_get_frame(self):
        ctx = ExecutionContext()

        frame0 = Frame(href="http://frame0.com", html="<html>frame0</html>")
        ctx.insert_frame("top.popups[0].frames[0]", frame0)

        frame0_get = ctx.get_frame("top.popups[0].frames[0]")
        self.assertIsNotNone(frame0_get)
        self.assertEqual(frame0_get.hierarchy(), "top.popups[0].frames[0]")
        self.assertEqual(frame0_get.href, "http://frame0.com")
        self.assertEqual(frame0_get.html, "<html>frame0</html>")

        self.assertIsNotNone(ctx.get_frame("top.popups[0]"))
        self.assertEqual(ctx.get_frame("top.popups[0]").hierarchy(), "top.popups[0]")
        
        self.assertIsNotNone(ctx.get_frame("top"))
        self.assertEqual(ctx.get_frame("top").hierarchy(), "top")

    def test_dump_ctx(self):
        ctx = ExecutionContext()

        frame0 = Frame()
        frame1 = Frame()
        frame2 = Frame()
        frame3 = Frame()
        frame4 = Frame()
        ctx.insert_frame("top.popups[0].frames[0].frames[0]", frame0)
        ctx.insert_frame("top.popups[0].frames[0].frames[1]", frame1)
        ctx.insert_frame("top.popups[0].frames[1]", frame2)
        ctx.insert_frame("top.frames[0]", frame3)
        ctx.insert_frame("top.frames[1]", frame4)

        ctx_str = str(ctx)
        print("Output: test_dump_ctx")
        print(ctx_str)

    def test_update_frame(self):
        ctx = ExecutionContext()

        frame0 = Frame(href="http://frame0.com", html="<html>frame0</html>")
        frame1 = Frame(href="http://frame1.com", html="<html>frame1</html>")
        frame2 = Frame(href="http://frame2.com", html="<html>frame2</html>")
        ctx.insert_frame("top.frames[0].frames[0]", frame0)
        ctx.insert_frame("top.frames[0]", frame1)
        ctx.insert_frame("top", frame2)

        self.assertIsNotNone(ctx.topframe)
        self.assertIsNotNone(ctx.topframe.frames[0])
        self.assertIsNotNone(ctx.topframe.frames[0].frames[0])
        
        self.assertNotEqual(ctx.topframe, frame2)
        self.assertNotEqual(ctx.topframe.frames[0], frame1)
        self.assertEqual(ctx.topframe.frames[0].frames[0], frame0)

        self.assertEqual(ctx.topframe.href, "http://frame2.com")
        self.assertEqual(ctx.topframe.html, "<html>frame2</html>")

        self.assertEqual(ctx.topframe.frames[0].href, "http://frame1.com")
        self.assertEqual(ctx.topframe.frames[0].html, "<html>frame1</html>")

        self.assertEqual(ctx.topframe.frames[0].frames[0].href, "http://frame0.com")
        self.assertEqual(ctx.topframe.frames[0].frames[0].html, "<html>frame0</html>")

if __name__ == "__main__":
    unittest.main()
